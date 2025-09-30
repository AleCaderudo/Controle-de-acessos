import sqlcipher3.dbapi2 as sqlite

DB_FILENAME = "geral.db"
DB_KEY = None   # será definida após login

def get_conn():
    if DB_KEY is None:
        raise RuntimeError("DB_KEY não definida. Faça login primeiro.")
    conn = sqlite.connect(DB_FILENAME)
    cur = conn.cursor()
    cur.execute("PRAGMA key = %s;" % repr(DB_KEY))
    return conn

def try_open_with_key(key):
    try:
        conn = sqlite.connect(DB_FILENAME)
        cur = conn.cursor()
        cur.execute("PRAGMA key = %s;" % repr(key))
        cur.execute("SELECT count(*) FROM sqlite_master;")
        conn.close()
        return True
    except Exception:
        return False
