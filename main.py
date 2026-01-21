import asyncio
import logging
from datetime import datetime
from typing import Optional

from src.recipe_agent import create_session, call_adk


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


async def chat_loop() -> None:
    """
    Interactive CLI that routes requests through the ADK runner
    (root_agent) instead of invoking the LangGraph directly.
    """
    logger.info("Starting Recipe Recommendation ADK App")

    session = await create_session()
    print("\n🍳 Recipe Recommendation Assistant (ADK)")
    print(f"(session_id={session.id}, user_id={session.user_id})")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            print("Please enter a query.")
            continue

        if user_input.lower() == "exit":
            logger.info("User exited the application")
            print("👋 Goodbye!")
            break

        logger.info("User input: %s", user_input)

        try:
            response = await call_adk(
                user_input,
                session_id=session.id,
                user_id=session.user_id,
            )
            print(f"\nAssistant:\n{response}\n")
            logger.info("Assistant response: %s", response)
        except Exception:
            logger.exception("Error during ADK execution")
            print(" Something went wrong. Please try again.")


def main() -> None:
    asyncio.run(chat_loop())


if __name__ == "__main__":
    main()
