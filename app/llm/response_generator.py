from app.llm.llm_client import LLMClient

from app.llm.prompts import (

    build_recommendation_prompt,

    build_comparison_prompt
)


class ResponseGenerator:

    def __init__(self):

        self.llm = LLMClient()

    # =========================
    # GENERATE RECOMMENDATION
    # RESPONSE
    # =========================

    def generate_recommendation_reply(

        self,

        query,

        recommendations
    ):

        prompt = build_recommendation_prompt(

            query=query,

            recommendations=recommendations
        )

        response = self.llm.generate(
            prompt
        )

        return response

    # =========================
    # GENERATE COMPARISON
    # RESPONSE
    # =========================

    def generate_comparison_reply(

        self,

        comparison_text
    ):

        prompt = build_comparison_prompt(

            comparison_text
        )

        response = self.llm.generate(
            prompt
        )

        return response