from dotenv import load_dotenv
load_dotenv()

import os
import json
from typing import Dict
from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools import tool


# Calculator tool: performs add, subtract, multiply, divide
@tool(name="calculator", description="Performs arithmetic operations. Input: '{\"a\":4,\"b\":2,\"operation\":\"add\"}'")
def calculator(input: str) -> Dict:
    print("Calculator tool called with input:", input)
    try:
        data = json.loads(input)
        a = data.get("a")
        b = data.get("b")
        operation = data.get("operation")

        if a is None or b is None or operation is None:
            return {"error": "Missing 'a', 'b', or 'operation'."}

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return {"error": "Division by zero is not allowed."}
            result = a / b
        else:
            return {"error": f"Unsupported operation: {operation}"}

        return {"result": result}
    except Exception as e:
        return {"error": str(e)}


# Mock API tool: returns echo with name and id
@tool(name="mock_api", description="Returns a mock message with name and id.")
def mock_api(name: str, id: int) -> Dict:
    return {
        "message": "Hello from the mock API!",
        "name": name,
        "id": id
    }


agent = Agent(
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
    ),
    tools=[calculator, mock_api],
    instructions=[
        "You are a helpful Orchestrator AI agent.",
        "If the user input matches a tool (calculator or mock_api), call that tool with appropriate input.",
        "If the user greets (e.g., 'hi', 'hello', 'hey', 'good morning'), respond naturally like 'Hello! How can I assist you today?'. Do not use any tool for this.",
        "If the user asks something unrelated to available tools (e.g., weather, time, general trivia), respond: 'I don't know how to answer that question.'",
        "Only call tools when absolutely needed. Otherwise, respond directly.",
        "Avoid hallucination. Do not invent tool responses or make up facts.",
    ],
    markdown=True,
)


# Test inputs
inputs = [
    "Hello",
    "Add 5 and 10",
    "What is the product of 4 and 6?",
    "I am abinash and I want to subtract 8 from 20",
    "Can you divide 100 by 4?",
    "Good morning, tell me about yourself",
    "Hi there, can you help me?",
    "I am abinash with id 121"
]

# Run and print responses
for user_input in inputs:
    print(f"\n🧠 User: {user_input}")
    try:
        response = agent.run(user_input)
        print(f"🤖 Agent: {response.content}")
    except Exception as e:
        print("Agent call failed with error:", e)