import sqlite3
import os
import sys

def _get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__ + "/.."))

DB_PATH = os.path.join(_get_base_path(), "database", "app.db")

def conectar():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar():
    conn = conectar()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS personagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            cla TEXT NOT NULL,
            nivel INTEGER NOT NULL DEFAULT 1,
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

        CREATE TABLE IF NOT EXISTS hunt_bonus (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hunt_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            duracao_minutos INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            FOREIGN KEY (hunt_id) REFERENCES hunts(id)
        );
    """)

    conn.commit()
    conn.close()