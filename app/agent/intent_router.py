class IntentRouter:

    def __init__(self):

        # =========================
        # ALLOWED SHL / HIRING TERMS
        # =========================

        self.allowed_keywords = [

            "assessment",
            "assessments",
            "test",
            "tests",
            "hiring",
            "hire",
            "candidate",
            "job",
            "role",
            "developer",
            "engineer",
            "frontend",
            "backend",
            "java",
            "python",
            "react",
            "leadership",
            "personality",
            "communication",
            "aptitude",
            "coding",
            "evaluation",
            "skill",
            "skills",
            "data scientist",
            "machine learning",
            "ai",
            "cloud",
            "devops",
            "stakeholder",
            "manager"
        ]

    # =========================
    # DETECT INTENT
    # =========================

    def detect_intent(
        self,
        messages
    ):

        """
        Detect user intent
        """

        text = " ".join(

            msg["content"].lower()

            for msg in messages
        )

        # =========================
        # COMPARISON
        # =========================

        comparison_keywords = [

            "compare",
            "difference",
            "vs",
            "versus"
        ]

        for keyword in comparison_keywords:

            if keyword in text:

                return "comparison"

        # =========================
        # REFINEMENT
        # =========================

        refinement_keywords = [

            "add",
            "remove",
            "also",
            "include",
            "instead",
            "only",
            "exclude"
        ]

        for keyword in refinement_keywords:

            if keyword in text:

                return "refine"

        # =========================
        # CLARIFICATION
        # =========================

        clarification_keywords = [

            "what do you mean",
            "explain",
            "clarify"
        ]

        for keyword in clarification_keywords:

            if keyword in text:

                return "clarification"

        # =========================
        # OFF TOPIC CHECK
        # =========================

        in_scope = any(

            keyword in text

            for keyword in (
                self.allowed_keywords
            )
        )

        if not in_scope:

            return "off_topic"

        # =========================
        # DEFAULT
        # =========================

        return "recommendation"