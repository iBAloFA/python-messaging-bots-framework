# Asynchronous Messaging Bot & State Persistence Framework

A production-ready, highly concurrent asynchronous chatbot engine built with Python. Designed to run on the Telegram Bot API and interact intelligently with Large Language Models (LLMs) while completely eliminating thread blocking, runtime deadlocks, and silent data drop-offs.

## 🚀 Key Architectural Features
- **Non-Blocking Async Event Loop:** Built entirely using `aiogram` and `AsyncOpenAI` to handle thousands of concurrent requests smoothly.
- **Persistent State Cache Engine:** Features an isolation-layer SQLite schema store mapping transactional conversation loops, allowing effortless migrations to heavy database systems like PostgreSQL or Redis.
- **Fail-Safe Fallback Logic:** Implements defensive exception structures to trap connection drop-outs, API timeouts, and payload limits gracefully without stopping execution.
- **Strong Environmental Sanitization:** Built using structural `pydantic-settings` objects to guarantee strict configurations and prevent token leakage.

## 🛠️ Installation & Setup

1. **Clone and Navigate to Folder:**
   ```bash
   git clone https://github.com
   cd python-messaging-bots-framework
   ```

2. **Configure Virtual Environment & Dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Establish Environment Secret Arrays (.env):**
   Create a `.env` file in the root directory:
   ```env
   BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
   OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
   DATABASE_URL="sqlite:///bot_memory.db"
   ```

4. **Launch Application Runner Loop:**
   ```bash
   python -m app.main
   ```

## 🏗️ Technical Architecture Diagram
```text
User Text Input ➡️ Telegram API ➡️ app/main.py (Async Router)
                                        │
           ┌────────────────────────────┴────────────────────────────┐
           ▼                                                         ▼
   Native Command (/start)                                    Generic Text Array
 [app/handlers/commands.py]                             [app/handlers/llm_fallback.py]
           │                                                         │
           ▼                                                         ▼
 Wipes/Instantiates Local State                              Queries Session Database
           │                                                   [app/database/state_store.py]
           │                                                         │
           ▼                                                         ▼
  Dispatches UI Confirmation                             Appends System Context Contexts
                                                                     │
                                                                     ▼
                                                         Dispatches Asynchronous LLM Thread
                                                                     │
                                                                     ▼
                                                          Persists State & Dispatches UI
```
