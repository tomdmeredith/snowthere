"""Style profiles for content post-processing.

Style profiles control the *reading experience* — pacing, rhythm, personality —
while voice profiles (voice_profiles.py) control *what to say* and *how to sound*.

Two profiles:
- SPIELPLATZ: Bold, playful, confident (default for Snowthere)
- CLEAN: Restrained, minimal personality (for formal/comparison pages)

Each knob is 0.0-1.0. Deterministic knobs set hard limits;
probabilistic knobs guide the LLM style editor.
"""

from dataclasses import dataclass, field


@dataclass
class StyleProfile:
    """Tunable style knobs for content post-processing."""

    name: str
    description: str

    # Pacing (guide sentence-level rhythm)
    sentence_variety: float = 0.7       # 0=uniform, 1=wild variety (long/short/fragment)
    paragraph_hooks: float = 0.6        # 0=none, 1=every paragraph opens with a hook
    fragment_tolerance: float = 0.5     # 0=no fragments, 1=frequent sentence fragments

    # Personality (guide humor/aside injection)
    parenthetical_humor: float = 0.4    # 0=none, 1=frequent parenthetical asides
    deadpan_observations: float = 0.3   # 0=none, 1=frequent dry/deadpan moments
    honest_asides: float = 0.5          # 0=none, 1=frequent honest-tension asides
    unexpected_details: float = 0.4     # 0=generic, 1=surprising specific details

    # Energy
    conversational_energy: float = 0.6  # 0=flat/neutral, 1=high energy
    confidence_level: float = 0.7       # 0=hedging, 1=bold assertions

    # Structure
    callout_frequency: float = 0.3      # 0=none, 1=frequent Pro tips / The move / etc
    question_hooks: float = 0.3         # 0=none, 1=frequent rhetorical questions

    # Deterministic limits (hard caps, not probabilistic)
    exclamation_max_per_section: int = 1
    max_paragraph_sentences: int = 4


# Bold, playful, confident — the Snowthere default
SPIELPLATZ = StyleProfile(
    name="spielplatz",
    description="Bold and playful. Memphis-inspired confidence. Like Morning Brew meets ski magazine.",
    sentence_variety=0.8,
    paragraph_hooks=0.6,
    fragment_tolerance=0.6,
    parenthetical_humor=0.5,
    deadpan_observations=0.4,
    honest_asides=0.6,
    unexpected_details=0.5,
    conversational_energy=0.7,
    confidence_level=0.8,
    callout_frequency=0.3,
    question_hooks=0.3,
    exclamation_max_per_section=1,
    max_paragraph_sentences=4,
)

# Restrained, minimal — for comparison tables, formal content
CLEAN = StyleProfile(
    name="clean",
    description="Restrained and clear. Personality through precision, not flair.",
    sentence_variety=0.4,
    paragraph_hooks=0.3,
    fragment_tolerance=0.2,
    parenthetical_humor=0.1,
    deadpan_observations=0.1,
    honest_asides=0.3,
    unexpected_details=0.2,
    conversational_energy=0.4,
    confidence_level=0.6,
    callout_frequency=0.1,
    question_hooks=0.1,
    exclamation_max_per_section=0,
    max_paragraph_sentences=3,
)

STYLE_PROFILES: dict[str, StyleProfile] = {
    "spielplatz": SPIELPLATZ,
    "clean": CLEAN,
}


def get_style_profile(name: str = "spielplatz") -> StyleProfile:
    """Get a style profile by name."""
    return STYLE_PROFILES.get(name.lower(), SPIELPLATZ)
