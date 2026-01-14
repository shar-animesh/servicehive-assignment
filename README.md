# AutoStream AI Agent

A conversational AI agent for AutoStream - an AI-powered video editing SaaS platform. This agent uses a simplified single-LLM architecture with RAG and tool calling for intelligent lead capture.

## 🎯 Project Overview

This project implements a production-ready conversational AI agent that:
- **Answers questions accurately** using RAG with ChromaDB vector storage
- **Identifies and captures leads** using LLM tool calling
- **Sends real email notifications** to admins via Resend API
- **Maintains conversation context** across multiple turns

Built for the ServiceHive Inflx platform assignment, showcasing a clean, maintainable GenAI agent architecture.

## 🏗️ Architecture

### Simplified Single-LLM Design

Instead of a complex multi-agent system, this project uses a **single LLM with RAG context and tool access**:

1. **RAG Pipeline**: For every user query, we retrieve relevant documents from ChromaDB and pass them as context to the LLM
2. **Tool Calling**: The LLM has access to a `lead_capture` tool that sends emails via Resend
3. **Unified Prompt**: One system prompt handles all intents (greetings, questions, lead collection)
4. **Smart Routing**: The LLM naturally handles different intents without separate agent nodes

**Benefits:**
- ✅ Simpler codebase
- ✅ Easier to maintain
- ✅ More natural conversations
- ✅ Real email integration
- ✅ Always-on RAG context

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed flow diagrams.

### Key Components

```
                                   └─ High Intent → Lead Collection → [Check Complete]
                                                                       ├─ Incomplete → Ask for Info
                                                                       └─ Complete → Lead Capture Tool
```

## 📋 Prerequisites

- Python 3.9 or higher
- UV package manager ([install here](https://github.com/astral-sh/uv))
- OpenAI API key

## 🚀 Installation

1. **Clone or navigate to the project directory:**
```bash
cd servicehive-assignment
```

2. **Install dependencies using UV:**
```bash
uv sync
```

This will install all required packages including:
- LangChain & LangGraph
- Chainlit
- ChromaDB
- OpenAI
- Pydantic

3. **Set up environment variables:**

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o-mini
CHROMA_DB_PATH=./data/chroma_db
RESEND_API_KEY=your_resend_api_key_here
ADMIN_EMAILS=admin@example.com,team@example.com
```

## 🎮 Running the Application

Start the Chainlit web interface:

```bash
uv run chainlit run src/app.py
```

The application will:
1. Initialize the vector store (first run will index the knowledge base)
2. Start the Chainlit server
3. Open your browser to `http://localhost:8000`

## 💬 Testing the Agent

Try this conversation flow to see all features:

1. **Greeting:**
   ```
   User: Hi there!
   Agent: [Welcomes and offers help]
   ```

2. **Product Inquiry (RAG):**
   ```
   User: What are your pricing plans?
   Agent: [Retrieves and explains Basic $29 and Pro $79 plans]
   ```

3. **High-Intent Lead:**
   ```
   User: That sounds good, I want to try the Pro plan for my YouTube channel
   Agent: [Detects high intent, starts collecting info]
   ```

4. **Lead Collection:**
   ```
   Agent: Great! What's your name?
   User: John Doe
   Agent: And what's your email address?
   User: john@example.com
   Agent: [Confirms and captures lead]
   ```

The `mock_lead_capture` function will print to console:
```
Lead captured successfully: John Doe, john@example.com, YouTube
```

## 📁 Project Structure

```
servicehive-assignment/
├── src/
│   ├── config/
│   │   └── settings.py              # Pydantic settings with LRU cache
│   ├── models/
│   │   ├── state.py                 # LangGraph state schema
│   │   └── lead.py                  # Lead data models
│   ├── agents/
│   │   ├── intent_detector.py       # Intent classification
│   │   ├── rag_retriever.py         # RAG pipeline
│   │   └── lead_collector.py        # Lead collection logic
│   ├── graph/
│   │   └── workflow.py              # LangGraph workflow
│   ├── tools/
│   │   └── lead_capture.py          # Mock lead capture tool
│   ├── services/
│   │   ├── vector_store.py          # ChromaDB integration
│   │   └── embeddings.py            # OpenAI embeddings
│   ├── utils/
│   │   └── prompt_loader.py         # Jinja2 prompt templates
│   └── app.py                       # Chainlit application
├── prompts/
│   ├── system_prompt.md             # Agent personality
│   ├── intent_classifier.md         # Intent detection
│   ├── rag_prompt.md                # RAG answer generation
│   └── lead_capture_prompt.md       # Lead collection
├── knowledge_base/
│   ├── pricing_features.md          # AutoStream pricing
│   ├── policies.md                  # Company policies
│   └── faq.md                       # FAQs
├── data/
│   └── chroma_db/                   # Vector database (auto-created)
├── pyproject.toml                   # UV dependencies
├── .env.example                     # Environment template
└── README.md                        # This file
```

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `MODEL_NAME`: LLM model to use (default: gpt-4o-mini)
- `CHROMA_DB_PATH`: Path for vector database storage

Settings are loaded using Pydantic Settings with `@lru_cache` for performance.

## 📱 WhatsApp Deployment

### Integration Approach

To deploy this agent on WhatsApp, you would use the **WhatsApp Business API** with webhooks:

#### Architecture

```
WhatsApp User → WhatsApp Business API → Webhook Server → AutoStream Agent → Response
```

#### Implementation Steps

1. **Set up WhatsApp Business API**
   - Register with Meta/Facebook Business
   - Get WhatsApp Business API credentials
   - Configure webhook URL

2. **Create Webhook Server**
   ```python
   from fastapi import FastAPI, Request
   from src.graph.workflow import AutoStreamWorkflow
   
   app = FastAPI()
   workflow = AutoStreamWorkflow()
   
   # Store user sessions (use Redis in production)
   sessions = {}
   
   @app.post("/webhook")
   async def whatsapp_webhook(request: Request):
       data = await request.json()
       
       # Extract message and user ID
       user_id = data['entry'][0]['changes'][0]['value']['contacts'][0]['wa_id']
       message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
       
       # Get or create session state
       if user_id not in sessions:
           sessions[user_id] = initialize_state()
       
       # Run workflow
       result = workflow.run(message, sessions[user_id])
       sessions[user_id] = result
       
       # Get response
       response = result['messages'][-1].content
       
       # Send back via WhatsApp API
       send_whatsapp_message(user_id, response)
       
       return {"status": "ok"}
   ```

3. **State Persistence**
   - Use **Redis** or **DynamoDB** to store user sessions
   - Implement session expiry (e.g., 24 hours)
   - Store lead data in database when captured

4. **Handle WhatsApp-Specific Features**
   - Format messages for WhatsApp (max 4096 chars)
   - Support quick reply buttons for lead collection
   - Handle media messages (ignore or process)

5. **Deployment**
   - Deploy webhook server on AWS Lambda, Google Cloud Run, or similar
   - Use HTTPS (required by WhatsApp)
   - Implement rate limiting and error handling
   - Set up monitoring and logging

#### Key Considerations

- **Session Management**: WhatsApp conversations are asynchronous, so robust session storage is critical
- **Message Formatting**: WhatsApp has character limits and formatting constraints
- **Verification**: WhatsApp requires webhook verification on setup
- **Scalability**: Use serverless or containerized deployment for handling multiple concurrent users
- **Security**: Validate webhook signatures to prevent unauthorized access

## 🧪 Testing

Test individual components:

```bash
# Test settings loading
uv run python -c "from src.config.settings import get_settings; print(get_settings())"

# Test vector store initialization
uv run python -c "from src.services.vector_store import VectorStoreManager; vm = VectorStoreManager(); vm.initialize_vector_store()"

# Test lead capture
uv run python -c "from src.tools.lead_capture import lead_capture; print(lead_capture('John Doe', 'john@example.com', 'YouTube'))"
```

## 🎨 Features

- ✅ **RAG-Powered Answers**: Uses ChromaDB + OpenAI embeddings for accurate responses  
- ✅ **Smart Lead Capture**: LLM conversationally collects name, email, and platform  
- ✅ **Real Email Notifications**: Sends emails to admins via Resend API  
- ✅ **State Management**: Maintains context across conversation turns  
- ✅ **Tool Calling**: LLM decides when to execute lead_capture tool  
- ✅ **Error Handling**: Graceful error handling with user-friendly messages  
- ✅ **Clean Architecture**: Simple, maintainable single-LLM design

## 📝 Assignment Requirements Met

- ✅ Intent identification (handled naturally by LLM)
- ✅ RAG-powered knowledge retrieval with ChromaDB
- ✅ Real lead capture with email notifications (Resend)
- ✅ State management across conversation turns
- ✅ Clean, maintainable single-LLM architecture
- ✅ Tool calling with LangChain
- ✅ Comprehensive documentation

## 🤝 Contributing

This is an assignment project, but suggestions for improvements are welcome!

## 📄 License

This project is created for the ServiceHive assignment.

---

**Built with ❤️ using LangChain, Chainlit, and OpenAI**
