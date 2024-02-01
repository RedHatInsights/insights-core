# -*- coding: utf-8 -*-
"""
Utilities for POSIX Bracket Expressions
=======================================

Per the Insights Client Configuration Guide, the "POSIX Bracket Expressions",
is also supported by the "file-content-redaction.yaml":
-  https://access.redhat.com/documentation/en-us/red_hat_insights/2023/html/client_configuration_guide_for_red_hat_insights/con-insights-client-data-redaction_insights-cg-data-redaction#proc-insights-client-cg-redact-pattern-keyword-yaml_insights-cg-data-redaction


This module provides a method to convert the "POSIX Bracket Expressions" to
ASCII Regular Expressions.


Reference:
- https://www.regular-expressions.info/posixbrackets.html
"""

POSIX_ASCII = {
    "[[:alnum:]]": "[a-zA-Z0-9]",
    "[[:alpha:]]": "[a-zA-Z]",
    "[[:ascii:]]": r"[\x00-\x7F]",
    "[[:blank:]]": r"[ \t]",
    "[[:cntrl:]]": r"[\x00-\x1F\x7F]",
    "[[:digit:]]": "[0-9]",
    "[[:graph:]]": r"[\x21-\x7E]",
    "[[:lower:]]": "[a-z]",
    "[[:print:]]": r"[\x20-\x7E]",
    "[[:punct:]]": r"""[!"\#$%&'()*+, \-./:;<=>?@\[ \\\]^_‘{|}~]""",
    "[[:space:]]": r"[ \t\r\n\v\f]",
    "[[:upper:]]": "[A-Z]",
    "[[:word:]]": "[A-Za-z0-9_]",
    "[[:xdigit:]]": "[A-Fa-f0-9]",
}


def replace_posix(text):
    """
    Replace the POSIX Bracket Expressions appear in the `text` to ASCII
    Regular Expressions.
    """
    new_text = text
    for old, new in POSIX_ASCII.items():
        new_text = new_text.replace(old, new)
    return new_text
