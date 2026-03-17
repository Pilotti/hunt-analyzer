import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio

class TelaHistorico(ctk.CTkFrame):
    def __init__(self, master, personagem, ao_voltar):
        super().__init__(master, fg_color="transparent")
        self.personagem = personagem
        self.ao_voltar = ao_voltar
        self._construir()
        self._carregar_hunts()

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 0))

        ctk.CTkLabel(header, text=f"Histórico — {self.personagem['nome']}",
            font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        ctk.CTkButton(header, text="← Voltar", width=100, fg_color="transparent",
            border_width=1, command=self.ao_voltar).pack(side="right")

        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=30, pady=(10, 0))

        ctk.CTkLabel(filtros, text="Ordenar por:").pack(side="left", padx=(0, 5))

        self.ordem = ctk.CTkComboBox(filtros,
            values=["Data (recente)", "Data (antiga)", "Maior lucro", "Menor lucro", "Maior duração"],
            width=180, state="readonly",
            command=lambda v: self._carregar_hunts())
        self.ordem.set("Data (recente)")
        self.ordem.pack(side="left", padx=5)

        self.card_resumo = ctk.CTkFrame(self, fg_color="#1e1e1e")
        self.card_resumo.pack(fill="x", padx=30, pady=(15, 0))

        self.resumo_labels = ctk.CTkFrame(self.card_resumo, fg_color="transparent")
        self.resumo_labels.pack(fill="x", padx=15, pady=10)

        self.frame_lista = ctk.CTkScrollableFrame(self)
        self.frame_lista.pack(fill="both", expand=True, padx=30, pady=20)

    def _atualizar_resumo_geral(self, hunts_data):
        for widget in self.resumo_labels.winfo_children():
            widget.destroy()

        if not hunts_data:
            ctk.CTkLabel(self.resumo_labels, text="Nenhuma hunt registrada.",
                text_color="gray").pack(side="left")
            return

        total_hunts = len(hunts_data)
        total_duracao = sum(h["duracao"] for h in hunts_data)
        total_lucro_npc = sum(h["lucro_npc"] for h in hunts_data)
        total_lucro_jogador = sum(h["lucro_jogador"] for h in hunts_data)
        horas = total_duracao // 60
        minutos = total_duracao % 60

        for texto, valor in [
            ("🗂 Hunts", str(total_hunts)),
            ("⏱ Tempo total", f"{horas}h{minutos:02d}min"),
            ("💰 Lucro NPC", f"{total_lucro_npc:,} gp"),
            ("💰 Lucro Jogador", f"{total_lucro_jogador:,} gp"),
        ]:
            frame = ctk.CTkFrame(self.resumo_labels, fg_color="transparent")
            frame.pack(side="left", expand=True)
            ctk.CTkLabel(frame, text=texto, font=ctk.CTkFont(size=11), text_color="gray").pack()
            ctk.CTkLabel(frame, text=valor, font=ctk.CTkFont(size=14, weight="bold")).pack()

    def _carregar_hunts(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()

        ordem = self.ordem.get() if hasattr(self, "ordem") else "Data (recente)"

        if ordem == "Data (recente)":
            order_sql = "ORDER BY criado_em DESC"
        elif ordem == "Data (antiga)":
            order_sql = "ORDER BY criado_em ASC"
        else:
            order_sql = "ORDER BY criado_em DESC"

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM hunts WHERE personagem_id = ? {order_sql}",
            (self.personagem["id"],))
        hunts = list(cursor.fetchall())
        conn.close()

        hunts_data = []
        hunts_com_calculos = []

        for hunt in hunts:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hunt_drops WHERE hunt_id = ?", (hunt["id"],))
            drops = [dict(d) for d in cursor.fetchall()]
            cursor.execute("SELECT * FROM hunt_gastos WHERE hunt_id = ?", (hunt["id"],))
            gastos = [dict(g) for g in cursor.fetchall()]
            conn.close()

            calculos = calcular_hunt(hunt["duracao_minutos"], drops, gastos)
            hunts_data.append({
                "duracao": hunt["duracao_minutos"],
                "lucro_npc": calculos["lucro_npc"],
                "lucro_jogador": calculos["lucro_jogador"]
            })
            hunts_com_calculos.append((hunt, calculos["lucro_jogador"]))

        if ordem == "Maior lucro":
            hunts = [h for h, _ in sorted(hunts_com_calculos, key=lambda x: x[1], reverse=True)]
        elif ordem == "Menor lucro":
            hunts = [h for h, _ in sorted(hunts_com_calculos, key=lambda x: x[1], reverse=False)]
        elif ordem == "Maior duração":
            hunts = sorted(hunts, key=lambda h: h["duracao_minutos"], reverse=True)

        self._atualizar_resumo_geral(hunts_data)

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
        janela.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 150
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 75
        janela.geometry(f"+{x}+{y}")

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
        janela.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() // 2) - 250
        y = self.master.winfo_y() + (self.master.winfo_height() // 2) - 300
        janela.geometry(f"+{x}+{y}")

        ctk.CTkLabel(janela, text="Resumo da Hunt",
            font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        texto = ctk.CTkTextbox(janela, width=450, height=400)
        texto.pack(pady=10)
        texto.insert("end", relatorio)
        texto.configure(state="disabled")

        ctk.CTkButton(janela, text="Copiar", width=200,
            command=lambda: self._copiar(relatorio)).pack(pady=5)
        ctk.CTkButton(janela, text="💾 Salvar como .txt", width=200,
            command=lambda: self._salvar_txt(relatorio, self.personagem["nome"])).pack(pady=5)
        ctk.CTkButton(janela, text="Fechar", width=200,
            fg_color="transparent", border_width=1,
            command=janela.destroy).pack(pady=5)

    def _salvar_txt(self, relatorio, nome_personagem):
        from tkinter import filedialog
        from datetime import datetime
        nome_arquivo = f"hunt_{nome_personagem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        caminho = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Texto", "*.txt")],
            initialfile=nome_arquivo
        )
        if caminho:
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(relatorio)

    def _copiar(self, texto):
        self.master.clipboard_clear()
        self.master.clipboard_append(texto)