<!-- omit in toc -->
# LaTeX Math Syntax

This document aims to provide an overview of the latex parsing capabilities of this plugin. As a general note, the parser was designed with standard latex notation in mind, so as long as no complex formatting or esoteric math functions are used, it should be pretty straight forward to write latex formulas parsable by this plugin.

Whilst this document should provide a good overview of the parser, one can always look at the [grammar files](sympy-client/sympy_client/grammar/latex_math_grammar.lark) for the concrete implementation.

<!-- omit in toc -->
## Table of Contents

- [Expression Structure](#expression-structure)
- [Symbols](#symbols)
- [Mathematical Functions](#mathematical-functions)
- [Mathematical Constants](#mathematical-constants)
- [Units and Physical Constants](#units-and-physical-constants)
  - [Supported Units](#supported-units)
  - [Supported Physical Constants](#supported-physical-constants)

## Expression Structure

The **LaTeX Math** parser is able to parse most mathematical expressions and optionally relations (*e.g.* `>`, `<`, `=`) between expressions.

An expression is any series of mathematical terms separated by `+` or `-` signs.
Terms consists of a series of factors separated by a multiplication sign (`*`, `\cdot`, `\times`) or a division sign (`/`), where a factor is one of the following:

<!-- no toc -->
- Number
- [Symbol](#symbols)
- [Unit / Constant](#units-and-physical-constants)
- Matrix
- Exponentiation
- [Funtion](#mathematical-functions)
- Expression delimited by `()`, `{}` or `[]`

If no multiplication or division sign is present, multiplication is implicitly assumed.

The parser also supports systems of equations. Notate these by placing a series of equations, separated by latex newlines (`\\\\`), inside a `cases` or `align` environment.

## Symbols

The parser understands various ways of notating symbols. The below table gives some examples for supported notation concepts.

| Type      | LaTeX String                                                       |
| :-------- | :----------------------------------------------------------------- |
| greek     | `\alpha` / `\beta` / `\gamma` / ...                                |
| latin     | `a` / `x` / `symbol` / ...                                         |
| formatted | `\mathrm{x}` / `\pmb{vector}` / `\mathit{whitespace symbol}` / ... |
| indexed   | `x_y` / `\alpha_\gamma` / `\pmb{M}_{1;2}` / ...                    |

Note that Latin symbols spelling out Greek letters will be converted to Greek symbols upon evaluation e.g. the Latin symbol `alpha` will be output as `\alpha` upon evaluation.
This is a side effect of how Sympy handles symbols internally.

## Mathematical Functions

Below is a table of all supported mathematical functions supported by the parser, this list may grow overtime as this project develops.
Note that a *mathematical function* also encompasses concepts not normally thought of as a function, e.g. `\frac` is considered part of this table whilst it may not intuitively be thought of as a function.

| Description                | LaTeX String                                                                           |
| :------------------------- | :------------------------------------------------------------------------------------- |
| sine                       | `\sin`                                                                                 |
| cosine                     | `\cos`                                                                                 |
| tangent                    | `\tan`                                                                                 |
| secant                     | `\sec`                                                                                 |
| cosecant                   | `\csc`                                                                                 |
| cotangent                  | `\cot`                                                                                 |
| arcus sine                 | `\arcsin`                                                                              |
| arcus cosine               | `\arccos`                                                                              |
| arcus tan                  | `\arctan`                                                                              |
| arcus secant               | `\arcsec`                                                                              |
| arcus cosecant             | `\arccsc`                                                                              |
| arcus cotangent            | `\arccot`                                                                              |
| hyperbolic sine            | `\sinh`                                                                                |
| hyperbolic cosine          | `\cosh`                                                                                |
| hyperbolic tangent         | `\tanh`                                                                                |
| hyperbolic secant          | `\mathrm{sech}` / `\operatorname{sech}`                                                |
| hyperbolic cosecant        | `\mathrm{csch}` / `\operatorname{csch}`                                                |
| hyperbolic cotangent       | `\coth`                                                                                |
| hyperbolic arcus sine      | `\mathrm{arsinh}` / `\operatorname{arsinh}`                                            |
| hyperbolic arcus cosine    | `\mathrm{arcosh}` / `\operatorname{arcosh}`                                            |
| hyperbolic arcus tangent   | `\mathrm{artanh}` / `\operatorname{artanh}`                                            |
| hyperbolic arcus secant    | `\mathrm{arsech}` / `\operatorname{arsech}`                                            |
| hyperbolic arcus cosecant  | `\mathrm{arcsch}` / `\operatorname{arcsch}`                                            |
| hyperbolic arcus cotangent | `\mathrm{arcoth}` / `\operatorname{arcoth}`                                            |
| log                        | `\log[base]?` / `\ln` / `\lg`                                                          |
| real part                  | `\Re .` / `\mathrm{Re} .`                                                              |
| imaginary part             | `\Im .` / `\mathrm{Im} .`                                                              |
| argument                   | `\arg .`                                                                               |
| sign                       | `\mathrm{sgn} .` / `\operatorname{sgn} .`                                              |
| exponential                | `\exp .`                                                                               |
| factorial                  | `. !`                                                                                  |
| percent                    | `. \%`                                                                                 |
| permille                   | `. \textperthousand`                                                                   |
| limit                      | `\lim_{ . \to . }`                                                                     |
| sum                        | `\sum_{ . = . }^.`                                                                     |
| product                    | `\prod_{ . = . }^.`                                                                    |
| minimum                    | `\min(. , . , ..., . )`                                                                |
| maximum                    | `\max( . , . , ..., . )`                                                               |
| standard inner product     | `\langle . \| . \rangle`                                                               |
| numeric value              | `\| . \|`                                                                              |
| norm                       | `\Vert . \Vert` / `\|\| . \|\|`                                                        |
| floor                      | `\lfloor . \rfloor`                                                                    |
| ceiling                    | `\lceil . \rceil`                                                                      |
| root                       | `\sqrt[index]?`                                                                        |
| conjugate                  | `\bar` / `\overline`                                                                   |
| fraction                   | `\frac{ . }{ . }`                                                                      |
| binomial                   | `\binom{ . }{ . }`                                                                     |
| partial derivative         | `\frac{ d ... }{ d . d . ... }` / `\frac{ \partial }{ \partial . \partial . ... } ...` |
| prime derivative           | `(...)'''...`                                                                          |
| integral                   | `\int ... d .` / `\int_a^b ... d .`                                                    |
| determinant                | `\det .` / `\begin{vmatrix} ... \end{vmatrix}`                                         |
| trace                      | `\mathrm{trace} .` / `\operatorname{trace} .`                                          |
| adjugate                   | `\mathrm{adjugate} .` / `\operatorname{adjugate} .`                                    |
| reduced row echelon form   | `\mathrm{rref} .` / `\operatorname{rref} .`                                            |
| gradient                   | `\nabla ...`                                                                           |
| hessian                    | `\mathbf{H} ...`                                                                       |
| Jacobian                   | `\mathbf{J} ...`                                                                       |
| permutations               | `P( ... ,  ... )` / `{[_^] ... P_ ... }`                                               |
| combinations               | `C( ... ,  ... )` / `{[_^] ... C_ ... }`                                               |
| derangements               | `D( ... )` / `{ ! ... }`                                                               |
| greatest common divisor    | `\gcd( ... ,  ... )`                                                                   |
| least common multiple      | `\mathrm{lcm}( ... ,  ... )` / `\operatorname{lcm}( ... ,  ... )`                      |
| modulo                     | `. \mod .`                                                                             |

## Mathematical Constants

The number of mathematical constants has intentionally been kept sparse, as their latex strings cannot be used as symbols. Furthermore, a symbol definition can always be made to emulate a constant in the current notebook.

Below is a table of all the mathematical constants the parser supports.

| Name           | LaTeX String |
| :------------- | :----------- |
| pi             | `\pi`        |
| euler          | `e`          |
| imaginary unit | `i`          |
| infinity       | `\infty`     |

## Units and Physical Constants

Units and physical constants are specified by surrounding them with braces `{}`. This, in general, is prioritized lower than braces being used as parentheses, or as argument delimiters to functions. This means that `\sin{km}` for example is parsed as sine to the symbol *km*, and not the unit *kilometer*. To get the unit, it would have to be written like the following `\sin{{km}}`.

The only case where this is not true, is for the base factor in exponentiations. For example here `{km}^2` is seen as kilometers squared.

The following sections provide an overview of all the supported units of the parser.

### Supported Units

| Unit                     | Aliases                           |
| :----------------------- | :-------------------------------- |
| ampere                   | amperes<br/>A                     |
| angstrom                 | angstroms                         |
| angular_mil              | mil<br/>angular_mils              |
| anomalistic_year         | anomalistic_years                 |
| astronomical_unit        | astronomical_units<br/>AU<br/>au  |
| atmosphere               | atmospheres<br/>atm               |
| bar                      | bars                              |
| becquerel                | Bq                                |
| bit                      | bits                              |
| byte                     | bytes                             |
| candela                  | cd<br/>candelas                   |
| centiliter               | cL<br/>cl<br/>centiliters         |
| common_year              | common_years                      |
| coulomb                  | C<br/>coulombs                    |
| curie                    | Ci                                |
| day                      | days                              |
| debye                    |                                   |
| deciliter                | dl<br/>deciliters<br/>dL          |
| degree                   | deg<br/>degrees                   |
| dioptre                  | optical_power<br/>D<br/>diopter   |
| draconic_year            | draconic_years                    |
| dyne                     |                                   |
| electron_rest_mass       | me                                |
| erg                      |                                   |
| farad                    | farads<br/>F                      |
| foot                     | ft<br/>feet                       |
| full_moon_cycle          | full_moon_cycles                  |
| gauss                    |                                   |
| gaussian_year            | gaussian_years                    |
| gram                     | g<br/>grams                       |
| gray                     | Gy                                |
| hectare                  | ha                                |
| henry                    | H<br/>henrys                      |
| hertz                    | Hz<br/>hz                         |
| hour                     | hours<br/>h                       |
| inch                     | inches                            |
| joule                    | J<br/>joules                      |
| julian_year              | julian_years                      |
| katal                    | kat                               |
| kelvin                   | kelvins<br/>K                     |
| lightyear                | lightyears<br/>ly                 |
| liter                    | liters<br/>l<br/>L                |
| lux                      | lx                                |
| maxwell                  |                                   |
| meter                    | meters<br/>m                      |
| mile                     | mi<br/>miles                      |
| milli_mass_unit          | mmu<br/>mmus                      |
| milliliter               | milliliters<br/>ml<br/>mL         |
| minute                   | minutes<br/>min                   |
| mmHg                     | torr                              |
| mole                     | mol<br/>moles                     |
| nautical_mile            | nmi<br/>nautical_miles            |
| newton                   | N<br/>newtons                     |
| oersted                  |                                   |
| ohm                      | ohms                              |
| pascal                   | Pa<br/>pascals<br/>pa             |
| percent                  | percents                          |
| permille                 |                                   |
| planck_acceleration      | a_P                               |
| planck_angular_frequency | omega_P                           |
| planck_area              |                                   |
| planck_charge            | q_P                               |
| planck_current           | I_P                               |
| planck_density           | rho_P                             |
| planck_energy            | E_P                               |
| planck_energy_density    | rho^E_P                           |
| planck_force             | F_P                               |
| planck_impedance         | Z_P                               |
| planck_intensity         |                                   |
| planck_length            | l_P                               |
| planck_mass              | m_P                               |
| planck_momentum          |                                   |
| planck_power             | P_P                               |
| planck_pressure          | p_P                               |
| planck_temperature       | T_P                               |
| planck_time              | t_P                               |
| planck_voltage           | V_P                               |
| planck_volume            |                                   |
| pound                    | pounds                            |
| psi                      |                                   |
| quart                    | quarts                            |
| radian                   | rad<br/>radians                   |
| rutherford               | Rd                                |
| second                   | s<br/>seconds                     |
| sidereal_year            | sidereal_years                    |
| siemens                  | mho<br/>mhos<br/>S                |
| statampere               |                                   |
| statcoulomb              | statC<br/>franklin                |
| statvolt                 |                                   |
| steradian                | sr<br/>steradians                 |
| tesla                    | T<br/>teslas                      |
| tropical_year            | year<br/>years<br/>tropical_years |
| volt                     | volts<br/>v<br/>V                 |
| watt                     | W<br/>watts                       |
| weber                    | Wb<br/>wb<br/>webers              |
| yard                     | yd<br/>yards                      |

### Supported Physical Constants

| Constant                    | Aliases                                               |
| :-------------------------- | :---------------------------------------------------- |
| acceleration_due_to_gravity | gee<br/>gees                                          |
| atomic_mass_constant        | amu<br/>atomic_mass_unit<br/>dalton<br/>Da<br/>amus   |
| avogadro_constant           | avogadro                                              |
| avogadro_number             |                                                       |
| boltzmann_constant          | boltzmann                                             |
| coulomb_constant            | electric_force_constant<br/>k_e<br/>coulombs_constant |
| electronvolt                | electronvolts<br/>eV                                  |
| elementary_charge           | e                                                     |
| faraday_constant            |                                                       |
| gravitational_constant      | G                                                     |
| hbar                        |                                                       |
| josephson_constant          | K_j                                                   |
| magnetic_constant           | vacuum_permeability<br/>u0                            |
| molar_gas_constant          | R                                                     |
| planck                      |                                                       |
| speed_of_light              | c                                                     |
| stefan_boltzmann_constant   | stefan                                                |
| vacuum_impedance            | Z_0<br/>Z0                                            |
| vacuum_permittivity         | e0<br/>electric_constant                              |
| von_klitzing_constant       | R_k                                                   |
