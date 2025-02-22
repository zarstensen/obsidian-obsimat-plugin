from ObsimatEnvironment import ObsimatEnvironment
from ObsimatEnvironmentUtils import ObsimatEnvironmentUtils
from grammar.SympyParser import SympyParser

# The SubstitutionCache class is responsible for caching parsed values from the given enviromnts symbols and variables fields.
class SubstitutionCache:
    # Construct a SubstitutionCache which will look for variables and symbols in the given environment, and parse them with the given parser.
    def __init__(self, environment: ObsimatEnvironment, latex_parser: SympyParser):
        self._environment: ObsimatEnvironment = environment
        self._latex_parser = latex_parser
        self._cached_substitutions = {}
    
    # Attempt to get the value which the given variable / symbol name should be substituted with.
    # If no such variable / symbol exists, returns None.
    def get_substitution(self, name):
        if name in self._cached_substitutions:
            return self._cached_substitutions[name]
        elif 'variables' in self._environment and name in self._environment['variables']:
            return self._cache_new_variable(name)    
        elif 'symbols' in self._environment and name in self._environment['symbols']:
            return self._cache_new_symbol(name)
        else:
            return None
        
    def _cache_new_variable(self, variable_name: str):
        variable_latex = self._environment['variables'][variable_name]
        variable_value = self._latex_parser.doparse(variable_latex, self._environment)
        self._cached_substitutions[variable_name] = variable_value
        return variable_value
    
    def _cache_new_symbol(self, symbol_name: str):
        symbol_value = ObsimatEnvironmentUtils.create_sympy_symbol(symbol_name, self._environment)
        self._cached_substitutions[symbol_name] = symbol_value
        return symbol_value
