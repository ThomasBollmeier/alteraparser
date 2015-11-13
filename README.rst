============
Alteraparser
============

Introduction
============

Alteraparser is a library that provides functions to define a grammar that can be passed to a parser.

Basic Usage
===========

Code sample::

    from alteraparser.parser import Parser
    from alteraparser import char_range, fork, many, grammar, ...

    ALPHA = fork(char_range('a', 'z'), char_range('A', 'Z'))
    NUM = char_range('0', '9')
    ALPHA_NUM = fork(ALPHA, NUM)
    ...

    variable = fork([ALPHA, many(ALPHA_NUM)]).set_name('var')
    ...
    my_grammar = grammar(variable, ...)

    my_parser = Parser(my_grammar)
    ast = my_parser.parse_file("my_code.txt")

