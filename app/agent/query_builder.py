class QueryBuilder:

    def __init__(self):

        # refinement keywords
        self.refinement_terms = {

            "also",
            "add",
            "include",
            "along",
            "with",
            "more",
            "senior",
            "junior",
            "leadership",
            "communication",
            "technical",
            "personality",
            "aptitude"
        }

    # =========================
    # CHECK IF FOLLOW-UP
    # =========================

    def is_refinement_query(
        self,
        message
    ):

        message = message.lower()

        return any(

            term in message

            for term in self.refinement_terms
        )

    # =========================
    # BUILD QUERY
    # =========================

    def build_query(
        self,
        messages
    ):

        user_messages = [

            msg["content"]

            for msg in messages

            if msg["role"] == "user"
        ]

        # no messages
        if not user_messages:

            return ""

        latest_message = user_messages[-1]

        # =========================
        # REFINEMENT QUERY
        # =========================

        if (

            len(user_messages) > 1

            and self.is_refinement_query(
                latest_message
            )
        ):

            previous_message = user_messages[-2]

            combined_query = (

                previous_message
                + " "
                + latest_message
            )

            return combined_query

        # =========================
        # NORMAL QUERY
        # =========================

        return latest_message