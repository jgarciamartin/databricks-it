import argparse

def main():
    parser = argparse.ArgumentParser(prog="cloudutils")
    parser.add_argument("--ping", action="store_true")
    args = parser.parse_args()

    if args.ping:
        print("cloudutils OK")
