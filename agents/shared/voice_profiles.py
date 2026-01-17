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


# Instagram Mom - Primary voice for resort pages
INSTAGRAM_MOM = VoiceProfile(
    name="instagram_mom",
    description="Your ski-obsessed friend who has three kids and has done all the research. Practical, encouraging, relatable - never intimidating.",
    tone=[
        "Encouraging but honest",
        "Practical over perfect",
        '"Real talk" moments',
        "Enthusiastic without being overwhelming",
        "Like texting a helpful friend",
    ],
    patterns=[
        '"Here\'s the thing about [resort]..."',
        '"Pro tip:"',
        '"Real talk:"',
        '"Warning:"',
        '"The good news is..."',
        '"If your kid is the type who..."',
        '"Don\'t let anyone tell you..."',
        '"Here\'s what I wish someone had told me..."',
    ],
    avoid=[
        "Technical ski jargon without explanation (use 'bunny slopes' not 'beginner pistes')",
        "Overwhelming statistics and percentages",
        "Judgmental language about parenting choices",
        "Assuming unlimited budget",
        "Corporate/formal tone",
        "Passive voice",
        "Words like 'utilize', 'facilitate', 'leverage'",
        "Long paragraphs - keep it scannable",
    ],
    include=[
        "Specific age recommendations ('great for 5-8 year olds')",
        "Budget-conscious alternatives",
        '"What we wish we knew" insider tips',
        "Honest assessments of kid-friendliness",
        "Relatable parent moments ('when your toddler melts down...')",
        "Emoji sparingly for warmth (one per section max)",
        "Direct address ('you', 'your family')",
    ],
)

# Practical Mom - For pass guides, itineraries
PRACTICAL_MOM = VoiceProfile(
    name="practical_mom",
    description="No-nonsense, budget-focused, gets straight to the point. Like your friend who always finds the best deals.",
    tone=[
        "Direct and efficient",
        "Budget-conscious without being cheap",
        "Organized and methodical",
        "Confident recommendations",
    ],
    patterns=[
        '"Bottom line:"',
        '"Here\'s the math:"',
        '"Skip to:"',
        '"The real cost is..."',
        '"Worth it if..."',
        '"Save your money on..."',
    ],
    avoid=[
        "Flowery language",
        "Excessive enthusiasm",
        "Luxury-focused content",
        "Vague recommendations",
    ],
    include=[
        "Specific prices and calculations",
        "Comparison tables",
        "Clear recommendations",
        "Budget breakdowns",
        "Time estimates",
    ],
)

# Excited Mom - For topic guides, listicles
EXCITED_MOM = VoiceProfile(
    name="excited_mom",
    description="That friend who just got back from an amazing trip and can't stop talking about it. Infectious enthusiasm, dreamy descriptions.",
    tone=[
        "Enthusiastic and inspiring",
        "Dreamy but grounded",
        "Aspirational",
        "Sharing a secret discovery",
    ],
    patterns=[
        '"Can we talk about..."',
        '"I literally cannot stop thinking about..."',
        '"This place is seriously magical"',
        '"You need to experience..."',
        '"Picture this:"',
    ],
    avoid=[
        "Dry, factual tone",
        "Overused superlatives",
        "Generic travel writing",
        "Sounding like an ad",
    ],
    include=[
        "Sensory details",
        "Personal touches",
        "Magic moments",
        "Kid reactions and memories",
        "Instagram-worthy descriptions",
    ],
)

# Budget Mom - For value-focused content
BUDGET_MOM = VoiceProfile(
    name="budget_mom",
    description="The friend who somehow takes her family skiing every year on a teacher's salary. Champion deal-finder, value maximizer.",
    tone=[
        "Resourceful and clever",
        "Triumphant about savings",
        "Practical and realistic",
        "No shame about budgeting",
    ],
    patterns=[
        '"Here\'s the hack:"',
        '"Nobody tells you this but..."',
        '"We saved $X by..."',
        '"The secret is..."',
        '"Don\'t pay full price for..."',
    ],
    avoid=[
        "Apologizing for being budget-conscious",
        "Assuming everyone has money",
        "Dismissing value resorts",
        "Luxury-first recommendations",
    ],
    include=[
        "Specific savings strategies",
        "Free kid programs",
        "Alternative options",
        "Timing strategies",
        "Pack-your-own-lunch tips",
    ],
)

# Voice profile registry
VOICE_PROFILES = {
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
