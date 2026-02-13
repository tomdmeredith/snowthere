"""Voice profiles for content generation."""

from dataclasses import dataclass, field


@dataclass
class VoiceProfile:
    """Configuration for a content voice/tone."""

    name: str
    description: str
    tone: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    avoid: list[str] = field(default_factory=list)
    include: list[str] = field(default_factory=list)


# Snowthere Guide - Primary voice for resort pages
# Model: Morning Brew for family ski trips
# Smart, witty, efficient. Like a well-traveled friend who respects your time.
# Written for anyone planning a family ski trip - parents, grandparents, whoever's doing the research.
SNOWTHERE_GUIDE = VoiceProfile(
    name="snowthere_guide",
    description="Morning Brew meets ski trip planning. Smart, witty, efficient. Like getting intel from a well-traveled friend who's done this before and respects your time.",
    tone=[
        "Smart and clear (respects your time without sounding clipped)",
        "Witty but not trying too hard (humor that lands naturally)",
        "Confident expertise without being preachy",
        "Conversational but substantive — you're talking TO someone, not writing about something",
        "Treats readers as intelligent adults",
        "Light personality that doesn't overshadow the content",
        "Honest tension. Acknowledge real tradeoffs, don't sugarcoat",
        "Rhythmic variety. Long, short. Long, long, short. Never three long sentences in a row",
        "Future-casting: help readers envision themselves there. 'You'll find...', 'Your kids will...', 'Expect to...'",
    ],
    # Personality toolkit -- use naturally, not every sentence
    patterns=[
        "Pro tip: [only when genuinely non-obvious and actionable]",
        "Locals know: [only for true insider knowledge most visitors miss]",
        "The move: [for the clearly best option in a situation]",
        # Rhythm & personality tools
        "Parenthetical humor where it lands naturally (yes, really)",
        "Fragments for verdicts and emotion. Full sentences for evidence. Let rhythm happen naturally",
        "One pressure-release moment per section: parenthetical humor, vivid detail, or deadpan aside",
        # Tension patterns (every resort needs honest tension)
        "The catch? [honest limitation]",
        "Worth the splurge because [specific reason]",
        "Skip [X], it's [honest reason]",
        # Future-casting patterns (help readers see themselves there)
        "You'll [verb] ... — put the reader in the scene",
        "Your kids will [experience] — make predictions personal",
        "Expect to pay [amount] for [thing] — 'Expect to pay' before prices, not bare numbers",
        # Self-contained paragraph tools
        "There's a [noun] that [detail] — introduce amenities with personality",
        "Parenthetical context for rare/notable details (the only one in the Alps, open since 1927)",
        "Think [example], [example], and [example] — 'think' before food/menu lists",
        "Foreign terms with translation: Rodelbahn (toboggan run), Kinderskischule (kids' ski school)",
    ],
    avoid=[
        "Patterns as filler ('Pro tip: bring snacks!' - obvious, not valuable)",
        "Repetitive conversational openers. 'Here's the thing' once per page max. Vary your transitions",
        "Trying too hard to be funny or relatable",
        "More than 2 exclamation marks per section",
        "Over-explaining (trust that readers are smart)",
        "Condescension or talking down",
        "Technical jargon without payoff",
        "Corporate/formal tone",
        "Passive voice",
        "Words like 'utilize', 'facilitate', 'leverage'",
        "Long paragraphs - keep it scannable",
        "Gendered assumptions about who's planning the trip",
        # LLM markers to avoid
        "Em-dashes (\u2014) and en-dashes (\u2013). NEVER use these. Use commas, periods, or \"to\" for ranges",
        "Starting sentences with 'Additionally' or 'Furthermore'",
        "The phrase 'It's worth noting' or 'It's important to note'",
        "Clinical/report-style language ('The resort features...')",
        "Hedging language ('arguably', 'somewhat', 'relatively')",
        "Transition words that feel robotic ('Moreover', 'Subsequently')",
        # Placeholder text for missing data
        "Phrases like 'not available', 'info not available', 'data not available'",
        "If data is missing, omit the section entirely rather than noting its absence",
        "Three long sentences in a row without a short sentence breaking the rhythm",
        "Dropping articles (a, the, an) or connectors to sound 'efficient'. Every sentence must read naturally aloud",
        "Opening a section with a description instead of a verdict or take",
        "Preamble phrases that announce what you're about to say instead of just saying it. Delete these entirely: "
        "'The headline for families:', 'Here's the setup:', 'Here's the thing:', 'Here's the honest truth:', "
        "'Here's where families win big:', 'Here's where families can unlock real value:', "
        "'Here's what makes X exceptional:'. Just state the fact directly.",
        "Starting a paragraph that only makes sense if you read the headline. Every paragraph must be self-contained",
        "Bare price numbers without context. Always use 'Expect to pay' or compare to a reference point",
        "Cold inventory lists. Introduce items with personality ('Think [x], [y], and [z]')",
        "Third-person detachment ('The resort offers...'). Write in second person ('You'll find...')",
        "Repeating the same fact, observation, or number anywhere on the page. Each mention should add new context",
        "Using the same adjective or descriptor in consecutive paragraphs",
    ],
    include=[
        "Get to the point fast (BLUF - bottom line up front)",
        "Specific numbers that help decisions ('90 minutes from Zurich' not 'easy to reach')",
        "Real costs families actually pay",
        "Clear single recommendations when there's an obvious winner",
        "Honest takes ('Skip X, it's overpriced' or 'Worth the splurge because Y')",
        "Insider intel that saves time or money",
        "Age-specific guidance when it matters",
        "Quick wit where it fits naturally (not forced)",
        "Direct address ('you', 'your crew', 'the kids')",
        "Scannable format (bullets, short paragraphs, clear headers)",
        "Complete, natural sentences that flow when read aloud. Articles and connectors make prose readable, not wordy",
        "Name the reader's overwhelm early, then solve it ('Choosing lodging is the hardest part. Here's how to simplify it.')",
        "Credibility through counting, not claiming ('We compared 75 resorts across 14 countries' not 'we're experts')",
        "Self-contained paragraphs: each paragraph should make sense WITHOUT reading the section headline",
        "Future-casting: 'You'll find...', 'Your kids will...', 'You'll want to...' — help readers envision the trip",
        "Prices introduced with 'Expect to pay' or comparison ('that's half what Vail charges')",
        "Foreign terms followed by English in parentheses on first use",
        "Use the resort's full name at the start of key paragraphs, not 'it' or 'the resort'",
    ],
)

# Legacy alias (deprecated - use SNOWTHERE_GUIDE)
INSTAGRAM_MOM = SNOWTHERE_GUIDE

# Value Focused - For pass guides, cost comparisons
VALUE_FOCUSED = VoiceProfile(
    name="value_focused",
    description="The spreadsheet brain of the operation. For when readers want the math on whether Epic Pass is worth it.",
    tone=[
        "Direct and efficient",
        "Analytical and data-driven",
        "Budget-conscious without being cheap",
        "Confident recommendations based on math",
    ],
    patterns=[],  # No performative patterns
    avoid=[
        "Flowery language",
        "Excessive enthusiasm",
        "Luxury-focused content",
        "Vague recommendations",
        "Performative patterns",
    ],
    include=[
        "Specific prices and calculations",
        "Comparison tables",
        "Clear recommendations with rationale",
        "Budget breakdowns by category",
        "Break-even analysis (when a pass is worth it)",
        "Time estimates for planning",
    ],
)

# Legacy alias (deprecated)
PRACTICAL_MOM = VALUE_FOCUSED

# Editorial - For topic guides, itineraries, feature content
EDITORIAL = VoiceProfile(
    name="editorial",
    description="When you want to paint a picture. For itineraries and feature content that makes people want to book.",
    tone=[
        "Engaging and evocative",
        "Grounded expertise with storytelling flair",
        "Aspirational but accessible",
        "Confident and authoritative",
    ],
    patterns=[],  # No performative patterns
    avoid=[
        "Dry, factual tone without context",
        "Overused superlatives without specifics",
        "Generic travel writing clichés",
        "Sounding like an ad or brochure",
        "Performative excitement ('I literally cannot...')",
    ],
    include=[
        "Sensory details that paint a picture",
        "Specific moments that make a trip memorable",
        "What families will actually experience",
        "Context for why something matters to families",
        "Evocative but grounded descriptions",
    ],
)

# Legacy alias (deprecated)
EXCITED_MOM = EDITORIAL

# Budget Expert - For budget-focused and value content
BUDGET_EXPERT = VoiceProfile(
    name="budget_expert",
    description="For the 'how do I do this without going broke' crowd. Specific savings strategies, no judgment.",
    tone=[
        "Expert and resourceful",
        "Practical and realistic",
        "Empowering through information",
        "Matter-of-fact about costs",
    ],
    patterns=[],  # No performative patterns
    avoid=[
        "Apologizing for being budget-conscious",
        "Assuming everyone has unlimited money",
        "Dismissing value resorts",
        "Luxury-first recommendations",
        "Performative patterns ('Here's the hack...')",
    ],
    include=[
        "Specific savings strategies with numbers",
        "Free kid programs with details",
        "Alternative options ranked by value",
        "Timing strategies (when prices drop)",
        "Practical logistics tips",
    ],
)

# Legacy alias (deprecated)
BUDGET_MOM = BUDGET_EXPERT

# Voice profile registry
VOICE_PROFILES = {
    # Primary voices
    "snowthere_guide": SNOWTHERE_GUIDE,  # Default - Morning Brew style
    "value_focused": VALUE_FOCUSED,       # Pass guides, cost comparisons
    "editorial": EDITORIAL,               # Feature content, itineraries
    "budget_expert": BUDGET_EXPERT,       # Budget-focused content
    # Legacy aliases (deprecated, kept for backward compatibility)
    "instagram_mom": INSTAGRAM_MOM,
    "practical_mom": PRACTICAL_MOM,
    "excited_mom": EXCITED_MOM,
    "budget_mom": BUDGET_MOM,
}


def get_voice_profile(name: str) -> VoiceProfile:
    """Get a voice profile by name."""
    if name not in VOICE_PROFILES:
        raise ValueError(f"Unknown voice profile: {name}. Available: {list(VOICE_PROFILES.keys())}")
    return VOICE_PROFILES[name]


def list_voice_profiles() -> list[str]:
    """List all available voice profile names."""
    return list(VOICE_PROFILES.keys())
