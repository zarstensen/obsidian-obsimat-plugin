from collections import deque
from copy import copy
from nt import environ
from typing import Iterable

from lark import Tree
from pytest import mark
from sympy import Expr, FiniteSet, Function, Symbol, isolate
from sympy_client.grammar.DefinitionStore import DefinitionStore, FunctionDefinition, SymbolDefinition
from sympy_client.LmatEnvironment import LmatEnvironment
from sympy_client.grammar.LatexCompiler import LatexSympyCompiler, LatexSympySymbolsCompiler
from sympy_client.grammar.SympyParser import DefStoreLarkCompiler
    
    
class LmatEnvFunctionDefinition(FunctionDefinition):
    def __init__(self, definition_store: DefinitionStore, parser: DefStoreLarkCompiler, args: Iterable[Symbol], latex_expr: str):
        super().__init__()
        self._definitions_store = definition_store
        self._parser = parser
        self._args = tuple(args)
        self._latex_expr = latex_expr

    def call(self, *args) -> Expr:
        assert len(args) == len(self.args)

        args_map = { arg: val for arg, val in zip(self.args, args) }
        func_def_store = LmantEnvFuncDefStore(args_map, self._definitions_store)
        
        expr = self._parser.compile(self.serialized_body, func_def_store)
        
        return expr
    
    def get_body(self):
        return self.call(*self.args)
    
    @property
    def args(self) -> tuple[Expr]:
        return self._args
    
    @property
    def serialized_body(self) -> str:
        return self._latex_expr

# Definition store implementation in the context of an LmatEnvironment.
# provides definitions and deserializatiosn based on the symbols, variables and functions tables.
class LmatEnvDefStore(DefinitionStore):
    
    def __init__(self, environment: LmatEnvironment, latex_str: str, expr_compiler: DefStoreLarkCompiler = LatexSympyCompiler, symbols_compiler: DefStoreLarkCompiler = LatexSympySymbolsCompiler):
        super().__init__()
        
        self._expr_compiler = expr_compiler
        self._symbols_compiler = symbols_compiler
        
        self._environment = environment
        
        symbol_dependencies: set[Symbol] = set(self._symbols_compiler.compile(latex_str, self))
        
        self._add_symbols(tuple(filter(lambda s: str(s) in environment.get('variables', {}), symbol_dependencies)))
        
        

        self._functions: dict[Symbol, FunctionDefinition] = {}
        
        if 'functions' in self._environment:
            for func_name, func_def in self._environment['functions'].items():
                
                func_args = [ self.deserialize_symbol(s) for s in func_def['args'] ]
                
                self._functions[self.deserialize_function(func_name)] = LmatEnvFunctionDefinition(
                    definition_store=self,
                    args=func_args,
                    latex_expr=func_def['expr'],
                    parser=expr_compiler
                )
    
    
    def get_function_definition(self, function: Function) -> FunctionDefinition | None:
        return self._functions.get(function)
    
    def deserialize_function(self, serialized_function: str) -> Function:
        return Function(serialized_function.strip())
    
    # Attempt to get the value which the given variable / symbol name should be substituted with.
    # If no such variable / symbol exists, returns None.
    def get_symbol_definition(self, symbol: Symbol) -> SymbolDefinition | None:
        return self._symbols.get(symbol, None)
    
    def get_symbol_dependencies(self, symbol) -> set[Symbol]:
        assert symbol in self._serialized_symbol_definitions
        
        symbol_dependencies = self._symbols_compiler.compile(self._serialized_symbol_definitions)
        
        assert isinstance(symbol_dependencies, FiniteSet)
        
        return set(symbol_dependencies)
    
    def deserialize_symbol(self, symbol_latex: str):
        return copy(Symbol(symbol_latex))
    
    def _add_symbols(self, symbols: tuple[Symbol]):
        
        self._symbols: dict[Symbol, SymbolDefinition] = { }
        
        # build the dependency graph (connected subcomponent) which contains all entries in the passed symbols list.
    
        dependency_graph: dict[Symbol, set[Symbol]] = { }
        marked_symbols = set({ })

        in_deg_table: dict[int, Symbol] = { }
        
        for symbol in symbols:
            if symbol in marked_symbols:
                continue
            
            visit_queue = deque({ symbol })
            
            dependency_graph[symbol] = set()
            in_deg_table[symbol] = 0
            marked_symbols.add(symbol)
            
            while len(visit_queue) > 0:
                
                symbol_vert = visit_queue.popleft()

                neighbours = set(self._symbols_compiler.compile(self._environment['variables'][str(symbol_vert)], self))
                
                for neighbour in neighbours:
                    dependency_graph[symbol_vert].add(neighbour)
                    
                    if neighbour not in marked_symbols:
                        marked_symbols.add(neighbour)
                        dependency_graph[neighbour] = set()
                        in_deg_table[neighbour] = 0
                        visit_queue.append(neighbour)
            
                    in_deg_table[neighbour] += 1
        
        print(dependency_graph)
        # process dependencies in reverse topological order according to the constructed dependency graph.
        # XXX: this ordering should be stored in the definition store.
        topological_ordering = [ ]
        
        source_symbols = deque(filter(lambda s: in_deg_table[s] == 0, dependency_graph))
        
        while len(source_symbols) > 0:
            source = source_symbols.popleft()
            
            topological_ordering.append(source)
            
            for neighbour in dependency_graph[source]:
                in_deg_table[neighbour] -= 1
                
                if in_deg_table[neighbour] == 0:
                    source_symbols.append(neighbour)
            
            del in_deg_table[source]
        
        if in_deg_table != { }:
            # in_deg_table is not empty => graph is not a DAG => there is a cyclic dependency in the remaining vertices in the graph.
            raise RuntimeError(f"There is a cyclic dependency between the following symbols: {', '.join(map(str, in_deg_table.keys()))}")
        
        for symbol in reversed(topological_ordering):
            self._symbols[symbol] = SymbolDefinition(symbol,
                                                     self._expr_compiler.compile(self._environment['variables'][str(symbol)], self),
                                                     dependency_graph[symbol])

# wrapper class for a DefinitionStore, which maps function args and their corresponding symbols to a given set of values.
# should be used in the context of parsing a function body.
class LmantEnvFuncDefStore(DefinitionStore):
    
    def __init__(self, args: dict[Symbol, Expr], definitions_store: DefinitionStore):
        super().__init__()
        self._definitions_store = definitions_store
        self._args = args
    
    def get_function_definition(self, function):
        return self._definitions_store.get_function_definition(function)
    
    def deserialize_function(self, serialized_function):
        return self._definitions_store.deserialize_function(serialized_function)
    
    def get_symbol_definition(self, symbol: Symbol) -> Expr | None:
        return self._args.get(symbol, self._definitions_store.get_symbol_definition(symbol))

    def deserialize_symbol(self, serialized_symbol):
        return self._definitions_store.deserialize_symbol(serialized_symbol)
    
