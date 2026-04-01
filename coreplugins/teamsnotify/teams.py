import json
import logging
import requests

logger = logging.getLogger('app.logger')


def send_card(webhook_url, title, message, status_color="good"):
    """
    Send an Adaptive Card to Microsoft Teams via a Power Automate
    Workflows webhook URL.

    status_color: "good" (green), "warning" (yellow), "attention" (red)
    """
    color_map = {
        "good": "Good",
        "warning": "Warning",
        "attention": "Attention",
    }
    style = color_map.get(status_color, "Default")

    card_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.2",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": title,
                            "style": "heading",
                        },
                        {
                            "type": "TextBlock",
                            "text": message,
                            "wrap": True,
                        },
                    ],
                },
            }
        ],
    }

    try:
        response = requests.post(
            webhook_url,
            data=json.dumps(card_payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        logger.info("TeamsNotify: Message sent successfully")
    except requests.exceptions.RequestException as e:
        logger.error("TeamsNotify: Failed to send message: %s" % str(e))
        raise
