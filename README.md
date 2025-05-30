<div align="center">
  <h1 align="center">Latex Math</h1>
</div>

[![GitHub Release](https://img.shields.io/github/v/release/zarstensen/obsidian-latex-math?style=flat-square&color=blue)](https://github.com/zarstensen/obsidian-latex-math/releases/latest)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/zarstensen/obsidian-latex-math/push.yml?style=flat-square&label=tests)


**Latex Math** is an [Obsidian](https://obsidian.md/) plugin that enables the evaluation of LaTeX blocks with [Sympy](https://www.sympy.org).

<!-- omit in toc -->
## Table of Contents

- [Usage](#usage)
  - [Evaluate](#evaluate)
    - [Variants](#variants)
  - [Solve](#solve)
  - [Definitions](#definitions)
  - [LMat Code Block](#lmat-code-block)
    - [Symbol Assumptions](#symbol-assumptions)
    - [Units](#units)
    - [Solution Domain](#solution-domain)
  - [Sympy Conversion](#sympy-conversion)
- [Installing](#installing)
  - [Linux](#linux)
- [Developing](#developing)
- [License](#license)

## Usage

### Evaluate

Evaluate a LaTeX math expressions with the `Evaluate LaTeX Expression` command.

**Latex Math** supports various math operations, ranging from basic addition and multiplication to more complex operations such as integration and differentiation.
Below is a table overview of an extract of usable functions.

| Operation                     | LaTeX                   | Rendered LaTeX         |
| :---------------------------- | :---------------------- | :--------------------- |
| Inner product of vectors      | `\langle x , y \rangle` | $\langle x, y \rangle$ |
| Norm of a single vector       | `\Vert x \Vert`         | $\Vert x \Vert$        |
| Quick differentiation         | `(x)''...`              | $(x)''^{\cdots}$       |
| Gradient vector of expression | `\nabla(x)`             | $\nabla(x)$            |
| Hessian matrix of expression  | `\mathbf{H}(x)`         | $\mathbf{H}(x)$        |
| Jacobi matrix of expression   | `\mathbf{J}(x)`         | $\mathbf{J}(x)$        |
| rref of matrix                | `\mathrm{rref}(x)`      | $\mathrm{rref}(x)$     |

#### Variants

The evaluate command has a series of variants, which all evaluates a given LaTeX expression, and then proceed to rewrite the result in some way.
Below is a table overview of the variants, as well as their function.

| Command Name                        | Function                                                                                |
| :---------------------------------- | :-------------------------------------------------------------------------------------- |
| `Evalf LaTeX expression`            | Evaluate LaTeX expression and convert it to floating point values instead of fractions. |
| `Expand LaTeX expression`           | Evaluate and expand LaTeX expression.                                                   |
| `Factor LaTeX expression`           | Evaluate and factor LaTeX expression.                                                   |
| `Apart LaTeX expression`            | Evaluate and perform partial fraction decomposition on LaTeX expression.                |
| `Convert units in LaTeX expression` | Evaluate LaTeX expression and convert result to units provided by the user.             |

### Solve

Solve LaTeX equations with the `Solve LaTeX expression` command.

If an equation has too many free variables to solve for all of them, a modal will pop up where you can pick which symbols to solve for. The solution domain can also be specified here [^1].

To solve a system of equations, place each equation on a new line inside either a `\begin{cases}` or `\begin{align}` LaTeX environment, and execute the solve command.

If an expression with no relation is solved, it is assumed it is set equal to 0.
For example, `a^2 + b` would be interpreted as `a^2 + b = 0`.

### Definitions

Define variables or functions inside LaTeX blocks with the `:=` operator.
The left-hand side specifies the name of the variable / function and its parameters, and the right-hand side its value / body.
Whenever it is used after it has been defined, it will be replaced by its defined expression.

> [!IMPORTANT]
> Only one definition can be present in a LaTeX block.
>

Definition persistence is based on the location they were defined inside the document, meaning f.ex. a variable cannot be used in the note above its LaTeX block definition. Furthermore, all `lmat` code blocks remove all definitions above themselves.

To remove a definition, leave the right hand of the `:=` operator blank.

> [!NOTE]
> **Variable Definition Example**
>
> Define a variable `x` with the value `\sqrt{99}`.
>
> `$x := \sqrt{99}$`
>
> Define a variable `y` dependent on the value of `x`.
>
> `$y := x^2$`
>
> Evaluate an expression containing the above variables after they have been defined.
>
> `$x^2 + y$` evaluates to 198
>
> Undefine previously defined variable `x`
>
> `x :=`

> [!NOTE]
> **Function Definition Example**
>
> 
> Define a function `f(x)` with the body `x^2`.
>
> `$f(x) := x^2$`
>
>
> Evaluate an expression containing the above function after they have been defined.
>
> `$f(3) + f(4)$` evaluates to 25
>
> Undefine previously defined function `f`
>
> `f() :=`

### LMat Code Block

`lmat` code blocks define a math environment for which all expressions following the code block will be evaluated. The contents of an `lmat` code block make use of the [TOML](https://toml.io) config format.

Each `lmat` code block functions as a complete reset, ignoring any previous variable definitions and `lmat` code blocks.

> [!NOTE]
> **LMat Code Block Example**
>
> ````text
> ```lmat
> [symbols]
> x = [ "real", "positive" ]
> y = [ "integer" ]
>
> [units]
> system = "SI"
> exclude = [ "g" ]
>
>
> [domain]
> domain="Reals"
> ```
> ````
>
> The below expressions will be evaluated to the following in this environment:
>
> | Expression                                     | Operation | Result                     |
> | :--------------------------------------------- | :-------- | :------------------------- |
> | $x^2=2$                                        | Solve     | $\sqrt{2}$                 |
> | $30 \frac{kg \ m}{s^2}$                        | Evaluate  | $30 N$                     |
> | `\begin{cases} x + y = 1 \\ x = y \end{cases}` | Solve     | $False$                    |
>

#### Symbol Assumptions

[Sympy Assumptions](https://docs.sympy.org/latest/guides/assumptions.html) can be specified for specific symbols in the `symbols` table.

This is done by setting the symbol name as a key in the `symbols` table, equal to a list of assumptions for this symbol.

#### Units

Unit conversion can be enabled and configured in the `units` table.

The `system` key specifies which unit system to use, when converting between units.
Possible values include `SI`, `MKS`, `MKSA` and `Natural system`.
If left blank, no unit conversion will be done.

The `exclude` key specifies a list of symbols, which should not be interpreted as units.
An example of this being useful could be *g* which is often used as a symbol for earths gravitational acceleration, but will be interpreted as *grams* when units are enabled.

#### Solution Domain

The `domain` key in the `domain` table specifies the default domain to restrict single equation solutions to.

The value should be a sympify'able Python expression that evaluates to a [sympy set](https://docs.sympy.org/latest/modules/sets.html).

If not specified, the default domain is the complex set.

### Sympy Conversion

Convert a LaTeX block to Sympy Python code with the `Convert LaTeX Expression To Sympy` command.

## Installing

Download the plugin zip file from the [latest release](https://github.com/zarstensen/obsidian-latex-math/releases/latest), and extract it to your vault's plugin folder, commonly located at `.obsidian/plugins`, relative to your vault's path.

### Linux

If you receive an error upon plugin load on Linux, you might need to give execute permissions to the `SympyClient` file located in the plugin's installation directory.

If this file is not present, please restart obsidian with the **Latex Math** plugin enabled. The file should then be downloaded automatically.

Perform the following commands inside the **Latex Math** installation directory, to give `SympyClient` the necessary permissions:

- (Optional) Check execution permissions of `SympyClient`: 
  
  `ls -l SympyClient`
  
  Something like `-rw-r--r--...` means no execute permission.

- Give execution permissions to `Sympyclient` (This will give every user access to execute `SympyClient`): 
  
  `chmod +x /path/to/SympyClient`

- (Optional) Perform step 1 to check if permissions have changed.

- Reload Obsidian with **Latex Math** enabled. 
  No errors should pop up and the plugin should now work as expected

## Developing

This section describes how to set up a development environment for **Latex Math** .
Make sure to have python and npm installed before continuing.

Start of with running the `setup-dev-env` python script from the root directory.

```sh
python setup-dev-env.py
```

This creates a virtual environment named `.venv` installed with all required dependencies. Furthermore, it sets up a git pre-push hook, which runs the entire test suite, before pushing.

To use this development environment in Obsidian, go to the **Latex Math**  settings in the vault this repo has been cloned to, and toggle the `Developer Mode` switch to on. Make sure to reload the vault after doing this.

The plugin should now use the python source files and the created virtual environment, instead of the auto installed `SympyClient` binary.

Any changes to the python source code requires reloading Obsidian to have any effect.

> [!CAUTION]
> If you are using vscode, make sure to add `push` as an entry to `git.commandsToLog` in vscode (user or workspace), if you want to see the output of the push hook if it fails.

## License

See [LICENSE](LICENSE)

[^1]: Solution domain is only accounted for in single equations. For systems of equations, restrict the solution domain by using symbols defined with assumptions.
