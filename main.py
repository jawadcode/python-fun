import argparse

from lexer import Lexer
from utils import Peekable


def run(source: str):
    lexer = Peekable(Lexer(source))
    while not ((token := next(lexer)) is None):
        print(token)


def repl():
    while line := input("$ "):
        run(line)


def main(args: argparse.Namespace):
    match args.command:
        case "repl":
            repl()
        case "run":
            source = open(args.path, "r").read()
            run(source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="python-fun",
        description="Some python langdev fun",
        epilog="I got bored at 1am",
    )
    modes = parser.add_subparsers(
        required=True, help="The different modes", dest="command"
    )
    modes.add_parser("repl")
    run_parser = modes.add_parser("run")
    run_parser.add_argument("path", help="The path of the source file to be run")
    main(parser.parse_args())
