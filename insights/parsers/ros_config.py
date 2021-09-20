"""
RosConfig - file ``/var/lib/pcp/config/pmlogger/config.ros``
============================================================
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

from insights import parser, Parser
from insights.specs import Specs
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

AccessHeader = WS >> Literal("[access]") << WS
Allow = WS >> Literal("allow") << WS
Disallow = WS >> Literal("disallow") << WS
AllowDisallow = Allow | Disallow


EnquireOp = WS >> Literal("enquire") << WS
AdvisoryOp = WS >> Literal("advisory") << WS
MandatoryOp = WS >> Literal("mandatory") << WS
AllExceptOp = WS >> Literal("all except") << WS
AllOp = WS >> Literal("all") << WS

Colon = WS >> Literal(":") << WS

Host = String(string.ascii_letters + string.digits + ".*:\"")
HostList = WS >> Host.sep_by(Comma) << WS

Operation = EnquireOp | AdvisoryOp | MandatoryOp | AllExceptOp | AllOp
OperationList = WS >> Operation.sep_by(Comma | WS) << WS

Semicolon = WS >> Char(";") << WS

AccessRule = AllowDisallow + HostList + Colon + OperationList << Semicolon
AccessRules = Many(AccessRule)
AccessControl = AccessHeader + AccessRules
Doc = LogSpecs + Opt(AccessControl)
parse = Doc << EOF


@parser(Specs.ros_config)
class RosConfig(Parser):
    def parse_content(self, content):
        print(content)
        self.data = parse("\n".join(content))
