from falafel.config import SimpleFileSpec, PatternSpec

specs = {
    "installed-rpms": SimpleFileSpec("installed-rpms"),
    "pg_log": PatternSpec(r"var/lib/pgsql/data/pg_log/postgresql-.*.log")
}
