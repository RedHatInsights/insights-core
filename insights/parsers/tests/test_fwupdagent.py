# -*- coding: utf-8 -*-

import doctest

import pytest

from insights.parsers import fwupdagent, ParseException
from insights.parsers.fwupdagent import FwupdagentDevices, FwupdagentSecurity
from insights.tests import context_wrap

DEVICES = """
{
  "Devices" : [
    {
      "Name" : "Thunderbolt host controller",
      "DeviceId" : "113494429de0754484e6b93d70e879a913311dd5",
      "Guid" : [
        "ea3c7ac8-d937-568a-aab5-e053bd6af9ce",
        "3d3f953a-3408-56fa-81f3-042d73c59c16",
        "e773c51e-a20c-5b29-9f09-6bb0e0ef7560",
        "f1793149-6c12-5a7f-95db-9fefd116748d"
      ],
      "Summary" : "Unmatched performance for high-speed I/O",
      "Plugin" : "thunderbolt",
      "Protocol" : "com.intel.thunderbolt",
      "Flags" : [
        "internal",
        "updatable",
        "require-ac",
        "supported",
        "registered",
        "dual-image"
      ],
      "Vendor" : "Lenovo",
      "VendorId" : "THUNDERBOLT:0x0109|TBT:0x0109",
      "VendorIds" : [
        "THUNDERBOLT:0x0109",
        "TBT:0x0109"
      ],
      "Version" : "20.00",
      "VersionFormat" : "pair",
      "Icons" : [
        "thunderbolt"
      ],
      "Created" : 1633947746,
      "Releases" : [
        {
          "AppstreamId" : "com.lenovo.ThinkPadN2JTF.firmware",
          "RemoteId" : "lvfs",
          "Summary" : "Lenovo ThinkPad X390/ThinkPad T490s Thunderbolt Firmware",
          "Description" : "<p>Lenovo ThinkPad X390/ThinkPad T490s Thunderbolt Firmware</p><p>Fix Thunderbolt SPI ROM Wear out issue.</p>",
          "Version" : "20.00",
          "Filename" : "fc93d9ff3f7ced7eb11d9bf7d8cd009ce408d7d9",
          "Protocol" : "com.intel.thunderbolt",
          "Checksum" : [
            "915a6657f6972937bcb88868e5d8ce1f1ec9fb85"
          ],
          "License" : "LicenseRef-proprietary",
          "Size" : 253952,
          "Created" : 1583253000,
          "Locations" : [
            "https://fwupd.org/downloads/8eef957c95cb6f534448be1faa7bbfc8702d620f64b757d40ee5e0b6b7094c0e-Lenovo-ThinkPad-X390-SystemFirmware-01.cab"
          ],
          "Uri" : "https://fwupd.org/downloads/8eef957c95cb6f534448be1faa7bbfc8702d620f64b757d40ee5e0b6b7094c0e-Lenovo-ThinkPad-X390-SystemFirmware-01.cab",
          "Homepage" : "http://www.lenovo.com",
          "Vendor" : "Lenovo Ltd."
        }
      ]
    },
    {
      "Name" : "USB3.0 Hub",
      "DeviceId" : "54f0d9041b6c5438c7ff825f5139559c5ca1b222",
      "Guid" : [
        "9429e4c7-f053-51d7-9289-75c4ddb14a97",
        "26f33695-3a3e-5c08-badb-f6141390ebd9",
        "10eb3a15-c177-5810-af53-1963e9200e65",
        "60e0a85e-b245-5c84-ba3b-d5bdb540cd47",
        "d91a45a0-4435-59d6-bb6b-9499f4a793c2",
        "022d2f73-4826-546a-ba0f-62579ea848ea"
      ],
      "Summary" : "USB 3.x Hub",
      "Plugin" : "vli",
      "Protocol" : "com.vli.usbhub",
      "Flags" : [
        "updatable",
        "registered",
        "can-verify",
        "can-verify-image",
        "dual-image",
        "self-recovery",
        "add-counterpart-guids"
      ],
      "Vendor" : "VIA Labs, Inc.",
      "VendorId" : "USB:0x2109",
      "Version" : "3.114",
      "VersionFormat" : "bcd",
      "Icons" : [
        "audio-card"
      ],
      "InstallDuration" : 15,
      "Created" : 1633947743
    }
  ]
}
"""

SECURITY = """
{
  "HostSecurityAttributes" : [
    {
      "AppstreamId" : "org.fwupd.hsi.Kernel.Tainted",
      "HsiResult" : "not-tainted",
      "Name" : "Linux kernel",
      "Uri" : "https://fwupd.github.io/hsi.html#org.fwupd.hsi.Kernel.Tainted",
      "Flags" : [
        "success",
        "runtime-issue"
      ]
    },
    {
      "AppstreamId" : "org.fwupd.hsi.EncryptedRam",
      "HsiLevel" : 4,
      "HsiResult" : "not-supported",
      "Name" : "Encrypted RAM",
      "Uri" : "https://fwupd.github.io/hsi.html#org.fwupd.hsi.EncryptedRam"
    }
  ]
}
"""

SECURITY_ERROR_1 = """
Failed to parse arguments: Unknown option --force
"""

SECURITY_ERROR_2 = """
Command not found

Usage:
  fwupdagent [OPTION…]

  get-devices                       Get all devices and possible releases
  get-updates                       Gets the list of updates for connected hardware
  get-upgrades                      Alias to get-updates

Help Options:
  -h, --help        Show help options

Application Options:
  -v, --verbose     Show extra debugging information

This tool can be used from other tools and from shell scripts.
"""


def test_devices():
    devices = FwupdagentDevices(context_wrap(DEVICES))

    assert len(devices["Devices"]) == 2
    assert devices["Devices"][0]["Name"] == "Thunderbolt host controller"
    assert devices["Devices"][0]["Version"] == "20.00"
    assert devices["Devices"][1]["Name"] == "USB3.0 Hub"
    assert devices["Devices"][1]["Version"] == "3.114"


def test_security():
    security = FwupdagentSecurity(context_wrap(SECURITY))
    assert len(security["HostSecurityAttributes"]) == 2
    assert security["HostSecurityAttributes"][0]["Name"] == "Linux kernel"
    assert security["HostSecurityAttributes"][0]["HsiResult"] == "not-tainted"
    assert security["HostSecurityAttributes"][1]["Name"] == "Encrypted RAM"
    assert security["HostSecurityAttributes"][1]["HsiLevel"] == 4

    with pytest.raises(ParseException):
        FwupdagentSecurity(context_wrap(SECURITY_ERROR_1))

    with pytest.raises(ParseException):
        FwupdagentSecurity(context_wrap(SECURITY_ERROR_2))


def test_doc_examples():
    env = {
        "devices": FwupdagentDevices(context_wrap(DEVICES)),
        "security": FwupdagentSecurity(context_wrap(SECURITY)),
    }
    failed, total = doctest.testmod(fwupdagent, globs=env)
    assert failed == 0
