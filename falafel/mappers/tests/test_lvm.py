from falafel.mappers import lvm

WARNINGS_CONTENT = """
WARNING
valid data 1
Checksum Error
valid data 2
  Failed to write
  Attempt To Close Device
valid data 3
""".strip()

WARNINGS_FOUND = """
WARNING
Checksum Error
  Failed to write
  Attempt To Close Device
""".strip()


def test_replace_spaces_in_keys():
    data = lvm.replace_spaces_in_keys("Lock Args  LV Tags")
    assert data == "Lock_Args  LV Tags"


def test_find_warnings():
    data = [l for l in lvm.find_warnings(WARNINGS_CONTENT.splitlines())]
    assert len(data) == len(WARNINGS_FOUND.splitlines())
    assert data == WARNINGS_FOUND.splitlines()
