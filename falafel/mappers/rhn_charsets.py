from falafel.core.plugins import mapper


@mapper('rhn-charsets')
def rhn_charsets(context):
    """
    ==== Sample (1) embedded database ====
     server_encoding
    -----------------
     UTF8
    (1 row)

     client_encoding
    -----------------
     UTF8
    (1 row)
    ==== Sample (2) Oracle database ====
    PARAMETER                  VALUE
    ---------------------------------
    NLS_CHARACTERSET           UTF8
    NLS_NCHAR_CHARACTERSET     UTF8
    ======================================
    Returns a dict:
    - {'db_backend':'postgresql', 'server_encoding': 'UTF8','client_encoding': 'UTF8'}
    - {'db_backend':'oracle', 'NLS_CHARACTERSET': 'UTF8','NLS_NCHAR_CHARACTERSET': 'UTF8'}
    """
    db_set = {}
    db_backend = None
    in_server = False
    in_client = False
    for line in context.content:
        line = line.strip()
        # skip empty and useless lines
        if not line or line.startswith(('----', '(', 'PARAMETER')):
            continue
        if '_encoding' in line:
            db_backend = 'postgresql'
            in_server = line.startswith('server_')
            in_client = line.startswith('client_')
        elif db_backend == 'postgresql':
            if in_server:
                db_set['server_encoding'] = line
            elif in_client:
                db_set['client_encoding'] = line
        elif line.startswith('NLS_'):
            db_backend = 'oracle'
            line_splits = line.split()
            if len(line_splits) == 2:
                db_set[line_splits[0]] = line_splits[1]
        db_set['db_backend'] = db_backend
    return db_set
