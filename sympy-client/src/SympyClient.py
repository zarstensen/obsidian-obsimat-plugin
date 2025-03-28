from ObsimatClient import ObsimatClient

from grammar.ObsimatLatexParser import ObsimatLatexParser
from modes.EvalMode import eval_handler
from modes.EvalfMode import evalf_handler
from modes.ExpandMode import expand_handler
from modes.FactorMode import factor_handler
from modes.ApartMode import apart_handler
from modes.SolveMode import solve_handler, solve_serializer
from modes.SymbolSetMode import symbol_set_handler, symbol_set_serializer
from modes.ConvertSympyMode import convertSympyMode, convertSympyModeFormatter

import asyncio
import sys

if len(sys.argv) < 2:
    print("Usage: python sympy_evaluator.py <port>")
    sys.exit(1)

port = int(sys.argv[1])


client = ObsimatClient(ObsimatLatexParser())
client.register_mode("eval", eval_handler)
client.register_mode("evalf", evalf_handler)
client.register_mode("expand", expand_handler)
client.register_mode("factor", factor_handler)
client.register_mode("apart", apart_handler)
client.register_mode("solve", solve_handler, solve_serializer)
client.register_mode("symbolsets", symbol_set_handler, symbol_set_serializer)
client.register_mode("convert-sympy", convertSympyMode, convertSympyModeFormatter)


async def main():
    await client.connect(port)
    await client.run_message_loop()

asyncio.run(main())
