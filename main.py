import argparse
from interpret import Interpret, NotBound, Ty, TypeMismatch

from parser import Parser, UnexpectedEOI, UnexpectedToken


def main(args: argparse.Namespace):
    match args.command:
        case "repl":
            repl()
        case "run":
            source = open(args.path, "r").read()
            run(source)


def run(source: str):
    parser = Parser(source)
    try:
        expr = parser.parse_expr()
        print(str(expr))
        print(Interpret(None).interpret(expr))
    except Exception as exp:
        match exp:
            case UnexpectedEOI():
                print("Unexpected end of input")
            case UnexpectedToken(expected, got):
                tokens = ", ".join(map(str, expected))
                print(f"Expected {tokens}, got {str(got)}")
            case NotBound(span):
                print(f"Unbound variable @ {str(span)}")
            case TypeMismatch(span, e, g):
                print(f"Type mismatch @ {str(span)}: expected {e}, got: {g}")


def repl():
    try:
        while line := input("$ "):
            if line.startswith(":"):
                match line[1:]:
                    case "h" | "help":
                        print_help()
                    case "q" | "quit":
                        exit(0)
            else:
                run(line)

    except (KeyboardInterrupt, EOFError):
        exit(1)


def print_help():
    print(
        """Commands:
    :h/:help - Print this message
    :q/:quit - Exit the REPL"""
    )


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
