import os

from insights.specs.datasources import get_recent_files


def test_get_recent_files_skips_symlink_and_hardlink(tmpdir):
    uploads = tmpdir.mkdir("uploads")
    uploads.join("plain.json").write("plain")

    outside = tmpdir.join("secret.json")
    outside.write("secret")
    os.link(outside.strpath, uploads.join("hard.json").strpath)
    os.symlink(outside.strpath, uploads.join("sym.json").strpath)

    names = sorted(os.path.basename(p) for p in get_recent_files(uploads.strpath))
    assert names == ["plain.json"]


def test_get_recent_files_rejects_symlink_target(tmpdir):
    real = tmpdir.mkdir("real")
    real.join("plain.json").write("plain")
    link = tmpdir.join("link")
    os.symlink(real.strpath, link.strpath)

    assert get_recent_files(link.strpath) == []
    assert os.path.basename(get_recent_files(real.strpath)[0]) == "plain.json"
