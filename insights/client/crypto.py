import errno
import os.path
import logging
import shutil
import tempfile
import subprocess

logger = logging.getLogger(__name__)


class GPGCommandResult(object):
    """Output of a GPGCommand.

    :param ok: Result of an operation.
    :type ok: bool
    :param return_code: Return code of an operation.
    :type return_code: int
    :param stdout: Standard output of the command.
    :type stdout: str
    :param stderr: Standard error of the command.
    :type stderr: str
    :param _command: An optional reference to the GPGCommand object that created the result.
    :type _command: GPGCommand | None
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

    :param command: The command to be executed.
    :type command: list[str]
    :param key: Path to the GPG public key to check against.
    :type key: str
    :param _home: Path to the temporary GPG home directory.
    :type _home: str | None
    :param _raw_command: The last invoked command.
    :type _raw_command: list[str] | None
    """
    TEMPORARY_GPG_HOME_PARENT_DIRECTORY = "/var/lib/insights/"

    def __init__(self, command, key):
        self.command = command
        self.key = key
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

        :returns: Result of the GPG key import.
        :rtype: GPGCommandResult
        """
        # The /var/lib/insights/ directory is used instead of /tmp/ because
        # GPG needs to have RW permissions in it, and existing SELinux rules only
        # allow access here.
        self._home = tempfile.mkdtemp(dir=type(self).TEMPORARY_GPG_HOME_PARENT_DIRECTORY)

        logger.debug("setting up gpg temporary environment in '{home}'".format(home=self._home))
        result = self._run(["--import", self.key])  # type: GPGCommandResult
        if not result.ok:
            logger.warning("failed to import key '{key}': {result}".format(
                key=self.key, result=result
            ))
        return result

    def _supports_cleanup_socket(self):
        """Queries for the version of GPG binary.

        :returns: `True` if the gnupg is known for supporting `--kill all`.
        :rtype: bool
        """
        version_process = subprocess.Popen(
            ["/usr/bin/gpg", "--version"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True,
            env={"GNUPGHOME": self._home, "LC_ALL": "C.UTF-8"},
        )
        stdout, stderr = version_process.communicate()
        if version_process.returncode != 0:
            stderr = "\n".join("stderr: {line}".format(line=line) for line in stderr.split("\n") if len(line))
            logger.debug("could not query for gpg version:\n{err}".format(err=stderr))
            return False

        for line in stdout.split("\n"):
            if line.startswith("gpg (GnuPG) "):
                version = line.split(" ")[-1]  # type: str
                break
        else:
            stdout = "\n".join("stdout: {line}".format(line=line) for line in stdout.split("\n") if len(line))
            logger.debug("could not query for gpg version: output not recognized:\n{out}".format(out=stdout))
            return False

        try:
            version_info = tuple(int(v) for v in version.split("."))
        except Exception as exc:
            logger.debug("gpg version could not be parsed: '{version}: {exc}".format(version=version, exc=str(exc)))
            return False
        if len(version_info) < 3:
            logger.debug("gpg version is not recognized: '{version}'".format(version=version))
            return False

        # `gpgconf --kill` was added in GnuPG 2.1.0-beta2 and `--kill all` exists since 2.1.18.
        # - 2.1.0b1: commit 7c03c8cc65e68f1d77a5a5a497025191fe5df5e9 in GPG's repository.
        # - 2.1.18: https://lists.gnupg.org/pipermail/gnupg-announce/2017q1/000401.html
        #
        # RHEL versions come with the following gpg versions:
        # - 6.10: 2.0.14
        # - 7.9:  2.0.22
        # - 8.9:  2.2.20
        # - 9.3:  2.3.3
        # which means this code should return `True` for RHEL 8 and above.
        return version_info >= (2, 1, 18)

    def _cleanup_socket(self):
        """Stop GPG socket in its home directory."""
        # GPG writes a temporary socket file for the gpg-agent into the home
        # directory. This is only supported since gnupg 2.1.18 (RHEL 8).
        shutdown_process = subprocess.Popen(
            ["/usr/bin/gpgconf", "--kill", "all"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True,
            env={"GNUPGHOME": self._home, "LC_ALL": "C.UTF-8"},
        )
        _, stderr = shutdown_process.communicate()
        if shutdown_process.returncode != 0:
            stderr = "\n".join("stderr: {line}".format(line=line) for line in stderr.split("\n") if len(line))
            logger.debug(
                "could not kill the GPG agent, got return code {rc}: \n{err}".format(
                    rc=shutdown_process.returncode, err=stderr
                )
            )

    def _cleanup(self):
        """Clean up GPG environment."""
        if self._supports_cleanup_socket():
            self._cleanup_socket()

        # Older systems do not support `gpgconf --kill`.
        # The socket may remove its socket file after `rmtree()` has determined
        # it should be deleted, but before the actual deletion occurs.
        # This would cause a FileNotFoundError/OSError.
        for _ in range(5):
            try:
                shutil.rmtree(self._home)
                break
            except OSError as exc:
                if exc.errno == errno.ENOENT:
                    # The file has already been removed by the `gpg-agent`.
                    continue
                raise
        else:
            logger.debug(
                "could not clean up temporary GPG directory '{path}'".format(path=self._home)
            )

    def _run(self, command):
        """Run the actual command.

        :returns: The result of the shell command.
        :rtype: GPGCommandResult
        """
        self._raw_command = ["/usr/bin/gpg", "--homedir", self._home] + command
        process = subprocess.Popen(
            self._raw_command,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={"LC_ALL": "C.UTF-8"},
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

        :returns: The result of the shell command.
        :rtype: GPGCommandResult
        """
        try:
            result = self._setup()
            if not result.ok:
                logger.debug("gpg setup failed")
                return result

            logger.debug("running gpg in the temporary environment")
            return self._run(self.command)
        finally:
            self._cleanup()


def verify_gpg_signed_file(file, signature, key):
    """
    Verify a file that was signed using GPG.

    :param file: A path to the signed file.
    :type file: str
    :param signature: A path to the detached signature.
    :type signature: str
    :param key: Path to the public GPG key on the filesystem to check against.
    :type key: str

    :returns: Evaluated GPG command.
    :rtype: GPGCommandResult
    """
    if not os.path.isfile(file):
        logger.debug(
            "cannot verify signature of '{file}', file does not exist".format(
                file=file
            )
        )
        return GPGCommandResult(
            ok=False,
            return_code=1,
            stdout="",
            stderr="file '{path}' does not exist".format(path=file),
            command=None,
        )

    if not os.path.isfile(signature):
        logger.debug((
            "cannot verify signature of '{file}', "
            "signature '{signature}' does not exist"
        ).format(file=file, signature=signature))
        return GPGCommandResult(
            ok=False,
            return_code=1,
            stdout="",
            stderr="file '{path}' does not exist".format(path=signature),
            command=None,
        )

    gpg = GPGCommand(command=["--verify", signature, file], key=key)

    logger.debug("starting gpg verification process for '{file}'".format(file=file))
    result = gpg.evaluate()  # type: GPGCommandResult

    if result.ok:
        logger.debug("signature verification of '{file}' passed".format(file=file))
    else:
        logger.debug("signature verification of '{file}' failed".format(file=file))

    return result
