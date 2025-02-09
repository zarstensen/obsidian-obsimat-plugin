from LatexParser import LatexParser
from ObsimatClient import ObsimatClient
from typing import *
from sympy import *
from sympy.parsing.latex import parse_latex_lark
import asyncio
import sys
import re

if len(sys.argv) < 2:
    print("Usage: python sympy_evaluator.py <port>")
    sys.exit(1)

port = int(sys.argv[1])


async def evaluateEquation(message: Any, obsimat: ObsimatClient):
    expression = message['expression'].split("=")[-1]

    sympy_expr = LatexParser.parse_latex(expression, message['environment'])
    # store expression before units are converted and it is evaluated,
    # so we can display this intermediate step in the result.
    before_units = sympy_expr.copy()
    sympy_expr = LatexParser.handle_units(sympy_expr, message['environment'])

    sympy_expr = sympy_expr.doit() or sympy_expr
    sympy_expr = sympy_expr.expand() or sympy_expr
    sympy_expr = sympy_expr.cancel() or sympy_expr
    sympy_expr = sympy_expr.simplify() or sympy_expr
    
    with evaluate(False):
        result = latex(Eq(before_units, sympy_expr), mat_symbol_style="bold")
    
    # TODO: this should be done with the regex package instead,
    # to ensure consistency among package usage.
    result = re.sub(r"\\text\{(.*?)\}", r"\1", result)

    await obsimat.sendResult({"result": result})

async def solveEquation(message: Any, obsimat: ObsimatClient):
    expression = LatexParser.parse_latex(message['expression'], message['environment'])
    expression = LatexParser.handle_units(expression, message['environment'])

    if 'symbol' not in message and len(expression.free_symbols) > 1:
        await obsimat.sendResult({"status": "multivariate_equation", "symbols": [str(s) for s in expression.free_symbols]})
        return

    if 'symbol' in message:
        print(expression.free_symbols, flush=True)
        for free_symbol in expression.free_symbols:
            print(free_symbol, flush=True)
            if str(free_symbol) == message['symbol']:
                symbol = free_symbol
                break

        if symbol is None:
            await obsimat.sendError(f"No such symbol: {message['symbol']}")
            return
    else:
        symbol = list(expression.free_symbols)[0]

    solution_set = solveset(expression, symbol)

    # if solution is finite set, do magic, otherwise do simple stuff

    if type(solution_set) is FiniteSet:
        solutions = []
        for solution in list(solution_set):
            solutions.append(f"{symbol} = {latex(solution)}")
        await obsimat.sendResult({"status": "solved", "result": ' \\vee '.join(solutions)})
    else:
        await obsimat.sendResult({"status": "solved", "result": f"{symbol} \\in {latex(solution_set)}"})


client = ObsimatClient()
client.register_mode("evaluate", evaluateEquation)
client.register_mode("solve", solveEquation)


async def main():
    await client.connect(port)
    await client.run_message_loop()


# initialize parser now, so there is no delay the first time an expression is parsed for the first time.
parse_latex_lark("1")

asyncio.run(main())
