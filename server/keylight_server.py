import os
from typing import Any, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("keylight")

# Constants
KEYLIGHT_API_BASE = os.environ.get("KEYLIGHT_API_BASE")


async def make_get_request(url: str) -> dict[str, Any] | None:
    """Make a get request to the elgato keylight API with proper error handling."""
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, headers=headers, timeout=30.0)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None


async def make_put_request(url: str, content: dict[str, Any]):
    """Make a put request to the elgato keylight API with proper error handling."""
    headers = {"Accept": "application/json"}
    async with httpx.AsyncClient() as client:
        try:
            print(content)
            res = await client.put(url, headers=headers, timeout=30.0, json=content)
            res.raise_for_status()
            return res.json()
        except Exception:
            return None


def format_light(light: dict) -> str:
    """Format the light status into a readable string."""
    return f"""
On: {light.get('on', 'Unknown')}
Brightness: {light.get('brightness', 'Unknown')}
Temperature: {light.get('temperature', 'Unknown')}
"""


@mcp.tool()
async def get_keylight_status() -> str:
    """Get elgato keylight status."""

    url = f"{KEYLIGHT_API_BASE}/elgato/lights"
    data = await make_get_request(url)

    if not data or "lights" not in data:
        return "Unable to fetch status or no lights found."

    if not data["lights"]:
        return "No lights found."

    lights = [format_light(light) for light in data["lights"]]
    return "\n---\n".join(lights)


@mcp.tool()
async def set_keylight_status(on: int, brightness: Optional[int], temperature: Optional[int]) -> str:
    """Turn elgato keylight on or of and optionally set its attributes.

    Args:
        on: Whether the light is on or off (0 or 1)
        brightness: Brightness of the light (0-100)
        temperature: Temperature of the light (143-344)
    """
    # First get the forecast grid endpoint
    url = f"{KEYLIGHT_API_BASE}/elgato/lights"
    light = {"on": on}
    if brightness is not None: light["brightness"] = brightness
    if temperature is not None: light["temperature"] = temperature
    data = await make_put_request(url, {"numberOfLights": 1, "lights": [light]})

    if not data: return "Unable to put status."
    if not data or "lights" not in data: return "No lights found."
    if not data["lights"]: return "No lights found."

    lights = [format_light(light) for light in data["lights"]]
    return "\n---\n".join(lights)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')
