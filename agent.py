"""
agent.py
"""

import re
from tools import search_listings, suggest_outfit, create_fit_card


def _new_session(query: str, wardrobe: dict) -> dict:
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


def run_agent(query: str, wardrobe: dict) -> dict:
    # Step 1: Initialize session
    session = _new_session(query, wardrobe)

    # Step 2: Parse the query for description, size, max_price
    size_match = re.search(r'\bsize\s+([A-Za-z0-9/]+)', query, re.IGNORECASE)
    price_match = re.search(r'\$?under\s+\$?(\d+)', query, re.IGNORECASE)
    size = size_match.group(1) if size_match else None
    max_price = float(price_match.group(1)) if price_match else None

    # Strip size/price mentions to get clean description
    description = re.sub(r'\bsize\s+\S+', '', query, flags=re.IGNORECASE)
    description = re.sub(r'under\s+\$?\d+', '', description, flags=re.IGNORECASE)
    description = description.strip()

    session["parsed"] = {
        "description": description,
        "size": size,
        "max_price": max_price,
    }

    # Step 3: Search listings
    results = search_listings(description, size, max_price)
    session["search_results"] = results

    if not results:
        session["error"] = "Try a different price or size — no listings matched your search."
        return session

    # Step 4: Select top result
    session["selected_item"] = results[0]

    # Step 5: Suggest outfit
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"],
        session["wardrobe"]
    )

    # Step 6: Create fit card
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"],
        session["selected_item"]
    )

    # Step 7: Return session
    return session


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")