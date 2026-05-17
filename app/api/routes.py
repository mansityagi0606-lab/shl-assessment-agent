from fastapi import APIRouter

from app.api.models import (
    ChatRequest,
    ChatResponse
)

from app.agent.conversation_agent import (
    ConversationAgent
)

# =========================
# ROUTER INIT (MUST BE TOP)
# =========================
router = APIRouter()

agent = ConversationAgent()


# =========================
# HEALTH ENDPOINT
# =========================
@router.get("/health")
def health():
    return {
        "status": "ok"
    }


# =========================
# UTILITY: MERGE MESSAGES
# =========================
def merge_user_messages(messages):
    return " ".join(
        msg["content"].strip()
        for msg in messages
        if msg["role"] == "user"
    )


# =========================
# CHAT ENDPOINT
# =========================
@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):

    # Convert Pydantic messages → dict format
    messages = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in request.messages
    ]

    # Merge multi-turn user messages into single intent
    merged_content = merge_user_messages(messages)

    # Build clean payload for agent
    processed_messages = [
        {
            "role": "user",
            "content": merged_content
        }
    ]

    # Call agent
    response = agent.handle_conversation(processed_messages)

    return response