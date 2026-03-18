import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio
from assets.theme import CORES

def _centralizar(janela, largura, altura):
    janela.update_idletasks()
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

class TelaHistorico(ctk.CTkFrame):
    def __init__(self, master, personagem, ao_voltar):
        super().__init__(master, fg_color=CORES["bg_principal"])
        self.personagem = personagem
        self.ao_voltar = ao_voltar
        self._construir()
        self._carregar_hunts()

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color=CORES["bg_header"], corner_radius=0)
        header.pack(fill="x")

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)

        ctk.CTkButton(inner, text="← Voltar", width=90,
            fg_color="transparent", border_width=1,
            border_color=CORES["borda"],
            text_color=CORES["texto_secundario"],
            hover_color=CORES["bg_input"],
            command=self.ao_voltar).pack(side="left")

        ctk.CTkLabel(inner, text=f"📋 Histórico — {self.personagem['nome']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=CORES["texto_principal"]).pack(side="left", padx=15)

        ctk.CTkFrame(self, fg_color=CORES["ouro_escuro"], height=2, corner_radius=0).pack(fill="x")

        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(filtros, text="Ordenar por:",
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 8))

        self.ordem = ctk.CTkComboBox(filtros,
            values=["Data (recente)", "Data (antiga)", "Maior lucro", "Menor lucro", "Maior duração"],
            width=190, state="readonly",
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"],
            button_color=CORES["borda"],
            dropdown_fg_color=CORES["bg_card"],
            command=lambda v: self._carregar_hunts())
        self.ordem.set("Data (recente)")
        self.ordem.pack(side="left")

        self.card_resumo = ctk.CTkFrame(self, fg_color=CORES["bg_card"],
            corner_radius=10, border_width=1, border_color=CORES["borda_ouro"])
        self.card_resumo.pack(fill="x", padx=20, pady=10)

        self.resumo_labels = ctk.CTkFrame(self.card_resumo, fg_color="transparent")
        self.resumo_labels.pack(fill="x", padx=15, pady=10)

        self.frame_lista = ctk.CTkScrollableFrame(self,
            fg_color="transparent",
            scrollbar_button_color=CORES["borda"])
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _atualizar_resumo_geral(self, hunts_data):
        for widget in self.resumo_labels.winfo_children():
            widget.destroy()

        if not hunts_data:
            ctk.CTkLabel(self.resumo_labels, text="Nenhuma hunt registrada.",
                text_color=CORES["texto_secundario"]).pack(side="left")
            return

        total_hunts = len(hunts_data)
        total_duracao = sum(h["duracao"] for h in hunts_data)
        total_lucro_npc = sum(h["lucro_npc"] for h in hunts_data)
        total_lucro_jogador = sum(h["lucro_jogador"] for h in hunts_data)
        horas = total_duracao // 60
        minutos = total_duracao % 60

        for texto, valor, cor in [
            ("🗂 Hunts", str(total_hunts), CORES["texto_principal"]),
            ("⏱ Tempo total", f"{horas}h{minutos:02d}min", CORES["texto_principal"]),
            ("💰 Lucro NPC", f"${total_lucro_npc:,}", CORES["verde"] if total_lucro_npc >= 0 else CORES["vermelho"]),
            ("💰 Lucro Jogador", f"${total_lucro_jogador:,}", CORES["verde"] if total_lucro_jogador >= 0 else CORES["vermelho"]),
        ]:
            frame = ctk.CTkFrame(self.resumo_labels, fg_color="transparent")
            frame.pack(side="left", expand=True)
            ctk.CTkLabel(frame, text=texto,
                font=ctk.CTkFont(size=11),
                text_color=CORES["texto_secundario"]).pack()
            ctk.CTkLabel(frame, text=valor,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=cor).pack()

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
            ctk.CTkLabel(self.frame_lista, text="Nenhuma hunt registrada.",
                text_color=CORES["texto_secundario"]).pack(pady=30)
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

        cursor.execute("SELECT * FROM hunt_bonus WHERE hunt_id = ?", (hunt["id"],))
        bonus = [dict(b) for b in cursor.fetchall()]
        conn.close()

        calculos = calcular_hunt(hunt["duracao_minutos"], drops, gastos)
        total_inimigos = sum(i["quantidade"] for i in inimigos)
        inimigos_calc = calcular_inimigos(total_inimigos, hunt["duracao_minutos"])

        horas = hunt["duracao_minutos"] // 60
        minutos = hunt["duracao_minutos"] % 60

        lucro_j = calculos["lucro_jogador"]
        cor_lucro = CORES["verde"] if lucro_j >= 0 else CORES["vermelho"]

        card = ctk.CTkFrame(self.frame_lista, fg_color=CORES["bg_card"],
            corner_radius=10, border_width=1, border_color=CORES["borda"])
        card.pack(fill="x", pady=5)

        ctk.CTkFrame(card, fg_color=cor_lucro, height=2, corner_radius=0).pack(fill="x")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="x", padx=15, pady=10)

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        # Data e duração na mesma linha
        linha_topo = ctk.CTkFrame(left, fg_color="transparent")
        linha_topo.pack(fill="x", anchor="w")
        ctk.CTkLabel(linha_topo, text=f"📅 {hunt['criado_em'][:16]}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=CORES["ouro"]).pack(side="left")
        ctk.CTkLabel(linha_topo, text=f"⏱ {horas}h{minutos:02d}min",
            font=ctk.CTkFont(size=12),
            text_color=CORES["texto_secundario"]).pack(side="right")

        ctk.CTkLabel(left,
            text=f"⚔️ {inimigos_calc['total']} inimigos ({inimigos_calc['por_hora']}/h)",
            font=ctk.CTkFont(size=12),
            text_color=CORES["texto_secundario"]).pack(anchor="w", pady=(2, 0))

        ctk.CTkLabel(left,
            text=f"💰 NPC: ${calculos['lucro_npc']:,} (${calculos['lucro_npc_hora']:,}/h)",
            font=ctk.CTkFont(size=12),
            text_color=CORES["verde"] if calculos["lucro_npc"] >= 0 else CORES["vermelho"]).pack(anchor="w")

        ctk.CTkLabel(left,
            text=f"💰 Jogador: ${calculos['lucro_jogador']:,} (${calculos['lucro_jogador_hora']:,}/h)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=cor_lucro).pack(anchor="w")

        if bonus:
            bonus_loot = [b for b in bonus if b["tipo"] == "loot"]
            bonus_geral = [b for b in bonus if b["tipo"] == "geral"]

            if bonus_loot:
                nomes = ", ".join([f"{b['nome']} x{b['quantidade']}" for b in bonus_loot])
                ctk.CTkLabel(left, text=f"🍀 {nomes}",
                    font=ctk.CTkFont(size=11),
                    text_color=CORES["ouro"]).pack(anchor="w", pady=(2, 0))

            if bonus_geral:
                nomes = ", ".join([f"{b['nome']} x{b['quantidade']}" for b in bonus_geral])
                ctk.CTkLabel(left, text=f"⚡ {nomes}",
                    font=ctk.CTkFont(size=11),
                    text_color=CORES["texto_secundario"]).pack(anchor="w")

        right = ctk.CTkFrame(body, fg_color="transparent")
        right.pack(side="right")

        ctk.CTkButton(right, text="Ver relatório", width=120,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda h=hunt, d=drops, g=gastos, i=inimigos, c=calculos, ic=inimigos_calc, b=bonus:
                self._ver_relatorio(h, d, g, i, c, ic, b)).pack(pady=3)

        ctk.CTkButton(right, text="🗑 Apagar", width=120,
            fg_color="transparent", border_width=1,
            border_color=CORES["vermelho"],
            text_color=CORES["vermelho"],
            hover_color=CORES["bg_input"],
            command=lambda hid=hunt["id"]: self._confirmar_apagar(hid)).pack(pady=3)

    def _confirmar_apagar(self, hunt_id):
        janela = ctk.CTkToplevel(self)
        janela.title("Confirmar")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 320, 160)

        ctk.CTkLabel(janela, text="Deseja apagar esta hunt?",
            font=ctk.CTkFont(size=14),
            text_color=CORES["texto_principal"]).pack(pady=25)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack()

        ctk.CTkButton(botoes, text="Sim, apagar", width=120,
            fg_color=CORES["vermelho"], hover_color=CORES["vermelho_hover"],
            command=lambda: [janela.destroy(), self._apagar_hunt(hunt_id)]).pack(side="left", padx=10)

        ctk.CTkButton(botoes, text="Cancelar", width=120,
            fg_color="transparent", border_width=1, border_color=CORES["borda"],
            text_color=CORES["texto_secundario"], hover_color=CORES["bg_input"],
            command=janela.destroy).pack(side="left", padx=10)

    def _apagar_hunt(self, hunt_id):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM hunt_drops WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunt_gastos WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunt_inimigos WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunt_bonus WHERE hunt_id = ?", (hunt_id,))
        cursor.execute("DELETE FROM hunts WHERE id = ?", (hunt_id,))
        conn.commit()
        conn.close()
        self._carregar_hunts()

    def _ver_relatorio(self, hunt, drops, gastos, inimigos, calculos, inimigos_calc, bonus):
        relatorio = gerar_relatorio(
            self.personagem["nome"], hunt["duracao_minutos"],
            drops, gastos, inimigos, calculos, inimigos_calc, bonus
        )

        janela = ctk.CTkToplevel(self)
        janela.title("Relatório da Hunt")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 500, 580)

        ctk.CTkLabel(janela, text="⚔ Resumo da Hunt",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=CORES["ouro"]).pack(pady=(15, 8))

        scroll = ctk.CTkScrollableFrame(janela, width=440, height=400,
            fg_color=CORES["bg_card"])
        scroll.pack(pady=5, padx=20)

        lucro_jogador = calculos["lucro_jogador"]
        lucro_npc = calculos["lucro_npc"]

        def add(texto, cor, bold=False, indent=0):
            ctk.CTkLabel(scroll,
                text=texto if texto else " ",
                font=ctk.CTkFont(size=12, weight="bold" if bold else "normal"),
                text_color=cor, anchor="w").pack(
                    fill="x", padx=(10 + indent, 10), pady=0)

        def sep():
            ctk.CTkFrame(scroll, fg_color=CORES["borda"], height=1).pack(
                fill="x", padx=10, pady=3)

        for linha in relatorio.split("\n"):
            l = linha.strip()

            if l.startswith("HEADER|"):
                _, nome, duracao = l.split("|")
                row = ctk.CTkFrame(scroll, fg_color="transparent")
                row.pack(fill="x", padx=10, pady=(8, 4))
                ctk.CTkLabel(row, text=f"👤 {nome}",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    text_color=CORES["ouro"]).pack(side="left")
                ctk.CTkLabel(row, text=f"⏱ {duracao}",
                    font=ctk.CTkFont(size=12),
                    text_color=CORES["texto_secundario"]).pack(side="right")
                sep()

            elif l == "SEP":
                sep()

            elif l.startswith("⚔️ Inimigos"):
                add(l, CORES["texto_principal"])

            elif l.startswith("🍀") or l.startswith("⚡"):
                add(l, CORES["ouro"], bold=True)

            elif l.startswith("📦") or l.startswith("🧪") or l.startswith("📝"):
                add(l, CORES["ouro"], bold=True)

            elif l.startswith("•") and "+$" in l:
                add(f"  {l}", CORES["verde"], indent=10)

            elif l.startswith("•") and "-$" in l:
                add(f"  {l}", CORES["vermelho"], indent=10)

            elif l.startswith("•"):
                add(f"  {l}", CORES["texto_secundario"], indent=10)

            elif l.startswith("💰 Loot"):
                add(l, CORES["verde"])

            elif l.startswith("💸"):
                add(l, CORES["vermelho"])

            elif l.startswith("✅ Lucro NPC") or l.startswith("❌ Lucro NPC"):
                cor = CORES["verde"] if lucro_npc >= 0 else CORES["vermelho"]
                add(l, cor, bold=True)

            elif l.startswith("✅ Lucro Jogador") or l.startswith("❌ Lucro Jogador"):
                cor = CORES["verde"] if lucro_jogador >= 0 else CORES["vermelho"]
                add(l, cor, bold=True)

            elif l:
                add(l, CORES["texto_secundario"], indent=10)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack(pady=8)

        ctk.CTkButton(botoes, text="📋 Copiar", width=130,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._copiar(relatorio)).pack(side="left", padx=5)

        ctk.CTkButton(botoes, text="💾 Salvar .txt", width=130,
            fg_color="transparent", border_width=1, border_color=CORES["ouro"],
            text_color=CORES["ouro"], hover_color=CORES["bg_input"],
            command=lambda: self._salvar_txt(relatorio, self.personagem["nome"])).pack(side="left", padx=5)

        ctk.CTkButton(botoes, text="Fechar", width=130,
            fg_color="transparent", border_width=1, border_color=CORES["borda"],
            text_color=CORES["texto_secundario"], hover_color=CORES["bg_input"],
            command=janela.destroy).pack(side="left", padx=5)

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