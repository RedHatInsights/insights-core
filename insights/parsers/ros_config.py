"""
RosConfig - file ``/var/lib/pcp/config/pmlogger/config.ros``
============================================================
This class provides parsing for the files:
    ``/var/lib/pcp/config/pmlogger/config.ros``
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
    """
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

    Examples:
        >>> type(ros_input)
        <class 'insights.parsers.ros_config.RosConfig'>
        >>> ros_input.rules[0]['allow_disallow']
        'disallow'
        >>> ros_input.rules[0]['hostlist']
        ['.*']
        >>> ros_input.rules[0]['operationlist']
        ['all']
        >>> ros_input.specs[0].get('state')
        'mandatory on'
        >>> ros_input.specs[0].get('metrics')['mem.util.used']
        []
        >>> ros_input.specs[0].get('metrics')['kernel.all.cpu.user']
        []
        >>> ros_input.specs[0].get('logging_interval')
        'default'

    Attributes:
        data(list): All parsed options and log files are stored in this
            list.
        specs(list of dicts): List of the ROS specifications present in
            config.ros file.
        rules(list of dicts): List of access control rules applied for
            config.ros file.

    """
    def parse_content(self, content):
        self.data = parse("\n".join(content))
        self.specs = []
        specifications = self.data[0]
        for spec in specifications:
            state = spec[0][0]
            logging_interval = spec[0][1] if state.endswith('on') else None
            self.specs.append({'state': state, 'logging_interval': logging_interval, 'metrics': spec[1]})
        access_rules = self.data[1][1]
        self.rules = []
        for rule in access_rules:
            self.rules.append({'allow_disallow': rule[0], 'hostlist': rule[1], 'operationlist': rule[3]})
