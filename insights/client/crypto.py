import errno
import os.path
import logging
import shutil
import tempfile
import subprocess

logger = logging.getLogger(__name__)


class GPGCommandResult(object):
    """Output of a GPGCommand.

    Attributes:
        ok (bool): Result of an operation.
        return_code (int): Return code of the operation.
        stdout (str): Standard output of the command.
        stderr (str): Standard error of the command.
        _command (GPGCommand | None):
            An optional reference to the GPGCommand object that created the result
    """
    def __init__(self, ok, return_code, stdout, stderr, command):
        self.ok = ok
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self._command = command

    def __str__(self):
        return (
            "<{cls} ok={ok} return_code={code} stdout={out} stderr={err}>"
        ).format(
            cls=self.__class__.__name__,
            ok=self.ok, code=self.return_code,
            out=self.stdout, err=self.stderr,
        )


class GPGCommand(object):
    """GPG command run in a temporary environment.

    Attributes:
        command (list(str)): The command to be executed.
        keys (list(str)): List of paths to GPG public keys to check against.

        _home (str): Path to the temporary GPG home directory.
        _raw_command (list(str)): The last invoked command.
    """

    def __init__(self, command, keys):
        self.command = command
        self.keys = keys

        self._home = None
        self._raw_command = None

    def __str__(self):
        return "<{cls} _home={home} _raw_command={raw}>".format(
            cls=self.__class__.__name__,
            home=self._home,
            raw=self._raw_command
        )

    def _setup(self):
        """Prepare GPG environment.

        Returns (bool):
            `True` if public GPG keys were imported into temporary environment,
            `False` if there was an error.
        """
        self._home = tempfile.mkdtemp()

        logger.debug("setting up gpg in the temporary environment")
        for key in self.keys:
            result = self._run(["--import", key])
            if not result.ok:
                logger.debug("failed to import key '{key}': {result}".format(
                    key=key, result=result
                ))
                return False

        return True

    def _cleanup(self):
        """Clean up GPG environment."""
        # Try to delete the temporary directory GPG used. As discovered by the
        # convert2rhel team, we need to handle race conditions:
        # https://github.com/oamg/convert2rhel/blob/23aadbf0df58c79a8910847d345fcd4092f4656f/convert2rhel/utils.py#L867-L893

        # GPG writes a temporary socket file for the gpg-agent into the home
        # directory. Sometimes it removes the socket file after `rmtree()` has
        # determined it should be deleted but before the actual deletion occurs.
        # This will cause a FileNotFoundError/OSError.
        # When we encounter that, try to run `rmtree()` again.
        for _ in range(0, 5):
            try:
                shutil.rmtree(self._home)
            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    # We are trying to remove a file that has already been
                    # removed by gpg-agent itself. Ignore it.
                    continue
                # Some other error has happened, let it bubble up.
                raise
            else:
                # We have successfully removed everything. This `break` will
                # prevent the log statement below from being run.
                break
        else:
            # We called `rmtree()` five times and it failed each time. We cannot
            # do more without knowing more.
            logger.debug(
                "could not clean up temporary gpg directory "
                "'{path}'".format(path=self._home)
            )

    def _run(self, command):
        """Run the actual command.

        Returns (CommandResult): The result of the shell command.
        """
        self._raw_command = ["/usr/bin/gpg", "--homedir", self._home] + command
        process = subprocess.Popen(
            self._raw_command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()

        result = GPGCommandResult(
            ok=process.returncode == 0,
            return_code=process.returncode,
            stdout=stdout.decode("utf-8"),
            stderr=stderr.decode("utf-8"),
            command=self,
        )

        if result.ok:
            logger.debug("gpg command {command}: ok".format(command=command))
        else:
            logger.debug(
                "gpg command {command} returned non-zero code: {result}".format(
                    command=command, result=result,
                )
            )

        return result

    def evaluate(self):
        """Run the command.

        Returns (CommandResult): The result of the shell command.
        """
        try:
            ok = self._setup()
            if not ok:
                return

            logger.debug("running gpg in the temporary environment")
            return self._run(self.command)
        finally:
            self._cleanup()


def verify_gpg_signed_file(file, signature, keys):
    """
    Verify a file that was signed using GPG.

    Parameters:
        file (str): A path to the signed file.
        signature (str): A path to the detached signature.
        keys (list(str)):
            List of paths to GPG public keys on the filesystem to check against.

    Returns (CommandResult): Evaluated GPG command.
    """
    if not os.path.isfile(file):
        logger.debug(
            "cannot verify signature of '{file}', file does not exist".format(
                file=file
            )
        )
        raise OSError(errno.ENOENT, "File '{file}' not found".format(file=file))

    if not os.path.isfile(signature):
        logger.debug((
            "cannot verify signature of '{file}', "
            "signature '{signature}' does not exist"
        ).format(file=file, signature=signature))
        raise OSError(
            errno.ENOENT,
            "Signature '{sig}' of file '{file}' not found.".format(
                sig=signature, file=file
            )
        )

    gpg = GPGCommand(["--verify", signature, file], keys)
    logger.debug("starting gpg verification process for '{file}'".format(file=file))

    result = gpg.evaluate()

    if result.ok:
        logger.debug("signature verification of '{file}' passed".format(file=file))
    else:
        logger.debug("signature verification of '{file}' failed".format(file=file))

    return result
