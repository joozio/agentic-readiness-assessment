"""Command-line entry point for the rate card."""
import argparse
import json
from pathlib import Path

from pricing import quote


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("weight", type=int)
    args = parser.parse_args()
    rates = json.loads((Path(__file__).parent / "data" / "rates.json").read_text())
    print(quote(args.weight, rates["base_fee"], rates["per_kilogram"]))


if __name__ == "__main__":
    main()

