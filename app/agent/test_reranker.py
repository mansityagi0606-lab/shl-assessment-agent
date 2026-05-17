from app.agent.query_builder import QueryBuilder
from app.agent.reranker import ReRanker
from app.retrieval.retriever import SHLRetriever


messages = [
    {
        "role": "user",
        "content": "Hiring Java backend developer"
    },
    {
        "role": "user",
        "content": "Need stakeholder communication"
    },
    {
        "role": "user",
        "content": "Add personality assessments"
    }
]

# =========================
# BUILD QUERY
# =========================

builder = QueryBuilder()

query = builder.build_query(messages)

print("\nFINAL QUERY:")
print(query)

# =========================
# RETRIEVE
# =========================

retriever = SHLRetriever()

results = retriever.retrieve(
    query=query,
    top_k=10
)

# =========================
# RERANK
# =========================

reranker = ReRanker()

reranked = reranker.rerank(
    query=query,
    retrieved_results=results
)

# =========================
# PRINT RESULTS
# =========================

print("\n========== FINAL RANKED RESULTS ==========\n")

for item in reranked[:5]:

    print(f"Name: {item['name']}")
    print(f"Final Score: {item['final_score']}")
    print(f"Skills: {item['skills']}")
    print(f"Test Type: {item['test_type']}")
    print("-" * 50)