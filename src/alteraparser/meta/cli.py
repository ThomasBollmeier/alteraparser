from argparse import ArgumentParser
from pathlib import Path
import sys
import tomllib

from alteraparser.meta.codegen import generate_python_module_code


def _read_project_version() -> str:
    for parent in Path(__file__).resolve().parents:
        pyproject = parent / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            data = tomllib.loads(content)
            return data["project"]["version"]
    raise FileNotFoundError("pyproject.toml not found")


def _create_argument_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Generate Python parser code from an Alteraparser grammar."
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {_read_project_version()}",
    )
    parser.add_argument(
        "infile",
        nargs="?",
        help="Path to grammar file. If omitted, grammar is read from stdin.",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="Path to write generated parser code to. Defaults to stdout.",
    )
    parser.add_argument(
        "-n",
        "--language-name",
        default="GeneratedLanguage",
        help="Name of the generated language classes.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    arg_parser = _create_argument_parser()
    args = arg_parser.parse_args(argv)

    if args.infile:
        grammar_code = Path(args.infile).read_text(encoding="utf-8")
    else:
        grammar_code = sys.stdin.read()

    generated_code = generate_python_module_code(grammar_code, args.language_name)

    if args.outfile:
        Path(args.outfile).write_text(generated_code, encoding="utf-8")
    else:
        print(generated_code)


if __name__ == "__main__":
    main()