import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio

class TelaHistorico(ctk.CTkToplevel):
    def __init__(self, master, personagem):
        super().__init__(master)
        self.personagem = personagem
        self.title(f"Histórico — {personagem['nome']}")
        self.geometry("600x600")
        self.grab_set()
        self._construir()
        self._carregar_hunts()

    def _construir(self):
        ctk.CTkLabel(self, text=f"Histórico de {self.personagem['nome']}",
            font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        self.frame_lista = ctk.CTkScrollableFrame(self, width=540, height=480)
        self.frame_lista.pack(pady=10, padx=20)

    def _carregar_hunts(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM hunts WHERE personagem_id = ?
            ORDER BY criado_em DESC
        """, (self.personagem["id"],))
        hunts = cursor.fetchall()
        conn.close()

        if not hunts:
            ctk.CTkLabel(self.frame_lista, text="Nenhuma hunt registrada.").pack(pady=20)
            return

        for hunt in hunts:
            self._criar_card_hunt(hunt)

    def _criar_card_hunt(self, hunt):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM hunt_drops WHERE hunt_id = ?", (hunt["id"],))
        drops = [dict(d) for d in cursor.fetchall()]

        cursor.execute("SELECT * FROM hunt_gastos WHERE hunt_id = ?", (hunt["id"],))
        gastos = [dict(g) for g in cursor.fetchall()]

        cursor.execute("SELECT * FROM hunt_inimigos WHERE hunt_id = ?", (hunt["id"],))
        inimigos = [dict(i) for i in cursor.fetchall()]
        conn.close()

        calculos = calcular_hunt(hunt["duracao_minutos"], drops, gastos)
        total_inimigos = sum(i["quantidade"] for i in inimigos)
        inimigos_calc = calcular_inimigos(total_inimigos, hunt["duracao_minutos"])

        horas = hunt["duracao_minutos"] // 60
        minutos = hunt["duracao_minutos"] % 60

        card = ctk.CTkFrame(self.frame_lista)
        card.pack(fill="x", pady=6, padx=5)

        ctk.CTkLabel(card, text=f"📅 {hunt['criado_em'][:16]}",
            font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=10, pady=(8, 2))

        ctk.CTkLabel(card, text=f"⏱ {horas}h{minutos:02d}min   ⚔️ {inimigos_calc['total']} inimigos ({inimigos_calc['por_hora']}/h)").pack(anchor="w", padx=10)
        ctk.CTkLabel(card, text=f"💰 Lucro NPC: {calculos['lucro_npc']:,} gp ({calculos['lucro_npc_hora']:,}/h)").pack(anchor="w", padx=10)
        ctk.CTkLabel(card, text=f"💰 Lucro Jogador: {calculos['lucro_jogador']:,} gp ({calculos['lucro_jogador_hora']:,}/h)").pack(anchor="w", padx=10, pady=(0, 5))

        botoes = ctk.CTkFrame(card, fg_color="transparent")
        botoes.pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkButton(botoes, text="Ver relatório completo", width=200,
            command=lambda h=hunt, d=drops, g=gastos, i=inimigos, c=calculos, ic=inimigos_calc:
                self._ver_relatorio(h, d, g, i, c, ic)).pack(side="left")

        ctk.CTkButton(botoes, text="🗑 Apagar", width=100,
            fg_color="transparent", border_width=1, text_color="red",
            command=lambda hid=hunt["id"]: self._confirmar_apagar(hid)).pack(side="right")

    def _confirmar_apagar(self, hunt_id):
        janela = ctk.CTkToplevel(self)
        janela.title("Confirmar")
        janela.geometry("300x150")
        janela.grab_set()
        janela.resizable(False, False)

        ctk.CTkLabel(janela, text="Deseja apagar esta hunt?",
            font=ctk.CTkFont(size=14)).pack(pady=25)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack()

        ctk.CTkButton(botoes, text="Sim, apagar", width=120, fg_color="red",
            command=lambda: [janela.destroy(), self._apagar_hunt(hunt_id)]).pack(side="left", padx=10)

        ctk.CTkButton(botoes, text="Cancelar", width=120, fg_color="transparent",
            border_width=1, command=janela.destroy).pack(side="left", padx=10)

    def _apagar_hunt(self, hunt_id):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hunt_drops WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunt_gastos WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunt_inimigos WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunts WHERE id = ?", (hunt_id,))
        conn.commit()
        conn.close()
        self._carregar_hunts()

    def _ver_relatorio(self, hunt, drops, gastos, inimigos, calculos, inimigos_calc):
        relatorio = gerar_relatorio(
            self.personagem["nome"], hunt["duracao_minutos"],
            drops, gastos, inimigos, calculos, inimigos_calc
        )

        janela = ctk.CTkToplevel(self)
        janela.title("Relatório da Hunt")
        janela.geometry("500x600")
        janela.grab_set()

        ctk.CTkLabel(janela, text="Resumo da Hunt",
            font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        texto = ctk.CTkTextbox(janela, width=450, height=400)
        texto.pack(pady=10)
        texto.insert("end", relatorio)
        texto.configure(state="disabled")

        ctk.CTkButton(janela, text="Copiar", width=200,
            command=lambda: self._copiar(relatorio)).pack(pady=5)
        ctk.CTkButton(janela, text="Fechar", width=200,
            fg_color="transparent", border_width=1,
            command=janela.destroy).pack(pady=5)

    def _copiar(self, texto):
        self.clipboard_clear()
        self.clipboard_append(texto)