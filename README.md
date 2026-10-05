AI Knowledge Assistant

An AI-powered knowledge assistant built with FastAPI, LangChain, Groq, RAG, ChromaDB, MySQL, and JWT authentication.

The application allows users to create chat sessions, communicate with an AI agent, use external tools, and upload PDF documents that can be searched using Retrieval-Augmented Generation (RAG).

🚀 Features

User registration and authentication

JWT-based authentication

Secure password hashing

User-specific chat sessions

Persistent chat history

AI Agent powered by Groq

LangChain Agent architecture

Web search

Calculator tool

Weather tool

Date & Time tool

URL Reader

PDF document upload

Retrieval-Augmented Generation (RAG)

Vector search with ChromaDB

Hugging Face embeddings

MySQL database

SQLAlchemy ORM

Request logging middleware

FastAPI automatic API documentation

🏗️ Architecture

┌─────────────────────┐
                    │      FastAPI        │
                    │       API           │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
          Authentication                Chat System
                 │                           │
             JWT + DB                 Sessions + Messages
                 │                           │
                 └─────────────┬─────────────┘
                               │
                         ┌─────▼─────┐
                         │ AI Agent  │
                         │ LangChain │
                         └─────┬─────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
          Web Search       Calculator       URL Reader
              │                │                │
              └────────────────┼────────────────┘
                               │
                         ┌─────▼─────┐
                         │    RAG    │
                         └─────┬─────┘
                               │
                     ┌─────────▼─────────┐
                     │     ChromaDB      │
                     │  Vector Database  │
                     └─────────┬─────────┘
                               │
                    Hugging Face Embeddings

🧠 RAG Pipeline

The document question-answering system follows this pipeline:

PDF Upload
    ↓
PDF Loader
    ↓
Text Splitting
    ↓
Document Chunks
    ↓
Hugging Face Embeddings
    ↓
ChromaDB
    ↓
Retriever
    ↓
Document Search Tool
    ↓
AI Agent
    ↓
Answer

When a user asks a question related to an uploaded document, the AI Agent can search the vector database and use the retrieved information to generate an answer.

🛠️ Tech Stack

Backend

Python

FastAPI

Uvicorn

Database

MySQL

SQLAlchemy

Authentication

JWT

Passlib

bcrypt

AI

LangChain

Groq

AI Agents

RAG

ChromaDB

Hugging Face Embeddings

PyPDF

Tools

Tavily Search

Calculator

Weather

Date & Time

URL Reader

Document Search

📁 Project Structure

ai-knowledge-assistant/
│
├── main.py
├── agent.py
├── tools.py
├── rag.py
│
├── models.py
├── database.py
├── security.py
├── middleware.py
├── schemas.py
│
├── uploads/
├── vector_db/
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md

⚙️ Installation

1. Clone the repository

git clone https://github.com/Amirreza-javadi/ai-knowledge-assistant.git cd ai-knowledge-assistant 

2. Create a virtual environment

python -m venv venv 

Activate it on Windows:

venv\Scripts\activate 

Linux / macOS:

source venv/bin/activate 

3. Install dependencies

pip install -r requirements.txt 

🔐 Environment Variables

Create a .env file in the project root:

DATABASE_URL=mysql+pymysql://USERNAME:PASSWORD@localhost/ai_knowledge_assistant

SECRET_KEY=your_secret_key

GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

HF_TOKEN=your_huggingface_token 

Never commit the .env file to GitHub.

🗄️ Database Setup

Create the MySQL database:

CREATE DATABASE ai_knowledge_assistant; 

The application uses SQLAlchemy to connect to and manage the database.

▶️ Running the Application

Start the FastAPI server:

uvicorn main:app --reload 

The API will be available at:

http://127.0.0.1:8000 

📚 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI

http://127.0.0.1:8000/docs 

ReDoc

http://127.0.0.1:8000/redoc 

🔑 Authentication Flow

Register
   ↓
Login
   ↓
JWT Token
   ↓
Authenticated Requests
   ↓
User Sessions
   ↓
Chat 

The user registers an account, logs in, receives a JWT token, and uses that token to access protected endpoints.

💬 Chat Flow

User
 ↓
FastAPI
 ↓
Authentication
 ↓
Chat Session
 ↓
AI Agent
 ↓
Tool Selection
 ↓
LLM / RAG
 ↓
Response
 ↓
Database

The AI Agent decides whether it needs to use an available tool or retrieve information from the knowledge base before generating a response.

📄 Document Flow

PDF
 ↓
Text Extraction
 ↓
Text Chunks
 ↓
Embeddings
 ↓
ChromaDB
 ↓
Retriever
 ↓
Document Search Tool
 ↓
AI Agent
 ↓
Answer

Uploaded PDF documents are processedand stored in a vector database so relevant information can be retrieved during conversations.

🎯 Example Use Cases

The assistant can:

Answer general questions

Search the web

Perform calculations

Get weather information

Provide date and time information

Read web pages

Search uploaded PDF documents

Maintain conversation history

🔒 Security

The project includes:

Password hashing

JWT authentication

Protected API routes

Environment variables for secrets

User-specific chat sessions

Input validation with Pydantic

🚧 Future Improvements

Possible future improvements include:

Frontend interface

Streaming AI responses

Per-user vector databases

Document management

Multiple document collections

Conversation title generation

Rate limiting

Docker deployment

Cloud deployment

Redis caching

PostgreSQL support

Advanced agent memory

Document citation and source tracking

👨‍💻 Author

Built as an AI Engineering portfolio project.

Focused on:

AI Agents

RAG

LLM Applications

FastAPI

Backend Engineering

Vector Databases

AI System Architecture