from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from pathlib import Path
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models import User, ChatSession, Message
from schemas import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
    SessionCreate,
    SessionResponse,
    MessageCreate,
    MessageResponse
)
from security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from middleware import request_logging_middleware
from agent import AIAgent
from rag import create_vector_store


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI Knowledge Assistant API",
    description="LLM-powered AI Knowledge Assistant",
    version="1.0.0"
)


app.middleware("http")(
    request_logging_middleware
)


agent = AIAgent()

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    exist_ok=True
)


# ==========================================
# Health
# ==========================================

@app.get("/")
def root():

    return {
        "message": "AI Knowledge Assistant API",
        "status": "running"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ==========================================
# Authentication
# ==========================================

@app.post(
    "/register",
    response_model=UserResponse
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_email:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(
            user_data.password
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.username == login_data.username
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(
        login_data.password,
        user.password
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        user.id
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(
        get_current_user
    )
):

    return current_user


# ==========================================
# Chat Sessions
# ==========================================

@app.post(
    "/sessions",
    response_model=SessionResponse
)
def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    new_session = ChatSession(
        title=session_data.title,
        user_id=current_user.id
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return new_session


@app.get(
    "/sessions",
    response_model=list[SessionResponse]
)
def get_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id
    ).order_by(
        ChatSession.created_at.desc()
    ).all()

    return sessions


@app.get(
    "/sessions/{session_id}",
    response_model=SessionResponse
)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session


# ==========================================
# Messages
# ==========================================

@app.get(
    "/sessions/{session_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    messages = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(
        Message.created_at.asc()
    ).all()

    return messages


# ==========================================
# AI Chat
# ==========================================

@app.post(
    "/sessions/{session_id}/chat"
)
async def chat(
    session_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()

    if not session:

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    user_message = Message(
        session_id=session_id,
        role="user",
        content=message_data.content
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    history = db.query(Message).filter(
        Message.session_id == session_id
    ).order_by(
        Message.created_at.asc()
    ).all()

    chat_history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in history
    ]

    ai_response = await agent.run(
        message=message_data.content,
        chat_history=chat_history
    )

    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=ai_response
    )

    db.add(assistant_message)
    db.commit()
    db.refresh(assistant_message)

    return {
        "session_id": session_id,
        "user_message": user_message.content,
        "assistant_message": assistant_message.content
    }


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    file_path = UPLOAD_DIR / file.filename

    content = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    create_vector_store(
        str(file_path)
    )

    return {
        "message": "Document uploaded successfully",
        "filename": file.filename
    }
