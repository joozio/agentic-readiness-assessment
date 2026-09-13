import argparse

def shipping(total):
    if total < 0:
        raise ValueError("total must be nonnegative")
    return 0 if total >= 5000 else 500

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("total", type=int)
    args = parser.parse_args()
    print(shipping(args.total))
