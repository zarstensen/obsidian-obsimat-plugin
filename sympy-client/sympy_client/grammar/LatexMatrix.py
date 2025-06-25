from sympy import Matrix
from sympy.core.sympify import converter


# The LatexMatrix class stores additional info about the eventual latex representation of a sympy matrix.
class LatexMatrix(Matrix):
    env_begin: str = None
    env_end: str = None

    def __new__(cls, *args, env_begin: str = None, env_end: str = None, **kwargs):
        # only the class type is propagated during matrix computations,
        # so a custom class is created for each new instance, which stores the latex strings.
        larr_cls = type(
            f"LatexArray {env_begin} {env_end}",
            (cls,),
            {"env_begin": env_begin, "env_end": env_end, "__new__": super().__new__},
        )

        return larr_cls(*args, **kwargs)


converter[LatexMatrix] = lambda x: type(x)(x)
