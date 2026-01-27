"""Newsletter primitives for weekly digest generation.

Agent-native design principles:
- Atomic, composable operations
- Each primitive does one thing well
- Claude generates content, database validates structure

Usage:
    from shared.primitives.newsletter import check_newsletter_due, generate_newsletter

    # Check if newsletter should be generated
    if check_newsletter_due():
        result = await generate_newsletter()
        if result.success:
            await send_newsletter(result.issue_id)
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import anthropic

from ..config import settings
from ..supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Newsletter configuration
NEWSLETTER_TIMEZONE = ZoneInfo("America/Los_Angeles")
NEWSLETTER_SEND_DAY = 4  # Thursday (0=Monday, 4=Thursday, 6=Sunday)
NEWSLETTER_SEND_HOUR = 6  # 6 AM PT


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class NewsletterSection:
    """A section of newsletter content."""

    section_type: str
    title: str | None = None
    content_html: str | None = None
    content_data: dict[str, Any] = field(default_factory=dict)
    source_ids: list[str] = field(default_factory=list)


@dataclass
class NewsletterContent:
    """Complete newsletter content with all sections."""

    subject: str
    preview_text: str
    sections: list[NewsletterSection] = field(default_factory=list)
    issue_number: int = 0


@dataclass
class NewsletterGenerationResult:
    """Result of newsletter generation."""

    success: bool
    message: str
    issue_id: str | None = None
    issue_number: int | None = None
    content: NewsletterContent | None = None
    error: str | None = None


@dataclass
class NewsletterSendResult:
    """Result of sending a newsletter."""

    success: bool
    message: str
    recipients_count: int = 0
    emails_sent: int = 0
    errors: list[str] = field(default_factory=list)


# =============================================================================
# SCHEDULE CHECKING
# =============================================================================


def check_newsletter_due(
    day_of_week: int = NEWSLETTER_SEND_DAY,
    hour: int = NEWSLETTER_SEND_HOUR,
) -> bool:
    """
    Check if the newsletter should be generated today.

    Returns True if:
    - Today is the scheduled day (default: Thursday)
    - Current hour is >= scheduled hour (default: 6 AM PT)
    - No newsletter has been sent for this week yet

    Args:
        day_of_week: Day to send (0=Monday, 4=Thursday)
        hour: Hour to send (0-23)

    Returns:
        True if newsletter should be generated
    """
    now = datetime.now(NEWSLETTER_TIMEZONE)

    # Check if today is the right day
    if now.weekday() != day_of_week:
        return False

    # Check if it's time
    if now.hour < hour:
        return False

    # Check if we've already sent this week
    supabase = get_supabase_client()

    # Get the start of this week (Monday)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    # Check for existing newsletter this week
    result = supabase.table("newsletter_issues").select("id").gte(
        "created_at", week_start.isoformat()
    ).in_("status", ["scheduled", "sending", "sent"]).execute()

    if result.data:
        logger.info(f"Newsletter already exists for this week: {result.data[0]['id']}")
        return False

    return True


def get_next_newsletter_send_time() -> datetime:
    """Get the next scheduled newsletter send time."""
    now = datetime.now(NEWSLETTER_TIMEZONE)

    # Find next Thursday
    days_ahead = NEWSLETTER_SEND_DAY - now.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7

    next_send = now + timedelta(days=days_ahead)
    next_send = next_send.replace(
        hour=NEWSLETTER_SEND_HOUR,
        minute=0,
        second=0,
        microsecond=0,
    )

    return next_send


# =============================================================================
# CONTENT QUERIES (Database)
# =============================================================================


def query_new_resorts(days: int = 7) -> list[dict[str, Any]]:
    """
    Query resorts published in the last N days.

    Returns list of resort summaries for the newsletter.
    """
    supabase = get_supabase_client()
    cutoff = datetime.now(NEWSLETTER_TIMEZONE) - timedelta(days=days)

    result = supabase.table("resorts").select(
        "id, name, slug, country, region, tagline"
    ).eq("status", "published").gte(
        "published_at", cutoff.isoformat()
    ).order("published_at", desc=True).limit(5).execute()

    return result.data or []


def query_trending_candidates(limit: int = 5) -> list[dict[str, Any]]:
    """
    Query trending discovery candidates for the "what's coming" section.

    Returns candidates with highest priority scores.
    """
    supabase = get_supabase_client()

    result = supabase.table("discovery_candidates").select(
        "id, name, country, discovery_reason, priority_score"
    ).eq("status", "queued").order(
        "priority_score", desc=True
    ).limit(limit).execute()

    return result.data or []


def query_pass_deals() -> list[dict[str, Any]]:
    """
    Query ski pass information for deals section.

    Returns pass info with any recent updates or deals.
    """
    supabase = get_supabase_client()

    result = supabase.table("ski_passes").select(
        "id, name, pass_type, season_price, child_price"
    ).limit(5).execute()

    return result.data or []


def query_ugc_photo() -> dict[str, Any] | None:
    """
    Query a featured UGC photo for the community section.

    Returns a recent, high-quality UGC photo.
    """
    supabase = get_supabase_client()

    # Get a recent UGC photo that's been attributed
    result = supabase.table("resort_images").select(
        "*, resort:resorts(name, slug, country)"
    ).eq("source_type", "google_places").not_.is_(
        "attribution_html", "null"
    ).order("created_at", desc=True).limit(1).execute()

    if result.data:
        return result.data[0]
    return None


# =============================================================================
# CONTENT GENERATION (Claude)
# =============================================================================


def _get_client() -> anthropic.Anthropic:
    """Get Anthropic client instance."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _call_claude(
    prompt: str,
    system: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 2000,
) -> str:
    """Make a Claude API call and return the text response."""
    client = _get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return response.content[0].text


def _parse_json_response(response: str) -> dict[str, Any]:
    """Parse JSON from Claude response, handling markdown code blocks."""
    text = response.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def generate_cold_open(
    week_number: int,
    current_date: datetime,
    new_resorts: list[dict],
) -> str:
    """
    Generate the newsletter cold open (50 words).

    This is the hook that gets people reading.
    """
    month = current_date.strftime("%B")
    seasonal_context = _get_seasonal_context(current_date)

    prompt = f"""Write a newsletter cold open for Snowthere's weekly family ski digest.

CONTEXT:
- Week {week_number} of the ski season
- Date: {current_date.strftime("%B %d, %Y")}
- Season context: {seasonal_context}
- New resort guides published: {len(new_resorts)}

VOICE: Instagram mom meets ski enthusiast - warm, practical, encouraging

REQUIREMENTS:
- Exactly 40-60 words
- Personal, conversational tone
- Reference something timely (season, weather, upcoming holidays)
- End with a hook to keep reading

EXAMPLES OF GOOD COLD OPENS:
- "Spring break is calling, and I've got your answer to 'where should we ski?' This week, we're exploring Europe's hidden family gems..."
- "Those 5am wakeups for first tracks? Worth it when your 6-year-old yells 'AGAIN!' at the bottom. Here's this week's inspiration..."

Return ONLY the cold open text, no quotes or labels."""

    system = "You are a ski mom writing to other parents. Be warm, relatable, and encouraging."

    try:
        response = _call_claude(prompt, system=system, max_tokens=200)
        return response.strip().strip('"')
    except Exception as e:
        logger.error(f"Cold open generation failed: {e}")
        return f"Another week of family ski adventures! Here's what's new at Snowthere this {month}."


def generate_trending_section(
    candidates: list[dict],
    new_resorts: list[dict],
) -> str:
    """
    Generate the trending/coming soon section (100 words).

    Teases what's coming to build anticipation.
    """
    if not candidates and not new_resorts:
        return "More resort guides are on the way! We're researching the best family destinations worldwide."

    prompt = f"""Write a "What's Coming" section for our ski family newsletter.

UPCOMING RESORTS BEING RESEARCHED:
{json.dumps(candidates[:3], indent=2)}

RECENTLY PUBLISHED:
{json.dumps([r['name'] for r in new_resorts[:3]])}

REQUIREMENTS:
- 80-120 words
- Build anticipation for upcoming content
- Mention 2-3 specific resorts by name
- End with a tease that keeps them subscribed

VOICE: Excited friend sharing insider knowledge

Return ONLY the section text."""

    try:
        response = _call_claude(prompt, max_tokens=300)
        return response.strip()
    except Exception as e:
        logger.error(f"Trending section generation failed: {e}")
        return "We're researching new family-friendly resorts every week. Stay tuned!"


def generate_parent_hack(recent_guides: list[dict]) -> str:
    """
    Generate the parent hack of the week (75 words).

    Extracts a useful tip from recent content.
    """
    prompt = f"""Extract a "Parent Hack of the Week" from these resort guides.

RECENT RESORT GUIDES:
{json.dumps(recent_guides[:3], indent=2, default=str)}

REQUIREMENTS:
- Single actionable tip families can use
- 60-80 words
- Specific (not generic advice)
- Format: Start with the hack, then explain why it works

GOOD EXAMPLES:
- "Book lessons for 10am, not 9am. Early morning ski schools are packed with fresh-off-the-plane families. The 10am slot gets smaller groups and more rested instructors."
- "Always pack an extra pair of kids' mittens. Wet mittens = cold kids = crying kids = end of ski day."

Return ONLY the hack text."""

    try:
        response = _call_claude(prompt, max_tokens=200)
        return response.strip()
    except Exception as e:
        logger.error(f"Parent hack generation failed: {e}")
        return "Pro tip: Pack hand warmers in your kids' pockets - they're a game changer for cold days on the mountain."


def _get_seasonal_context(date: datetime) -> str:
    """Get seasonal context for content generation."""
    month = date.month

    if month in [11, 12]:
        return "Early season - holiday planning, deals, new pass benefits"
    elif month in [1, 2]:
        return "Peak season - best conditions, school breaks, crowded periods"
    elif month in [3, 4]:
        return "Spring skiing - deals, warmer weather, end of season"
    elif month in [5, 6, 7, 8]:
        return "Off-season - summer activities, early bird pass sales"
    else:  # 9, 10
        return "Pre-season - planning, pass decisions, gear prep"


# =============================================================================
# NEWSLETTER GENERATION ORCHESTRATION
# =============================================================================


async def generate_newsletter() -> NewsletterGenerationResult:
    """
    Generate a complete newsletter issue.

    Orchestrates all content queries and generation, creates the
    newsletter_issues record, and returns the complete content.

    Returns:
        NewsletterGenerationResult with issue_id and content
    """
    supabase = get_supabase_client()
    now = datetime.now(NEWSLETTER_TIMEZONE)

    logger.info("Starting newsletter generation...")

    try:
        # Get sequence ID for weekly newsletter
        sequence = supabase.table("email_sequences").select("id").eq(
            "name", "weekly_newsletter"
        ).single().execute()

        if not sequence.data:
            return NewsletterGenerationResult(
                success=False,
                message="Weekly newsletter sequence not found",
                error="SEQUENCE_NOT_FOUND",
            )

        sequence_id = sequence.data["id"]

        # Get next issue number
        issue_num_result = supabase.rpc(
            "get_next_issue_number",
            {"p_sequence_id": sequence_id}
        ).execute()
        issue_number = issue_num_result.data or 1

        # Create draft issue record
        issue_data = {
            "sequence_id": sequence_id,
            "issue_number": issue_number,
            "subject": f"Snowthere Weekly #{issue_number}",
            "status": "generating",
            "generation_started_at": now.isoformat(),
        }

        issue_result = supabase.table("newsletter_issues").insert(issue_data).execute()
        if not issue_result.data:
            return NewsletterGenerationResult(
                success=False,
                message="Failed to create newsletter issue",
                error="DATABASE_INSERT_FAILED",
            )

        issue_id = issue_result.data[0]["id"]
        logger.info(f"Created newsletter issue {issue_number} (ID: {issue_id})")

        # Query content sources
        new_resorts = query_new_resorts(days=7)
        trending = query_trending_candidates(limit=5)
        pass_info = query_pass_deals()
        ugc_photo = query_ugc_photo()

        # Generate sections
        sections = []

        # 1. Cold Open
        cold_open = generate_cold_open(issue_number, now, new_resorts)
        sections.append(NewsletterSection(
            section_type="cold_open",
            content_html=f"<p>{cold_open}</p>",
            content_data={"week_number": issue_number},
        ))

        # 2. New Resorts
        if new_resorts:
            resorts_html = _format_resorts_section(new_resorts)
            sections.append(NewsletterSection(
                section_type="new_resorts",
                title="Fresh Off the Slopes",
                content_html=resorts_html,
                source_ids=[r["id"] for r in new_resorts],
            ))

        # 3. Trending / Coming Soon
        trending_content = generate_trending_section(trending, new_resorts)
        sections.append(NewsletterSection(
            section_type="trending",
            title="Coming Soon",
            content_html=f"<p>{trending_content}</p>",
        ))

        # 4. Parent Hack
        parent_hack = generate_parent_hack(new_resorts)
        sections.append(NewsletterSection(
            section_type="parent_hack",
            title="Parent Hack of the Week",
            content_html=f"<p>{parent_hack}</p>",
        ))

        # 5. Pass Intel (if we have pass data)
        if pass_info:
            pass_html = _format_pass_section(pass_info)
            sections.append(NewsletterSection(
                section_type="pass_intel",
                title="Pass Intelligence",
                content_html=pass_html,
            ))

        # 6. Community Photo
        if ugc_photo:
            photo_html = _format_ugc_section(ugc_photo)
            sections.append(NewsletterSection(
                section_type="community_photo",
                title="From the Slopes",
                content_html=photo_html,
                source_ids=[ugc_photo["id"]],
            ))

        # 7. Referral CTA (static)
        sections.append(NewsletterSection(
            section_type="referral_cta",
            content_html=_get_referral_cta_html(),
        ))

        # Generate subject and preview
        subject = _generate_subject(issue_number, new_resorts, now)
        preview_text = cold_open[:150] + "..." if len(cold_open) > 150 else cold_open

        # Compile content
        content = NewsletterContent(
            subject=subject,
            preview_text=preview_text,
            sections=sections,
            issue_number=issue_number,
        )

        # Save sections to database
        for section in sections:
            section_data = {
                "issue_id": issue_id,
                "section_type": section.section_type,
                "title": section.title,
                "content_html": section.content_html,
                "content_data": section.content_data,
                "source_type": "ai_generated",
                "source_ids": section.source_ids,
            }
            supabase.table("newsletter_sections").insert(section_data).execute()

        # Update issue with full content
        full_html = _render_newsletter_html(content)
        content_json = {
            "subject": subject,
            "preview_text": preview_text,
            "sections": [
                {
                    "type": s.section_type,
                    "title": s.title,
                    "html": s.content_html,
                }
                for s in sections
            ],
        }

        supabase.table("newsletter_issues").update({
            "subject": subject,
            "preview_text": preview_text,
            "content_html": full_html,
            "content_json": content_json,
            "status": "draft",
            "generation_completed_at": datetime.now(NEWSLETTER_TIMEZONE).isoformat(),
        }).eq("id", issue_id).execute()

        logger.info(f"Newsletter #{issue_number} generated successfully")

        return NewsletterGenerationResult(
            success=True,
            message=f"Newsletter #{issue_number} generated with {len(sections)} sections",
            issue_id=issue_id,
            issue_number=issue_number,
            content=content,
        )

    except Exception as e:
        logger.error(f"Newsletter generation failed: {e}")
        return NewsletterGenerationResult(
            success=False,
            message=f"Newsletter generation failed: {e}",
            error=str(e),
        )


# =============================================================================
# NEWSLETTER SENDING
# =============================================================================


async def send_newsletter(issue_id: str) -> NewsletterSendResult:
    """
    Send a newsletter to all active subscribers.

    Args:
        issue_id: UUID of the newsletter issue to send

    Returns:
        NewsletterSendResult with send statistics
    """
    from .email import send_email, substitute_template_variables

    supabase = get_supabase_client()
    errors = []
    emails_sent = 0

    try:
        # Get the newsletter issue
        issue = supabase.table("newsletter_issues").select("*").eq(
            "id", issue_id
        ).single().execute()

        if not issue.data:
            return NewsletterSendResult(
                success=False,
                message="Newsletter issue not found",
                errors=["ISSUE_NOT_FOUND"],
            )

        issue_data = issue.data

        if issue_data["status"] not in ("draft", "scheduled"):
            return NewsletterSendResult(
                success=False,
                message=f"Newsletter already {issue_data['status']}",
                errors=["INVALID_STATUS"],
            )

        # Update status to sending
        supabase.table("newsletter_issues").update({
            "status": "sending",
        }).eq("id", issue_id).execute()

        # Get all active subscribers
        subscribers = supabase.table("subscribers").select(
            "id, email, name, referral_code"
        ).eq("status", "active").execute()

        if not subscribers.data:
            return NewsletterSendResult(
                success=True,
                message="No active subscribers",
                recipients_count=0,
            )

        recipients = subscribers.data
        logger.info(f"Sending newsletter to {len(recipients)} subscribers")

        # Send to each subscriber
        for subscriber in recipients:
            try:
                # Personalize content
                variables = {
                    "name": subscriber.get("name") or "there",
                    "email": subscriber["email"],
                    "referral_code": subscriber.get("referral_code", ""),
                }

                html = substitute_template_variables(
                    issue_data["content_html"],
                    variables,
                )
                subject = substitute_template_variables(
                    issue_data["subject"],
                    variables,
                )

                # Send email
                result = await send_email(
                    to=subscriber["email"],
                    subject=subject,
                    html=html,
                    subscriber_id=subscriber["id"],
                )

                if result.success:
                    emails_sent += 1

                    # Log the send
                    supabase.table("newsletter_sends").insert({
                        "issue_id": issue_id,
                        "subscriber_id": subscriber["id"],
                        "resend_id": result.resend_id,
                        "status": "sent",
                        "sent_at": datetime.now(NEWSLETTER_TIMEZONE).isoformat(),
                    }).execute()
                else:
                    errors.append(f"{subscriber['email']}: {result.error}")

            except Exception as e:
                errors.append(f"{subscriber['email']}: {str(e)}")

        # Update issue status
        final_status = "sent" if emails_sent > 0 else "failed"
        supabase.table("newsletter_issues").update({
            "status": final_status,
            "sent_at": datetime.now(NEWSLETTER_TIMEZONE).isoformat(),
            "stats": {
                "recipients": len(recipients),
                "sent": emails_sent,
                "errors": len(errors),
            },
        }).eq("id", issue_id).execute()

        return NewsletterSendResult(
            success=emails_sent > 0,
            message=f"Sent {emails_sent}/{len(recipients)} emails",
            recipients_count=len(recipients),
            emails_sent=emails_sent,
            errors=errors[:10],  # Limit error list
        )

    except Exception as e:
        logger.error(f"Newsletter send failed: {e}")
        return NewsletterSendResult(
            success=False,
            message=f"Send failed: {e}",
            errors=[str(e)],
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _format_resorts_section(resorts: list[dict]) -> str:
    """Format new resorts as HTML for newsletter."""
    if not resorts:
        return "<p>No new resorts this week - but we're working on it!</p>"

    html = "<ul style='padding-left: 20px;'>"
    for resort in resorts:
        name = resort.get("name", "Unknown")
        country = resort.get("country", "")
        slug = resort.get("slug", "")
        tagline = resort.get("tagline", "")

        url = f"https://snowthere.com/resorts/{country.lower().replace(' ', '-')}/{slug}"

        html += f"""<li style='margin-bottom: 12px;'>
            <a href="{url}" style='color: #ff6f61; font-weight: 600; text-decoration: none;'>{name}</a>
            <span style='color: #666;'> - {country}</span>
            {f"<br><span style='font-size: 14px; color: #888;'>{tagline}</span>" if tagline else ""}
        </li>"""

    html += "</ul>"
    return html


def _format_pass_section(passes: list[dict]) -> str:
    """Format ski pass info as HTML."""
    html = "<p>Quick pass overview for family planning:</p><ul style='padding-left: 20px;'>"
    for pass_info in passes[:3]:
        name = pass_info.get("name", "")
        price = pass_info.get("season_price", "")
        child = pass_info.get("child_price", "")

        if price:
            html += f"<li><strong>{name}</strong>: ${price} adult"
            if child:
                html += f", ${child} child"
            html += "</li>"

    html += "</ul>"
    return html


def _format_ugc_section(photo: dict) -> str:
    """Format UGC photo as HTML."""
    resort = photo.get("resort", {})
    resort_name = resort.get("name", "")
    url = photo.get("url", "")
    attribution = photo.get("attribution_html", "")

    html = f"""<div style='text-align: center;'>
        <img src="{url}" alt="{resort_name}" style='max-width: 100%; border-radius: 8px;'>
        <p style='font-size: 12px; color: #888; margin-top: 8px;'>
            {resort_name} {f'| {attribution}' if attribution else ''}
        </p>
    </div>"""
    return html


def _get_referral_cta_html() -> str:
    """Get the referral CTA HTML."""
    return """<div style='background: linear-gradient(135deg, #ff6f61, #ff9a8b); padding: 24px; border-radius: 12px; text-align: center; color: white;'>
        <h3 style='margin: 0 0 12px 0;'>Know a Ski Family?</h3>
        <p style='margin: 0 0 16px 0;'>Share Snowthere with friends and earn rewards!</p>
        <a href="https://snowthere.com?ref={{referral_code}}" style='display: inline-block; background: white; color: #ff6f61; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;'>Share Your Link</a>
    </div>"""


def _generate_subject(
    issue_number: int,
    new_resorts: list[dict],
    date: datetime,
) -> str:
    """Generate email subject line."""
    if new_resorts:
        first_resort = new_resorts[0].get("name", "")
        if len(new_resorts) > 1:
            return f"New: {first_resort} + {len(new_resorts)-1} more family ski guides"
        return f"New family ski guide: {first_resort}"

    month = date.strftime("%B")
    return f"Snowthere Weekly #{issue_number} - Your {month} ski update"


def _render_newsletter_html(content: NewsletterContent) -> str:
    """Render full newsletter HTML from content object."""
    sections_html = ""

    for section in content.sections:
        if section.title:
            sections_html += f"""<tr>
                <td style='padding: 24px 32px 8px 32px;'>
                    <h2 style='margin: 0; color: #1a2f4f; font-size: 20px;'>{section.title}</h2>
                </td>
            </tr>"""

        if section.content_html:
            sections_html += f"""<tr>
                <td style='padding: 8px 32px 24px 32px; color: #333; font-size: 16px; line-height: 1.6;'>
                    {section.content_html}
                </td>
            </tr>"""

    # Full HTML template
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content.subject}</title>
</head>
<body style='margin: 0; padding: 0; background-color: #f5f5f5; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style='background-color: #f5f5f5;'>
        <tr>
            <td align="center" style='padding: 40px 20px;'>
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" style='background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                    <!-- Header -->
                    <tr>
                        <td style='background: linear-gradient(135deg, #ff6f61, #ff9a8b); padding: 32px; text-align: center;'>
                            <h1 style='margin: 0; color: white; font-size: 28px;'>Snowthere Weekly</h1>
                            <p style='margin: 8px 0 0 0; color: rgba(255,255,255,0.9); font-size: 14px;'>Your family ski trip insider</p>
                        </td>
                    </tr>

                    <!-- Content Sections -->
                    {sections_html}

                    <!-- Footer -->
                    <tr>
                        <td style='background-color: #1a2f4f; padding: 24px 32px; text-align: center;'>
                            <p style='margin: 0 0 8px 0; color: rgba(255,255,255,0.8); font-size: 14px;'>
                                <a href="https://snowthere.com" style='color: #ff9a8b; text-decoration: none;'>snowthere.com</a>
                            </p>
                            <p style='margin: 0; color: rgba(255,255,255,0.6); font-size: 12px;'>
                                <a href="https://snowthere.com/unsubscribe?email={{{{email}}}}" style='color: rgba(255,255,255,0.6);'>Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return html
