import os

from insights.specs.datasources import get_recent_files


def test_get_recent_files_skips_symlink_and_hardlink(tmp_path):
    uploads = tmp_path / "uploads"
    uploads.mkdir()

    (uploads / "plain.json").write_text("plain")

    outside = tmp_path / "secret.json"
    outside.write_text("secret")
    os.link(outside, uploads / "hard.json")
    os.symlink(outside, uploads / "sym.json")

    names = sorted(os.path.basename(p) for p in get_recent_files(str(uploads)))
    assert names == ["plain.json"]
