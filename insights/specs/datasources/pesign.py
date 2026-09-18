"""
Custom datasources for ``pesign`` command outputs
"""

from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """Local specs used only by pesign datasources"""

    pesign_show_signature_shimx64_raw = simple_command("/usr/bin/pesign --show-signature --in=/boot/efi/EFI/redhat/shimx64.efi")


@datasource(LocalSpecs.pesign_show_signature_shimx64_raw)
def pesign_show_signature_shimx64(broker):
    """
    Filter pesign --show-signature output to remove email address lines.

    This datasource processes signing certificate information while excluding
    email addresses to prevent exposure of customer personal/internal emails
    from custom-signed binaries.

    Collects:
        - Signer's common name (e.g., "Microsoft Corporation UEFI CA 2011")
        - Signing time (e.g., "Jul 7, 2011")
        - Signature validation status (e.g., "There is a valid signature")
        - Cryptographic algorithms (e.g., "SHA256", "RSA pkcs1 padding")
        - Output delimiters

    Filters out:
        - Email address lines (privacy concern with custom-signed binaries)

    Arguments:
        broker: the broker object for the current session

    Returns:
        DatasourceProvider: Filtered pesign output without email lines

    Raises:
        SkipComponent: When no output after filtering email lines
    """
    raw_output = broker[LocalSpecs.pesign_show_signature_shimx64_raw]

    if not raw_output or not raw_output.content:
        raise SkipComponent("No pesign output available")

    # Filter out email address lines (case-insensitive)
    filtered_lines = []
    for line in raw_output.content:
        if "email address" not in line.lower():
            filtered_lines.append(line)

    if not filtered_lines:
        raise SkipComponent("No output after filtering email lines")

    content = "\n".join(filtered_lines)

    return DatasourceProvider(
        content=content,
        relative_path="insights_commands/pesign_show_signature_shimx64"
    )
