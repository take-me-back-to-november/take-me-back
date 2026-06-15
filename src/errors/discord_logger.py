import traceback

from config.discord import DISCORD_WEBHOOK_URL
from instances.http_client import get_http_client

DISCORD_EMBED_COLOR_ERROR = 0xE74C3C
MAX_TRACEBACK_LENGTH = 3500


async def log_server_error_to_discord(
    *,
    method: str,
    path: str,
    exc: Exception,
) -> None:
    if not DISCORD_WEBHOOK_URL:
        return

    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    if len(tb) > MAX_TRACEBACK_LENGTH:
        tb = tb[: MAX_TRACEBACK_LENGTH - 3] + "..."

    payload = {
        "embeds": [
            {
                "title": "500 Internal Server Error",
                "color": DISCORD_EMBED_COLOR_ERROR,
                "fields": [
                    {"name": "Method", "value": method, "inline": True},
                    {"name": "Path", "value": path[:1024], "inline": True},
                    {
                        "name": "Exception",
                        "value": f"`{type(exc).__name__}`: {str(exc)[:900]}",
                        "inline": False,
                    },
                ],
                "description": f"```\n{tb}\n```",
            }
        ]
    }

    try:
        client = get_http_client()
        await client.post(DISCORD_WEBHOOK_URL, json=payload)
    except Exception:
        pass
