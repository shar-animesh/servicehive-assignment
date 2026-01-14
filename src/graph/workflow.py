"""
LangGraph workflow for the AutoStream AI agent.

Defines the state machine that routes conversations through different
nodes based on intent and conversation state.
"""

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph

from src.agents.intent_detector import IntentDetector
from src.agents.lead_collector import LeadCollector
from src.agents.rag_retriever import RAGRetriever
from src.models.lead import LeadData
from src.models.state import AgentState
from src.tools.lead_capture import mock_lead_capture


class AutoStreamWorkflow:
    """
    LangGraph workflow for the AutoStream agent.
    
    Manages the conversation flow through different nodes based on
    detected intent and conversation state.
    """
    
    def __init__(self):
        """Initialize the workflow with all agent components."""
        self.intent_detector = IntentDetector()
        self.rag_retriever = RAGRetriever()
        self.lead_collector = LeadCollector()
        
        # Build the workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        
        Returns:
            Compiled state graph
        """
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("intent_detection", self.intent_detection_node)
        workflow.add_node("greeting", self.greeting_node)
        workflow.add_node("rag_answer", self.rag_answer_node)
        workflow.add_node("lead_collection", self.lead_collection_node)
        workflow.add_node("lead_capture", self.lead_capture_node)
        
        # Set entry point
        workflow.set_entry_point("intent_detection")
        
        # Add conditional edges from intent detection
        workflow.add_conditional_edges(
            "intent_detection",
            self.route_by_intent,
            {
                "greeting": "greeting",
                "inquiry": "rag_answer",
                "high_intent_lead": "lead_collection"
            }
        )
        
        # Add edges from other nodes to END
        workflow.add_edge("greeting", END)
        workflow.add_edge("rag_answer", END)
        
        # Lead collection can either end or proceed to capture
        workflow.add_conditional_edges(
            "lead_collection",
            self.check_lead_ready,
            {
                "capture": "lead_capture",
                "continue": END
            }
        )
        
        workflow.add_edge("lead_capture", END)
        
        # Compile the graph
        return workflow.compile()
    
    def intent_detection_node(self, state: AgentState) -> AgentState:
        """
        Detect the intent of the user's message.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with detected intent
        """
        # Get the last user message
        last_message = state["messages"][-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Detect intent
        intent = self.intent_detector.detect_intent(user_message)
        
        # Update state
        state["current_intent"] = intent
        
        return state
    
    def greeting_node(self, state: AgentState) -> AgentState:
        """
        Handle greeting messages.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with greeting response
        """
        greeting_response = (
            "Hi there! 👋 Welcome to AutoStream! "
            "I'm here to help you learn about our AI-powered video editing platform. "
            "Whether you're creating content for YouTube, Instagram, TikTok, or other platforms, "
            "we can help you save time and create amazing videos. "
            "What would you like to know?"
        )
        
        state["messages"].append(AIMessage(content=greeting_response))
        
        return state
    
    def rag_answer_node(self, state: AgentState) -> AgentState:
        """
        Answer user questions using RAG.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with RAG answer
        """
        # Get the last user message
        last_message = state["messages"][-1]
        user_question = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Get answer using RAG
        answer, context = self.rag_retriever.answer_question(user_question)
        
        # Update state
        state["retrieved_context"] = context
        state["messages"].append(AIMessage(content=answer))
        
        return state
    
    def lead_collection_node(self, state: AgentState) -> AgentState:
        """
        Collect lead information from the user.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with lead collection message
        """
        # Get current lead data or initialize
        if "lead_data" not in state or state["lead_data"] is None:
            state["lead_data"] = LeadData()
        
        # Get the last user message
        last_message = state["messages"][-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Extract information from message
        state["lead_data"] = self.lead_collector.extract_info_from_message(
            user_message,
            state["lead_data"]
        )
        
        # Generate collection message
        collection_message = self.lead_collector.generate_collection_message(
            state["lead_data"]
        )
        
        state["messages"].append(AIMessage(content=collection_message))
        
        return state
    
    def lead_capture_node(self, state: AgentState) -> AgentState:
        """
        Execute the lead capture tool.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with capture confirmation
        """
        lead_data = state["lead_data"]
        
        # Call the mock lead capture function
        result = mock_lead_capture(
            name=lead_data.name,
            email=lead_data.email,
            platform=lead_data.platform
        )
        
        # Update state
        state["lead_captured"] = True
        state["messages"].append(AIMessage(content=result))
        
        return state
    
    def route_by_intent(
        self, 
        state: AgentState
    ) -> Literal["greeting", "inquiry", "high_intent_lead"]:
        """
        Route to appropriate node based on detected intent.
        
        Args:
            state: Current agent state
            
        Returns:
            Next node to execute
        """
        return state["current_intent"]
    
    def check_lead_ready(
        self, 
        state: AgentState
    ) -> Literal["capture", "continue"]:
        """
        Check if lead data is complete and ready for capture.
        
        Args:
            state: Current agent state
            
        Returns:
            "capture" if ready, "continue" if more info needed
        """
        if self.lead_collector.is_ready_for_capture(state["lead_data"]):
            return "capture"
        return "continue"
    
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
                "lead_data": LeadData(),
                "lead_captured": False,
                "conversation_history": [],
                "retrieved_context": None,
                "next_action": None
            }
        
        # Add user message to state
        state["messages"].append(HumanMessage(content=user_message))
        
        # Run the graph
        result = self.graph.invoke(state)
        
        # Update conversation history (keep last 6 messages)
        if len(result["messages"]) > 12:  # 6 turns = 12 messages
            result["messages"] = result["messages"][-12:]
        
        return result
