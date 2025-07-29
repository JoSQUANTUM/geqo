# Installation

The geqo package can be installed by the following steps.

## Clone the repository
```bash
git clone https://github.com/JoSQUANTUM/geqo.git
```
## Installation with pip
The following command installs geqo with all options. The options are explained in
the corresponding section below.

The command has to be executed in the geqo folder
obtained by the clone command in the previous step.
```bash
pip install -e .[dev,visualization,sympy,numpy]
```
## Installation with uv
The `pyproject.toml` is already configured to support uv.
```bash
uv sync --extra visualization --extra sympy
```

## Installation options
The geqo package supports the following optional installation extras:

 - `[dev]`: Includes development dependencies, such as testing and linting tools.
 - `[visualization]`: Includes functions for data visualization. This includes functions to plot quantum circuits in both LaTeX and Matplotlib, as well as create bar plots for measurement outcomes
 - `[sympy]`: Includes the SymPy library for symbolic mathematics. This enables the use of SymPy-based simulators for symbolic math operations.
 - `[numpy]`: Includes the NumPy library for numeric mathematics. This enables the use of NumPy-based simulators.

You can choose to install any combination of these extras by including them in the installation command, as shown in the examples above. For example, to install the core functionality and the visualization extras, you would use:

```bash
pip install -e .[dev,visualization]
```
or
```bash
uv add git+https://github.com/JoSQUANTUM/geqo.git --optional dev --optional visualization
```
This allows you to customize the installation to include only the features you need for your specific use case.
