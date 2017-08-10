
## Fava is YAML plus Jinja2 expressions

Fava (like Ansible Playbooks) is a combination of YAML (yaml.org) and Jinja2 Expressions (http://jinja.pocoo.org/docs/2.9/templates/#expressions).

The overall syntax is YAML, a Fava Rule is a YAML document.  A Fava Rule is loaded/deserialized
as a YAML document.

Certian parts of a Fava Rule can be Jinja2 Expressions (not any Jinja2 template, just Jinja2 Expressions).  In most of these parts the Jinja2 Expressions must be surrounded by double curly braces, {{ and }}, and those must be surrounded by double quotes to keep YAML happy.  Contrary to most parts, in the 'when' pair, the Jinja2 Expression must not be surrounded double curly braces.  This is confusing till you get used to it.  It is done this way to be as much like Ansible as possible without reusing Ansible, and still get YAML and Jinja2 to work together.

When a YAML document is loaded, we loose the order in which the individual key/value pairs of a dictionary are defined.  Generally this is not a problem, but there can be an issue for the 'vars' pair.  There may be a temptation to assume the variables in the 'vars' pair (see below) are evaluated and defined in the order specified in the file, they are not.  You can not use a variable defined in the vars pair in the same vars pair.  See below for more information, and for how to resolve issues related to this.




### The value of the 'rule' pair, the 'name'/'pydata'/'when' dictionary

A rule consists of a dictionary containing three manditory keys ('name', 'pydata', and 'when'), and one optional key ('vars').  The keys can be in any order.

```yaml
---
rule:
  name: "BROKEN_FLUX_CAPACITOR"
  pydata:
    kernel: "{{ Uname.kernel }}"
    fluxlevel: "{{ FluxCapacitor.level }}"
  when: FluxCapacitor.level < 42 and fluxbrand == "FarFutureInc"
  vars:
    fluxbrand: "{{ FluxCapacitor.brandname }}"
```


The 'name' (the value associated with the 'name' key) must be a string.  If the rule fires it will be passed to the 'make_result' function.  In this example the name of the rule is "BROKEN_FLUX_CAPACITOR".

The 'pydata' (the value ...) must be a dictionary.  If the rule fires, the key/value pairs will be passed as keyword arguments to the 'make_result' function.   The keys must be strings, the values may be arbitrarys YAML values, and may contain Jinja2 expressions.  In this example, the pydata consists of two pairs, 'kernel' and 'fluxlevel'.

The 'when' must be a Jinja2 expression.  It's value will be treated as a boolean, exactly as Python does.  This determines when the rule fires.

The 'vars' must be a dictionary.  The keys must be strings, the values may be arbitrarys YAML values, and may contain Jinja2 expressions.  If the values are Jinja2 expressions they will be evaluated before any other parts of the rule are evaluated.  The keys are then defined as local variables, usable in other parts of the rule.  In this example, there is only one var, 'fluxbrand'.  It is defined in the 'vars' pair, and used in the 'when' pair.



## The 'vars'/'in' dictionary

The 'vars'/'in' dictionary can be used anywhere a Jinja2 expression can be used, instead of the Jinja2 expression.  It allows you to define new variables that will be available within a Jinja2 expression.

Replace the Jinja2 expression with a dictionary with two keys, 'in' and 'vars'.  The 'vars' pair is like the top level 'vars' pair in a rule definition, but the variables defined in a
'vars'/'in' dictionary are only available within the assiciated 'in' pair.

The 'in' pair must be a Jinja2 expression (or another 'vars'/'in' dictionary).

When YAML documents are loaded, the order of the key/value pairs of a dictionary is lost; dictionary's don't have an order.

But sometimes you want to define a variable, and then use that variable to define another variable.

So in Python you might write:

```python
versions_to_check = [ 'bash-3.0-19.7.el4_7.1', 'bash-3.0-21.el4', 'bash-3.0-21.el4_8.1', AND SO ON ]
vulnerable = InstalledRpms.check_versions_installed(versions_to_check)
```

The 'versions_to_check' variable is defined first, and then used in the definition of 'vulnerable'.

But in YAML we don't know the order in which the vars in a single dictionary are defined.

The following WON'T work, because the variable 'version_to_check' is used in the same 'vars' pair
as it is defined.

```yaml
---
rule:
  name: "VULNERABLE_BASH_DETECTED"
  pydata:
    package: "{{ vulnerable['PACKAGES'][0] }}"
  when: vulnerable
  vars:
    versions_to_check:
      - bash-3.0-19.7.el4_7.1
      - bash-3.0-21.el4
      - bash-3.0-21.el4_8.1
      - AND SO ON
    vulnerable: '{{ InstalledRpms.check_versions_installed(versions_to_check) }}'
```




Instead, anytime you need to define a variable before it is used in the definition of
another variable, you need to use a 'vars'/'in' dictionary.



```yaml
---
rule:
  name: "VULNERABLE_BASH_DETECTED"
  pydata:
    package: "{{ vulnerable['PACKAGES'][0] }}"
  when: vulnerable
  vars:
    vulnerable:
      in: '{{ InstalledRpms.check_versions_installed(versions_to_check) }}'
      vars:
        versions_to_check:
          - bash-3.0-19.7.el4_7.1
          - bash-3.0-21.el4
          - bash-3.0-21.el4_8.1
          - AND SO ON
```

In this example there is a 'vars'/'in' dictionary nested with the toplevel 'vars' pair.  The toplevel
'vars' pair only defines 'vulnerable', and the nested 'vars'/'in' dictionary only defines the variable 'versions_to_check'.  The value of 'versions_to_check' is evaluated first, in this case it is an array of constant strings.  The variable 'versions_to_check' is only valid within the 'in' pair.
