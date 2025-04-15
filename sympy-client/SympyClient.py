from sympy_client.ObsimatClient import ObsimatClient
from sympy_client.grammar.ObsimatLatexParser import ObsimatLatexParser
from sympy_client.modes.EvalMode import eval_handler
from sympy_client.modes.EvalfMode import evalf_handler
from sympy_client.modes.ExpandMode import expand_handler
from sympy_client.modes.FactorMode import factor_handler
from sympy_client.modes.ApartMode import apart_handler
from sympy_client.modes.SolveMode import solve_handler, solve_formatter
from sympy_client.modes.ConvertUnitsMode import convert_units_handler
from sympy_client.modes.SymbolSetMode import symbol_set_handler, symbol_set_formatter
from sympy_client.modes.ConvertSympyMode import convert_sympy_handler, convert_sympy_formatter

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
client.register_mode("solve", solve_handler, solve_formatter)
client.register_mode("symbolsets", symbol_set_handler, symbol_set_formatter)
client.register_mode("convert-sympy", convert_sympy_handler, convert_sympy_formatter)
client.register_mode("convert-units", convert_units_handler)

async def main():
    await client.connect(port)
    await client.run_message_loop()

asyncio.run(main())
