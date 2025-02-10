from ObsimatClient import ObsimatClient

from modes.EvaluateMode import evaluateMode
from modes.SolveMode import solveMode
from modes.SymbolSetMode import symbolSetMode

from sympy.parsing.latex import parse_latex_lark
import asyncio
import sys

if len(sys.argv) < 2:
    print("Usage: python sympy_evaluator.py <port>")
    sys.exit(1)

port = int(sys.argv[1])


client = ObsimatClient()
client.register_mode("evaluate", evaluateMode)
client.register_mode("solve", solveMode)
client.register_mode("symbolsets", symbolSetMode)


async def main():
    await client.connect(port)
    await client.run_message_loop()


# initialize parser now, so there is no delay the first time an expression is parsed for the first time.
parse_latex_lark("1")

asyncio.run(main())
