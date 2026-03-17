import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "app.db")

def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar():
    conn = conectar()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS personagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

        CREATE TABLE IF NOT EXISTS hunts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            personagem_id INTEGER NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (personagem_id) REFERENCES personagens(id)
        );

        CREATE TABLE IF NOT EXISTS hunt_drops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hunt_id INTEGER NOT NULL,
            item_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_npc INTEGER NOT NULL,
            preco_jogador INTEGER NOT NULL,
            FOREIGN KEY (hunt_id) REFERENCES hunts(id)
        );

        CREATE TABLE IF NOT EXISTS hunt_gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hunt_id INTEGER NOT NULL,
            item_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_npc INTEGER NOT NULL,
            FOREIGN KEY (hunt_id) REFERENCES hunts(id)
        );

        CREATE TABLE IF NOT EXISTS hunt_inimigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hunt_id INTEGER NOT NULL,
            inimigo_nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            FOREIGN KEY (hunt_id) REFERENCES hunts(id)
        );
    """)

    conn.commit()
    conn.close()