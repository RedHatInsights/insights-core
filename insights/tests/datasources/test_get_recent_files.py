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


def test_get_recent_files_rejects_symlink_target(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    (real / "plain.json").write_text("plain")
    link = tmp_path / "link"
    os.symlink(real, link)

    assert get_recent_files(str(link)) == []
    assert os.path.basename(get_recent_files(str(real))[0]) == "plain.json"
