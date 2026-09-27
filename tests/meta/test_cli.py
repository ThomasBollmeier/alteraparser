from pathlib import Path
import tomllib

import pytest

from alteraparser.meta.cli import main


GRAMMAR = """
tokens {
    WS regex(\\s+) ignore;
    ID regex([a-zA-Z_][a-zA-Z0-9_]*);
}

start -> ID;
"""


def test_cli_reads_from_stdin_and_writes_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin.read", lambda: GRAMMAR)

    main(["-n", "MyLang"])

    out = capsys.readouterr().out
    assert "class MyLangLexerGrammar(LexerGrammar):" in out
    assert "class MyLangParser:" in out


def test_cli_reads_from_file_and_writes_to_outfile(tmp_path):
    grammar_file = tmp_path / "grammar.ap"
    outfile = tmp_path / "generated.py"
    grammar_file.write_text(GRAMMAR, encoding="utf-8")

    main([str(grammar_file), "-o", str(outfile), "-n", "DemoLang"])

    generated = outfile.read_text(encoding="utf-8")
    assert "class DemoLangLexerGrammar(LexerGrammar):" in generated
    assert "class DemoLangParser:" in generated

