# FitFindr 🛍️

A multi-tool AI agent that helps you find secondhand clothing and build outfits around it.
Describe what you're looking for, and FitFindr searches listings, suggests outfits from your 
wardrobe, and generates a shareable fit card — all in sequence.

---

## How to Run

1. Clone the repo and activate your virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Add your Groq API key to a `.env` file: `GROQ_API_KEY=your_key_here`
4. Run: `python app.py`
5. Open the URL shown in your terminal

---

## Tool Inventory

**1. search_listings(description: str, size: str, max_price: float) → list[dict]**
Searches listings.json for items matching the user's description, size, and budget.
Scores each item by keyword overlap and returns results sorted by relevance.
Returns `[]` if nothing matches — never crashes.

**2. suggest_outfit(new_item: dict, wardrobe: dict) → str**
Takes the found item and the user's wardrobe and uses the Groq LLM to suggest
1-2 complete outfit combinations using specific wardrobe pieces.
If the wardrobe is empty, returns general styling advice instead.

**3. create_fit_card(outfit: str, new_item: dict) → str**
Takes the outfit suggestion and item details and generates a short Instagram-style
caption. If outfit is empty, returns an error message string instead of crashing.

---

## How the Planning Loop Works

The agent parses the user's query for a description, size, and max price using regex.
It then runs through this sequence:

1. Call `search_listings()` — if results are empty, save an error message and stop.
   `suggest_outfit` is never called with empty input.
2. Save `results[0]` to `session["selected_item"]` and call `suggest_outfit()`
3. Save the suggestion to `session["outfit_suggestion"]` and call `create_fit_card()`
4. Return the completed session

The agent behaves differently based on what each tool returns — it does not call
all three tools unconditionally.

---

## State Management

All data is stored in a session dict initialized at the start of each interaction:

- `session["selected_item"]` — set after search, passed into suggest_outfit
- `session["outfit_suggestion"]` — set after suggest_outfit, passed into create_fit_card
- `session["fit_card"]` — set after create_fit_card, displayed in the UI
- `session["error"]` — set if a tool fails or returns nothing, stops the loop early

No data is re-entered between steps — everything flows through the session.

---

## Error Handling

| Tool | Failure | Response |
|---|---|---|
| search_listings | No matches found | Returns `[]`, agent sets error message "Try a different price or size" and stops |
| suggest_outfit | Empty wardrobe | Returns general styling advice instead of outfit combinations |
| create_fit_card | Empty outfit string | Returns "Could not generate fit card: no outfit suggestion provided" |

**Example from testing:**
Running `search_listings("designer ballgown", "XXS", 5)` returns `[]` and the agent
responds with "Try a different price or size — no listings matched your search."
without calling any further tools.

---

## Spec Reflection

**What matched:** The planning loop branching logic worked exactly as designed —
the diagram in planning.md translated directly into the if/else structure in agent.py.

**What diverged:** The query parsing ended up using regex instead of the LLM,
which was simpler and faster. The tradeoff is that unusual query formats might
not parse correctly, but it works reliably for standard inputs.

---

## AI Usage

**1. search_listings implementation:**
I gave Claude my Tool 1 spec (inputs, return value, failure mode) and asked it to
implement the function using `load_listings()`. I reviewed the output and changed
the filtering logic to use keyword scoring instead of exact string matching,
which returned better results.

**2. suggest_outfit and create_fit_card:**
I gave Claude both tool specs and asked it to implement them using the Groq API.
I adjusted the prompts to sound more natural and increased the temperature on
`create_fit_card` to 1.2 so outputs vary between runs.

**3. Planning loop:**
I gave Claude my architecture diagram and asked it to implement `run_agent()`.
I added the regex query parser myself since the generated code didn't include
query parsing at all.