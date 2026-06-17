# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them. 

### Tool 1: search_listings

**What it does:**
Searches listings.json in the project and return items matching the user's self description, ideally with size and budget 
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): A description of what type of clothing item the user is looking for.
- `size` (str): The size of the clothing item that can range from xs to xl.
- `max_price` (float): The maximum price the user is willing to pay.

**What it returns:**
Returns matching clothing items in dicts, or an empty [] 
<!-- Describe the return value — what fields does a result contain? -->

**What happens if it fails or returns nothing:**
if it returns nothing it will return []. If it fails to find an item return "Try a different price or size"
<!-- What should the agent do if no listings match? -->

---

### Tool 2: suggest_outfit

**What it does:**
     It provides a description of how well the wardrobe item matches the users self description, user an llm to return an intelligently worded suggestion.
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): the final item chosen in search_listings, eg. {"title": "Faded Band Tee", "price": 22, ...}
- `wardrobe` (dict): the user's current clothing items in get_example_wardrobe()

**What it returns:**
Returns string such as, eg. "Pair this band tee with your wide-leg jeans and chunky sneakers for a 90s grunge look."
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
If wardrobe is empty or nothing can be suggested return general styling advice instead.
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

---

### Tool 3: create_fit_card

**What it does:**
Takes the outfit suggestion, uses some item information from the wardrobe, to post a personalized, short message, similar to what people post on instagram.
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): the suggestion from suggest_outfit, eg. "Pair with wide leg jeans and platform Docs" 
- 'new_item' (dict) — same item dict from search_listings

**What it returns:**
A short and sweet, instagram styled caption like "thrifted this faded band tee for $22 and it was made for my wide-legs 🖤"
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
if outfit is empty return "Could not generate fit card" no outfit suggestion provided"
If outfit data is incomplete then increase LLM temperature. 
<!-- What should the agent do if the outfit data is incomplete? -->

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:


User query
    │
    ▼
Planning Loop ───────────────────────────────────────────┐
    │                                                    │
    ├─► search_listings(description, size, max_price)    │
    │       │ results=[]                                 │
    │       ├──► [ERROR] "Try a different price          │
    │       │             or size" → return              │
    │       │                                            │
    │       │ results=[item, ...]                        │
    │       ▼                                            │
    │   Session: selected_item = results[0]              │
    │       │                                            │
    ├─► suggest_outfit(selected_item, wardrobe)          │
    │       │ wardrobe=[]                                │
    │       ├──► [FALLBACK] general styling              │
    │       │              advice → continue             │
    │       │                                            │
    │   Session: outfit_suggestion = "Pair this band     │
    │            tee with your wide-leg jeans..."        │
    │       │                                            │
    └─► create_fit_card(outfit_suggestion, selected_item)│
            │ outfit=""                                  │
            ├──► [ERROR] "Could not generate fit card:   │
            │    no outfit suggestion provided" → return │
            │                                            │
        Session: fit_card = "thrifted this faded band    │
                 tee for $22 and it was made for         │
                 my wide-legs 🖤"                        │
            │                                            └─ error path returns here
            ▼
        Return session


     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:

**Tool 1 — search_listings:**

     I'll use Claude. I'll paste my Tool 1 spec (description, size, max_price inputs, 
     returns [] on no match, error message "Try a different price or size") and say: 
     "Implement search_listings() using load_listings() from data_loader.py. Filter by 
     all 3 parameters. Return [] if nothing matches — no exceptions."
     I'll verify by running it with 3 queries: one that should find results, one with 
     an impossible price, one with a size that doesn't exist.

**Tool 2 — suggest_outfit:**

     I'll use Claude. I'll paste my Tool 2 spec (new_item dict, wardrobe dict inputs, 
     returns outfit string) and say: "Implement suggest_outfit() using Groq 
     llama-3.3-70b-versatile. If wardrobe is empty, return general styling advice 
     instead of crashing."
     I'll verify by testing with both get_example_wardrobe() and get_empty_wardrobe() 
     and confirming both return a string, never an exception.

**Tool 3 — create_fit_card:**

     I'll use Claude. I'll paste my Tool 3 spec (outfit str, new_item dict inputs, 
     returns Instagram-style caption) and say: "Implement create_fit_card() using Groq 
     llama-3.3-70b-versatile. If outfit is an empty string, return 'Could not generate 
     fit card: no outfit suggestion provided' — no exceptions."
     I'll verify by running it 3 times on the same input to confirm outputs vary, and 
     once with an empty outfit string to confirm it returns the error message.

**Planning Loop:**

     I'll use Claude. I'll paste my Architecture diagram and Planning Loop section and 
     say: "Implement run_agent() following this exact diagram. Save each result to the 
     session dict. Stop and return early if search_listings returns []."
     I'll verify by checking the code branches on search_listings result before running 
     it, then testing with both a valid query and an impossible query.



     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
FitFindr will first search the listings looking for an item that matches the users self description. The search listings tool is called. With the input of the user.
<!-- What does the agent do first? Which tool is called? With what input? -->

**Step 2:**
The second step the bot will create a suggestion regarding the chosen item in a specified format. The suggestion will include intelligent styling options based on a top choice matching the users self description. From here the fit card is called.
<!-- What happens next? What was returned from step 1? What tool is called now? -->

**Step 3:**
Finally, the bot will create a fit card using the suggestion and item information completing the interaction. This fit card will compile the suggestion and some item information together.
<!-- Continue until the full interaction is complete -->

**Final output to user:**
The user will see a personalized "fit card" with FitFindr's final suggestions with some item information as well.
<!-- What does the user actually see at the end? -->
