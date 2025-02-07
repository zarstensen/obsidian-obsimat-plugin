from ObsimatClient import ObsimatClient
from typing import *
from sympy import *
from sympy.parsing.latex import parse_latex, parse_latex_lark
from sympy.solvers.solveset import NonlinearError
import sympy.physics.units as u
import asyncio
import sys
from lark import Tree
import re

if len(sys.argv) < 2:
    print("Usage: python sympy_evaluator.py <port>")
    sys.exit(1)

port = int(sys.argv[1])


async def evaluateMode(message: Any, obsimat: ObsimatClient):
    expression = message['expression'].split("=")[-1]

    sympy_expr = parse_latex(expression, backend="lark")

    if type(sympy_expr) is Tree:
        sympy_expr = sympy_expr.children[0]

        # units on / off here for the future
    if True:
        for symbol in sympy_expr.free_symbols:
            try:
                units = u.find_unit(str(symbol))
                if units[0] == str(symbol):
                    sympy_expr = sympy_expr.subs({symbol: getattr(u, units[0])})
            except AttributeError:
                continue

    tmp = sympy_expr.doit()
    if tmp is not None:
        sympy_expr = tmp

    tmp = sympy_expr.expand()
    if tmp is not None:
        sympy_expr = tmp

    tmp = sympy_expr.simplify()
    if tmp is not None:
        sympy_expr = tmp

    result = latex(sympy_expr, mat_symbol_style="bold")
    result = re.sub(r"\\text\{(.*?)\}", r"\1", result)

    await obsimat.sendResult({"result": result})


client = ObsimatClient()
client.register_mode("evaluate", evaluateMode)


async def main():
    await client.connect(port)
    await client.run_message_loop()


parse_latex("1")

asyncio.run(main())
