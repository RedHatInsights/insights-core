from falafel.contrib import pyparsing as p
from .. import Mapper, LogFileOutput, mapper


# For "Status of node" section's erlang block prasing only, could not cover
# sections "Cluster status of node" & "Application environment of node".
def erlblock_parser():
    COMMA = p.Suppress(',')
    LBRACE, RBRACE = map(p.Suppress, "{}")
    LBRACKET, RBRACKET = map(p.Suppress, "[]")

    key = p.Word(p.alphas + '_')
    value_tnum = p.Word(p.nums + '.')
    value_tword = p.Word(p.alphanums + '/"-[]:.()')
    value_tstr = p.OneOrMore(value_tword)
    value_tdoustrs = value_tstr + COMMA + value_tstr
    value_tnumstr = value_tnum + value_tstr
    value = value_tdoustrs | value_tnumstr | value_tstr | value_tnum

    attr = LBRACE + p.Group(key + COMMA + value) + RBRACE
    attr_list = p.Dict(p.ZeroOrMore(attr + COMMA) + p.ZeroOrMore(attr))
    block = LBRACKET + attr_list + RBRACKET

    value_plus = block | attr | value
    attr = LBRACE + p.Group(key + COMMA + value_plus) + RBRACE
    attr_list = p.Dict(p.OneOrMore(attr + COMMA) + p.OneOrMore(attr))
    block = LBRACKET + attr_list + RBRACKET

    return block


# For "Permissions on" section parsing only
def perm_parser():
    COLON = p.Suppress(":")
    WHITE = p.Suppress(p.White())

    vhostname = p.Word(p.alphanums + '_-/')
    username = p.Word(p.alphanums + '_-')
    conf = p.Word(p.alphanums + '.*#')

    perm_vhost = p.Suppress("Permissions on") + vhostname + COLON
    ucwr = p.Suppress("user" + WHITE + "configure" + WHITE + "write" + WHITE + "read")
    perm_line = p.Group(username + 3 * (WHITE + conf))

    perm_con = p.Optional(ucwr + p.Dict(p.OneOrMore(perm_line)))
    perm_block = p.Group(perm_vhost + perm_con)
    perm = p.Dict(p.OneOrMore(perm_block))

    return perm


# Parsing "Status of node" & "Permissions on" sections, skip the other content.
def create_parser():
    DOTS = p.Suppress("...")
    NSTAT_PREFIX = p.Suppress("Status of node")
    PERM_PREFIX = p.Suppress("Permissions on")
    nodename = p.Word(p.alphanums + '\'_-@')

    block_nstat = p.Group(NSTAT_PREFIX + nodename + DOTS + erlblock_parser())
    nstat = p.Dict(p.OneOrMore(p.Suppress(p.SkipTo(NSTAT_PREFIX)) +
            block_nstat)).setResultsName('nstat')
    perm = p.Suppress(p.SkipTo(PERM_PREFIX)) + perm_parser().setResultsName('perm')

    return nstat + perm


@mapper("rabbitmq_report")
class RabbitMQReport(Mapper):

    def parse_content(self, content):
        """
        Support StatusOfNode and Permissions Sections only
        IF encounter any Error in parsing, self.result = None;
        Otherwise, parsing result stored in self.result as Dict.

        self.result =
        {'nstat': {
            "'rabbit@overcloud-controller-0'": {
                'file_descriptors': {
                    'total_used': '967',
                    'sockets_used': '965',
                    'total_limit': '3996',
                    'sockets_limit': '3594'},
                'uptime': '3075485',
                'pid': '6005',
                'disk_free': '259739344896',
                'disk_free_limit': '50000000'},
            "'rabbit@overcloud-controller-1'": {
                'file_descriptors': {
                    'total_used': '853',
                    'sockets_used': '851',
                    'total_limit': '3996',
                    'sockets_limit': '3594'},
                'uptime': '3075482',
                'pid': '9304',
                'disk_free': '260561866752',
                'disk_free_limit': '50000000'}}
         'perm': {
            '/': {
                'redhat1': ['redhat.*', '.*', '.*'],
                'guest': ['.*', '.*', '.*'],
                'redhat':['redhat.*', '.*', '.*']},
            'test_vhost': ''}}

        fd_total_limit can be get by:
            self.result.get("nstat").get(NODENAME).\
                    get("file_descriptors").get("total_limit")

        permissions can be get by:
            self.result.get("perm")
        """
        try:
            self.result = create_parser().parseString("\n".join(content)).asDict()
        except p.ParseException:
            self.result = None


@mapper("rabbitmq_report", ["total_limit"])
def fd_total_limit(context):
    """Deprecated, do not use."""
    for line in context.content:
        if "file_descriptors" in line and "total_limit" in line:
            line_splits = line.replace("}", "").split(",")
            if len(line_splits) > 3:
                return int(line_splits[2])


@mapper("rabbitmq_report", ["total_limit"])
class RabbitMQFileDescriptors(Mapper):

    NO_VALUE = -1

    def parse_content(self, content):
        self.fd_total_limit = self.NO_VALUE
        for line in content:
            if "file_descriptors" in line and "total_limit" in line:
                line_splits = line.replace("}", "").split(",")
                if len(line_splits) > 3:
                    self.fd_total_limit = int(line_splits[2])
                    break


@mapper("rabbitmq_users")
class RabbitMQUsers(Mapper):

    def parse_content(self, content):
        users_dict = {}
        for line in content[1:-1]:
            line_splits = line.split()
            if len(line_splits) > 1:
                users_dict[line_splits[0]] = line_splits[1][1:-1]
        self.data = users_dict


@mapper("rabbitmq_startup_log")
class RabbitMQStartupLog(LogFileOutput):
    pass
