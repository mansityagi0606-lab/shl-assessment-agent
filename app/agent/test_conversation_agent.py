from app.agent.conversation_agent import ConversationAgent


messages = [
    {
        "role": "user",
        "content": "Need Java backend developer assessment"
    }
]

agent = ConversationAgent()

response = agent.handle_conversation(
    messages
)

print("\n========== AGENT RESPONSE ==========\n")

print(response)