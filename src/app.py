"""
AutoStream AI Agent - Chainlit Application.

Main entry point for the Chainlit web interface.
"""

import os
import sys

# Ensure project root is on sys.path so 'src' package imports work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage

from src.graph.workflow import AutoStreamWorkflow
from src.models.lead import LeadData
from src.services.vector_store import VectorStoreManager


# Initialize the workflow (will be created per session)
workflow = None
vector_store_manager = None


@cl.on_chat_start
async def start():
    """
    Initialize the chat session.
    
    Sets up the workflow and vector store for the user's session.
    """
    global workflow, vector_store_manager
    
    # Send welcome message
    await cl.Message(
        content="🎬 **Initializing AutoStream AI Agent...**\n\nLoading knowledge base and preparing the agent..."
    ).send()
    
    try:
        # Initialize vector store (this will load or create the ChromaDB)
        vector_store_manager = VectorStoreManager()
        vector_store_manager.initialize_vector_store()
        
        # Initialize the workflow
        workflow = AutoStreamWorkflow()
        
        # Initialize session state
        cl.user_session.set("state", {
            "messages": [],
            "current_intent": None,
            "lead_data": LeadData(),
            "lead_captured": False,
            "conversation_history": [],
            "retrieved_context": None,
            "next_action": None
        })
        
        # Send ready message
        await cl.Message(
            content=(
                "✅ **AutoStream AI Agent is ready!**\n\n"
                "Hi there! 👋 I'm your AutoStream assistant. I can help you with:\n"
                "- Information about our pricing plans\n"
                "- Features and capabilities\n"
                "- Getting started with AutoStream\n\n"
                "What would you like to know?"
            )
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ **Error initializing agent:** {str(e)}\n\nPlease check your configuration and try again."
        ).send()
        raise


@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming user messages.
    
    Processes messages through the LangGraph workflow and returns responses.
    
    Args:
        message: User's message from Chainlit
    """
    global workflow
    
    try:
        # Get current state from session
        state = cl.user_session.get("state")
        
        # Run the workflow with the user's message
        result = workflow.run(message.content, state)
        
        # Update session state
        cl.user_session.set("state", result)
        
        # Get the last AI message from the result
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        if ai_messages:
            last_response = ai_messages[-1].content
            
            # Check if lead was captured
            if result.get("lead_captured", False):
                # Add extra formatting for successful lead capture
                response_message = f"🎉 {last_response}"
            else:
                response_message = last_response
            
            # Send the response
            await cl.Message(content=response_message).send()
        else:
            # Fallback if no AI message (shouldn't happen)
            await cl.Message(
                content="I'm here to help! What would you like to know about AutoStream?"
            ).send()
    
    except Exception as e:
        # Handle errors gracefully
        error_message = (
            f"❌ **Oops! Something went wrong.**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please try again or rephrase your question."
        )
        await cl.Message(content=error_message).send()


if __name__ == "__main__":
    # This is just for reference - Chainlit runs via CLI
    print("Run this app with: chainlit run src/app.py")
