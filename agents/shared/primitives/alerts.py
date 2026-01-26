"""Alerting primitives for pipeline notifications."""

import json
import logging
from datetime import datetime
from typing import Any

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)


def send_slack_alert(
    title: str,
    message: str,
    severity: str = "info",
    metadata: dict[str, Any] | None = None,
) -> bool:
    """
    Send an alert to Slack via incoming webhook.

    Args:
        title: Alert title/headline
        message: Alert message body
        severity: One of 'info', 'warning', 'error', 'success'
        metadata: Additional context to include

    Returns:
        True if sent successfully, False otherwise
    """
    settings = get_settings()
    webhook_url = settings.slack_webhook_url

    # Graceful fallback: log to stdout if no webhook configured
    if not webhook_url:
        log_level = {
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "success": logging.INFO,
        }.get(severity, logging.INFO)

        logger.log(log_level, f"[ALERT] {title}: {message}")
        if metadata:
            logger.log(log_level, f"[ALERT METADATA] {json.dumps(metadata, indent=2)}")
        return False

    # Build Slack message with Block Kit
    emoji = {
        "info": ":information_source:",
        "warning": ":warning:",
        "error": ":rotating_light:",
        "success": ":white_check_mark:",
    }.get(severity, ":speech_balloon:")

    color = {
        "info": "#3498db",
        "warning": "#f39c12",
        "error": "#e74c3c",
        "success": "#27ae60",
    }.get(severity, "#95a5a6")

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} {title}", "emoji": True},
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": message},
        },
    ]

    # Add metadata fields if provided
    if metadata:
        fields = []
        for key, value in metadata.items():
            fields.append({"type": "mrkdwn", "text": f"*{key}:*\n{value}"})
            if len(fields) >= 10:  # Slack limit
                break

        if fields:
            blocks.append({"type": "section", "fields": fields})

    # Add timestamp footer
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Snowthere Pipeline • {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                }
            ],
        }
    )

    payload = {
        "attachments": [{"color": color, "blocks": blocks}],
    }

    try:
        response = httpx.post(
            webhook_url,
            json=payload,
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info(f"Slack alert sent: {title}")
        return True
    except httpx.HTTPError as e:
        logger.error(f"Failed to send Slack alert: {e}")
        return False


def alert_pipeline_error(
    error_type: str,
    error_message: str,
    resort_name: str | None = None,
    task_id: str | None = None,
) -> bool:
    """
    Send an alert for a pipeline error.

    Convenience wrapper for common error alerts.
    """
    metadata = {}
    if resort_name:
        metadata["Resort"] = resort_name
    if task_id:
        metadata["Task ID"] = task_id

    return send_slack_alert(
        title=f"Pipeline Error: {error_type}",
        message=error_message,
        severity="error",
        metadata=metadata or None,
    )


def alert_budget_warning(
    current_spend: float,
    daily_limit: float,
    threshold_pct: float = 0.75,
) -> bool:
    """
    Send an alert when budget usage exceeds threshold.

    Args:
        current_spend: Current daily spend in dollars
        daily_limit: Daily budget limit in dollars
        threshold_pct: Percentage threshold to trigger alert (default 75%)

    Returns:
        True if alert was sent, False if below threshold or failed
    """
    if daily_limit <= 0:
        return False

    pct_used = current_spend / daily_limit
    if pct_used < threshold_pct:
        return False

    remaining = daily_limit - current_spend
    severity = "error" if pct_used >= 0.95 else "warning"

    return send_slack_alert(
        title=f"Budget Alert: {pct_used:.0%} Used",
        message=(
            f"*Daily budget usage is high*\n"
            f"• Spent: ${current_spend:.2f}\n"
            f"• Limit: ${daily_limit:.2f}\n"
            f"• Remaining: ${remaining:.2f}"
        ),
        severity=severity,
        metadata={"percentage_used": f"{pct_used:.1%}", "remaining": f"${remaining:.2f}"},
    )


def alert_startup_failure(errors: list[str]) -> bool:
    """
    Send an alert when pipeline startup validation fails.

    Args:
        errors: List of validation error messages

    Returns:
        True if sent successfully, False otherwise
    """
    return send_slack_alert(
        title="Pipeline Startup Failed",
        message=(
            f"*Environment validation failed*\n"
            f"The daily pipeline could not start due to configuration issues:\n"
            + "\n".join(f"• {e}" for e in errors)
        ),
        severity="error",
        metadata={"error_count": str(len(errors))},
    )


def alert_pipeline_summary(
    total_processed: int,
    successful: int,
    failed: int,
    resorts: list[str] | None = None,
) -> bool:
    """
    Send a daily pipeline summary alert.

    Args:
        total_processed: Number of resorts attempted
        successful: Number of successful completions
        failed: Number of failures
        resorts: List of resort names processed
    """
    if failed > 0:
        severity = "warning" if successful > 0 else "error"
        title = f"Pipeline Complete: {failed} failures"
    else:
        severity = "success"
        title = f"Pipeline Complete: {successful} resorts"

    message = (
        f"*Daily pipeline run complete*\n"
        f"• Processed: {total_processed}\n"
        f"• Successful: {successful}\n"
        f"• Failed: {failed}"
    )

    metadata = {}
    if resorts:
        metadata["Resorts"] = ", ".join(resorts[:5])
        if len(resorts) > 5:
            metadata["Resorts"] += f" (+{len(resorts) - 5} more)"

    return send_slack_alert(
        title=title,
        message=message,
        severity=severity,
        metadata=metadata or None,
    )
