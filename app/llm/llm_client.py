import os

from groq import Groq

from dotenv import load_dotenv


# =========================
# LOAD ENV VARIABLES
# =========================

load_dotenv()


class LLMClient:

    def __init__(self):

        self.api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not self.api_key:

            raise ValueError(
                "GROQ_API_KEY not found in .env"
            )

        self.client = Groq(

            api_key=self.api_key
        )

        self.model = "llama-3.3-70b-versatile"

    # =========================
    # GENERATE RESPONSE
    # =========================

    def generate(
        self,
        prompt,
        temperature=0.3
    ):

        response = self.client.chat.completions.create(

            model=self.model,

            temperature=temperature,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "You are an SHL assessment "
                        "recommendation assistant."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return (

            response
            .choices[0]
            .message
            .content
        )