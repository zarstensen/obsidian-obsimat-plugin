from sympy import *
from sympy import sympify
from sympy.parsing.latex import parse_latex, parse_latex_lark
from sympy.solvers.solveset import NonlinearError

def evaluateMode():
    expression = ""
    
    while True:
        new_line = input()
        
        if new_line == "END_EVALUATE":
            break
        
        expression += new_line
    
    expression = expression.split('=')[-1]
    
    sympy_expr = parse_latex(expression, backend="lark")
    
    result = latex(sympy_expr.expand().simplify()) 
    
    print("BEGIN_RESULT")
    print(result)
    print("END_RESULT")

MODES = {
    "BEGIN_EVALUATE": evaluateMode,
    "ERROR": lambda x: print("BEGIN_ERROR\n" + x + "\nEND_ERROR")
}

parse_latex("1")

while True:

    mode = input()
    
    if mode in MODES:
        MODES[mode]()
    else:
        MODES["ERROR"]("Invalid mode: " + mode)
    
    # while True:
    #     latex_input = input()
        
    #     if latex_input == "END":
    #         print("BEGIN_SOLVE")
    #         if len(expressions) == 1:
    #             print(solveset(expressions[0]))
    #         elif len(expressions) <= 0:
    #             pass
    #         else:
    #             # determine symbols now
                
    #             symbols = {}
                
    #             for expr in expressions:
    #                 for symbol in expr.free_symbols:
    #                     symbols[symbol] = True
                
    #             try:
    #                 print(linsolve(expressions, list(symbols.keys())))
    #             except NonlinearError as e:
    #                 print(nonlinsolve(expressions, list(symbols.keys())))
    #         print("END_SOLVE")
    #         continue
        
    #     try:
    #         sympy_expr = parse_latex(latex_input)
    #     except Exception as e:
    #         print("BEGIN_ERROR")
    #         print(e)
    #         print("END_ERROR")

    #     if type(sympy_expr) is not Eq:
    #         # expression is not an equation, ignore all previous expressions and just evaluate this one.
    #         print("BEGIN_EVALUATE")
    #         print(sympy_expr.expand().simplify())
    #         print("END_EVALUATE")
    #     else:
    #         expressions.append(sympy_expr) 
    