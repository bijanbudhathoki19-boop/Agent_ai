import os
import logging
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from sqlalchemy import create_engine, text, inspect
from langchain_openai import ChatOpenAI
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

# Configure logging - only to file, minimal format
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s', 
    handlers=[
        logging.FileHandler('sql_agent.log')
    ]
)
logger = logging.getLogger(__name__)

api_key = os.getenv("OPENAI_API_KEY")

# Initialize your LLM
model = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0)

# Store generated queries for logging
generated_queries = []

# Detect database type from connection URI
def get_db_type(connection_uri: str) -> str:
    """Detect database type from connection URI"""
    if connection_uri.startswith('sqlite'):
        return 'sqlite'
    elif connection_uri.startswith('postgresql') or connection_uri.startswith('postgres'):
        return 'postgresql'
    else:
        return 'unknown'

# Universal SQL execution tool for SQLite and PostgreSQL
def sqlalchemy_execute_query(input_string: str) -> str:
    """
    Executes any SQL query on SQLite or PostgreSQL database including schema queries and data queries.
    Input format: 'SQL_QUERY|||CONNECTION_URI'
    """
    try:
        parts = input_string.split("|||")
        if len(parts) != 2:
            return "Error: Please provide input in format 'SQL_QUERY|||CONNECTION_URI'"
        
        query, connection_uri = parts[0].strip(), parts[1].strip()
        db_type = get_db_type(connection_uri)
        
        # Store non-schema queries (the actual data queries)
        query_upper = query.strip().upper()
        is_schema_query = (
            query_upper.startswith('PRAGMA') or
            'SQLITE_MASTER' in query_upper or
            'INFORMATION_SCHEMA.TABLES' in query_upper or
            'INFORMATION_SCHEMA.COLUMNS' in query_upper or
            'INFORMATION_SCHEMA.TABLE_CONSTRAINTS' in query_upper or
            'INFORMATION_SCHEMA.KEY_COLUMN_USAGE' in query_upper or
            'INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE' in query_upper
        )
        
        if not is_schema_query and 'SELECT' in query_upper and 'FROM' in query_upper:
            generated_queries.append(query)
        
        engine = create_engine(connection_uri)
        with engine.connect() as connection:
            result = connection.execute(text(query))
            
            # Handle SELECT queries and schema queries
            if query.strip().upper().startswith(('SELECT', 'PRAGMA', 'SHOW', 'DESCRIBE', 'EXPLAIN', 'WITH')):
                rows = result.fetchall()
                columns = result.keys()
                
                if not rows:
                    return "Query executed successfully. No rows returned."
                
                # Create formatted output
                output = f"Results ({len(rows)} rows):\n\n"
                output += " | ".join(columns) + "\n"
                output += "-" * (len(" | ".join(columns))) + "\n"
                
                for row in rows[:100]:
                    output += " | ".join(str(val) if val is not None else "NULL" for val in row) + "\n"
                
                if len(rows) > 100:
                    output += f"\n... and {len(rows) - 100} more rows"
                
                return output
            else:
                # Handle INSERT, UPDATE, DELETE queries
                connection.commit()
                return f"Query executed successfully. Rows affected: {result.rowcount}"
        
    except Exception as e:
        error_msg = str(e)
        
        # Provide helpful hints for common errors
        if "no such table" in error_msg.lower() or "does not exist" in error_msg.lower():
            if db_type == 'sqlite':
                return f"Error: Table does not exist. Please check your SQLite database schema. Details: {error_msg}"
            elif db_type == 'postgresql':
                return f"Error: Table does not exist. Please check your PostgreSQL database schema. Details: {error_msg}"
        elif "syntax error" in error_msg.lower():
            return f"Error: SQL syntax error. Please check your query syntax. Details: {error_msg}"
        elif "permission denied" in error_msg.lower():
            return f"Error: Permission denied. Please check your database user permissions. Details: {error_msg}"
        else:
            return f"Error executing query: {error_msg}"