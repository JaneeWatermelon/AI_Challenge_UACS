import argparse
from warer_agent import WarerAgent
from dotenv import load_dotenv


def main(prompt: str) -> None:
    load_dotenv()
    agent = WarerAgent(rate_limit=6)
    agent.run(prompt)

if __name__ == "__main__":
    main("Create a file at `/app/bye.txt` whose entire content is exactly the single word `Bye` (no trailing newline required, but the file must contain only those three characters).")