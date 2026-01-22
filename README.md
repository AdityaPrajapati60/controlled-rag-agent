# Controlled RAG + Agent Execution System

This is a backend project I built to explore how **AI agents should be used in real systems**.

Most AI demos let the LLM directly take actions.  
In this project, I did the opposite.

Here, the **LLM is only used for planning and reasoning**.  
All execution, permissions, and limits are handled by the backend.



## What this project does

- Users can create and manage tasks
- Users can upload PDFs and ask questions about them
- Document questions are answered using **explicit RAG**
- An agent can understand natural language and suggest actions
- The backend decides whether those actions are allowed or not

There is **no frontend UI**.  
All APIs are tested using **Swagger UI**


## Why I built it this way

I wanted to avoid:
- Hallucinated actions
- Prompt injection issues
- LLMs doing things they shouldn’t

So the design follows a simple rule:

> The LLM suggests.  
> The system decides.



## Main features

- Explicit RAG (no document → no answer)
- LangGraph-based planning
- Deterministic execution engine
- Role-based permissions for tools
- Rate limiting and token limits
- Full logging of agent runs and actions
- Proper user-level data isolation



## High-level architecture

- FastAPI for the API layer
- JWT-based authentication
- SQL database for users, tasks, documents, and logs
- Chroma vector DB for document embeddings (per user)
- Groq / LLaMA for planning and answering



## About the missing UI

This project is intentionally backend-focused.  
The goal was to design a **safe and controlled AI system**.

All functionality is available through `/docs` (Swagger UI).  
A UI can be added later without changing the core logic.



## Project status

Core functionality is complete.  
I may improve documentation and add examples over time.


