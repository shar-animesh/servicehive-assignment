# AutoStream AI Agent

> **Simple RAG-powered conversational AI with tool calling for lead capture**
> 
> Built for ServiceHive's Inflx platform assignment

## 🎯 Overview

AI agent for **AutoStream** - an AI-powered video editing SaaS for content creators.

**Simple Architecture**:
1. User query → Embed & retrieve from ChromaDB  
2. Pass context + system prompt to LLM
3. LLM responds naturally OR calls `lead_capture` tool
4. Show response to user

**No complex intent classification** - the LLM handles everything with one system prompt!

### Features

✅ RAG-powered Q&A using ChromaDB  
✅ Natural conversation flow  
✅ Automatic lead capture with email notifications  
✅ Clean, maintainable ~150 line implementation

## 🚀 Quick Start

### 1. Install

```bash
cd servicehive-assignment
uv sync
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

### 3. Test

```bash
uv run python test_setup.py
```

### 4. Run

```bash
uv run chainlit run src/app.py
```

Visit: **http://localhost:8000**

## 💬 Example Conversations

**Greeting:**
```
You: Hi!
Agent: Hi! 👋 Welcome to AutoStream! I'm here to help you learn about our 
      AI-powered video editing platform...
```

**Pricing Question:**
```
You: How much does it cost?
Agent: [Retrieves from ChromaDB and explains Basic $29/mo and Pro $79/mo plans]
```

**Lead Capture:**
```
You: I want to sign up!
Agent: Awesome! To get you started, what's your name?
You: Sarah
Agent: Great! And your email?
You: sarah@example.com
Agent: Perfect! Which platform do you create content for?
You: YouTube
Agent: [Calls lead_capture tool] Thank you, Sarah! 🎉 Our team will reach out shortly!

[Email sent to admins automatically]
```

## 🏗️ Architecture

### Tech Stack

- **UI**: ChainLit
- **LLM**: OpenAI GPT-4o-mini (via LangChain)
- **Vector DB**: ChromaDB
- **Embeddings**: text-embedding-3-small
- **Models**: Pydantic
- **Templates**: Jinja2

### Project Structure

```
servicehive-assignment/
├── src/
│   ├── app.py              # Main application (~150 lines)
│   ├── models.py           # Pydantic models
│   ├── config/settings.py  # Environment config
│   ├── services/           # Embeddings & vector store
│   ├── tools/              # Lead capture tool
│   └── utils/              # Prompt loader (Jinja2)
├── prompts/
│   └── system_prompt.md    # Single system prompt
├── knowledge_base/          # RAG data
│   ├── pricing_features.md
│   ├── policies.md
│   └── faq.md
└── data/chroma_db/         # Vector DB (auto-created)
```

### How It Works

```
User: "What are your plans?"
         ↓
Embed query using OpenAI
         ↓
Retrieve top-4 chunks from ChromaDB
         ↓
Build messages:
  - SystemMessage(system_prompt)
  - ConversationHistory
  - HumanMessage(query + context)
         ↓
LLM.invoke() with lead_capture tool bound
         ↓
LLM decides:
  - Regular response, OR
  - Call lead_capture(name, email, platform)
         ↓
Show response + tool result to user
```

## 📋 Assignment Requirements

### ✅ All Requirements Met

**3.1 Intent Identification**
- ✅ Handles greetings, product questions, pricing, high-intent leads
- ✅ No hardcoded intent classification - LLM does it naturally

**3.2 RAG-Powered Knowledge Retrieval**
- ✅ ChromaDB vector store
- ✅ OpenAI embeddings
- ✅ AutoStream pricing & features in knowledge base
- ✅ Company policies (refunds, support)

**3.3 Lead Capture**
- ✅ Identifies high-intent users naturally
- ✅ Collects name, email, platform conversationally
- ✅ Calls tool when ready
- ✅ Sends email to admins via Resend API

### Implementation Highlights

- **Single system prompt** - No separate prompts for intent classification
- **No hardcoded logic** - LLM decides when to capture leads
- **Clean codebase** - Main app is ~150 lines
- **Uses existing infrastructure** - Prompt loader, settings, vector store services
- **Tool calling** - LLM naturally invokes lead_capture when appropriate

## 🔧 Configuration

Environment variables (`.env`):

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ Yes |
| `MODEL_NAME` | LLM model | No (default: gpt-4o-mini) |
| `CHROMA_DB_PATH` | Vector DB path | No (default: ./data/chroma_db) |
| `KNOWLEDGE_BASE_PATH` | KB directory | No (default: ./knowledge_base) |
| `RESEND_API_KEY` | For email notifications | No |
| `ADMIN_EMAILS` | Email recipients | No |

## 🧪 Testing

Run setup verification:
```bash
uv run python test_setup.py
```

Tests:
- ✅ Imports
- ✅ Settings loading
- ✅ Prompt loader (Jinja2)
- ✅ Vector store initialization
- ✅ LLM connection
- ✅ Tool binding

## 📚 Knowledge Base

Three markdown files in `knowledge_base/`:

1. **pricing_features.md**
   - Basic Plan: $29/mo, 10 videos, 720p
   - Pro Plan: $79/mo, unlimited, 4K, AI captions

2. **policies.md**
   - 7-day refund policy
   - 24/7 support on Pro plan only

3. **faq.md**
   - Product capabilities
   - Technical specs
   - Billing info

## 🛠️ Development

### Key Files

**[src/app.py](src/app.py)** - Main application
- Simple RAG flow
- Tool calling integration
- ChainLit UI handlers

**[prompts/system_prompt.md](prompts/system_prompt.md)** - System prompt
- Loaded via Jinja2 (not hardcoded!)
- Handles all conversation scenarios
- Instructs LLM on tool usage

**[src/tools/lead_capture.py](src/tools/lead_capture.py)** - Lead capture
- Sends emails via Resend API
- LangChain tool decorator
- Returns confirmation message

### Why This Design?

✅ **Simple**: One prompt, one flow, ~150 lines  
✅ **Maintainable**: No hardcoded prompts in code  
✅ **Natural**: LLM handles intent organically  
✅ **Extensible**: Easy to add more tools  
✅ **Production-ready**: Uses existing services properly

## 🚀 Deployment

For production:
- Use persistent session storage (Redis)
- Add rate limiting
- Use production vector DB (Pinecone, Weaviate)
- Set up monitoring
- Add authentication
- Configure proper logging

## 📝 Notes

- First run indexes knowledge base (~10 seconds)
- Conversation history kept in session (last 10 messages)
- Tool calls include text response for UI
- All settings from `.env` (no hardcoded values)

## 🎓 Built With

- Python 3.12
- ChainLit - UI
- LangChain - LLM framework
- OpenAI - LLM & embeddings
- ChromaDB - Vector database
- Pydantic - Data validation
- Jinja2 - Template loading
- Resend - Email API

---

**ServiceHive Inflx Platform Assignment - Machine Learning Intern**
