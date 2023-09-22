"""
Custom datasource for gathering a list of encrypted LUKS block devices and their properties.
"""
import re

from insights.components.cryptsetup import HasCryptsetupWithTokens, HasCryptsetupWithoutTokens
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, foreach_execute
from insights.parsers.blkid import BlockIDInfo
from insights.specs import Specs


@datasource(BlockIDInfo, HostContext)
def luks_block_devices(broker):
    """
    This datasource provides a list of LUKS encrypted device.

    Sample data returned::

        ['/dev/sda', '/dev/nvme0n1p3']

    Returns:
        list: List of the LUKS encrypted block devices.

    Raises:
        SkipComponent: When there is not any LUKS encrypted block device on the
        system.
    """

    block_id = broker[BlockIDInfo]
    if block_id:
        devices = block_id.filter_by_type("crypto_LUKS")
        if devices:
            return sorted(map(lambda x: x["NAME"], devices))

    raise SkipComponent


class LocalSpecs(Specs):
    """ Local specs used only by LUKS_data_sources datasource. """
    cryptsetup_luks_dump_token_commands = foreach_execute(luks_block_devices, "/usr/sbin/cryptsetup luksDump --disable-external-tokens %s", deps=[luks_block_devices, HasCryptsetupWithTokens])
    cryptsetup_luks_dump_commands = foreach_execute(luks_block_devices, "/usr/sbin/cryptsetup luksDump %s", deps=[luks_block_devices, HasCryptsetupWithoutTokens])


def line_indentation(line):
    """
    Compute line indentation level

    Arguments:
        line(str): The whole line

    Returns:
        int: the number of spaces the line is indentated by
    """
    line = line.replace("\t", " " * 8)
    return len(line) - len(line.lstrip())


def filter_token_lines(lines):
    """
    Filter out token descriptions to keep just the Keyslot filed

    Arguments:
        lines(list): List of lines of the luksDump output

    Returns:
        list: The original lines, except the tokens section only contains only token name and associated keyslot
    """
    in_tokens = False
    remove_indices = []

    for i, line in enumerate(lines):
        if line == "Tokens:":
            in_tokens = True
            continue

        if in_tokens and line_indentation(line) == 0:
            in_tokens = False

        if not in_tokens or line_indentation(line) == 2 or line.startswith("\tKeyslot:"):
            continue

        remove_indices.append(i)

    return [i for j, i in enumerate(lines) if j not in remove_indices]


@datasource(HostContext, [LocalSpecs.cryptsetup_luks_dump_token_commands, LocalSpecs.cryptsetup_luks_dump_commands])
def luks_data_sources(broker):
    """
    This datasource provides the output of 'cryptsetup luksDump' command for
    every LUKS encrypted device on the system. The digest and salt fields are
    filtered out as they can be potentially sensitive.

    Returns:
        list: List of outputs of the cryptsetup luksDump command.

    Raises:
        SkipComponent: When there is not any LUKS encrypted block device on the
        system.
    """
    datasources = []

    commands = []
    if LocalSpecs.cryptsetup_luks_dump_token_commands in broker:
        commands.extend(broker[LocalSpecs.cryptsetup_luks_dump_token_commands])
    if LocalSpecs.cryptsetup_luks_dump_commands in broker:
        commands.extend(broker[LocalSpecs.cryptsetup_luks_dump_commands])

    for command in commands:
        lines_without_tokens = filter_token_lines(command.content)

        regex = re.compile(r'[\t ]*(MK digest:|MK salt:|Salt:|Digest:)(\s*([a-z0-9][a-z0-9] ){16}\n)*(\s*([a-z0-9][a-z0-9] )+\n)?', flags=re.IGNORECASE)
        filtered_content = regex.sub("", "\n".join(lines_without_tokens) + "\n")

        datasources.append(
            DatasourceProvider(content=filtered_content, relative_path="insights_commands/" + command.cmd.replace("/", ".").replace(" ", "_"))
        )

    if datasources:
        return datasources

    raise SkipComponent
