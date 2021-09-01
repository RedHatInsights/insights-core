"""
RosConfig - file ``/var/lib/pcp/config/pmlogger/config.ros``
======================================================
This class provides parsing for the files:
    ``/var/lib/pcp/config/pmlogger/config.ros``

Sample input data is in the format::

log mandatory on default {
    mem.util.used
    mem.physmem
    kernel.all.cpu.user
    kernel.all.cpu.sys
    kernel.all.cpu.nice
    kernel.all.cpu.steal
    kernel.all.cpu.idle
    kernel.all.cpu.wait.total
    disk.all.total
    mem.util.cached
    mem.util.bufmem
    mem.util.free
}
[access]
disallow .* : all;
disallow :* : all;
allow local:* : enquire;
"""

from insights import Parser
from insights.parsr import EOF, EOL, Char, Literal, Many, OneLineComment, Opt, QuotedString, String, WSChar
import string


# https://man7.org/linux/man-pages/man1/pmlogger.1.html#CONFIGURATION_FILE_SYNTAX

WS = Many(WSChar | EOL | OneLineComment("#"))

Log = WS >> Literal("log") << WS
MandatoryOn = WS >> Literal("mandatory on") << WS
MandatoryOff = WS >> Literal("mandatory off") << WS
MandatoryMaybe = WS >> Literal("mandatory maybe") << WS
AdvisoryOn = WS >> Literal("advisory on") << WS
AdvisoryOff = WS >> Literal("advisory off") << WS

Once = WS >> Literal("once") << WS
Default = WS >> Literal("default") << WS
Every = WS >> Literal("every") << WS
UnsignedInt = String(string.digits).map(int)
TimeUnits = WS >> String(string.ascii_letters) << WS
Freq = Opt(Every) >> (UnsignedInt + TimeUnits)

Interval = Once | Default | Freq
OnStates = MandatoryOn | AdvisoryOn
OtherStates = MandatoryMaybe | MandatoryOff | AdvisoryOff

Preamble = Opt(Log) >> ((OnStates + Interval) | OtherStates)

LeftBrace = WS >> Char("{") << WS
RightBrace = WS >> Char("}") << WS
Comma = WS >> Char(",") << WS

Name = WS >> String(string.ascii_letters + string.digits + "-._") << WS

LeftBracket = WS >> Char('[') << WS
RightBracket = WS >> Char(']') << WS
InstanceName = QuotedString | UnsignedInt | Name
InstanceNames = LeftBracket >> InstanceName.sep_by(Comma | WS) << RightBracket
MetricSpec = Name + Opt(InstanceNames, default=[])

OneMetricSpec = MetricSpec.map(lambda s: [s])
MultipleMetricSpecs = LeftBrace >> MetricSpec.sep_by(Comma | WS) << RightBrace
MetricSpecs = (OneMetricSpec | MultipleMetricSpecs).map(dict)

LogSpec = Preamble + MetricSpecs

LogSpecs = Many(LogSpec)

parse = LogSpecs << EOF

AccessHeader = WS >> Literal("[access]") << WS
AllowRule = WS >> Literal("allow") << WS
DisallowRule = WS >> Literal("disallow") << WS
AllIPv4Addresses = WS >> Literal(".*") << WS
AllIPv6Addresses = WS >> Literal(":*") << WS
Enquire = WS >> Literal("enquire;") << WS
Advisory = WS >> Literal("advisory;") << WS
Mandatory = WS >> Literal("mandatory;") << WS
All = WS >> Literal("all;") << WS
Operation = Enquire | Advisory | Mandatory | All
Rule = AllowRule | DisallowRule + AllIPv4Addresses | AllIPv6Addresses + Enquire | Advisory | Mandatory | All
AccessRules = Many(Rule)
AccessControl = AccessHeader >> AccessRules
Doc = LogSpecs + Opt(AccessControl)
parse = Doc << EOF

#    10.  Following all of the logging specifications, there may be an
#         optional access control section, introduced by the literal
#         token [access].  Thereafter come access control rules that
#         allow or disallow operations from particular hosts or groups
#         of hosts.

#         The operations may be used to interrogate or control a
#         running pmlogger using pmlc(1) and fall into the following
#         classes:

#         enquire
#                interrogate the status of pmlogger and the metrics it
#                is logging
#         advisory
#                Change advisory logging.
#         mandatory
#                Change mandatory logging.
#         all    All of the above.

#         Access control rules are of the form ``allow hostlist :
#         operationlist ;'' and ``disallow hostlist : operationlist
#         ;''.

#         The hostlist follows the syntax and semantics for the access
#         control mechanisms used by PMCD and are fully documented in
#         pmcd(1).  An operationslist is a comma separated list of the
#         operations advisory, mandatory, enquire and all.

#         A missing [access] section allows all access and is
#         equivalent to allow * : all;.

#    The configuration (either from standard input or conffile) is
#    initially scanned by pmcpp(1) with the options -rs and -I
#    $PCP_VAR_DIR/config/pmlogger.  This extends the configuration
#    file syntax with include file processing (%include), a common
#    location to search for include files
#    ($PCP_VAR_DIR/config/pmlogger), macro definitions (%define),
#    macro expansion (%name and %{name}) and conditional inclusion of
#    lines (%ifdef name ... %else ... %endif and %ifndef name ...
#    %else ... %endif).


class RosConfig(Parser):
    def parse_content(self, content):
        self.data = parse("".join(content))
