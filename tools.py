"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    
    try:
        listings = load_listings()
        results = []

        for item in listings:
            # Filter by size
            if size and size.lower() not in item.get("size", "").lower():
                continue
            # Filter by price
            if max_price and item.get("price", 0) > max_price:
                continue

            # Score by keyword overlap
            desc_words = description.lower().split()
            searchable = (
                item.get("title", "").lower() + " " +
                item.get("description", "").lower() + " " +
                " ".join(item.get("style_tags", []))
            )
            score = sum(1 for word in desc_words if word in searchable)
            if score > 0:
                results.append((score, item))

        # Sort by score, return just the dicts
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results]

    except Exception:
        return []

    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.

    Args:
        description: Keywords describing what the user is looking for
                     (e.g., "vintage graphic tee").
        size:        Size string to filter by, or None to skip size filtering.
                     Matching is case-insensitive (e.g., "M" matches "S/M").
        max_price:   Maximum price (inclusive), or None to skip price filtering.

    Returns:
        A list of matching listing dicts, sorted by relevance (best match first).
        Returns an empty list if nothing matches — does NOT raise an exception.

    Each listing dict has the following fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand, platform

    TODO:
        1. Load all listings with load_listings().
        2. Filter by max_price and size (if provided).
        3. Score each remaining listing by keyword overlap with `description`.
        4. Drop any listings with a score of 0 (no relevant matches).
        5. Sort by score, highest first, and return the listing dicts.

    Before writing code, fill in the Tool 1 section of planning.md.
    """
    # Replace this with your implementation
    return []


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:


    try:
        client = _get_groq_client()
        wardrobe_items = wardrobe.get("items", [])

        if not wardrobe_items:
            prompt = (
                f"I just thrifted a {new_item.get('title')}. "
                f"It's described as: {new_item.get('description')}. "
                f"Give me general styling advice — what kinds of pieces pair well "
                f"with this and what vibe does it suit?"
            )
        else:
            wardrobe_text = "\n".join(
                f"- {i.get('name')}: {i.get('description', '')}"
                for i in wardrobe_items
            )
            prompt = (
                f"I just thrifted a {new_item.get('title')}. "
                f"It's described as: {new_item.get('description')}. "
                f"Here's my current wardrobe:\n{wardrobe_text}\n"
                f"Suggest 1-2 complete outfit combinations using this new item "
                f"and specific pieces from my wardrobe."
            )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Could not generate outfit suggestion: {str(e)}"


    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.

    Args:
        new_item: A listing dict (the item the user is considering buying).
        wardrobe: A wardrobe dict with an 'items' key containing a list of
                  wardrobe item dicts. May be empty — handle this gracefully.

    Returns:
        A non-empty string with outfit suggestions.
        If the wardrobe is empty, offer general styling advice for the item
        rather than raising an exception or returning an empty string.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If empty: call the LLM with a prompt for general styling ideas
           (what kinds of items pair well, what vibe it suits, etc.).
        3. If not empty: format the wardrobe items into a prompt and ask
           the LLM to suggest specific outfit combinations using the new item
           and named pieces from the wardrobe.
        4. Return the LLM's response as a string.

    Before writing code, fill in the Tool 2 section of planning.md.
    """
    # Replace this with your implementation
    return ""


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:

    if not outfit or not outfit.strip():
        return "Could not generate fit card: no outfit suggestion provided."

    try:
        client = _get_groq_client()
        prompt = (
            f"Write a short 2-3 sentence Instagram caption for this thrifted outfit. "
            f"The item is a {new_item.get('title')} bought on {new_item.get('platform')} "
            f"for ${new_item.get('price')}. "
            f"The outfit: {outfit}. "
            f"Make it casual, authentic, and specific — like a real OOTD post. "
            f"Mention the item name, price, and platform naturally."
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=1.2,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Could not generate fit card: {str(e)}"


    """
    Generate a short, shareable outfit caption for the thrifted find.

    Args:
        outfit:   The outfit suggestion string from suggest_outfit().
        new_item: The listing dict for the thrifted item.

    Returns:
        A 2–4 sentence string usable as an Instagram/TikTok caption.
        If outfit is empty or missing, return a descriptive error message
        string — do NOT raise an exception.

    The caption should:
    - Feel casual and authentic (like a real OOTD post, not a product description)
    - Mention the item name, price, and platform naturally (once each)
    - Capture the outfit vibe in specific terms
    - Sound different each time for different inputs (use higher LLM temperature)

    TODO:
        1. Guard against an empty or whitespace-only outfit string.
        2. Build a prompt that gives the LLM the item details and the outfit,
           and asks for a caption matching the style guidelines above.
        3. Call the LLM and return the response.

    Before writing code, fill in the Tool 3 section of planning.md.
    """
    # Replace this with your implementation
    return ""
