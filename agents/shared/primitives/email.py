"""Email primitives for agent-native email operations via Resend.

Agent-native design principles:
- Full parity: Agents can do anything users can (send, track, manage)
- Atomic primitives: Small, composable operations
- Explicit completion signals: Every operation returns success/error/retry

Usage:
    from shared.primitives.email import send_email, add_subscriber

    # Add a subscriber
    result = await add_subscriber("user@example.com", name="Jane", source="lead_magnet")

    # Send an email
    result = await send_email(
        to="user@example.com",
        subject="Welcome to Snowthere!",
        html="<h1>Welcome!</h1><p>Your checklist is attached.</p>",
    )

Requires:
    - RESEND_API_KEY environment variable
    - Database tables from migration 026_email_system.sql
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import httpx

from ..config import settings
from ..supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# Resend API base URL
RESEND_API_URL = "https://api.resend.com"

# Sender configuration
DEFAULT_FROM_EMAIL = "Snowthere <hello@snowthere.com>"
DEFAULT_REPLY_TO = "hello@snowthere.com"


@dataclass
class EmailResult:
    """Result of an email operation."""

    success: bool
    message: str
    resend_id: str | None = None
    error: str | None = None


@dataclass
class SubscriberResult:
    """Result of a subscriber operation."""

    success: bool
    message: str
    subscriber_id: str | None = None
    referral_code: str | None = None
    error: str | None = None


@dataclass
class SequenceStepResult:
    """Result of a sequence step operation."""

    success: bool
    message: str
    emails_sent: int = 0
    errors: list[str] = field(default_factory=list)


async def send_email(
    to: str | list[str],
    subject: str,
    html: str,
    text: str | None = None,
    from_email: str = DEFAULT_FROM_EMAIL,
    reply_to: str = DEFAULT_REPLY_TO,
    tags: list[dict[str, str]] | None = None,
    subscriber_id: str | None = None,
    template_id: str | None = None,
    sequence_id: str | None = None,
    step_number: int | None = None,
) -> EmailResult:
    """
    Send an email via Resend API.

    Args:
        to: Recipient email(s)
        subject: Email subject line
        html: HTML body content
        text: Optional plain text body (auto-generated if not provided)
        from_email: Sender email address
        reply_to: Reply-to address
        tags: Optional Resend tags for tracking
        subscriber_id: Optional subscriber ID for tracking
        template_id: Optional template ID for tracking
        sequence_id: Optional sequence ID for tracking
        step_number: Optional step number for tracking

    Returns:
        EmailResult with success status and Resend message ID
    """
    api_key = settings.resend_api_key
    if not api_key:
        return EmailResult(
            success=False,
            message="Resend API key not configured",
            error="RESEND_API_KEY environment variable not set",
        )

    # Normalize recipients to list
    recipients = [to] if isinstance(to, str) else to

    payload = {
        "from": from_email,
        "to": recipients,
        "subject": subject,
        "html": html,
        "reply_to": reply_to,
    }

    if text:
        payload["text"] = text

    if tags:
        payload["tags"] = tags

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{RESEND_API_URL}/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                resend_id = data.get("id")

                # Log to email_sends table if subscriber context provided
                if subscriber_id:
                    await _log_email_send(
                        subscriber_id=subscriber_id,
                        template_id=template_id,
                        sequence_id=sequence_id,
                        step_number=step_number,
                        resend_id=resend_id,
                        status="sent",
                    )

                return EmailResult(
                    success=True,
                    message=f"Email sent to {len(recipients)} recipient(s)",
                    resend_id=resend_id,
                )
            else:
                error_data = response.json()
                error_msg = error_data.get("message", f"HTTP {response.status_code}")
                logger.error(f"Resend API error: {error_msg}")
                return EmailResult(
                    success=False,
                    message="Failed to send email",
                    error=error_msg,
                )

        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending email: {e}")
            return EmailResult(
                success=False,
                message="HTTP error sending email",
                error=str(e),
            )
        except Exception as e:
            logger.error(f"Unexpected error sending email: {e}")
            return EmailResult(
                success=False,
                message="Unexpected error",
                error=str(e),
            )


async def add_subscriber(
    email: str,
    name: str | None = None,
    source: str = "api",
    source_detail: str | None = None,
    referral_code: str | None = None,
    preferences: dict[str, Any] | None = None,
) -> SubscriberResult:
    """
    Add a new subscriber to the email list.

    Args:
        email: Subscriber email address
        name: Optional subscriber name
        source: Acquisition source (api, website, lead_magnet, referral)
        source_detail: Additional source details
        referral_code: Optional referral code for attribution
        preferences: Optional preferences dict

    Returns:
        SubscriberResult with subscriber ID and referral code
    """
    supabase = get_supabase_client()
    email_normalized = email.lower().strip()

    # Check if already exists
    existing = supabase.table("subscribers").select("id, status, referral_code").eq(
        "email", email_normalized
    ).execute()

    if existing.data:
        subscriber = existing.data[0]

        # Reactivate if unsubscribed
        if subscriber["status"] == "unsubscribed":
            supabase.table("subscribers").update({
                "status": "active",
                "unsubscribed_at": None,
                "updated_at": datetime.now().isoformat(),
            }).eq("id", subscriber["id"]).execute()

            return SubscriberResult(
                success=True,
                message="Subscriber reactivated",
                subscriber_id=subscriber["id"],
                referral_code=subscriber["referral_code"],
            )

        return SubscriberResult(
            success=True,
            message="Subscriber already exists",
            subscriber_id=subscriber["id"],
            referral_code=subscriber["referral_code"],
        )

    # Look up referrer
    referred_by = None
    if referral_code:
        referrer = supabase.table("subscribers").select("id").eq(
            "referral_code", referral_code.lower().strip()
        ).execute()
        if referrer.data:
            referred_by = referrer.data[0]["id"]

    # Insert new subscriber
    insert_data = {
        "email": email_normalized,
        "name": name,
        "source": source,
        "source_detail": source_detail,
        "referred_by": referred_by,
        "preferences": preferences or {},
        "status": "active",
    }

    result = supabase.table("subscribers").insert(insert_data).execute()

    if result.data:
        subscriber = result.data[0]
        return SubscriberResult(
            success=True,
            message="Subscriber added successfully",
            subscriber_id=subscriber["id"],
            referral_code=subscriber["referral_code"],
        )

    return SubscriberResult(
        success=False,
        message="Failed to add subscriber",
        error="Database insert failed",
    )


async def remove_subscriber(email: str) -> SubscriberResult:
    """
    Unsubscribe an email address (soft delete).

    Args:
        email: Email address to unsubscribe

    Returns:
        SubscriberResult with operation status
    """
    supabase = get_supabase_client()
    email_normalized = email.lower().strip()

    result = supabase.table("subscribers").update({
        "status": "unsubscribed",
        "unsubscribed_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }).eq("email", email_normalized).execute()

    if result.data:
        return SubscriberResult(
            success=True,
            message="Subscriber unsubscribed",
            subscriber_id=result.data[0]["id"],
        )

    return SubscriberResult(
        success=False,
        message="Subscriber not found",
        error="Email not in database",
    )


async def trigger_sequence(
    subscriber_id: str,
    sequence_name: str,
) -> SubscriberResult:
    """
    Start a subscriber on an email sequence.

    Args:
        subscriber_id: UUID of the subscriber
        sequence_name: Name of the sequence to start

    Returns:
        SubscriberResult with operation status
    """
    supabase = get_supabase_client()

    # Get sequence
    sequence = supabase.table("email_sequences").select("id").eq(
        "name", sequence_name
    ).eq("status", "active").execute()

    if not sequence.data:
        return SubscriberResult(
            success=False,
            message=f"Sequence '{sequence_name}' not found or inactive",
            error="SEQUENCE_NOT_FOUND",
        )

    sequence_id = sequence.data[0]["id"]

    # Check if already in sequence
    existing = supabase.table("subscriber_sequence_progress").select("id").eq(
        "subscriber_id", subscriber_id
    ).eq("sequence_id", sequence_id).execute()

    if existing.data:
        return SubscriberResult(
            success=True,
            message="Subscriber already in sequence",
            subscriber_id=subscriber_id,
        )

    # Start sequence at step 0 (will advance to step 1 on first run)
    # Set next_send_at to now for immediate processing
    supabase.table("subscriber_sequence_progress").insert({
        "subscriber_id": subscriber_id,
        "sequence_id": sequence_id,
        "current_step": 0,
        "started_at": datetime.now().isoformat(),
        "next_send_at": datetime.now().isoformat(),
        "status": "active",
    }).execute()

    return SubscriberResult(
        success=True,
        message=f"Started subscriber on sequence '{sequence_name}'",
        subscriber_id=subscriber_id,
    )


async def advance_sequences() -> SequenceStepResult:
    """
    Advance all active sequences - called by daily cron.

    Finds subscribers who are due for their next email and sends it.

    Returns:
        SequenceStepResult with count of emails sent
    """
    supabase = get_supabase_client()
    now = datetime.now()
    emails_sent = 0
    errors: list[str] = []

    # Find subscribers due for next email
    due = supabase.table("subscriber_sequence_progress").select(
        "*, subscriber:subscribers(*), sequence:email_sequences(*)"
    ).eq("status", "active").lte("next_send_at", now.isoformat()).execute()

    for progress in due.data or []:
        subscriber = progress["subscriber"]
        sequence = progress["sequence"]

        if not subscriber or subscriber["status"] != "active":
            continue

        if not sequence or sequence["status"] != "active":
            continue

        # Get next step
        next_step_num = progress["current_step"] + 1
        step = supabase.table("email_sequence_steps").select(
            "*, template:email_templates(*)"
        ).eq("sequence_id", sequence["id"]).eq("step_number", next_step_num).execute()

        if not step.data:
            # Sequence complete
            supabase.table("subscriber_sequence_progress").update({
                "status": "completed",
                "completed_at": now.isoformat(),
            }).eq("id", progress["id"]).execute()
            continue

        step_data = step.data[0]
        template = step_data["template"]

        if not template:
            errors.append(f"Missing template for step {next_step_num}")
            continue

        # Send email
        result = await send_email(
            to=subscriber["email"],
            subject=template["subject"],
            html=template["body_html"],
            text=template.get("body_text"),
            subscriber_id=subscriber["id"],
            template_id=template["id"],
            sequence_id=sequence["id"],
            step_number=next_step_num,
        )

        if result.success:
            emails_sent += 1

            # Calculate next send time
            next_delay_days = step_data.get("delay_days", 1)
            next_send = now + timedelta(days=next_delay_days)

            supabase.table("subscriber_sequence_progress").update({
                "current_step": next_step_num,
                "last_sent_at": now.isoformat(),
                "next_send_at": next_send.isoformat(),
            }).eq("id", progress["id"]).execute()
        else:
            errors.append(f"Failed to send to {subscriber['email']}: {result.error}")

    return SequenceStepResult(
        success=len(errors) == 0,
        message=f"Sent {emails_sent} emails" + (f", {len(errors)} errors" if errors else ""),
        emails_sent=emails_sent,
        errors=errors,
    )


async def get_sequence_stats(sequence_name: str) -> dict[str, Any]:
    """
    Get statistics for an email sequence.

    Args:
        sequence_name: Name of the sequence

    Returns:
        Dict with subscriber counts, completion rate, etc.
    """
    supabase = get_supabase_client()

    sequence = supabase.table("email_sequences").select("id").eq(
        "name", sequence_name
    ).execute()

    if not sequence.data:
        return {"error": "Sequence not found"}

    sequence_id = sequence.data[0]["id"]

    # Get progress stats
    progress = supabase.table("subscriber_sequence_progress").select(
        "status"
    ).eq("sequence_id", sequence_id).execute()

    stats = {
        "total": len(progress.data or []),
        "active": 0,
        "completed": 0,
        "paused": 0,
        "cancelled": 0,
    }

    for p in progress.data or []:
        status = p["status"]
        if status in stats:
            stats[status] += 1

    # Calculate completion rate
    if stats["total"] > 0:
        stats["completion_rate"] = round(stats["completed"] / stats["total"] * 100, 1)
    else:
        stats["completion_rate"] = 0

    return stats


async def _log_email_send(
    subscriber_id: str,
    template_id: str | None,
    sequence_id: str | None,
    step_number: int | None,
    resend_id: str | None,
    status: str,
) -> None:
    """Log an email send to the database for tracking."""
    supabase = get_supabase_client()

    supabase.table("email_sends").insert({
        "subscriber_id": subscriber_id,
        "template_id": template_id,
        "sequence_id": sequence_id,
        "step_number": step_number,
        "resend_id": resend_id,
        "status": status,
        "sent_at": datetime.now().isoformat(),
    }).execute()
