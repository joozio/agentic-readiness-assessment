"""An intentionally small, synthetic Python CLI used for skill evaluation."""
import argparse


def quote(weight):
    if weight <= 0:
        raise ValueError('weight must be positive')
    return 5 + 2 * weight


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('weight', type=int)
    args = parser.parse_args()
    print(quote(args.weight))
