"""
Chat API Endpoint for Todo AI Chatbot
Implements the chat endpoint that integrates with the AI agent
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, desc
from app.database import get_session
from app.models.conversation import Conversation, Message
from app.middleware.auth import get_current_user
from app.agents.todo_agent import create_todo_agent, run_agent_with_input
from typing import Optional, Dict, Any
from pydantic import BaseModel
import uuid
from datetime import datetime
from app.models.user import User


class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    tool_calls: Optional[list] = []


router = APIRouter()


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Chat endpoint that receives user messages and returns AI responses.
    Implements the required chat flow:
    1. Receive user message
    2. Fetch conversation history from DB
    3. Store user message
    4. Run agent with function tools
    5. Execute tool calls
    6. Store assistant response
    7. Return response to frontend
    """
    # Verify user_id matches authenticated user
    if str(current_user["user_id"]) != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another user's chat"
        )

    # Validate user exists
    user = session.get(User, uuid.UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get or create conversation
    conversation_id = None
    if request.conversation_id:
        try:
            conversation_uuid = uuid.UUID(request.conversation_id)
            conversation = session.get(Conversation, conversation_uuid)
            if conversation and str(conversation.user_id) == user_id:
                conversation_id = conversation_uuid
        except ValueError:
            # Invalid UUID format, create new conversation
            pass

    if not conversation_id:
        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        conversation_id = conversation.id

    # Store user message
    user_message = Message(
        user_id=uuid.UUID(user_id),
        conversation_id=conversation_id,
        role="user",
        content=request.message,
        created_at=datetime.utcnow()
    )
    session.add(user_message)
    session.commit()

    # Fetch conversation history for context
    conversation_history = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(20)  # Get last 20 messages for context
    ).all()

    # Reverse to get chronological order (oldest first)
    conversation_history.reverse()

    # Create message history for the agent
    message_history = [
        {"role": msg.role, "content": msg.content}
        for msg in conversation_history
    ]

    # Create the agent with user context
    agent = create_todo_agent(user_id)

    # Run agent with user input and session (passing conversation history)
    try:
        response_text, executed_tool_calls = await run_agent_with_input(agent, request.message, session, message_history)
        # Return the executed tool calls to the frontend
        tool_calls = executed_tool_calls

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

    # Store assistant response
    assistant_message = Message(
        user_id=uuid.UUID(user_id),
        conversation_id=conversation_id,
        role="assistant",
        content=response_text,
        created_at=datetime.utcnow()
    )
    session.add(assistant_message)
    session.commit()

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    return ChatResponse(
        conversation_id=str(conversation_id),
        response=response_text,
        tool_calls=tool_calls
    )