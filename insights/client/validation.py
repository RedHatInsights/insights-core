import tempfile
import gpg
import os
import logging

logger = logging.getLogger(__name__)

def gpg_validate(path, gpg_key, sig=None):

    # creastes temporary directory for gnu gpg validation
    with tempfile.TemporaryDirectory() as tmpd:

        with gpg.Context(home_dir=tmpd) as c:

            with open(gpg_key, 'rb') as gpg_key_bytes:
                c.op_import(gpg_key_bytes.read())

            try:
                if sig is None:
                    sig = path + ".asc"
                logger.debug("Verifying %s against %s, Result: " % (path, sig))

                with open(path, "rb") as f_egg:
                    with open(sig, "r") as f_asc:
                        _, result = c.verify(f_egg, f_asc)

            except gpg.errors.BadSignatures:
                logger.debug("Failed to verify %s" % path)
                return -1

    logger.debug("Verified %s" % path)
    return result.signatures[0].status
