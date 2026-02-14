import os
import json
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.prebuilt import create_react_agent
from server.tools import ALL_TOOLS, DB_PATH

PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "..", "prompts", "system_prompt.txt")


def get_system_prompt():
    with open(PROMPTS_PATH, "r") as f:
        return f.read().strip()


def get_llm():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "ollama":
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.1,
        )
    else:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.1,
        )


def create_agent():
    llm = get_llm()
    system_prompt = get_system_prompt()
    agent = create_react_agent(llm, ALL_TOOLS, state_modifier=system_prompt)
    return agent


agent_executor = None


def get_agent():
    global agent_executor
    if agent_executor is None:
        agent_executor = create_agent()
    return agent_executor


def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
    finally:
        conn.close()


def save_tool_call(session_id: str, name: str, args_json: str, result_json: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT INTO tool_calls (session_id, name, args_json, result_json) VALUES (?, ?, ?, ?)",
            (session_id, name, args_json, result_json)
        )
        conn.commit()
    finally:
        conn.close()


def load_chat_history(session_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at ASC",
            (session_id,)
        ).fetchall()
        
        messages = []
        for row in rows:
            if row["role"] == "user":
                messages.append(HumanMessage(content=row["content"]))
            elif row["role"] == "assistant":
                messages.append(AIMessage(content=row["content"]))
        return messages
    finally:
        conn.close()


def get_sessions():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT DISTINCT session_id, MIN(created_at) as started, 
               COUNT(*) as message_count 
               FROM messages 
               GROUP BY session_id 
               ORDER BY MAX(created_at) DESC"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


async def chat(session_id: str, user_message: str):
    agent = get_agent()
    
    save_message(session_id, "user", user_message)
    
    history = load_chat_history(session_id)
    
    input_messages = {"messages": history}
    
    result = await agent.ainvoke(input_messages)
    
    response_messages = result["messages"]
    
    assistant_response = ""
    tool_calls_made = []
    
    for msg in response_messages:
        if isinstance(msg, AIMessage) and msg.content:
            assistant_response = msg.content
        if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_calls_made.append({
                    "name": tc["name"],
                    "args": tc["args"]
                })
        if isinstance(msg, ToolMessage):
            if tool_calls_made:
                last_tc = tool_calls_made[-1]
                save_tool_call(
                    session_id,
                    last_tc["name"],
                    json.dumps(last_tc["args"]),
                    msg.content
                )
    
    if assistant_response:
        save_message(session_id, "assistant", assistant_response)
    
    return {
        "response": assistant_response,
        "tool_calls": tool_calls_made
    }