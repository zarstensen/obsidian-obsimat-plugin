from ObsimatEnvironment import ObsimatEnvironment
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from grammar.SympyParser import SympyParser
from sympy import Expr
from copy import deepcopy

# The FunctionSubstitutor class is responsible for producing a sympy expression to substitute a defined function in the given obsimat environment.
class FunctionSubstitutor:
    def __init__(self, environment: ObsimatEnvironment, parser: SympyParser):
        self._environment = environment
        self._parser = parser

    # Attempt to compute value which the given function name with the given argument values should be substituted with.
    # Returns None if no such function has been defined.
    def get_function_substitution(self, func_name, func_arg_values) -> Expr:
        if 'functions' not in  self._environment or func_name not in self._environment['functions']:
            return None

        func_args = self._environment['functions'][func_name]['args']
        func_expr = self._environment['functions'][func_name]['expr']
        
        # check if args match
        if len(func_arg_values) != len(func_args):
            raise ValueError(f"Function '{func_name}' expected {len(func_args)} arguments but got {len(func_arg_values)} {func_arg_values}")
        
        
        new_env: dict = deepcopy(self._environment)
        
        if 'variables' not in new_env:
            new_env['variables'] = {}
            
        
        for arg_symbol, arg_value in zip(func_args, func_arg_values):
            new_env['variables'][arg_symbol] = arg_value
        
        func_expr = self._parser.doparse(func_expr, new_env)
        
        return func_expr
        
        
        
        