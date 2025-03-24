import asyncio
import logging

from anthropic import Anthropic
from dotenv import load_dotenv

from multi.chat_session import ChatSession
from multi.server import Server

load_dotenv()  # load environment variables from .env

# Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def main() -> None:
    """Initialize and run the chat session."""
    servers = [
        Server("Key Light", "http://localhost:8000/sse"),
        Server("Weather", "http://localhost:8001/sse"),
    ]
    chat_session = ChatSession(servers, Anthropic())
    await chat_session.start()


if __name__ == "__main__":
    asyncio.run(main())
