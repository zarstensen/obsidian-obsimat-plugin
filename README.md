# Obsimat

**Obsimat** is an [Obsidian](https://obsidian.md/) plugin that enables the evaluation of $\LaTeX$ blocks with [Sympy](https://www.sympy.org).

<!-- omit in toc -->
## Table of Contents

- [Usage](#usage)
  - [Evaluate](#evaluate)
  - [Solve](#solve)
  - [Variables](#variables)
  - [Obsimat Code Block](#obsimat-code-block)
  - [Sympy Conversion](#sympy-conversion)
- [Installing](#installing)
- [License](#license)

## Usage

### Evaluate

Evaluate a $\LaTeX$ math expressions with the `Evaluate LaTeX Expression` command (alt + B).

Obsimat supports various math operations, ranging from basic addition and multiplication to more complex operations such as integration and differentiation. In general, Obsimat will support any operation that Sympy's Lark $\LaTeX$ parser can parse. Furthermore, the Lark parser has been extended to support the following additional operations:

| Operation                | $\LaTeX$                | Rendered $\LaTeX$      |
| :----------------------- | :---------------------- | :--------------------- |
| Inner product of vectors | `\langle x , y \rangle` | $\langle x, y \rangle$ |
| Norm of a single vector  | `\Vert x \Vert`         | $\Vert x \Vert$        |
| Quick differentiation    | `(x)''...`              | $(x)''^{\cdots}$       |

### Solve

Solve $\LaTeX$ equations with the `Solve LaTeX Expression` command (alt + L).

If an equation has too many free variables to solve for all of them, a modal will pop up where you can pick which symbols to solve for. The solution domain can also be specified here [^1].

To solve a system of equations, place each equation on a new line inside either a `\begin{cases}` or `\begin{align}` $\LaTeX$ environment, and execute the solve command.

If an expression with no relation is solved, it is assumed it is set equal to $0$.
For example, $a^2 + b$ would be interpreted as $a^2 + b = 0$.

### Variables

Define variables inside $\LaTeX$ blocks with the `:=` operator.
The left-hand side specifies the name of the variable, and the right-hand side its value.
Whenever this variable is used after it has been defined, it will be replaced by its value.

> [!IMPORTANT]
> Only one variable can be defined per $\LaTeX$ block.
>

Variable persistence is based on the location they were defined inside the document, meaning a variable cannot be used in the note above its LaTeX block definition. Furthermore, all Obsimat code blocks remove all variable definitions above themselves.

> [!TIP] Variable Definition Example
> Define a variable `x` with the value `\sqrt{99}`.
>
> $\text{\verb|x := \sqrt{99}|} \to x := \sqrt{99}$
>
> Define a variable `y` dependent on the value of `x`.
>
> $\text{\verb|y := x^2|} \to y := x^2$
>
> Evaluate an expression containing the above variables after they have been defined.
>
> $\text{\verb|x^2 + y|} \to x^2 + y \text{\verb| evaluates to |} 198$
>

### Obsimat Code Block

Obsimat code blocks define a math environment for which all expressions following the code block will be evaluated. The contents of an Obsimat code block make use of the [TOML](https://toml.io) config format.

Each Obsimat code block functions as a complete reset, ignoring any previous variable definitions and Obsimat code blocks.

> [!TIP] Obsimat Code Block Example
>
> ````toml
> ```obsimat
>
> [symbols]
> x = [ "real", "positive" ]
> y = [ "integer" ]
>
> [units]
> units = [ "km", "h" ]
> base-units = [ "m", "s" ]
>
>
> [domain]
> domain="Reals"
>
> ```
> ````
>
> The below expressions will be evaluated to the following in this environment:
>
> | Expression                                     | Operation | Result                     |
> | :--------------------------------------------- | :-------- | :------------------------- |
> | $x^2=2$                                        | Solve     | $\sqrt{2}$                 |
> | $30 \frac{km}{h}$                              | Evaluate  | $\frac{25}{3} \frac{m}{s}$ |
> | $\begin{cases} x + y = 1 \\ x = y \end{cases}$ | Solve     | $False$                    |
>

#### Symbol Assumptions

[Sympy Assumptions](https://docs.sympy.org/latest/guides/assumptions.html) can be specified for specific symbols in the `symbols` table.

This is done by setting the symbol name as a key in the `symbols` table, equal to a list of assumptions for this symbol.

#### Units

Units and unit conversions can be specified in the `units` table.

The `units` key specifies a list of all units that can be used in the environment.

The `base-units` key specifies a list of units, which all results will be converted to.

Units specified in `base-units` do not have to be present in `units`.

#### Solution Domain

The `domain` key in the `domain` table specifies the default domain to restrict single equation solutions to.

The value should be a sympify'able Python expression that evaluates to a [sympy set](https://docs.sympy.org/latest/modules/sets.html).

If not specified, the default domain is the complex ($\mathbb{C}$) set.

### Sympy Conversion

Convert a $\LaTeX$ block to Sympy Python code with the `Convert LaTeX Expression To Sympy` command.

## Installing

Download the plugin zip file from the [latest release](https://github.com/zarstensen/obsidian-obsimat-plugin/releases/latest), and extract it to your vault's plugin folder, commonly located at `.obsidian/plugins`, relative to your vault's path.

## License

See [LICENSE](LICENSE)

[^1]: Solution domain is only accounted for in single equations. For systems of equations, restrict the solution domain by using symbols defined with assumptions.
