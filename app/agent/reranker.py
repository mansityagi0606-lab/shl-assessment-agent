class ReRanker:

    def __init__(self):

        # =====================================
        # TECHNICAL KEYWORDS
        # =====================================

        self.technical_keywords = [

            "java",
            "python",
            "sql",
            "javascript",
            "backend",
            "frontend",
            "developer",
            "engineering",
            "software",
            "coding",
            "api",
            "microservices",
            "cloud",
            "database",
            "spring",
            "react"
        ]

        # =====================================
        # SOFT SKILLS
        # =====================================

        self.soft_skill_keywords = [

            "communication",
            "stakeholder",
            "leadership",
            "teamwork",
            "collaboration",
            "presentation",
            "management"
        ]

        # =====================================
        # PERSONALITY
        # =====================================

        self.personality_keywords = [

            "personality",
            "behavior",
            "behavioral",
            "culture fit",
            "motivation"
        ]

    # =====================================
    # SAFE ASSESSMENT TEXT
    # =====================================

    def get_assessment_text(
        self,
        assessment
    ):

        return (

            assessment.get("name", "")
            + " "
            + assessment.get("description", "")
            + " "
            + " ".join(
                assessment.get("skills", [])
            )
            + " "
            + assessment.get("category", "")

        ).lower()

    # =====================================
    # KEYWORD OVERLAP
    # =====================================

    def keyword_overlap_score(
        self,
        query,
        assessment_text,
        keywords,
        weight
    ):

        overlap = 0

        for keyword in keywords:

            if (
                keyword in query
                and keyword in assessment_text
            ):

                overlap += 1

        return overlap * weight

    # =====================================
    # DOMAIN BOOST
    # =====================================

    def domain_boost(
        self,
        query,
        assessment_text
    ):

        boost = 0

        # =====================================
        # BACKEND BOOST
        # =====================================

        if "backend" in query:

            backend_terms = [

                "backend",
                "java",
                "python",
                "sql",
                "api",
                "microservices",
                "server"
            ]

            for term in backend_terms:

                if term in assessment_text:
                    boost += 1

            # penalize frontend
            if (
                "frontend" in assessment_text
                or "react" in assessment_text
            ):

                boost -= 2

        # =====================================
        # FRONTEND BOOST
        # =====================================

        if "frontend" in query:

            frontend_terms = [

                "frontend",
                "react",
                "javascript",
                "html",
                "css",
                "ui"
            ]

            for term in frontend_terms:

                if term in assessment_text:
                    boost += 1

            # penalize backend
            if (
                "backend" in assessment_text
                or "java" in assessment_text
            ):

                boost -= 2

        return boost

    # =====================================
    # CATEGORY BOOST
    # =====================================

    def category_boost(
        self,
        query,
        assessment
    ):

        category = assessment.get(
            "category",
            ""
        ).lower()

        boost = 0

        if (
            any(
                word in query
                for word in self.technical_keywords
            )
            and category == "technical"
        ):

            boost += 2

        if (
            any(
                word in query
                for word in self.soft_skill_keywords
            )
            and (
                category == "skills"
                or category == "behavioral"
            )
        ):

            boost += 2

        if (
            any(
                word in query
                for word in self.personality_keywords
            )
            and category == "personality"
        ):

            boost += 2

        return boost

    # =====================================
    # MAIN RERANK
    # =====================================

    def rerank(
        self,
        query,
        retrieved_results
    ):

        query = query.lower()

        reranked = []

        for result in retrieved_results:

            assessment_text = (
                self.get_assessment_text(
                    result
                )
            )

            # =====================================
            # BASE VECTOR SCORE
            # =====================================

            faiss_distance = result.get(
                "score",
                999
            )

            # lower distance = better
            similarity_score = 1 / (
                1 + faiss_distance
            )

            final_score = similarity_score * 5

            # =====================================
            # TECHNICAL BOOST
            # =====================================

            final_score += self.keyword_overlap_score(

                query=query,

                assessment_text=assessment_text,

                keywords=self.technical_keywords,

                weight=2.5
            )

            # =====================================
            # SOFT SKILL BOOST
            # =====================================

            final_score += self.keyword_overlap_score(

                query=query,

                assessment_text=assessment_text,

                keywords=self.soft_skill_keywords,

                weight=2
            )

            # =====================================
            # PERSONALITY BOOST
            # =====================================

            final_score += self.keyword_overlap_score(

                query=query,

                assessment_text=assessment_text,

                keywords=self.personality_keywords,

                weight=2
            )

            # =====================================
            # DOMAIN BOOST
            # =====================================

            final_score += self.domain_boost(

                query=query,

                assessment_text=assessment_text
            )

            # =====================================
            # CATEGORY BOOST
            # =====================================

            final_score += self.category_boost(

                query=query,

                assessment=result
            )

            # =====================================
            # STORE FINAL SCORE
            # =====================================

            result["final_score"] = round(
                final_score,
                4
            )

            reranked.append(
                result
            )

        # =====================================
        # SORT
        # =====================================

        reranked = sorted(

            reranked,

            key=lambda x: x.get(
                "final_score",
                0
            ),

            reverse=True
        )

        return reranked