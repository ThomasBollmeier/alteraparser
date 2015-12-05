"""
Script to generate a parser from a grammar file
Syntax: python altparsgen.py <grammar_file> [<output_file>]
"""

import sys
from alteraparser.io.file_input import FileInput
from alteraparser.io.output import ConsoleOutput, FileOutput
from alteraparser.codegen.generator import Generator


if len(sys.argv) < 2:
    print('SYNTAX: python3 altparsgen.py <grammar_file> [<output_file>]')
    exit(1)

grammar_path = sys.argv[1]
if len(sys.argv) > 2:
    output = FileOutput(sys.argv[2])
    write_to_file = True
else:
    output = ConsoleOutput()
    write_to_file = False

generator = Generator(output)

if write_to_file:
    output.open()

generator.generate_parser(FileInput(grammar_path))

if write_to_file:
    output.close()
