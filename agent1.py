from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
import pandas as pd
import streamlit as st
from typing import Literal
from dotenv import load_dotenv

# LangChain & LangGraph Imports
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool, ListSQLDatabaseTool, QuerySQLDatabaseTool
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import InMemorySaver

# 1. SETUP & LUXURY UI CSS
load_dotenv()
st.set_page_config(page_title="Nexus AI Dashboard", layout="wide", page_icon="💠")

st.markdown("""
    <style>
    /* Global Background & Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    
    .stApp { background-color: #080808; color: #ffffff; }
    
    /* Sidebar Styling (Image 4 Style) */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    
    /* Logo / Brand */
    .brand {
        font-size: 24px;
        font-weight: 700;
        background: linear-gradient(to right, #8A2BE2, #FF8C00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 30px;
    }

    /* Glassmorphic Dashboard Cards (Image 2/4 Style) */
    .stat-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transition: 0.3s;
    }
    .stat-card:hover { border: 1px solid #8A2BE2; background: rgba(138, 43, 226, 0.05); }

    /* The "World-Class" Glowy Pill Input (Image 1 Style) */
    div[data-testid="stChatInput"] {
        border-radius: 50px !important;
        border: 1px solid transparent !important;
        background-image: linear-gradient(#080808, #080808), 
                          linear-gradient(135deg, #8A2BE2, #FF8C00) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
        box-shadow: 0 0 30px rgba(138, 43, 226, 0.15) !important;
        padding: 5px !important;
    }

    /* Chat Messages */
    .stChatMessage { border-radius: 15px !important; border: 1px solid #222 !important; margin-bottom: 10px !important; }
    .stChatMessage.assistant { background: rgba(138, 43, 226, 0.02) !important; border-left: 4px solid #8A2BE2 !important; }
    
    /* Buttons */
    .stButton>button {
        border-radius: 10px;
        background: #1A1A1A;
        color: white;
        border: 1px solid #333;
        transition: 0.3s;
    }
    .stButton>button:hover { border-color: #8A2BE2; color: #8A2BE2; }
    </style>
""", unsafe_allow_html=True)

# 2. DATABASE LOGIC
def init_db():
    conn = sqlite3.connect("nexus_students.db")
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS departments (id INTEGER PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY, name TEXT, dept_id INTEGER, 
            grade TEXT, course TEXT, FOREIGN KEY (dept_id) REFERENCES departments(id)
        );
        INSERT OR IGNORE INTO departments VALUES (1, 'Computer Science'), (2, 'Mathematics');
        INSERT OR IGNORE INTO students (name, dept_id, grade, course) VALUES 
        ('Alice', 1, 'A', 'Quantum Computing'), ('Bob', 1, 'B', 'Cyber Security'),
        ('Charlie', 2, 'A', 'Advanced Calculus'), ('David', 2, 'C', 'Statistics');
    """)
    conn.commit()
    conn.close()
    return SQLDatabase.from_uri("sqlite:///nexus_students.db")

# 3. UPDATED AGENT LOGIC (FIXED MODEL)
def get_nexus_agent(api_key, db):
    # CHANGED: Using llama-3.3-70b-versatile (The current Groq standard)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0, 
        groq_api_key=api_key
    )
    
    sql_db_query = QuerySQLDatabaseTool(db=db)
    sql_db_schema = InfoSQLDatabaseTool(db=db)
    sql_db_list_tables = ListSQLDatabaseTool(db=db)

    def list_tables_node(state: MessagesState):
        return {"messages": [AIMessage(content=sql_db_list_tables.invoke(""))]}

    def generate_query_node(state: MessagesState):
        sys_msg = SystemMessage(content="You are Nexus AI, a SQL expert. Use sql_db_query tool to answer questions.")
        return {"messages": [llm.bind_tools([sql_db_query]).invoke([sys_msg] + state["messages"])]}

    builder = StateGraph(MessagesState)
    builder.add_node("list_tables", list_tables_node)
    builder.add_node("get_schema", ToolNode([sql_db_schema]))
    builder.add_node("generate_query", generate_query_node)
    builder.add_node("run_query", ToolNode([sql_db_query]))

    builder.add_edge(START, "list_tables")
    builder.add_edge("list_tables", "get_schema")
    builder.add_edge("get_schema", "generate_query")
    builder.add_conditional_edges("generate_query", 
        lambda s: "run_query" if getattr(s["messages"][-1], 'tool_calls', None) else END)
    builder.add_edge("run_query", "generate_query")

    return builder.compile(checkpointer=InMemorySaver())

# 4. STATE & APP LOGIC
if "sessions" not in st.session_state:
    st.session_state.sessions = {"General": []}
if "active_id" not in st.session_state:
    st.session_state.active_id = "General"
if "db" not in st.session_state:
    st.session_state.db = init_db()

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="brand">💠 NEXUS PRO</div>', unsafe_allow_html=True)
    
    # API KEY HANDLING
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        api_key = st.text_input("Groq API Key", type="password")

    if st.button("＋ New Session", use_container_width=True):
        new_id = f"Session {len(st.session_state.sessions) + 1}"
        st.session_state.sessions[new_id] = []
        st.session_state.active_id = new_id

    st.markdown("### History")
    for sid in reversed(list(st.session_state.sessions.keys())):
        style = "border-color: #8A2BE2;" if sid == st.session_state.active_id else ""
        if st.button(f"󱜚 {sid}", key=sid, use_container_width=True):
            st.session_state.active_id = sid

    st.divider()
    if st.button("🗑 Reset Database"):
        st.session_state.db = init_db()
        st.rerun()

# MAIN CONTENT (Image 4 Dashboard Look)
col1, col2, col3 = st.columns(3)
with col1: st.markdown('<div class="stat-card"><h3>340</h3><p>Total Executions</p></div>', unsafe_allow_html=True)
with col2: st.markdown('<div class="stat-card"><h3>12</h3><p>Active Workflows</p></div>', unsafe_allow_html=True)
with col3: st.markdown('<div class="stat-card"><h3>100%</h3><p>Success Rate</p></div>', unsafe_allow_html=True)

st.divider()

# CHAT AREA
chat_placeholder = st.container()
with chat_placeholder:
    for msg in st.session_state.sessions[st.session_state.active_id]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# INPUT AREA
if prompt := st.chat_input("Tell us about your capabilities..."):
    if not api_key:
        st.error("Please provide a Groq API Key in the sidebar or .env file.")
    else:
        # User input
        st.session_state.sessions[st.session_state.active_id].append({"role": "user", "content": prompt})
        with chat_placeholder:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Agent response
        with chat_placeholder:
            with st.chat_message("assistant"):
                try:
                    agent = get_nexus_agent(api_key, st.session_state.db)
                    config = {"configurable": {"thread_id": st.session_state.active_id}}
                    
                    full_text = ""
                    with st.status("💠 Analyzing Request...", expanded=False) as status:
                        # Prepare message history for the agent
                        agent_input = {"messages": [HumanMessage(content=prompt)]}
                        
                        for event in agent.stream(agent_input, config, stream_mode="values"):
                            msg = event["messages"][-1]
                            
                            # Log tool usage
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                for tool in msg.tool_calls:
                                    st.code(tool['args'].get('query', 'Scanning schema...'), language="sql")
                            
                            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                                full_text = msg.content
                        
                        status.update(label="✅ Computation Complete", state="complete")
                    
                    st.markdown(full_text)
                    st.session_state.sessions[st.session_state.active_id].append({"role": "assistant", "content": full_text})
                
                except Exception as e:
                    st.error(f"Nexus encountered an error: {str(e)}")