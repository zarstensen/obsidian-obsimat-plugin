from lark import Token, Transformer, v_args
from sympy import *
from sympy.logic.boolalg import *


# The FucntionsTransformer holds the implementation of various mathematical function rules,
# defined in the latex math grammar.
@v_args(inline=True)
class PropositionsTransformer(Transformer):
        
    def CMD_TAUTOLOGY(self, _) -> Expr:
        return S.true
    
    def CMD_CONTRADICTION(self, _) -> Expr:
        return S.false
    
        
    def prop_iff(self, *args: tuple[Expr]) -> Expr:
        return Equivalent(*args)

    def prop_implies(self, *args: tuple[Expr|Token]) -> Expr:
        
        args = list(args)
        
        while len(args) > 1:
            right = args.pop()
            op_token = args.pop()
            left = args.pop()
            
            match op_token.type:
                case "_PROP_OP_LR_IMPLICATION":
                    implication = Implies(left, right)
                case "_PROP_OP_RL_IMPLICATION":
                    implication = Implies(right, left)
                case _:
                    raise ValueError(f"Unexpected token: {repr(op_token)}")
            
            args.append(implication)

        return args[0]

    def prop_or(self, *args: tuple[Expr]) -> Expr:
        return Or(*args)
    
    def prop_nand(self, *args: tuple[Expr]) -> Expr:
        return Nand(*args)
    
    def prop_and(self, *args: tuple[Expr]) -> Expr:
        return And(*args)
    
    def prop_nor(self, *args: tuple[Expr]) -> Expr:
        return Nor(*args)
    
    def prop_xor(self, *args: tuple[Expr]) -> Expr:
        return Xor(*args)
    
    def prop_xnor(self, *args: tuple[Expr]) -> Expr:
        return Xnor(*args)
    
    def prop_not(self, arg: Expr) -> Expr:
        return Not(arg)
