import re

from difflib import get_close_matches


class ComparisonEngine:

    def __init__(self):

        # ==========================================
        # COMMON ALIASES
        # ==========================================

        self.aliases = {

            # ==========================================
            # GSA
            # ==========================================

            "gsa": [

                "Global Skills Assessment"
            ],

            # ==========================================
            # OPQ
            # ==========================================

            "opq": [

                "OPQ"
            ],

            # ==========================================
            # DATA SCIENCE
            # ==========================================

            "data science": [

                "Data Science (New)",

                "Automata Data Science (New)",

                "Automata Data Science Pro (New)"
            ],

            # ==========================================
            # DATA ENTRY
            # ==========================================

            "data entry": [

                "Data Entry (New)",

                "Data Entry Numeric Split Screen - US",

                "Data Entry Alphanumeric Split Screen - US"
            ],

            # ==========================================
            # JAVA
            # ==========================================

            "java 8": [

                "Core Java"
            ],

            "core java": [

                "Core Java"
            ]
        }

    # ==========================================
    # DETECT COMPARISON QUERY
    # ==========================================

    def is_comparison_query(
        self,
        query
    ):

        query = query.lower().strip()

        comparison_patterns = [

            r"compare .+ and .+",

            r"compare .+ with .+",

            r"compare .+ vs .+",

            r"difference between .+ and .+",

            r"differentiate .+ and .+",

            r"distinguish .+ and .+",

            r"contrast .+ and .+",

            r".+ vs .+",

            r".+ versus .+"
        ]

        return any(

            re.search(pattern, query)

            for pattern in comparison_patterns
        )

    # ==========================================
    # NORMALIZE QUERY
    # ==========================================

    def normalize_query(
        self,
        query
    ):

        query = query.lower().strip()

        query = query.replace(
            " versus ",
            " vs "
        )

        query = query.replace(
            " against ",
            " vs "
        )

        return query

    # ==========================================
    # EXTRACT TERMS
    # ==========================================

    def extract_terms(
        self,
        query
    ):

        query = self.normalize_query(
            query
        )

        patterns = [

            r"difference between (.+?) and (.+)",

            r"compare (.+?) and (.+)",

            r"compare (.+?) with (.+)",

            r"compare (.+?) vs (.+)",

            r"differentiate (.+?) and (.+)",

            r"distinguish (.+?) and (.+)",

            r"contrast (.+?) and (.+)",

            r"(.+?) vs (.+)",

            r"(.+?) versus (.+)"
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                query
            )

            if match:

                return [

                    match.group(1).strip(),

                    match.group(2).strip()
                ]

        return []

    # ==========================================
    # FIND BEST MATCH
    # ==========================================

    def find_best_match(
        self,
        search_term,
        metadata,
        exclude_name=None
    ):

        if not metadata:
            return None

        search_term = (
            search_term.lower().strip()
        )

        candidate_terms = [search_term]

        # ==========================================
        # ALIAS EXPANSION
        # ==========================================

        if search_term in self.aliases:

            candidate_terms.extend([

                term.lower()

                for term in self.aliases[
                    search_term
                ]
            ])

        best_match = None

        best_score = 0

        # ==========================================
        # SEARCH
        # ==========================================

        for item in metadata:

            name = item.get(
                "name",
                ""
            )

            if not name:
                continue

            if (
                exclude_name
                and name == exclude_name
            ):
                continue

            searchable_text = (

                item.get("name", "")
                + " "
                + item.get("description", "")
                + " "
                + " ".join(
                    item.get("skills", [])
                )

            ).lower()

            score = 0

            for candidate in candidate_terms:

                # Exact match
                if candidate in searchable_text:
                    score += 10

                # Token overlap
                tokens = candidate.split()

                for token in tokens:

                    if token in searchable_text:
                        score += 2

            if score > best_score:

                best_score = score

                best_match = item

        # ==========================================
        # FUZZY MATCH
        # ==========================================

        if not best_match:

            possible_names = [

                item.get("name", "")

                for item in metadata
            ]

            matches = get_close_matches(

                search_term,

                possible_names,

                n=1,

                cutoff=0.2
            )

            if matches:

                matched_name = matches[0]

                for item in metadata:

                    if (
                        item.get("name")
                        == matched_name
                    ):

                        return item

        return best_match

    # ==========================================
    # SHORT DESCRIPTION
    # ==========================================

    def short_description(
        self,
        text,
        limit=300
    ):

        if not text:

            return (
                "No description available."
            )

        text = text.strip()

        if len(text) <= limit:
            return text

        return text[:limit] + "..."

    # ==========================================
    # BUILD RECOMMENDATION
    # ==========================================

    def build_recommendation(
        self,
        assessment
    ):

        return {

            "name": assessment.get(
                "name",
                ""
            ),

            "url": assessment.get(
                "url",
                ""
            ),

            "test_type": assessment.get(
                "test_type",

                assessment.get(
                    "category",
                    "General"
                )
            )
        }

    # ==========================================
    # MAIN COMPARISON
    # ==========================================

    def compare(
        self,
        query,
        metadata
    ):

        try:

            terms = self.extract_terms(
                query
            )

            if len(terms) != 2:

                return {

                    "reply": (
                        "Please specify two "
                        "SHL assessments to compare."
                    ),

                    "recommendations": [],

                    "end_of_conversation": False
                }

            term1, term2 = terms

            # ==========================================
            # FIND MATCHES
            # ==========================================

            assessment1 = self.find_best_match(

                term1,
                metadata
            )

            assessment2 = self.find_best_match(

                term2,
                metadata,

                exclude_name=(

                    assessment1.get("name")

                    if assessment1
                    else None
                )
            )

            # ==========================================
            # NOT FOUND
            # ==========================================

            if not assessment1 or not assessment2:

                missing = []

                if not assessment1:
                    missing.append(term1)

                if not assessment2:
                    missing.append(term2)

                return {

                    "reply": (

                        "I could not find the following "
                        "assessment(s) in the SHL catalog: "
                        + ", ".join(missing)

                    ),

                    "recommendations": [],

                    "end_of_conversation": False
                }

            # ==========================================
            # EXTRACT DATA
            # ==========================================

            name1 = assessment1.get(
                "name",
                "Assessment 1"
            )

            name2 = assessment2.get(
                "name",
                "Assessment 2"
            )

            category1 = assessment1.get(
                "category",
                "General"
            )

            category2 = assessment2.get(
                "category",
                "General"
            )

            desc1 = self.short_description(

                assessment1.get(
                    "description",
                    ""
                )
            )

            desc2 = self.short_description(

                assessment2.get(
                    "description",
                    ""
                )
            )

            # ==========================================
            # BUILD RESPONSE
            # ==========================================

            reply = f"""

{name1} is primarily focused on {category1.lower()} evaluation.

{name2} is primarily focused on {category2.lower()} evaluation.

{name1} evaluates:
{desc1}

Whereas {name2} evaluates:
{desc2}
"""

            # ==========================================
            # BUILD RECOMMENDATIONS
            # ==========================================

            recommendations = []

            added = set()

            for assessment in [

                assessment1,
                assessment2
            ]:

                name = assessment.get(
                    "name",
                    ""
                )

                url = assessment.get(
                    "url",
                    ""
                )

                if not url:
                    continue

                if name in added:
                    continue

                added.add(name)

                recommendations.append(

                    self.build_recommendation(
                        assessment
                    )
                )

            return {

                "reply": reply.strip(),

                "recommendations": recommendations,

                "end_of_conversation": True
            }

        except Exception as e:

            print(
                "\nCOMPARISON ERROR:"
            )

            print(str(e))

            return {

                "reply": (
                    f"Internal error occurred: {str(e)}"
                ),

                "recommendations": [],

                "end_of_conversation": False
            }