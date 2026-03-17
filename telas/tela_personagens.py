import customtkinter as ctk
from utils.database import conectar

CLAS = ["Volcanic", "Raibolt", "Orebound", "Naturia", "Gardestrike",
        "Ironhard", "Wingeon", "Psycraft", "Seavell", "Malefic"]

class TelaPersonagens(ctk.CTkFrame):
    def __init__(self, master, usuario, ao_selecionar, ao_historico):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self.ao_selecionar = ao_selecionar
        self.ao_historico = ao_historico
        self._construir()
        self._carregar_personagens()

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 0))

        ctk.CTkLabel(header, text=f"Olá, {self.usuario['email'].split('@')[0]}!",
            font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        ctk.CTkButton(header, text="+ Adicionar Personagem", width=180,
            command=self._abrir_adicionar).pack(side="right")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=30, pady=20)

        ctk.CTkLabel(content, text="Selecione um personagem",
            font=ctk.CTkFont(size=13)).pack(anchor="w", pady=(0, 10))

        self.frame_lista = ctk.CTkScrollableFrame(content)
        self.frame_lista.pack(fill="both", expand=True)

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
            card = ctk.CTkFrame(self.frame_lista)
            card.pack(fill="x", pady=4)

            # Lado esquerdo — info + botões pequenos
            esquerda = ctk.CTkFrame(card, fg_color="transparent")
            esquerda.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            nome_row = ctk.CTkFrame(esquerda, fg_color="transparent")
            nome_row.pack(anchor="w")

            ctk.CTkLabel(nome_row, text=p["nome"],
                font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")

            ctk.CTkButton(nome_row, text="✏", width=24, height=24,
                fg_color="transparent", border_width=1, font=ctk.CTkFont(size=11),
                command=lambda p=dict(p): self._abrir_editar(p)).pack(side="left", padx=(8, 2))

            ctk.CTkButton(nome_row, text="🗑", width=24, height=24,
                fg_color="transparent", border_width=1, font=ctk.CTkFont(size=11),
                text_color="red",
                command=lambda pid=p["id"]: self._confirmar_remover(pid)).pack(side="left", padx=2)

            ctk.CTkLabel(esquerda, text=f"Clã: {p['cla']}   •   Nível: {p['nivel']}",
                font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w")

            # Lado direito — ações principais
            direita = ctk.CTkFrame(card, fg_color="transparent")
            direita.pack(side="right", padx=10, pady=8)

            ctk.CTkButton(direita, text="Histórico", width=90, fg_color="transparent",
                border_width=1,
                command=lambda pid=p["id"], pnome=p["nome"]: self.ao_historico({"id": pid, "nome": pnome})).pack(side="left", padx=4)

            ctk.CTkButton(direita, text="Nova Hunt", width=100,
                command=lambda pid=p["id"], pnome=p["nome"]: self.ao_selecionar({"id": pid, "nome": pnome})).pack(side="left", padx=4)

    def _abrir_adicionar(self):
        self._abrir_form("Adicionar Personagem")

    def _abrir_editar(self, personagem):
        self._abrir_form("Editar Personagem", personagem)

    def _abrir_form(self, titulo, personagem=None):
        janela = ctk.CTkToplevel(self)
        janela.title(titulo)
        janela.geometry("350x360")
        janela.grab_set()
        janela.resizable(False, False)

        ctk.CTkLabel(janela, text=titulo,
            font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 15))

        ctk.CTkLabel(janela, text="Nome").pack(anchor="w", padx=30)
        entry_nome = ctk.CTkEntry(janela, width=290)
        entry_nome.pack(padx=30, pady=(0, 10))

        ctk.CTkLabel(janela, text="Clã").pack(anchor="w", padx=30)
        combo_cla = ctk.CTkComboBox(janela, values=CLAS, width=290, state="readonly")
        combo_cla.pack(padx=30, pady=(0, 10))

        ctk.CTkLabel(janela, text="Nível").pack(anchor="w", padx=30)
        entry_nivel = ctk.CTkEntry(janela, width=290)
        entry_nivel.pack(padx=30, pady=(0, 15))

        if personagem:
            entry_nome.insert(0, personagem["nome"])
            combo_cla.set(personagem["cla"])
            entry_nivel.insert(0, str(personagem["nivel"]))

        mensagem = ctk.CTkLabel(janela, text="", text_color="red")
        mensagem.pack()

        def salvar():
            nome = entry_nome.get().strip()
            cla = combo_cla.get()
            nivel = entry_nivel.get().strip()

            if not nome or not cla or not nivel:
                mensagem.configure(text="Preencha todos os campos.")
                return
            if not nivel.isdigit() or not (5 <= int(nivel) <= 625):
                mensagem.configure(text="Nível deve ser entre 5 e 625.")
                return

            conn = conectar()
            cursor = conn.cursor()
            if personagem:
                cursor.execute("UPDATE personagens SET nome=?, cla=?, nivel=? WHERE id=?",
                    (nome, cla, int(nivel), personagem["id"]))
            else:
                cursor.execute("INSERT INTO personagens (usuario_id, nome, cla, nivel) VALUES (?, ?, ?, ?)",
                    (self.usuario["id"], nome, cla, int(nivel)))
            conn.commit()
            conn.close()

            janela.destroy()
            self._carregar_personagens()

        ctk.CTkButton(janela, text="Salvar", width=290, command=salvar).pack(padx=30, pady=5)

    def _confirmar_remover(self, personagem_id):
        janela = ctk.CTkToplevel(self)
        janela.title("Confirmar")
        janela.geometry("300x150")
        janela.grab_set()
        janela.resizable(False, False)

        ctk.CTkLabel(janela, text="Deseja apagar este personagem?",
            font=ctk.CTkFont(size=14)).pack(pady=25)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack()

        ctk.CTkButton(botoes, text="Sim, apagar", width=120, fg_color="red",
            command=lambda: [janela.destroy(), self._remover(personagem_id)]).pack(side="left", padx=10)

        ctk.CTkButton(botoes, text="Cancelar", width=120, fg_color="transparent",
            border_width=1, command=janela.destroy).pack(side="left", padx=10)

    def _remover(self, personagem_id):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM hunts WHERE personagem_id = ?", (personagem_id,))
        hunts = cursor.fetchall()

        for hunt in hunts:
            cursor.execute("DELETE FROM hunt_drops WHERE hunt_id = ?", (hunt["id"],))
            cursor.execute("DELETE FROM hunt_gastos WHERE hunt_id = ?", (hunt["id"],))
            cursor.execute("DELETE FROM hunt_inimigos WHERE hunt_id = ?", (hunt["id"],))

        cursor.execute("DELETE FROM hunts WHERE personagem_id = ?", (personagem_id,))
        cursor.execute("DELETE FROM personagens WHERE id = ?", (personagem_id,))
        conn.commit()
        conn.close()
        self._carregar_personagens()