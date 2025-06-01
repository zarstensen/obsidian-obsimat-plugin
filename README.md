<div align="center">
  
  <h1 align="center">
  Latex Math

  <a>[![GitHub Release](https://img.shields.io/github/v/release/zarstensen/obsidian-latex-math?style=flat-square&color=blue)](https://github.com/zarstensen/obsidian-latex-math/releases/latest) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/zarstensen/obsidian-latex-math/push.yml?style=flat-square&label=tests)
  </a>

  </h1>

</div>

**Latex Math** is an [Obsidian](https://obsidian.md/) plugin which adds mathematical evaluation of LaTeX math blocks to your notes, using [Sympy](https://www.sympy.org).

![demo](readme-assets/frontpage-demo.gif)
*`Evaluate LaTeX expression` is bound to `Alt + B` in the above demo.
In general, all demo GIFs will make use of the [recommended hotkeys](#command-list). [^demo-gif-plugins]*
[^demo-gif-plugins]: All demo GIFs were produced with the [Obsidian Latex Suite](https://github.com/artisticat1/obsidian-latex-suite) plugin installed.

## Usage

Start out by placing the cursor inside any math block. Then execute the `Evaluate LaTeX expression` command (or any other command from the [command list](#command-list)). **Latex Math** will now parse the latex math, evaluate the equation, and insert the result at the end of the math block.

Take a look at the [command list](#command-list) a brief overview of what this plugin can do, or go look at the [features](#features) list, for a more in depth walkthrough of this plugin's advanced features.

If you are a Linux user, make sure to read the [Linux](#linux) subsection of the [Installing](#installing) section to ensure this plugin runs correctly.

<!-- omit in toc -->
## Table of Contents

- [Usage](#usage)
- [Command List](#command-list)
- [Features](#features)
  - [Evaluate](#evaluate)
  - [Solve](#solve)
  - [Symbol and Function Definitions](#symbol-and-function-definitions)
  - [Units and Physical Constants](#units-and-physical-constants)
  - [Symbol Assumptions](#symbol-assumptions)
  - [Convert To Sympy Code](#convert-to-sympy-code)
- [Installing](#installing)
  - [Linux](#linux)
- [Developing](#developing)
  - [Developing the Sympy Client](#developing-the-sympy-client)
  - [Developing the Obsidian Plugin](#developing-the-obsidian-plugin)
- [License](#license)

## Command List

Below is a table of all the commands this plugin provides, along with a brief description of what it does and optionally a recommended hotkey.

| Command                                     | Recommended Hotkey | Usage                                                                                                                       |
| ------------------------------------------- | :----------------: | --------------------------------------------------------------------------------------------------------------------------- |
| Evaluate LaTeX expression                   |     `Alt + B`      | Evaluate the right most expression (if in a relation) and simplify the result.                                              |
| Evalf LaTeX expression                      |     `Alt + F`      | Evaluate expression and output decimal numbers instead of fractions in the result.                                          |
| Expand LaTeX expression                     |     `Alt + E`      | Evaluate expression and expand the result as much as possible.                                                              |
| Factor LaTeX expression                     |                    | Evaluate expression and factorize the result as much as possible.                                                           |
| Partial fraction decompose LaTeX expression |                    | Evaluate expression and perform partial fraction decomposition on the result.                                               |
| Solve LaTeX expression                      |     `Alt + L`      | Solve a single equation or a system of equations. Output the result in a new math block below the current one.              |
| Convert units in LaTeX expression           |     `Alt + U`      | Try to convert the units in the right most expression to the user supplied one.                                             |
| Convert LaTeX expression to Sympy.          |                    | Convert entire expression to its equivalent Sympy code, and insert the result in a code block below the current math block. |

## Features

### Evaluate

Evaluate equations in various ways using the evaluate command suite. The computed output varies, depending on the chosen command.

The entire evaluate suite consists of the following commands: `Evaluate LaTeX expression`, `Evalf LaTeX expression`, `Expand LaTeX expression`, `Factor LaTeX expression` and `Partial fraction decompose LaTeX expression`.

<!-- TODO: update this one so it uses the newest version -->
![demo](readme-assets/evaluate-demo.gif)

### Solve

Solve equations using the `Solve LaTeX expression` command.
To solve a system of equations, place them in a `align` or `cases` environment separated by latex newlines (`\\\\`).

The solution domain can be restricted for system of equations in the solve equation modal, see the [relevant Sympy documentation](https://docs.sympy.org/latest/modules/sets.html#module-sympy.sets.fancysets) for a list of possible values.[^lmat-solve-domain]
Restrict the solution domain of a single equation with [symbol assumptions](#symbol-assumptions) on the free symbols.

[^lmat-solve-domain]: The default solution domain for systems of equations can be set via. The `domain` key in the `domain` table in an `lmat` environment.

<!-- TODO: update this one so it has a set solution (sin for example with a periodic solution domain) -->

![demo](readme-assets/solve-demo.gif)

### Symbol and Function Definitions

Define values of symbols or functions using the `:=` operator.
Only one symbol or function can be defined per math block.

Definitions persistence are location based, any math block below a definition will make use of it, all others will ignore it. Furthermore, all definitions are reset after an `lmat` code block.

To undefine a symbol or function, leave the right-hand side of the `:=` operator blank.

### Units and Physical Constants

Denote units or physical constants in equations by surrounding them with braces `{}`.
Latex Math automatically handles conversions between units, constants and their various prefixes. See the [syntax](SYNTAX.md#unit-list) document for a list of supported units and physical constants.

### Symbol Assumptions

Use an `lmat` code block to tell **Latex Math** about various assumptions it may make about specific symbols. This is used to further simplify expressions, such as roots, or limit the solution domain of equations. By default, all symbols are assumed to be complex numbers.

`lmat` code blocks make use of the [TOML](https://toml.io) config format. To define assumptions for a symbol, assign the symbol's name to a list of assumptions Latex Math should make, under the `symbols` table. Like definitions, an `lmat` code block's persistence is based on its location. See below for a simple example.

> [!TIP]
> **Example**
> 
> ````text
> ```lmat
> [symbols]
> x = [ "real", "positive" ]
> y = [ "integer" ]
> ```
> ````

See the [Sympy documentation](https://docs.sympy.org/latest/guides/assumptions.html#id28) for a list of possible assumptions.

### Convert To Sympy Code

Quickly convert latex to Sympy code to perform more advanced computations using the `Convert LaTeX expression to Sympy` command.
This will insert a python code block containing the equivalent Sympy code of the selected math block.

## Installing

Download the plugin zip file from the [latest release](https://github.com/zarstensen/obsidian-latex-math/releases/latest), and extract it to your vault's plugin folder, commonly located at `.obsidian/plugins`, relative to your vault's path.

### Linux

If you receive an error upon plugin load on Linux, you might need to give execute permissions to the `SympyClient-linux.bin` file located in the plugin's installation directory.

Perform the following commands inside the **Latex Math** installation directory, to give the necessary permissions:

- (Optional) Check execution permissions of `SympyClient-linux.bin`:
  
  `ls -l ./bin/SympyClient-linux.bin`
  
  Something like `-rw-r--r--...` means no execute permission.

- Give execution permissions to `Sympyclient-linux.bin` (This will give every user access to execute `SympyClient-linux.bin`):
  
  `chmod +x ./bin/SympyClient-linux.bin`

- (Optional) Perform step 1 to check if permissions have changed.

- Reload Obsidian with **Latex Math** enabled.
  No errors should pop up, and the plugin should now work as expected

## Developing

This section describes how to set up a development environment for **Latex Math**.
Make sure to have python (for Sympy client development) and / or NPM (for obsidian plugin development) installed before continuing.

### Developing the Sympy Client

Start of with running the `setup-dev-env` python script from the root directory.

```sh
python setup-dev-env.py
```

This creates a virtual environment named `.venv` installed with all required dependencies. Furthermore, it sets up a git pre-push hook, which runs the entire test suite, before pushing.

To use this development environment in Obsidian, go to the **Latex Math** settings in the vault this repo has been cloned to, and toggle the `Developer Mode` switch to on. Make sure to reload the vault after doing this.

The plugin should now use the python source files and the created virtual environment, instead of the auto installed `SympyClient` binary.

Any changes to the python source code requires reloading Obsidian to have any effect.

> [!CAUTION]
> If you are using VS Code as an ide, make sure to add `push` as an entry to `git.commandsToLog` in VS Code (user or workspace), if you want to see the output of the push hook if it fails.

### Developing the Obsidian Plugin

Start out by downloading the [`bundle-bin.zip`](https://github.com/zarstensen/obsidian-latex-math/releases/latest) file from the latest release, and extract it in the root directory.

Now run `npm -i` still in the root directory.

To start auto building the project on any source code change, run `npm run dev`.
To perform a one-time production ready build, run `npm run build`.

## License

See [LICENSE](LICENSE)
