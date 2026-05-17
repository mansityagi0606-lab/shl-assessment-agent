import json
import os
import re

# =========================
# PATHS
# =========================

INPUT_PATH = "data/raw/shl_catalog_raw.json"

OUTPUT_PATH = "data/processed/shl_catalog_cleaned.json"

# =========================
# MASTER SKILLS
# =========================

MASTER_SKILLS = [
    "java",
    "python",
    "sql",
    "javascript",
    "cloud",
    "devops",
    "backend",
    "frontend",
    "software engineering",
    "communication",
    "leadership",
    "stakeholder management",
    "problem solving",
    "customer service",
    "data analysis",
    "analytics",
    "teamwork",
    "cognitive",
    "personality",
    "behavioral",
    "reasoning"
]

# =========================
# CLEAN TEXT
# =========================

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text

# =========================
# EXTRACT SKILLS
# =========================

def extract_skills(name, description):

    combined = (
        name + " " + description
    ).lower()

    found = []

    for skill in MASTER_SKILLS:

        if skill in combined:
            found.append(skill)

    return list(set(found))

# =========================
# INFER TEST TYPE
# =========================

def infer_test_type(name, description, skills):

    combined = (
        name + " " +
        description + " " +
        " ".join(skills)
    ).lower()

    # =========================
    # PERSONALITY
    # =========================

    personality_keywords = [
        "personality",
        "behavior",
        "behavioral",
        "motivation",
        "work style",
        "culture fit"
    ]

    for keyword in personality_keywords:

        if keyword in combined:
            return "P"

    # =========================
    # TECHNICAL
    # =========================

    technical_keywords = [
        "java",
        "python",
        "sql",
        "javascript",
        "cloud",
        "coding",
        "programming",
        "software",
        "developer",
        "technical",
        "backend",
        "frontend"
    ]

    for keyword in technical_keywords:

        if keyword in combined:
            return "T"

    # =========================
    # APTITUDE
    # =========================

    aptitude_keywords = [
        "cognitive",
        "numerical",
        "verbal",
        "logical",
        "reasoning",
        "problem solving"
    ]

    for keyword in aptitude_keywords:

        if keyword in combined:
            return "A"

    # =========================
    # SKILLS
    # =========================

    skills_keywords = [
        "communication",
        "leadership",
        "customer service",
        "stakeholder"
    ]

    for keyword in skills_keywords:

        if keyword in combined:
            return "S"

    return "General"

# =========================
# INFER CATEGORY
# =========================

def infer_category(test_type):

    mapping = {
        "P": "personality",
        "T": "technical",
        "A": "aptitude",
        "S": "skills"
    }

    return mapping.get(test_type, "general")

# =========================
# BUILD SEARCH TEXT
# =========================

def build_search_text(item):

    fields = [
        item["name"],
        item["description"],
        item["category"],
        item["test_type"],
        " ".join(item["skills"])
    ]

    combined = " ".join(fields)

    combined = clean_text(combined)

    return combined

# =========================
# MAIN
# =========================

def main():

    print("\nLoading raw catalog...")

    with open(INPUT_PATH, "r", encoding="utf-8") as f:

        raw_data = json.load(f)

    print(f"Loaded {len(raw_data)} assessments.")

    cleaned_data = []

    for item in raw_data:

        name = clean_text(
            item.get("name", "")
        )

        description = clean_text(
            item.get("description", "")
        )

        url = item.get("url", "")

        # =========================
        # SKILLS
        # =========================

        skills = extract_skills(
            name,
            description
        )

        # =========================
        # TEST TYPE
        # =========================

        test_type = infer_test_type(
            name,
            description,
            skills
        )

        # =========================
        # CATEGORY
        # =========================

        category = infer_category(
            test_type
        )

        cleaned_item = {
            "name": name,
            "description": description,
            "url": url,
            "skills": skills,
            "test_type": test_type,
            "category": category
        }

        # =========================
        # SEARCH TEXT
        # =========================

        cleaned_item["search_text"] = build_search_text(
            cleaned_item
        )

        cleaned_data.append(
            cleaned_item
        )

    # =========================
    # CREATE OUTPUT DIRECTORY
    # =========================

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    # =========================
    # SAVE CLEANED DATA
    # =========================

    with open(
        OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            cleaned_data,
            f,
            indent=2,
            ensure_ascii=False
        )

    print("\n========== CLEANING COMPLETE ==========")

    print(f"\nTotal cleaned assessments: {len(cleaned_data)}")

    print(f"\nSaved cleaned catalog to:\n{OUTPUT_PATH}")

# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":

    main()