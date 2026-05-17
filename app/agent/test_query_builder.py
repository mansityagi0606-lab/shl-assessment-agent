from query_builder import QueryBuilder

messages = [
    {
        "role": "user",
        "content": "Hiring Java backend developer"
    },
    {
        "role": "assistant",
        "content": "What seniority level?"
    },
    {
        "role": "user",
        "content": "Mid-level with stakeholder communication"
    },
    {
        "role": "user",
        "content": "Also add personality tests"
    }
]

builder = QueryBuilder()

query = builder.build_query(messages)

print("\nFINAL QUERY:\n")
print(query)