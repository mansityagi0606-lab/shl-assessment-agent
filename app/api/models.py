from pydantic import BaseModel
from typing import List


# =========================
# MESSAGE MODEL
# =========================

class Message(BaseModel):

    role: str

    content: str


# =========================
# CHAT REQUEST
# =========================

class ChatRequest(BaseModel):

    messages: List[Message]


# =========================
# RECOMMENDATION MODEL
# =========================

class Recommendation(BaseModel):

    name: str

    url: str

    test_type: str


# =========================
# CHAT RESPONSE
# =========================

class ChatResponse(BaseModel):

    reply: str

    recommendations: List[Recommendation]

    end_of_conversation: bool