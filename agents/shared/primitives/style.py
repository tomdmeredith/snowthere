"""Style editing primitive — 3-layer architecture for content polish.

Layer 1 (Deterministic pre-pass): Free. Formatting fixes, forbidden patterns,
    exclamation capping, em-dash removal for clear errors.

Layer 2 (Haiku contextual): ~$0.002/section. Context-appropriate em-dash
    replacement (4 distinct patterns need different replacements).

Layer 3 (Sonnet style edit): ~$0.05-0.10/section. Full prose rewrite for
    delight, preserving all facts/links/HTML.

Round 24: Created to address em-dash proliferation (23 on Alta, 18 on
Crested Butte) and add a reading-experience layer beyond voice control.
"""

import logging
import re
from typing import Any

import anthropic

from ..config import settings
from ..style_profiles import StyleProfile, get_style_profile
from .system import log_cost

logger = logging.getLogger(__name__)


# =============================================================================
# Layer 1: Deterministic Pre-Pass (free)
# =============================================================================

# Patterns that are always wrong regardless of context
FORMATTING_FIXES: list[tuple[str, str]] = [
    # Double spaces
    (r"  +", " "),
    # Space before punctuation
    (r" ([.,!?;:])", r"\1"),
    # Multiple exclamation/question marks
    (r"!{2,}", "!"),
    (r"\?{2,}", "?"),
]

# Phrases that should never appear
FORBIDDEN_PHRASES: list[tuple[str, str]] = [
    # LLM transition markers
    ("Additionally,", ""),
    ("Furthermore,", ""),
    ("Moreover,", ""),
    ("Subsequently,", ""),
    ("In addition,", ""),
    ("It's worth noting", "Note:"),
    ("It's important to note", "Note:"),
    ("It should be noted", "Note:"),
    ("That being said,", ""),
    ("With that being said,", ""),
    ("Having said that,", ""),
    # Performative openers
    ("I'm not gonna lie", ""),
    ("Confession:", ""),
    ("Truth bomb:", ""),
    ("Hot take:", ""),
    # Corporate filler
    ("At the end of the day,", ""),
    ("When all is said and done,", ""),
    ("For what it's worth,", ""),
]


def apply_deterministic_style(
    content: dict[str, Any],
    profile: StyleProfile | None = None,
) -> dict[str, Any]:
    """Layer 1: Deterministic formatting fixes + exclamation capping.

    Free. Safe to run on every content write.

    Args:
        content: Dict of section_name -> HTML/text content
        profile: Style profile for deterministic limits

    Returns:
        Cleaned content dict
    """
    if profile is None:
        profile = get_style_profile("spielplatz")

    processed = {}

    for key, value in content.items():
        if not isinstance(value, str):
            processed[key] = value
            continue

        text = value

        # Forbidden phrases (case-insensitive)
        for pattern, replacement in FORBIDDEN_PHRASES:
            text = re.sub(re.escape(pattern), replacement, text, flags=re.IGNORECASE)

        # Formatting fixes
        for pattern, replacement in FORMATTING_FIXES:
            text = re.sub(pattern, replacement, text)

        # Em-dash / en-dash deterministic removal (obvious formatting errors only)
        # Replace " — " or " – " at start of lines (bullet-style misuse)
        text = re.sub(r"^\s*[—–]\s+", "- ", text, flags=re.MULTILINE)
        # Replace triple em-dashes (clearly wrong)
        text = re.sub(r"—{2,}", " - ", text)

        # Cap exclamation marks per section
        max_excl = profile.exclamation_max_per_section
        excl_count = text.count("!")
        if excl_count > max_excl:
            # Keep only the first N exclamation marks, replace rest with periods
            parts = text.split("!")
            rebuilt = []
            kept = 0
            for i, part in enumerate(parts):
                if i == len(parts) - 1:
                    rebuilt.append(part)
                elif kept < max_excl:
                    rebuilt.append(part + "!")
                    kept += 1
                else:
                    rebuilt.append(part + ".")
            text = "".join(rebuilt)

        # Clean up artifacts from removals
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+([.,!?])", r"\1", text)
        text = re.sub(r"^\s+", "", text)
        text = re.sub(r"\s+$", "", text)
        text = re.sub(r"^[.,!?]\s*", "", text)

        processed[key] = text.strip()

    return processed


# =============================================================================
# Layer 2: Haiku Contextual Em-Dash Replacement (~$0.002/section)
# =============================================================================


async def replace_em_dashes_contextually(
    text: str,
    section_name: str = "",
) -> str:
    """Layer 2: Use Haiku to replace em-dashes with context-appropriate alternatives.

    4 patterns need different replacements:
    1. Independent clauses → period or semicolon
    2. Parenthetical → commas
    3. Amplifying → colon
    4. Trailing → period

    Args:
        text: Content text with em-dashes
        section_name: For logging context

    Returns:
        Text with em-dashes replaced contextually
    """
    # Count em-dashes first
    em_dash_count = text.count("—") + text.count("\u2014")
    if em_dash_count == 0:
        return text

    if not settings.anthropic_api_key:
        # Fallback: simple replacement
        return text.replace(" — ", " - ").replace("—", " - ")

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        prompt = f"""Replace ALL em-dashes (—) in this text with appropriate alternatives.

Rules:
- Independent clauses separated by em-dash → period or semicolon
- Parenthetical aside set off by em-dashes → commas
- Amplifying/explaining clause → colon
- Trailing thought → period

IMPORTANT: Preserve ALL other content exactly. Only change em-dashes.
Do NOT add or remove any other words, links, HTML tags, or formatting.

Text:
{text}

Return ONLY the corrected text, nothing else."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=len(text) + 200,
            messages=[{"role": "user", "content": prompt}],
        )

        log_cost("anthropic", 0.002, None, {
            "stage": "em_dash_replacement",
            "section": section_name,
            "em_dash_count": em_dash_count,
        })

        result = response.content[0].text.strip()

        # Verify no em-dashes remain (safety check)
        remaining = result.count("—") + result.count("\u2014")
        if remaining > 0:
            logger.warning(f"[style] {remaining} em-dashes remain after Haiku replacement in {section_name}")

        return result

    except Exception as e:
        logger.error(f"[style] Haiku em-dash replacement failed: {e}")
        return text.replace(" — ", " - ").replace("—", " - ")


async def apply_em_dash_fix(content: dict[str, Any]) -> dict[str, Any]:
    """Apply contextual em-dash replacement to all text sections."""
    processed = {}

    for key, value in content.items():
        if isinstance(value, str) and ("—" in value or "\u2014" in value):
            processed[key] = await replace_em_dashes_contextually(value, section_name=key)
        else:
            processed[key] = value

    return processed


# =============================================================================
# Layer 3: Sonnet Style Edit (~$0.05-0.10/section)
# =============================================================================


async def apply_style_edit(
    text: str,
    section_name: str,
    profile: StyleProfile | None = None,
) -> str:
    """Layer 3: Full Sonnet prose rewrite for reading delight.

    Preserves all facts, links, HTML, proper nouns. Only rewrites
    for rhythm, personality, and reading experience.

    Args:
        text: Content text to style-edit
        section_name: Section context for the editor
        profile: Style profile with knobs

    Returns:
        Style-edited text
    """
    if not settings.anthropic_api_key:
        return text

    if profile is None:
        profile = get_style_profile("spielplatz")

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        knob_desc = f"""Style knobs (0.0-1.0 scale):
- Sentence variety: {profile.sentence_variety} (mix long/short/fragment)
- Paragraph hooks: {profile.paragraph_hooks} (strong opening lines)
- Fragment tolerance: {profile.fragment_tolerance} (sentence fragments OK)
- Parenthetical humor: {profile.parenthetical_humor}
- Deadpan observations: {profile.deadpan_observations}
- Honest asides: {profile.honest_asides} (acknowledge real tradeoffs)
- Unexpected details: {profile.unexpected_details} (surprising specifics)
- Conversational energy: {profile.conversational_energy}
- Confidence level: {profile.confidence_level}
- Max {profile.max_paragraph_sentences} sentences per paragraph"""

        prompt = f"""You are a style editor for Snowthere, a family ski trip guide.

Rewrite this {section_name} section for READING DELIGHT while preserving every fact.

{knob_desc}

RULES:
1. PRESERVE all facts, prices, proper nouns, ages, dates, links, and HTML tags EXACTLY
2. PRESERVE the overall structure and information order
3. DO NOT add new facts or remove existing ones
4. DO NOT use em-dashes (—) anywhere
5. DO NOT use exclamation marks (max {profile.exclamation_max_per_section} per section)
6. Vary sentence rhythm: long, short, long long short. Never three long sentences in a row
7. Make paragraphs scannable (max {profile.max_paragraph_sentences} sentences each)

Text to edit:
{text}

Return ONLY the edited text, nothing else."""

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=len(text) + 500,
            messages=[{"role": "user", "content": prompt}],
        )

        log_cost("anthropic", 0.08, None, {
            "stage": "style_edit",
            "section": section_name,
            "profile": profile.name,
        })

        return response.content[0].text.strip()

    except Exception as e:
        logger.error(f"[style] Sonnet style edit failed for {section_name}: {e}")
        return text


async def apply_full_style_edit(
    content: dict[str, Any],
    profile: StyleProfile | None = None,
    sections: list[str] | None = None,
) -> dict[str, Any]:
    """Apply full Sonnet style edit to content sections.

    Args:
        content: Dict of section_name -> text
        profile: Style profile
        sections: Only edit these sections (None = all text sections)

    Returns:
        Style-edited content dict
    """
    processed = {}

    for key, value in content.items():
        if not isinstance(value, str):
            processed[key] = value
            continue

        if sections and key not in sections:
            processed[key] = value
            continue

        # Skip very short sections
        if len(value) < 100:
            processed[key] = value
            continue

        processed[key] = await apply_style_edit(value, key, profile)

    return processed
