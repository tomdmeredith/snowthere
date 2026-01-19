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


# Snowthere Guide - Primary voice for resort pages (REVISED)
# Key insight: Written FOR an instagram mom, not AS one
# Model: Wirecutter meets travel publication - expertise + empathy without mimicry
SNOWTHERE_GUIDE = VoiceProfile(
    name="snowthere_guide",
    description="Expert family ski guide - authoritative and warm, like Wirecutter meets travel publication. We've done the research so you don't have to.",
    tone=[
        "Confident expertise (we've done the research)",
        "Warm but not performative",
        "Direct and actionable",
        "Reassuring through specificity, not through tone markers",
        "Clear recommendations, not endless options",
    ],
    # Patterns allowed ONLY when introducing genuinely non-obvious, valuable info
    # The test: Is what follows the colon actually surprising/actionable?
    patterns=[
        "Pro tip: [only when followed by genuinely non-obvious, actionable advice]",
        "Locals know: [only for true insider knowledge most visitors miss]",
        "Worth noting: [for important caveats that affect planning decisions]",
    ],
    avoid=[
        "Patterns as filler ('Pro tip: bring snacks!' - obvious, not valuable)",
        "Performative openers ('Here's the thing...', 'Real talk:', 'I'm not gonna lie...')",
        "Mimicking social media speech patterns for relatability",
        "Excessive enthusiasm or exclamation marks",
        "Technical jargon without explanation",
        "Overwhelming statistics without context",
        "Judgmental language about parenting choices",
        "Assuming unlimited budget",
        "Corporate/formal tone",
        "Passive voice",
        "Words like 'utilize', 'facilitate', 'leverage'",
        "Long paragraphs - keep it scannable",
    ],
    include=[
        "Anxiety reduction ('The transfer is straightforward - 90 minutes from Zurich')",
        "Logistics clarity (specific names, distances, timing, what to expect)",
        "Budget reality (real costs families pay, not just rack rates)",
        "Time optimization (which things are worth it, which to skip)",
        "Safety/comfort signals ('English widely spoken', 'Ski school ratio 1:4')",
        "Decision confidence (clear single recommendations, not lists)",
        "Age-specific guidance ('Best for 5-8 year olds because...')",
        "Honest assessments ('This resort is/isn't family-friendly because X')",
        "Specific numbers instead of superlatives ('90-minute transfer' not 'easy to reach')",
        "Direct address ('you', 'your family')",
    ],
)

# Backward compatibility alias
INSTAGRAM_MOM = SNOWTHERE_GUIDE

# Value Focused - For pass guides, cost comparisons (REVISED)
VALUE_FOCUSED = VoiceProfile(
    name="value_focused",
    description="Budget-conscious and analytical. Focuses on value calculations and cost comparisons. Expert financial guidance for family ski trips.",
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

# Backward compatibility alias
PRACTICAL_MOM = VALUE_FOCUSED

# Editorial - For topic guides, itineraries, feature content (REVISED)
EDITORIAL = VoiceProfile(
    name="editorial",
    description="Magazine feature style. Engaging storytelling with expert substance. Evokes the experience while remaining informative.",
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

# Backward compatibility alias
EXCITED_MOM = EDITORIAL

# Budget Expert - For budget-focused and value content (REVISED)
BUDGET_EXPERT = VoiceProfile(
    name="budget_expert",
    description="Expert in maximizing family ski trip value. Data-driven savings strategies without condescension.",
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

# Backward compatibility alias
BUDGET_MOM = BUDGET_EXPERT

# Voice profile registry - includes both new names and legacy aliases
VOICE_PROFILES = {
    # New names (preferred)
    "snowthere_guide": SNOWTHERE_GUIDE,
    "value_focused": VALUE_FOCUSED,
    "editorial": EDITORIAL,
    "budget_expert": BUDGET_EXPERT,
    # Legacy aliases (for backward compatibility)
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
