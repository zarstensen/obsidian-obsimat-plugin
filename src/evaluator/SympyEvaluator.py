from ObsimatClient import ObsimatClient

from grammar.ObsimatLatexParser import ObsimatLatexParser
from modes.EvaluateMode import evaluateMode
from modes.SolveMode import solveMode, solveModeFormatter
from modes.SymbolSetMode import symbolSetMode, symbolSetModeFormatter

from sympy.parsing.latex import parse_latex_lark
import asyncio
import sys

if len(sys.argv) < 2:
    print("Usage: python sympy_evaluator.py <port>")
    sys.exit(1)

port = int(sys.argv[1])


client = ObsimatClient(ObsimatLatexParser())
client.register_mode("evaluate", evaluateMode)
client.register_mode("solve", solveMode, solveModeFormatter)
client.register_mode("symbolsets", symbolSetMode, symbolSetModeFormatter)


async def main():
    await client.connect(port)
    await client.run_message_loop()

# initialize parser now, so there is no delay the first time an expression is parsed for the first time.
parse_latex_lark("1")

asyncio.run(main())
