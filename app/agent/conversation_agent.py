import time
import traceback

from sentence_transformers import (
    SentenceTransformer
)


from app.agent.intent_router import (
    IntentRouter
)

from app.agent.query_builder import (
    QueryBuilder
)

from app.agent.reranker import (
    ReRanker
)

from app.agent.guardrails import (
    Guardrails
)

from app.agent.comparison_engine import (
    ComparisonEngine
)

from app.retrieval.retriever import (
    SHLRetriever
)

from app.llm.response_generator import (
    ResponseGenerator
)


class ConversationAgent:

    def __init__(self):

        self.intent_router = (
            IntentRouter()
        )

        self.query_builder = (
            QueryBuilder()
        )

        self.reranker = (
            ReRanker()
        )

        self.guardrails = (
            Guardrails()
        )

        self.retriever = (
            SHLRetriever()
        )

        self.comparison_engine = (
            ComparisonEngine()
        )

        self.response_generator = (
            ResponseGenerator()
        )

        

        # =========================
        # EMBEDDING MODEL
        # =========================

        self.embedding_model = (
            SentenceTransformer(
                "all-MiniLM-L6-v2"
            )
        )

        # =========================
        # ROLE FILTERS
        # =========================

        self.role_filters = {

            "Frontend Engineer": [

                "javascript",
                "react",
                "frontend",
                "ui",
                "css",
                "html"
            ],

            "Backend Engineer": [

                "backend",
                "api",
                "python",
                "java",
                "sql"
            ],

            "Data Scientist": [

                "machine learning",
                "python",
                "statistics",
                "data analysis",
                "ai"
            ]
        }

    # =========================
    # FORMAT RESULTS
    # =========================

    def format_results(
        self,
        results
    ):

        formatted = []

        for result in results:

            formatted.append({

                "name": result.get(
                    "name",
                    ""
                ),

                "url": result.get(
                    "url",
                    ""
                ),

                "category": result.get(
                    "category",
                    ""
                ),

                "test_type": result.get(
                    "test_type",
                    ""
                ),

                "skills": result.get(
                    "skills",
                    []
                ),

                "description": result.get(
                    "description",
                    ""
                )
            })

        return formatted

    # =========================
    # EXTRACT INTENT
    # =========================

    def extract_intent(
        self,
        messages
    ):

        conversation_text = " ".join(

            msg.get(
                "content",
                ""
            ).lower()

            for msg in messages
        )

        role = None

        requested_assessments = []

        # =========================
        # ROLE DETECTION
        # =========================

        if any(

            keyword in conversation_text

            for keyword in [

                "frontend",
                "react",
                "ui",
                "javascript"
            ]
        ):

            role = "Frontend Engineer"

        elif any(

            keyword in conversation_text

            for keyword in [

                "backend",
                "java",
                "api",
                "python"
            ]
        ):

            role = "Backend Engineer"

        elif any(

            keyword in conversation_text

            for keyword in [

                "data scientist",
                "machine learning",
                "ai"
            ]
        ):

            role = "Data Scientist"

        # =========================
        # ASSESSMENT DETECTION
        # =========================

        if "personality" in conversation_text:

            requested_assessments.append(
                "Personality"
            )

        if "aptitude" in conversation_text:

            requested_assessments.append(
                "Aptitude"
            )

        if "coding" in conversation_text:

            requested_assessments.append(
                "Coding"
            )

        if "communication" in conversation_text:

            requested_assessments.append(
                "Communication"
            )

        return {

            "role": role,

            "requested_assessments": (
                requested_assessments
            )
        }

    # =========================
    # CLARIFICATION CHECK
    # =========================

    def needs_clarification(
        self,
        messages
    ):

        latest_message = messages[-1][
            "content"
        ].lower()

        vague_terms = [

            "assessment",
            "test",
            "hire",
            "hiring",
            "candidate",
            "evaluation"
        ]

        role_keywords = [

            "frontend",
            "backend",
            "developer",
            "engineer",
            "data scientist",
            "python",
            "java",
            "react"
        ]

        has_vague_term = any(

            term in latest_message

            for term in vague_terms
        )

        has_role_context = any(

            keyword in latest_message

            for keyword in role_keywords
        )

        return (
            has_vague_term
            and not has_role_context
        )

    # =========================
    # MAIN HANDLER
    # =========================

    def handle_conversation(
        self,
        messages
    ):

        start_time = time.time()

        try:

            latest_message = messages[-1][
                "content"
            ]

            # =========================
            # DETECT INTENT
            # =========================

            try:

                intent = (

                    self.intent_router
                    .detect_intent(messages)
                )

            except Exception:

                intent = "recommendation"

            # =========================
            # OFF TOPIC
            # =========================

            if intent == "off_topic":

                return {

                    "reply": (

                        self.guardrails
                        .off_topic_response()
                    ),

                    "recommendations": [],

                    "end_of_conversation": False
                }

            # =========================
            # COMPARISON
            # =========================

            try:

                is_comparison = (

                    self.comparison_engine
                    .is_comparison_query(
                        latest_message
                    )
                )

            except Exception:

                is_comparison = False

            if is_comparison:

                return (

                    self.comparison_engine
                    .compare(

                        query=latest_message,

                        metadata=(
                            self.retriever
                            .metadata
                        )
                    )
                )

            # =========================
            # CLARIFICATION
            # =========================

            if self.needs_clarification(
                messages
            ):

                return {

                    "reply": (
                        "Please specify "
                        "the role or skills "
                        "you are hiring for."
                    ),

                    "recommendations": [],

                    "end_of_conversation": False
                }

            # =========================
            # EXTRACT INTENT
            # =========================

            structured_intent = (
                self.extract_intent(
                    messages
                )
            )

            role = structured_intent[
                "role"
            ]

            requested_assessments = (
                structured_intent[
                    "requested_assessments"
                ]
            )

            # =========================
            # BUILD QUERY
            # =========================

            try:

                query = (
                    self.query_builder
                    .build_query(messages)
                )

            except Exception:

                query = latest_message

            # =========================
            # GENERATE EMBEDDING
            # =========================

            try:

                query_embedding = (

                    self.embedding_model
                    .encode(query)
                    .astype("float32")
                )

            except Exception:

                return {

                    "reply": (
                        "Failed to process "
                        "your request."
                    ),

                    "recommendations": [],

                    "end_of_conversation": False
                }

            # =========================
            # FILTERS
            # =========================

            filters = self.role_filters.get(
                role,
                []
            )

            # =========================
            # RETRIEVE
            # =========================

            try:

                retrieved = (

                    self.retriever.retrieve(

                        query_embedding=(
                            query_embedding
                        ),

                        top_k=10,

                        filters=filters
                    )
                )

            except Exception:

                retrieved = []

            # =========================
            # EMPTY RESULTS
            # =========================

            if not retrieved:

                return {

                    "reply": (

                        self.guardrails
                        .empty_results_response()
                    ),

                    "recommendations": [],

                    "end_of_conversation": False
                }

            # =========================
            # RERANK
            # =========================

            try:

                reranked = (

                    self.reranker.rerank(

                        query=query,

                        retrieved_results=retrieved
                    )
                )

            except Exception:

                reranked = retrieved

            # =========================
            # FORMAT
            # =========================

            formatted_results = (
                self.format_results(
                    reranked[:10]
                )
            )

            # =========================
            # REMOVE DUPLICATES
            # =========================

            unique_results = []

            seen_names = set()

            for result in formatted_results:

                name = result.get(
                    "name",
                    ""
                )

                url = result.get(
                    "url",
                    ""
                )

                # Skip duplicates
                if name in seen_names:
                    continue

                # Skip empty URLs
                if not url:
                    continue

                seen_names.add(name)

                unique_results.append({

                    "name": name,

                    "url": url,

                    "test_type": result.get(
                        "test_type",
                        "General"
                    )
                })

            # =========================
            # LIMIT TO 10
            # =========================

            final_recommendations = (
                unique_results[:10]
            )

            # =========================
            # GENERATE RESPONSE
            # =========================

            try:

                llm_reply = (

                    self.response_generator
                    .generate_recommendation_reply(

                        query=query,

                        recommendations=(
                            final_recommendations
                        )
                    )
                )

            except Exception:

                llm_reply = (
                    "Here are the recommended "
                    "SHL assessments."
                )

            # =========================
            # TIME LOG
            # =========================

            total_time = round(

                time.time() - start_time,

                2
            )

            print(
                f"\nTOTAL RESPONSE TIME: "
                f"{total_time} sec"
            )

            # =========================
            # FINAL RESPONSE
            # =========================

            return {

                "reply": llm_reply,

                "recommendations": (
                    final_recommendations
                ),

                "end_of_conversation": True
            }

        except Exception as e:

            print(
                "\nERROR IN CONVERSATION AGENT:"
            )

            traceback.print_exc()

            total_time = round(

                time.time() - start_time,

                2
            )

            print(
                f"\nFAILED AFTER: "
                f"{total_time} sec"
            )

            return {

                "reply": (
                    f"Internal error occurred: "
                    f"{str(e)}"
                ),

                "recommendations": [],

                "end_of_conversation": False
            }