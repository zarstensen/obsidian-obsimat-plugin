<div align="center">
  
  <h1 align="center">
  Latex Math

  <a>[![GitHub Release](https://img.shields.io/github/v/release/zarstensen/obsidian-latex-math?style=flat-square&color=blue)](https://github.com/zarstensen/obsidian-latex-math/releases/latest) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/zarstensen/obsidian-latex-math/push.yml?style=flat-square&label=tests)
  </a>

  </h1>

</div>

**Latex Math** is an [Obsidian](https://obsidian.md/) plugin which adds mathematical evaluation of LaTeX math blocks to your notes, using [Sympy](https://www.sympy.org).

![demo](readme-assets/LatexMathDemo.gif)
*`Evaluate LaTeX expression` is bound to  `Alt + B` in the above demo. 
In general, all demo Gifs will make use of the [recommended hotkeys](#command-list). [^demo-gif-plugins]*
[^demo-gif-plugins]: All demo Gif's were produced with the [Obsidian Latex Suite](https://github.com/artisticat1/obsidian-latex-suite) plugin installed.

## Usage
Start out by placing the cursor inside any math block. Then execute the `Evaluate LaTeX expression` command (or any other command from the [command list](#command-list)). **Latex Math** will now parse the latex math, evaluate the equation, and insert the result at the end of the math block.

Take a look at the [command list](#command-list) a brief overview of what this plugin can do, or go look at the [features](#features) list, for a more in depth walkthrough of this plugin's advanced features.

If you are a linux user, make sure to read the [Linux](#linux) subsection of the [Installing](#installing) section to ensure this plugin runs correctly.

<!-- omit in toc -->
## Table of Contents

- [Usage](#usage)
- [Command List](#command-list)
- [Features](#features)
  - [Evaluate](#evaluate)
  - [Solve](#solve)
  - [Variable and Function Definitions](#variable-and-function-definitions)
  - [Unit Support](#unit-support)
  - [Symbol Assumptions](#symbol-assumptions)
  - [Convert To Sympy Code](#convert-to-sympy-code)
- [Installing](#installing)
  - [Linux](#linux)
- [Developing](#developing)
- [License](#license)

## Command List

Below is a table of all the commands this plugin provides, along with a brief description of what it does and optionally a recommended hotkey.

| Command                                     | Recommended Hotkey | Usage                                                                                                                      |
| ------------------------------------------- | :----------------: | -------------------------------------------------------------------------------------------------------------------------- |
| Evaluate LaTeX expression                   |     `Alt + B`      | Evaluate the right most expression (if in a relation) and simplify the result.                                             |
| Evalf LaTeX expression                      |     `Alt + F`      | Evaluate expression and output decimal numbers instead of fractions in the result.                                         |
| Expand LaTeX expression                     |     `Alt + E`      | Evaluate expression and expand the result as much as possible.                                                             |
| Factor LaTeX expression                     |                    | Evaluate expression and factorize the result as much as possible.                                                          |
| Partial fraction decompose LaTeX expression |                    | Evaluate expression and perform partial fraction decomposition on the result.                                              |
| Solve LaTeX expression                      |     `Alt + L`      | Solve a single equation or a system of equations. Output the result in a new math block below the current one.             |
| Convert units in LaTeX expression           |     `Alt + U`      | Try to convert the units in the right most expression to the user supplied one.                                            |
| Convert LaTeX expression to Sympy.          |                    | Convert entire expression to its equivalent Sympy code, and insert the result in a codeblock below the current math block. |

## Features

### Evaluate
### Solve
### Variable and Function Definitions
### Unit Support
### Symbol Assumptions
### Convert To Sympy Code


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

This section describes how to set up a development environment for **Latex Math**.
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
