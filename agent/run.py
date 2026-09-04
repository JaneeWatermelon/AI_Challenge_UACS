import argparse
from warer_agent import WarerAgent


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run local non-interactive coding agent"
    )
    parser.add_argument("prompt", nargs="+", help="Prompt for the agent")
    args = parser.parse_args()
    prompt = " ".join(args.prompt)
    print(prompt)

    agent = WarerAgent(rate_limit=0)
    agent.run(prompt)


if __name__ == "__main__":
    main()