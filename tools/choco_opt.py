#!/usr/bin/env python3

import argparse
import ast
from io import IOBase

from xdsl.ir import MLContext
from xdsl.dialects.builtin import ModuleOp

from choco.lexer import Lexer as ChocoLexer
from choco.parser import Parser as ChocoParser

from choco.dialects.choco_ast import ChocoAST

from typing import Callable, Dict, List

from xdsl.xdsl_opt_main import xDSLOptMain


class ChocoOptMain(xDSLOptMain):

    passes_native = []

    passes_integrated = []

    def register_all_passes(self):
        self.available_passes = self.get_passes_as_dict()

    def register_all_targets(self):
        super().register_all_targets()

    def pipeline_entry(self, k: str, entries: Dict):
        """Helper function that returns a pass"""
        if k in entries.keys():
            return entries[k]

    def setup_pipeline(self):
        self.pipeline = []

    def register_all_dialects(self):
        super().register_all_dialects()
        """Register all dialects that can be used."""
        self.ctx.register_dialect(ChocoAST)

    @staticmethod
    def get_passes_as_dict(
    ) -> Dict[str, Callable[[MLContext, ModuleOp], None]]:
        """Add all passes that can be called by choco-opt in a dictionary."""

        pass_dictionary = {}

        passes = ChocoOptMain.passes_native + ChocoOptMain.passes_integrated

        for pass_function in passes:
            pass_dictionary[pass_function.__name__.replace(
                "_", "-")] = pass_function

        return pass_dictionary

    def get_passes_as_list(self,
                           native: bool = False,
                           integrated=False) -> List[str]:
        """Add all passes that can be called by choco-opt in a list."""

        pass_list = []

        assert not (native and integrated)

        if native:
            passes = ChocoOptMain.passes_native
        elif integrated:
            passes = ChocoOptMain.passes_integrated
        else:
            passes = ChocoOptMain.passes_native + ChocoOptMain.passes_integrated
        for pass_function in passes:
            pass_list.append(pass_function.__name__.replace("_", "-"))

        return pass_list

    def register_all_frontends(self):
        super().register_all_frontends()

        def parse_choco(f: IOBase):
            lexer = ChocoLexer(f)  # type: ignore
            parser = ChocoParser(lexer)
            program = parser.parse_program()
            return program

        self.available_frontends['choc'] = parse_choco
        self.available_frontends['py'] = parse_choco


def __main__():
    choco_main = ChocoOptMain()

    try:
        module = choco_main.parse_input()
        choco_main.apply_passes(module)
    except Exception as e:
        print(str(e))
        exit(0)

    contents = choco_main.output_resulting_program(module)
    choco_main.print_to_output_stream(contents)


if __name__ == "__main__":
    __main__()
