# Falafel

**Falafel** is the framework, common components and utilities, and mappers for Insights rules.

To get the project set up: 

```
virtualenv .
source bin/activate
pip install -e .[develop]
```

To run the tests: 

```
py.test
```

To generate docs:

```
cd docs/
make html
```

And they can be found under `docs/_build/html`.

## Configuration

Falafel also houses the centralized configuration module for the Insights
Engine and Insights Content Server.  This is to enable each project to use the
same file(s) and code module for configuration.  Falafel checks several locations for the configuration file, in this order:

- `$FALAFEL_HOME/falafel/defaults.yaml`
- `/etc/falafel.yaml`
- `$HOME/.local/falafel.yaml`
- `$PWD/.falafel.yaml`

Options from files read later will override options from files read earlier.

To see the layout of the file and the available options, please take a look at [defaults.yaml](falafel/defaults.yaml) in this repo.
