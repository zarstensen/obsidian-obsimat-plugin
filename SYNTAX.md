# Latex Math Syntax

This document aims to provide an overview of the latex parsing capabilites of this plugin. As a general note, the parser was designed with standard latex notation in mind, so as long as no complex formatting or esoteric math functions are used, it should be pretty straight forward to write latex code parsable by this plugin.

Whilst this document should provide a good overview of the parser, one can always look at the grammar files for the concrete implementation.

## Table of Contents

- [Table of Contents](#table-of-contents)
- [Expression Structure](#expression-structure)
- [Symbols](#symbols)
- [Mathematical Functions](#mathematical-functions)
- [Mathematical Constants](#mathematical-constants)
- [Units and Physical Constants](#units-and-physical-constants)
  - [Supported Units](#supported-units)
  - [Supported Physical Constants](#supported-physical-constants)


## Expression Structure

## Symbols

| Type  | Latex String             |
| :---- | :----------------------- |
| greek | `\alpha` / `\beta` / `\gamma` / ... |
| latin      | `a` / `x` / `symbol` / ... |
| formatted      | `\mathrm{x}` / `\pmb{vector}` / `\mathit{whitespace symbol}` / ... |
| indexed      | `x_y` / `\alpha_\gamma` / `\pmb{M}_{1;2}` / ... |

## Mathematical Functions

| Description              | Latex String                                                                           |
| :----------------------- | :------------------------------------------------------------------------------------- |
| sinus                    | `\sin`                                                                                 |
| cosinus                  | `\cos`                                                                                 |
| tangent                  | `\tan`                                                                                 |
| secant                   | `\sec`                                                                                 |
| cosecant                 | `\csc`                                                                                 |
| cotangent                | `\cot`                                                                                 |
| arcus sinus              | `\arcsin`                                                                              |
| arcus cosinus            | `\arccos`                                                                              |
| arcus tan                | `\arctan`                                                                              |
| arcus secant             | `\arcsec`                                                                              |
| arcus cosecant           | `\arccsc`                                                                              |
| arcus cotangent          | `\arccot`                                                                              |
| hyperbolic sinus         | `\sinh`                                                                                |
| hyperbolic cosinus       | `\cosh`                                                                                |
| hyperbolic tangent       | `\tanh`                                                                                |
| hyperbolic arcus sinus   | `\arsinh`                                                                              |
| hyperbolic arcus cosinus | `\arcosh`                                                                              |
| hyperbolic arcus tangent | `\artanh`                                                                              |
| log                      | `\log[base]?` / `\ln` / `\lg`                                                          |
| exponential              | `\exp`                                                                                 |
| factorial                | `!`                                                                                    |
| limit                    | `\lim_{ . \to . }`                                                                     |
| sum                      | `\sum_{ . = . }^.`                                                                     |
| product                  | `\prod_{ . = . }^.`                                                                    |
| minimum                  | `\min(. , . , ..., . )`                                                                |
| maximum                  | `\max( . , . , ..., . )`                                                               |
| standard inner product   | `\langle . \| . \rangle `                                                              |
| numeric value            | `\| . \|`                                                                              |
| norm                     | `\Vert . \Vert` / `\|\| . \|\|`                                                        |
| floor                    | `\lfloor . \rfloor`                                                                    |
| ceil                     | `\lceil . \rceil`                                                                      |
| root                     | `\sqrt[index]?`                                                                        |
| conjugate                | `\bar` / `\overline`                                                                   |
| fraction                 | `\frac{ . }{ . }`                                                                      |
| binomial                 | `\binom{ . }{ . }`                                                                     |
| partial derivative       | `\frac{ d ... }{ d . d . ... }` / `\frac{ \partial }{ \partial . \partial . ... } ...` |
| prime derivative         | `(...)'''...`                                                                          |
| integral                 | `\int ... d .` / `\int_a^b ... d .`                                                    |
| determinant              | `\det .` / `\begin{vmatrix} ... \end{vmatrix}`                                         |
| trace                    | `\mathrm{trace} .` / `\operatorname{trace} .`                                          |
| adjugate                 | `\mathrm{adjugate} .` / `\operatorname{adjugate} .`                                    |
| reduced row echelon form | `\mathrm{rref} .` / `\operatorname{rref} .`                                            |
| gradient                 | `\nabla ...`                                                                           |
| hessian                  | `\mathbf{H} ...`                                                                       |
| jacobian                 | `\mathbf{J} ...`                                                                       |

## Mathematical Constants

The number of mathematical constants has intentionally been kept quite low, as their latex strings cannot be used as symbols. Furthermore, a symbol definition can always be made to emulate a constant in the current notebook.

Below is a table of all the mathematical constants the parser supports.


| Name           | Latex String |
| :------------- | :----------- |
| pi             | `\pi`        |
| euler          | `e`          |
| imaginary unit | `i`          |
| infinity       | `\infty`     |

## Units and Physical Constants

Units and physical constants are specified by surrounding them with braces `{}`. This, in general, is prioritized lower than braces being used as parentheses, or as argument delimiters to functions. This means that `\sin{km}` for example is parsed as sinus to the symbol km, and not the unit km. To get the unit km, it would have to be written like the following `\sin{{km}}`.

The only case were this is not true, is for the base factor in exponentiations. For example here `{km}^2` is seen as kilometers squared. 

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
