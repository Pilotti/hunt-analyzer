import customtkinter as ctk
from utils.database import conectar

class TelaPersonagens(ctk.CTk):
    def __init__(self, usuario, ao_selecionar):
        super().__init__()
        self.usuario = usuario
        self.ao_selecionar = ao_selecionar
        self.title("Hunt Analyzer — Personagens")
        self.geometry("400x600")
        self.resizable(False, False)
        self._construir()
        self._carregar_personagens()

    def _construir(self):
        ctk.CTkLabel(self, text=f"Olá, {self.usuario['email'].split('@')[0]}!",
            font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(30, 5))
        ctk.CTkLabel(self, text="Selecione ou adicione um personagem",
            font=ctk.CTkFont(size=13)).pack(pady=(0, 20))

        self.frame_lista = ctk.CTkScrollableFrame(self, width=340, height=300)
        self.frame_lista.pack(pady=10)

        self.mensagem = ctk.CTkLabel(self, text="", text_color="red")
        self.mensagem.pack(pady=5)

        self.entry_personagem = ctk.CTkEntry(self, placeholder_text="Nome do personagem", width=300)
        self.entry_personagem.pack(pady=8)

        ctk.CTkButton(self, text="Adicionar personagem", width=300, command=self._adicionar).pack(pady=4)

    def _carregar_personagens(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personagens WHERE usuario_id = ?", (self.usuario["id"],))
        personagens = cursor.fetchall()
        conn.close()

        if not personagens:
            ctk.CTkLabel(self.frame_lista, text="Nenhum personagem cadastrado.").pack(pady=10)
            return

        for p in personagens:
            frame = ctk.CTkFrame(self.frame_lista, fg_color="transparent")
            frame.pack(fill="x", pady=4)

            ctk.CTkButton(frame, text=p["nome"], width=220,
                command=lambda pid=p["id"], pnome=p["nome"]: self._selecionar(pid, pnome)).pack(side="left", padx=4)

            ctk.CTkButton(frame, text="🗑", width=40, fg_color="transparent",
                border_width=1, text_color="red",
                command=lambda pid=p["id"]: self._remover(pid)).pack(side="left", padx=4)

    def _adicionar(self):
        nome = self.entry_personagem.get().strip()
        if not nome:
            self.mensagem.configure(text="Digite um nome.", text_color="red")
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO personagens (usuario_id, nome) VALUES (?, ?)",
            (self.usuario["id"], nome))
        conn.commit()
        conn.close()

        self.entry_personagem.delete(0, "end")
        self.mensagem.configure(text="")
        self._carregar_personagens()

    def _remover(self, personagem_id):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personagens WHERE id = ?", (personagem_id,))
        conn.commit()
        conn.close()
        self._carregar_personagens()

    def _selecionar(self, personagem_id, nome):
        self.destroy()
        self.ao_selecionar({"id": personagem_id, "nome": nome})