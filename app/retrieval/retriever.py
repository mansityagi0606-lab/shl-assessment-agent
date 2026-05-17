import faiss
import numpy as np


class SHLRetriever:

    def __init__(self):

        # =====================================
        # LOAD FAISS INDEX
        # =====================================

        self.index = faiss.read_index(
            "data/faiss/index.faiss"
        )

        # =====================================
        # LOAD METADATA
        # =====================================

        self.metadata = np.load(
            "data/faiss/metadata.pkl",
            allow_pickle=True
        )

    # =====================================
    # SAFE TEXT EXTRACTION
    # =====================================

    def build_search_text(
        self,
        item
    ):

        return (

            item.get("name", "")
            + " "
            + item.get("description", "")
            + " "
            + " ".join(
                item.get("skills", [])
            )
            + " "
            + item.get("category", "")

        ).lower()

    # =====================================
    # FILTER MATCH
    # =====================================

    def matches_filters(
        self,
        item,
        filters
    ):

        if not filters:
            return True

        combined_text = self.build_search_text(
            item
        )

        return any(

            keyword.lower() in combined_text

            for keyword in filters
        )

    # =====================================
    # RETRIEVE
    # =====================================

    def retrieve(
        self,
        query_embedding,
        top_k=10,
        filters=None
    ):

        try:

            # =====================================
            # FORMAT EMBEDDING
            # =====================================

            query_embedding = np.array(
                [query_embedding]
            ).astype("float32")

            # =====================================
            # SEARCH INDEX
            # =====================================

            distances, indices = self.index.search(

                query_embedding,

                top_k
            )

            results = []

            # =====================================
            # BUILD RESULTS
            # =====================================

            for rank, idx in enumerate(indices[0]):

                # invalid index
                if idx == -1:
                    continue

                # out of range
                if idx >= len(self.metadata):
                    continue

                metadata_item = dict(
                    self.metadata[idx]
                )

                # =====================================
                # ADD FAISS SCORE
                # =====================================

                metadata_item["score"] = float(
                    distances[0][rank]
                )

                # =====================================
                # FILTER INVALID ITEMS
                # =====================================

                if not metadata_item.get(
                    "name"
                ):
                    continue

                if not metadata_item.get(
                    "url"
                ):
                    continue

                # =====================================
                # FILTER MATCHING
                # =====================================

                if self.matches_filters(
                    metadata_item,
                    filters
                ):

                    results.append(
                        metadata_item
                    )

            return results

        except Exception as e:

            print("\nERROR IN RETRIEVER")
            print(str(e))

            return []
    