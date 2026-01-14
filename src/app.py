"""
AutoStream AI Agent - Simple RAG-powered agent with tool calling

Flow:
1. User sends message
2. Retrieve relevant chunks from ChromaDB  
3. Pass context + system prompt + conversation history to LLM
4. LLM responds naturally and calls lead_capture tool when ready
5. Show both tool result AND LLM's text response to user
"""

import sys
import os
import json
from typing import Optional, Dict, Any

# Ensure project root is on sys.path so `src` package imports work
# when the file is executed directly (e.g. `chainlit run src/app.py`).
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import chainlit as cl
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage

from src.config.settings import get_settings
from src.services.vector_store import VectorStoreManager
from src.utils.prompt_loader import PromptLoader
from src.tools.lead_capture import lead_capture_tool


# Initialize services
settings = get_settings()
vector_store_manager = VectorStoreManager()
prompt_loader = PromptLoader()


@cl.on_chat_start
async def start():
    """Initialize agent when chat starts"""
    
    await cl.Message(content="🎬 **Initializing AutoStream AI Assistant...**").send()
    
    try:
        # Initialize vector store
        vector_store = vector_store_manager.initialize_vector_store()
        
        # Initialize LLM with tool calling
        llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.7,
            api_key=settings.openai_api_key
        ).bind_tools([lead_capture_tool])
        
        # Load system prompt
        system_prompt = prompt_loader.load_prompt("system_prompt.md")
        
        # Store in session
        cl.user_session.set("vector_store", vector_store)
        cl.user_session.set("llm", llm)
        cl.user_session.set("system_prompt", system_prompt)
        cl.user_session.set("conversation_history", [])
        
        await cl.Message(
            content=(
                "✅ **Ready!**\n\n"
                "I'm your AutoStream AI assistant. I can help you with:\n"
                "- Product features and capabilities\n"
                "- Pricing plans (Basic $29/mo, Pro $79/mo)\n"
                "- Policies and support questions\n"
                "- Getting started with AutoStream\n\n"
                "What would you like to know?"
            )
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **Error:** {str(e)}\n\nPlease check your environment configuration."
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages"""
    
    # Get session data
    vector_store = cl.user_session.get("vector_store")
    llm = cl.user_session.get("llm")
    system_prompt = cl.user_session.get("system_prompt")
    conversation_history = cl.user_session.get("conversation_history", [])
    
    if not llm or not vector_store:
        await cl.Message(content="Please refresh the page to restart.").send()
        return
    
    # Step 1: Retrieve relevant context from ChromaDB
    docs = vector_store.similarity_search(message.content, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Step 2: Build messages for LLM
    messages = [SystemMessage(content=system_prompt)]
    
    # Add conversation history
    messages.extend(conversation_history)
    
    # Add current message with context
    user_message_with_context = f"""User Query: {message.content}

Relevant Knowledge Base Context:
{context}

Answer the user's query naturally using the context provided. If the user is ready to sign up and you have their name, email, and platform, call the lead_capture tool."""
    
    messages.append(HumanMessage(content=user_message_with_context))
    
    # Step 3: Get LLM response
    try:
        response = await llm.ainvoke(messages)
        
        # Extract text content for display
        response_text = response.content if response.content else ""
        
        # Step 4: Handle tool calls if present
        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "lead_capture_tool":
                    # Execute the tool
                    args = tool_call["args"]
                    tool_result = lead_capture_tool.invoke(args)
                    
                    # Add tool call and result to messages
                    messages.append(response)
                    messages.append(ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    ))
                    
                    # Get final response from LLM after tool execution
                    final_response = await llm.ainvoke(messages)
                    response_text = final_response.content
                    
                    # Update conversation history with tool interaction
                    conversation_history.append(HumanMessage(content=message.content))
                    conversation_history.append(response)
                    conversation_history.append(ToolMessage(
                        content=tool_result,
                        tool_call_id=tool_call["id"]
                    ))
                    conversation_history.append(final_response)
                    
                    break
        else:
            # No tool calls, just regular response
            conversation_history.append(HumanMessage(content=message.content))
            conversation_history.append(response)
        
        # Keep conversation history manageable (last 10 messages)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        cl.user_session.set("conversation_history", conversation_history)
        
        # Step 5: Send response to user
        await cl.Message(content=response_text).send()
        
    except Exception as e:
        print(f"Error: {e}")
        await cl.Message(
            content="I apologize, but I encountered an error. Could you please rephrase your question?"
        ).send()
