import bcrypt
import re
from utils.database import conectar

def email_valido(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email) is not None

def cadastrar_usuario(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        hash_senha = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO usuarios (email, senha) VALUES (?, ?)",
            (email, hash_senha)
        )
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def login_usuario(email, senha):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()

        if usuario and bcrypt.checkpw(senha.encode("utf-8"), usuario["senha"]):
            return dict(usuario)
        return None
    finally:
        conn.close()