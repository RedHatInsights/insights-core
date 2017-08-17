######################
Parsing and Exceptions
######################

When parsers parse input data there are three likely outcomes:

1. All data is parsed as expected
2. Data is unparsable due to errors in the data and nothing can be retrieved by
   the parser
3. Data is unparsable due to errors in the data but some useful information can
   be retrieved

   a. The useful information is from the parsable portion of the data
   b. The useful information is the fact that an error is present in the data

In each of these cases the parser should produce a response that is predictable
to the insights framework and should produce output that is deterministic in
terms of being processed by the rules.

Case 1 all Data is Parsed as Expected
=====================================

In case 1 the parser should store the information in a representation that is
consistent with the input data.  For example, generally, log data should be
stored in a python list, configuration data should be stored in a python
dictionary, and discrete data items should be stored as attributes or properties
of the parser.

Exceptions that are raised during parsing of the data are not anticipated by the
parser, and if raised should be presumed to be potential errors in either the
collection or the parsing of the data.  These need to be logged and investigated.

Case 2 Data is Unparsable
=========================

In case 2 the parser is expecting to receive parsable data and instead receives
data that is corrupt or not present as expected in a form that renders it impossible
for the parser to have a substantial level of confidence in the data. The parser
should provide logic to identify known issues in the data (such as error messages
indicating the data was not present) and attempt to catch via python mechanisms
issues that could reasonably be expected (conversion of a character to a number,
missing values, etc.).  When a parser makes the determination that the data is
not usable, then it should explicitly raise a
:py:class:`insights.parsers.ParseException` and provide as much
useful information as is possible to help the Insights team and parser developer
understand what happened.  If any exception is expected to be raised it should be
caught, and the :py:class:`insights.parsers.ParseException` raised in its place.
No data will be made available
to other parsers, combiners or rules in this case.  It will be as if the data was
not present in the input.

Case 3 Unparsable Data Provides Useful Information
==================================================

Case 3a Parsable Data having Some Errors
----------------------------------------

In case 3 there are two subcases.  The first subcase (a), is that the parser is able
to detect errors in the input data but is also able to successfully parse at least
some portion of the data.  In this subcase the parser must do the following:

1. Document how partial data will be handled in the module or class documentation
   so that a rule developer will understand how to determine what data is valid
   and what data is not valid.
2. Do not leave any attributes or properties in an unknown state, meaning that all
   attributes should be initialized to known values and if unparsable they should
   either be removed or be reset to known values as documented in step 1.
3. A specific attribute/property should be provided to allow rules to determine
   the quality of the data, rather than for example the rule having to check
   every attribute for None.

No exception will be explicitly raised by the parser in this case.

Case 3b Parsing Data to Find Errors (“Dirty Parser”)
----------------------------------------------------

In case 3 (b) the parser is specifically written to identify errors in the data.
This is the desired case for known errors/vulnerabilities.  For example for a known
issue with RPM data one parser will parse the data to return valid information from
the input data (“clean parser”), and a second parser will be responsible for identifying
any exceptions in the data (“dirty parser”). This allows rules that don’t care about the
exceptions to rely on only the first parser, and those rules will not run if valid data
is not present.  If the dirty parser identifies errors in the data then it will save
information regarding the errors for use by rules.  If no errors are found in the data
then the dirty parser will raise :py:class:`insights.parsers.SkipException` to indicate
to the engine that it should
be removed from the dependency hierarchy.

Other Exceptions from Parsers
=============================

Parsers should not explicitly raise any exceptions that would be raised in a rule-calling
context.  Problems that could be detected in parse_content should be detected there and
not pushed out to the rules.  Parser methods and functions should however be prepared
to handle common exceptional cases (such as an invalid argument type) via standard python
exception handling processes.  That is, try something and handle the exception where you
can.  Parsers probably shouldn't eagerly check types since there are many cases where strict
types aren’t important and such checks may limit expressiveness and flexibility.

Parsers should not use the assert statement in place of error handling code.
Asserts are for debugging purposes only.

Exception Recognition by the Insights Engine
============================================

Exceptions that are raised by parsers and combiners will be collected by the engine in
order to determine whether to remove the parser/combiner from the dependency hierarchy,
for data metrics, and to help identify issues with the parsing code or with the data.
Specific use of :py:class:`insights.parsers.ParseException` and
:py:class:`insights.parsers.SkipException` will
make it much easier for the engine
to identify and quickly deal with known conditions versus unanticipated conditions
(i.e., other exceptions being raised) which could indicate errors in the parsing code,
errors in data collection, or data errors.