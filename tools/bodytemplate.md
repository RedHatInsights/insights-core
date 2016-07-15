##What's new
The following changes to what information is collected have been made
since *DATE*.

{% if doc.added_files or doc.added_commands %}
###Additions
{% if doc.added_files %}
#### Files
{% for item in doc.added_files %}
- {{ item }}
{% endfor %}
{% endif %}
{% if doc.added_commands %}
#### Commands
{% for item in doc.added_commands %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}
{% if doc.removed_files and doc.removed_commands %}
###Removals
{% if doc.removed_files %}
#### Files
{% for item in removed_files %}
- {{ item }}
{% endfor %}
{% endif %}
{% if doc.removed_commands %}
#### Commands
{% for item in removed_commands %}
- {{ item }}
{% endfor %}
{% endif %}
{% endif %}

## Overview
[Red Hat Insights](https://access.redhat.com/insights/info/) must collect some system information for analysis. The information listed in this document is the minimum subset required to determine if a system is affected by any of the issues known to the Red Hat Insights engine.

In the interest of full transparency, the information collected by the client is listed below in subheadings. The actual configuration file used by the Red Hat Insights client is [here](https://api.access.redhat.com/r/insights/v1/static/uploader.json).

## Files collected in their entirety
{% for item in doc.all_files %}
- {{ item }}
{% endfor %}

## Patterns collected from files
For the files listed below, only the lines containing the keyword patterns listed below the file are collected.

{% for name, patterns in doc.file_patterns.iteritems() %}
- {{ name }}
    {% for pattern in patterns %}
    - *{{ pattern }}*
    {% endfor %}
{% endfor %}

## Commands collected in their entirety

{% for item in doc.all_commands %}
- {{ item }}
{% endfor %}

## Patterns collected from commands
For the commands listed below, only the lines containing the keyword patterns listed below the command are collected.

{% for name, patterns in doc.command_patterns.iteritems() %}
- {{ name }}
    {% for pattern in patterns %}
    - *{{ pattern }}*
    {% endfor %}
{% endfor %}

## Excluding data
For information on how to exclude metadata from being sent from the Insights client, see [Opt out of sending metadata from Red Hat Insights client](https://access.redhat.com/articles/2025273).
