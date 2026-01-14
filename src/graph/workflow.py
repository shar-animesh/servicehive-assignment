"""
Simplified workflow for the AutoStream AI agent.

Uses a single LLM call with RAG context and tool access instead of
multiple agent nodes. The LLM handles all intents and lead capture.
"""

from typing import AsyncIterator

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.config.settings import get_settings
from src.models.state import AgentState
from src.services.vector_store import VectorStoreManager
from src.tools.lead_capture import lead_capture_tool
from src.utils.prompt_loader import PromptLoader


class AutoStreamWorkflow:
    """
    Simplified workflow for the AutoStream agent.
    
    Uses a single LLM with:
    - RAG context retrieved for every query
    - Access to lead_capture tool
    - Unified system prompt
    """
    
    def __init__(self):
        """Initialize the workflow with LLM, RAG, and tools."""
        settings = get_settings()
        
        # Load system prompt
        self.prompt_loader = PromptLoader()
        self.system_prompt = self.prompt_loader.load_prompt("system_prompt.md")
        
        # Initialize vector store for RAG
        self.vector_store_manager = VectorStoreManager()
        self.vector_store = self.vector_store_manager.get_vector_store()
        
        # Initialize LLM with tool binding
        self.llm = ChatOpenAI(
            model=settings.model_name,
            temperature=0.7,
            streaming=True
        )
        
        # Bind the lead capture tool to the LLM
        self.llm_with_tools = self.llm.bind_tools([lead_capture_tool])
    
    def _retrieve_context(self, query: str, k: int = 3) -> str:
        """
        Retrieve relevant context from the knowledge base.
        
        Args:
            query: User's query
            k: Number of documents to retrieve
            
        Returns:
            Formatted context string
        """
        # Retrieve relevant documents
        docs = self.vector_store.similarity_search(query, k=k)
        
        if not docs:
            return "No relevant information found in the knowledge base."
        
        # Format context
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"Document {i}:\n{doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def _build_messages(self, user_message: str, conversation_history: list) -> list:
        """
        Build the message list for the LLM.
        
        Args:
            user_message: Current user message
            conversation_history: Previous messages
            
        Returns:
            List of messages including system prompt, history, and context
        """
        # Retrieve RAG context for the current query
        context = self._retrieve_context(user_message)
        
        # Build system message with context
        system_content = f"""{self.system_prompt}

## Knowledge Base Context
The following information from our knowledge base is relevant to the current conversation:

{context}

Use this context to answer the user's questions accurately."""
        
        messages = [SystemMessage(content=system_content)]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    def run(self, user_message: str, state: AgentState = None) -> AgentState:
        """
        Run the workflow with a user message.
        
        Args:
            user_message: User's input message
            state: Optional existing state (for conversation continuity)
            
        Returns:
            Updated state after processing
        """
        # Initialize state if not provided
        if state is None:
            state = {
                "messages": [],
                "current_intent": None,
                "lead_data": None,
                "lead_captured": False,
                "conversation_history": [],
                "retrieved_context": None,
                "next_action": None
            }
        
        # Build messages with RAG context
        messages = self._build_messages(user_message, state["messages"])
        
        # Get LLM response with tool calling
        response = self.llm_with_tools.invoke(messages)
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        
        # Check if tool was called
        if response.tool_calls:
            # Execute tool calls
            for tool_call in response.tool_calls:
                if tool_call["name"] == "lead_capture_tool":
                    args = tool_call["args"]
                    result = lead_capture_tool.invoke(args)
                    state["lead_captured"] = True
                    state["messages"].append(AIMessage(content=result))
        else:
            # Regular response without tool call
            state["messages"].append(AIMessage(content=response.content))
        
        # Keep conversation history manageable (last 12 messages = 6 turns)
        if len(state["messages"]) > 12:
            state["messages"] = state["messages"][-12:]
        
        return state
    
    async def run_stream(self, user_message: str, state: AgentState = None) -> AsyncIterator[dict]:
        """
        Run the workflow with streaming support.
        
        Args:
            user_message: User's input message
            state: Optional existing state (for conversation continuity)
            
        Yields:
            Chunks of content as they're generated
        """
        # Initialize state if not provided
        if state is None:
            state = {
                "messages": [],
                "current_intent": None,
                "lead_data": None,
                "lead_captured": False,
                "conversation_history": [],
                "retrieved_context": None,
                "next_action": None
            }
        
        # Build messages with RAG context
        messages = self._build_messages(user_message, state["messages"])
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        
        # Stream LLM response
        full_response = ""
        tool_calls = []
        
        async for chunk in self.llm_with_tools.astream(messages):
            # Handle content chunks
            if chunk.content:
                full_response += chunk.content
                yield {"content": chunk.content}
            
            # Collect tool calls
            if hasattr(chunk, "tool_calls") and chunk.tool_calls:
                tool_calls.extend(chunk.tool_calls)
        
        # Execute any tool calls after streaming completes
        if tool_calls:
            for tool_call in tool_calls:
                if tool_call["name"] == "lead_capture_tool":
                    args = tool_call["args"]
                    result = lead_capture_tool.invoke(args)
                    state["lead_captured"] = True
                    # Yield the tool result
                    yield {"content": f"\n\n{result}"}
                    state["messages"].append(AIMessage(content=result))
        else:
            # Add the full response to state
            if full_response:
                state["messages"].append(AIMessage(content=full_response))
        
        # Keep conversation history manageable
        if len(state["messages"]) > 12:
            state["messages"] = state["messages"][-12:]
        
        # Yield final state
        yield {"state": state}
