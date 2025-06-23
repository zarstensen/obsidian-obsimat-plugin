from lark import Token, Transformer, v_args
from sympy import *
from sympy.logic.boolalg import *

from sympy_client.grammar.SystemOfExpr import SystemOfExpr


# The FucntionsTransformer holds the implementation of various mathematical function rules,
# defined in the latex math grammar.
@v_args(inline=True)
class PropositionsTransformer(Transformer):

    def CMD_TAUTOLOGY(self, _) -> Expr:
        return S.true

    def CMD_CONTRADICTION(self, _) -> Expr:
        return S.false

    @v_args(meta=True, inline=True)
    def proposition_chain(self, meta, *props: tuple[Expr]) -> SystemOfExpr:
        if len(props) > 1:
            return SystemOfExpr([(prop, meta) for prop in props])
        else:
            return props[0]

    def prop_iff(self, *args: tuple[Expr]) -> Expr:
        equiv = Equivalent(*args, evaluate=False)

        if not equiv.is_Boolean:
            # figure out how to do this...
            equiv.lmat_is_Boolean = True

        return equiv

    def prop_implies(self, *args: tuple[Expr|Token]) -> Expr:

        args = list(args)

        while len(args) > 1:
            right = args.pop()
            op_token = args.pop()
            left = args.pop()

            match op_token.type:
                case "_PROP_OP_LR_IMPLICATION":
                    implication = Implies(left, right, evaluate=False)
                case "_PROP_OP_RL_IMPLICATION":
                    implication = Implies(right, left, evaluate=False)
                case _:
                    raise ValueError(f"Unexpected token: {repr(op_token)}")

            args.append(implication)

        return args[0]

    def prop_or(self, *args: tuple[Expr]) -> Expr:
        return Or(*args, evaluate=False)

    def prop_nand(self, *args: tuple[Expr]) -> Expr:
        return Nand(*args, evaluate=False)

    def prop_and(self, *args: tuple[Expr]) -> Expr:
        return And(*args, evaluate=False)

    def prop_nor(self, *args: tuple[Expr]) -> Expr:
        return Nor(*args, evaluate=False)

    def prop_xor(self, *args: tuple[Expr]) -> Expr:
        return Xor(*args, evaluate=False)

    def prop_xnor(self, *args: tuple[Expr]) -> Expr:
        return Xnor(*args, evaluate=False)

    def prop_not(self, arg: Expr) -> Expr:
        return Not(arg, evaluate=False)
