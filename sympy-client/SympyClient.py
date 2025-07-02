import asyncio
import sys

from sympy_client.command_handlers.ApartHandler import ApartHandler
from sympy_client.command_handlers.ConvertSympyHandler import ConvertSympyHandler
from sympy_client.command_handlers.ConvertUnitsHandler import ConvertUnitsHandler
from sympy_client.command_handlers.EvalfHandler import EvalfHandler
from sympy_client.command_handlers.EvalHandler import EvalHandler
from sympy_client.command_handlers.ExpandHandler import ExpandHandler
from sympy_client.command_handlers.FactorHandler import FactorHandler
from sympy_client.command_handlers.SolveHandler import SolveHandler
from sympy_client.command_handlers.SymbolSetHandler import SymbolSetHandler
from sympy_client.command_handlers.TruthTableHandler import TruthTableHandler
from sympy_client.grammar.LatexParser import LatexParser
from sympy_client.LatexMathClient import LatexMathClient

if len(sys.argv) < 2:
    print("Usage: python sympy_evaluator.py <port>")
    sys.exit(1)

port = int(sys.argv[1])

latex_parser = LatexParser()

client = LatexMathClient()

client.register_handler("eval", EvalHandler(latex_parser))
client.register_handler("evalf", EvalfHandler(latex_parser))
client.register_handler("expand", ExpandHandler(latex_parser))
client.register_handler("factor", FactorHandler(latex_parser))
client.register_handler("apart", ApartHandler(latex_parser))
client.register_handler("solve", SolveHandler(latex_parser))
client.register_handler("symbolsets", SymbolSetHandler(latex_parser))
client.register_handler("convert-sympy", ConvertSympyHandler(latex_parser))
client.register_handler("convert-units", ConvertUnitsHandler(latex_parser))
client.register_handler("truth-table", TruthTableHandler(latex_parser))

async def main():
    await client.connect(port)
    await client.run_message_loop()

asyncio.run(main())
