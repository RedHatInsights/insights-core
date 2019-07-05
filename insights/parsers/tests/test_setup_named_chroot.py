from insights.parsers import setup_named_chroot, SkipException
from insights.parsers.setup_named_chroot import SetupNamedChroot
from insights.tests import context_wrap
import doctest
import pytest

CHROOT_CONTENT_FILTERED = """
#!/bin/bash
# it MUST be listed last. (/var/named contains /var/named/chroot)
ROOTDIR_MOUNT='/etc/localtime /etc/named /etc/pki/dnssec-keys /etc/named.root.key /etc/named.conf
/etc/named.dnssec.keys /etc/named.rfc1912.zones /etc/rndc.conf /etc/rndc.key /usr/lib64/bind
/usr/lib/bind /etc/named.iscdlv.key /run/named /var/named /etc/protocols /etc/services'
    for all in $ROOTDIR_MOUNT; do
    for all in $ROOTDIR_MOUNT; do,
    # Check if file is mount target. Do not use /proc/mounts because detecting
""".strip()

CHROOT_CONTENT_ALL = """
#!/bin/bash

# Warning: the order is important
# If a directory containing $ROOTDIR is listed here,
# it MUST be listed last. (/var/named contains /var/named/chroot)
ROOTDIR_MOUNT='/etc/localtime /etc/named /etc/pki/dnssec-keys /etc/named.root.key /etc/named.conf
/etc/named.dnssec.keys /etc/named.rfc1912.zones /etc/rndc.conf /etc/rndc.key /etc/named.iscdlv.key /etc/protocols /etc/services
/usr/lib64/bind /usr/lib/bind /run/named
/var/named'

usage()
{
  echo
  echo 'This script setups chroot environment for BIND'
  echo 'Usage: setup-named-chroot.sh ROOTDIR [on|off]'
}

if ! [ "$#" -eq 2 ]; then
  echo 'Wrong number of arguments'
  usage
  exit 1
fi

ROOTDIR="$1"

# Exit if ROOTDIR doesn't exist
if ! [ -d "$ROOTDIR" ]; then
  echo "Root directory $ROOTDIR doesn't exist"
  usage
  exit 1
fi

mount_chroot_conf()
{
  if [ -n "$ROOTDIR" ]; then
    for all in $ROOTDIR_MOUNT; do
      # Skip nonexistant files
      [ -e "$all" ] || continue

      # If mount source is a file
      if ! [ -d "$all" ]; then
        # mount it only if it is not present in chroot or it is empty
        if ! [ -e "$ROOTDIR$all" ] || [ `stat -c'%s' "$ROOTDIR$all"` -eq 0 ]; then
          touch "$ROOTDIR$all"
          mount --bind "$all" "$ROOTDIR$all"
        fi
      else
        # Mount source is a directory. Mount it only if directory in chroot is
        # empty.
        if [ -e "$all" ] && [ `ls -1A $ROOTDIR$all | wc -l` -eq 0 ]; then
          mount --bind --make-private "$all" "$ROOTDIR$all"
        fi
      fi
    done
  fi
}

umount_chroot_conf()
{
  if [ -n "$ROOTDIR" ]; then
    for all in $ROOTDIR_MOUNT; do
      # Check if file is mount target. Do not use /proc/mounts because detecting
      # of modified mounted files can fail.
      if mount | grep -q '.* on '"$ROOTDIR$all"' .*'; then
        umount "$ROOTDIR$all"
        # Remove temporary created files
        [ -f "$all" ] && rm -f "$ROOTDIR$all"
      fi
    done
  fi
}

case "$2" in
  on)
    mount_chroot_conf
    ;;
  off)
    umount_chroot_conf
    ;;
  *)
    echo 'Second argument has to be "on" or "off"'
    usage
    exit 1
esac

exit 0
""".strip()

EXCEPTION1 = """
""".strip()

EXCEPTION2 = """
usage()
{
  echo
  echo 'This script setups chroot environment for BIND'
  echo 'Usage: setup-named-chroot.sh ROOTDIR [on|off]'
}

if ! [ "$#" -eq 2 ]; then
  echo 'Wrong number of arguments'
  usage
  exit 1
fi
""".strip()


def test_setup_named_chroot_all():
    snc = SetupNamedChroot(context_wrap(CHROOT_CONTENT_ALL))
    assert snc["ROOTDIR_MOUNT"][-1] == "/var/named"
    assert len(snc) == 2


def test_setup_named_chroot_filtered():
    snc = SetupNamedChroot(context_wrap(CHROOT_CONTENT_FILTERED))
    assert "ROOTDIR_MOUNT" in snc
    assert snc["ROOTDIR_MOUNT"][-1] != "/var/named"
    assert len(snc.raw) == 5


def test_doc_examples():
    env = {
            'snc': SetupNamedChroot(context_wrap(CHROOT_CONTENT_ALL)),
          }
    failed, total = doctest.testmod(setup_named_chroot, globs=env)
    assert failed == 0


def test_setup_named_chroot_exception1():
    with pytest.raises(SkipException) as e:
        SetupNamedChroot(context_wrap(EXCEPTION1))
    assert "Empty file" in str(e)


def test_setup_named_chroot_exception2():
    with pytest.raises(SkipException) as e:
        SetupNamedChroot(context_wrap(EXCEPTION2))
    assert "Input content is not empty but there is no useful parsed data." in str(e)
