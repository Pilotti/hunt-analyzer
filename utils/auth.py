import bcrypt
from utils.database import conectar

def cadastrar_usuario(username, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        hash_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO usuarios (username, senha) VALUES (?, ?)",
            (username, hash_senha)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def login_usuario(username, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        usuario = cursor.fetchone()

        if usuario and bcrypt.checkpw(senha.encode("utf-8"), usuario["senha"]):
            return dict(usuario)
        return None
    finally:
        conn.close()