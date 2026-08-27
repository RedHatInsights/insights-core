"""
Custom datasource for gathering the signature certificate chain details of
the UEFI shim boot loader.
"""

import os

from tempfile import NamedTemporaryFile

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT

SHIM_PATH = "/boot/efi/EFI/redhat/shimx64.efi"
CERT_FIELDS = ("Subject:", "Issuer:", "Not Before", "Not After")


@datasource(HostContext)
def shim_certs(broker):
    """
    This datasource gathers the certificate chain (Subject, Issuer and
    validity dates) of every signature embedded in the UEFI shim bootloader.

    It reproduces the output generated for the following shell script::

        COUNT=$(pesign --show-signature --in=/boot/efi/EFI/redhat/shimx64.efi | grep -c "certificate address")
        for ((i=0; i<COUNT; i++)); do
            echo "=== signum $i ==="
            pesign -i /boot/efi/EFI/redhat/shimx64.efi -u $i --force --export-signature /tmp/sig${i}.p7
            openssl pkcs7 -inform DER -print_certs -text -in /tmp/sig${i}.p7 | grep -E "Subject:|Issuer:|Not Before|Not After"
        done

    Returns:
        DatasourceProvider: Return certificate details for signatures present in
        the shim bootloader that are successfully exported and processed,
        separated by line "=== signum N ===". Individual signatures may be
        omitted if exporting or processing fails.

    Raises:
        SkipComponent: Raises SkipComponent in following cases
        - When the shim binary is not present
        - When the `pesign`/`openssl` commands fail unexpectedly
        - When no signature is found.
    """
    ctx = broker[HostContext]

    if not os.path.exists(SHIM_PATH):
        raise SkipComponent()

    lines = []
    try:

        show_signature_cmd = "/usr/bin/pesign --show-signature --in={0}".format(SHIM_PATH)
        rc, show_signature = ctx.shell_out(show_signature_cmd, keep_rc=True, timeout=DEFAULT_SHELL_TIMEOUT)

        if rc == 0 and show_signature:
            count = sum(1 for line in show_signature if 'certificate address' in line)

            for i in range(count):

                with NamedTemporaryFile(prefix='pesign_sig{0}_'.format(i), suffix='.p7', delete=True) as sig_file:

                    export_signature_cmd = "/usr/bin/pesign -i {0} -u {1} --force --export-signature {2}".format(SHIM_PATH, i, sig_file.name)
                    rc, export_signature = ctx.shell_out(export_signature_cmd, keep_rc=True, timeout=DEFAULT_SHELL_TIMEOUT)

                    if rc != 0:
                        continue

                    openssl_print_certs_cmd = "/usr/bin/openssl pkcs7 -inform DER -print_certs -text -in {0}".format(sig_file.name)
                    rc, cert_info = ctx.shell_out(openssl_print_certs_cmd, keep_rc=True, timeout=DEFAULT_SHELL_TIMEOUT)

                if rc == 0 and cert_info:
                    lines.append('=== signum {0} ==='.format(i))
                    lines.extend(line for line in cert_info if line.strip().startswith(CERT_FIELDS))

    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))

    if lines:
        return DatasourceProvider(
            content=lines,
            relative_path='insights_datasources/pesign_shim_certificates',
            ds=Specs.pesign_shim_certificates,
            ctx=ctx,
            cleaner=broker.get('cleaner'),
        )

    raise SkipComponent
