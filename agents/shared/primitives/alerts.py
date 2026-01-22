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
