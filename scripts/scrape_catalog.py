import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re
from tqdm import tqdm
from urllib.parse import urljoin

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"

headers = {
    "User-Agent": "Mozilla/5.0"
}


def get_catalog_page(page_number=1):
    """
    Fetch catalog page using correct pagination offset
    """

    PRODUCTS_PER_PAGE = 12

    offset = (page_number - 1) * PRODUCTS_PER_PAGE

    url = f"{CATALOG_URL}?start={offset}"

    print(f"Fetching URL: {url}")

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to load page {page_number}")

    return BeautifulSoup(response.text, "lxml")


def extract_product_links(soup):
    """
    Extract product links from catalog page
    """

    products = []

    links = soup.find_all("a", href=True)

    seen = set()

    for link in links:

        href = link["href"]
        text = link.get_text(strip=True)

        # Product detail pages
        if "/products/product-catalog/view/" in href:

            # Skip empty names
            if not text:
                continue

            # Skip packaged job solutions
            if "solution" in text.lower():
                continue

            full_url = urljoin(BASE_URL, href)

            if full_url not in seen:

                seen.add(full_url)

                products.append({
                    "name": text,
                    "url": full_url
                })

    return products


def scrape_product_details(product):
    """
    Scrape individual product page
    """

    try:

        response = requests.get(product["url"], headers=headers)

        if response.status_code != 200:
            print(f"Failed URL: {product['url']}")
            return None

        soup = BeautifulSoup(response.text, "lxml")

        # =========================
        # DESCRIPTION
        # =========================

        description = ""

        meta_desc = soup.find("meta", attrs={"name": "description"})

        if meta_desc:
            description = meta_desc.get("content", "").strip()

        # =========================
        # FULL PAGE TEXT
        # =========================

        page_text = soup.get_text(" ", strip=True)

        # =========================
        # CATEGORY
        # =========================

        category = ""

        possible_categories = [
            "Ability & Aptitude",
            "Personality & Behavior",
            "Technical",
            "Skills",
            "Competency",
            "Simulation"
        ]

        for cat in possible_categories:

            if cat.lower() in page_text.lower():
                category = cat
                break

        # =========================
        # DURATION
        # =========================

        duration = ""

        duration_match = re.search(
            r"(\d+)\s*(minutes|minute|mins|min)",
            page_text,
            re.IGNORECASE
        )

        if duration_match:
            duration = duration_match.group(0)

        # =========================
        # SKILLS EXTRACTION
        # =========================

        skills_keywords = [
            "java",
            "python",
            "sql",
            "javascript",
            "cloud",
            "devops",
            "leadership",
            "communication",
            "problem solving",
            "cognitive",
            "personality",
            "analytics",
            "software development",
            "teamwork",
            "stakeholder management",
            "attention to detail",
            "critical thinking",
            "data analysis",
            "customer service"
        ]

        found_skills = []

        for skill in skills_keywords:

            if skill.lower() in page_text.lower():
                found_skills.append(skill)

        # =========================
        # REMOTE TESTING
        # =========================

        remote_testing = "yes" if "remote testing" in page_text.lower() else "no"

        # =========================
        # ADAPTIVE SUPPORT
        # =========================

        adaptive_support = "yes" if "adaptive" in page_text.lower() else "no"

        # =========================
        # TEST TYPE
        # =========================

        test_type = ""

        if "personality" in page_text.lower():
            test_type = "P"

        elif "ability" in page_text.lower():
            test_type = "A"

        elif "technical" in page_text.lower():
            test_type = "T"

        elif "skill" in page_text.lower():
            test_type = "S"

        # =========================
        # FINAL DATA
        # =========================

        product_data = {
            "name": product["name"],
            "url": product["url"],
            "description": description,
            "category": category,
            "skills": found_skills,
            "duration": duration,
            "languages": [],
            "remote_testing": remote_testing,
            "adaptive_support": adaptive_support,
            "test_type": test_type
        }

        return product_data

    except Exception as e:

        print(f"Error scraping: {product['url']}")
        print(e)

        return None


def main():

    print("\nStarting SHL catalog scraping...\n")

    all_products = []
    seen_urls = set()

    TOTAL_PAGES = 12

    # =========================
    # SCRAPE ALL PAGES
    # =========================

    for page in range(1, TOTAL_PAGES + 1):

        print(f"Scraping catalog page {page}...")

        try:

            soup = get_catalog_page(page)

            products = extract_product_links(soup)

            print(f"Found {len(products)} products on page {page}")

            for product in products:

                if product["url"] not in seen_urls:

                    seen_urls.add(product["url"])
                    all_products.append(product)

            time.sleep(1)

        except Exception as e:

            print(f"Error on page {page}")
            print(e)

    print(f"\nTotal unique products found: {len(all_products)}")

    # =========================
    # SCRAPE PRODUCT DETAILS
    # =========================

    detailed_products = []

    failed_urls = []

    for product in tqdm(all_products):

        data = scrape_product_details(product)

        if data:
            detailed_products.append(data)

        else:
            failed_urls.append(product["url"])

        time.sleep(1)

    # =========================
    # CREATE OUTPUT DIRECTORY
    # =========================

    output_dir = "data/raw"

    os.makedirs(output_dir, exist_ok=True)

    # =========================
    # SAVE PRODUCT DATA
    # =========================

    output_path = os.path.join(
        output_dir,
        "shl_catalog_raw.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(
            detailed_products,
            f,
            indent=4,
            ensure_ascii=False
        )

    # =========================
    # SAVE FAILED URLS
    # =========================

    failed_output = os.path.join(
        output_dir,
        "failed_urls.json"
    )

    with open(failed_output, "w", encoding="utf-8") as f:

        json.dump(
            failed_urls,
            f,
            indent=4
        )

    # =========================
    # FINAL LOGS
    # =========================

    print("\n========== SCRAPING COMPLETE ==========")

    print(f"Total scraped products: {len(detailed_products)}")

    print(f"Failed URLs: {len(failed_urls)}")

    print(f"\nSaved catalog to:\n{output_path}")

    print(f"\nSaved failed URLs to:\n{failed_output}")


if __name__ == "__main__":
    main()