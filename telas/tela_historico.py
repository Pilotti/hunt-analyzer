import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio
from assets.theme import CORES
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

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
        self._hunts_selecionadas = []
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

        ctk.CTkButton(inner, text="📊 Gráficos", width=110,
            fg_color="transparent", border_width=1,
            border_color=CORES["ouro"],
            text_color=CORES["ouro"],
            hover_color=CORES["bg_input"],
            command=self._abrir_graficos).pack(side="right", padx=5)

        ctk.CTkButton(inner, text="⚖ Comparar", width=110,
            fg_color="transparent", border_width=1,
            border_color=CORES["borda"],
            text_color=CORES["texto_secundario"],
            hover_color=CORES["bg_input"],
            command=self._abrir_comparativo).pack(side="right", padx=5)

        ctk.CTkFrame(self, fg_color=CORES["ouro_escuro"], height=2, corner_radius=0).pack(fill="x")

        # Filtros
        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(filtros, text="Ordenar:",
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))

        self.ordem = ctk.CTkComboBox(filtros,
            values=["Data (recente)", "Data (antiga)", "Maior lucro", "Menor lucro", "Maior duração"],
            width=170, state="readonly",
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"],
            button_color=CORES["borda"],
            dropdown_fg_color=CORES["bg_card"],
            command=lambda v: self._carregar_hunts())
        self.ordem.set("Data (recente)")
        self.ordem.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(filtros, text="Período:",
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 5))

        self.periodo = ctk.CTkComboBox(filtros,
            values=["Todos", "Hoje", "Últimos 7 dias", "Últimos 30 dias", "Últimos 90 dias"],
            width=160, state="readonly",
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"],
            button_color=CORES["borda"],
            dropdown_fg_color=CORES["bg_card"],
            command=lambda v: self._carregar_hunts())
        self.periodo.set("Todos")
        self.periodo.pack(side="left")

        # Card resumo
        self.card_resumo = ctk.CTkFrame(self, fg_color=CORES["bg_card"],
            corner_radius=10, border_width=1, border_color=CORES["borda_ouro"])
        self.card_resumo.pack(fill="x", padx=20, pady=10)

        self.resumo_labels = ctk.CTkFrame(self.card_resumo, fg_color="transparent")
        self.resumo_labels.pack(fill="x", padx=15, pady=10)

        self.frame_lista = ctk.CTkScrollableFrame(self,
            fg_color="transparent",
            scrollbar_button_color=CORES["borda"])
        self.frame_lista.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _filtrar_por_periodo(self, hunts):
        periodo = self.periodo.get() if hasattr(self, "periodo") else "Todos"
        if periodo == "Todos":
            return hunts

        agora = datetime.now()
        if periodo == "Hoje":
            limite = agora.replace(hour=0, minute=0, second=0)
        elif periodo == "Últimos 7 dias":
            limite = agora - timedelta(days=7)
        elif periodo == "Últimos 30 dias":
            limite = agora - timedelta(days=30)
        elif periodo == "Últimos 90 dias":
            limite = agora - timedelta(days=90)
        else:
            return hunts

        filtrados = []
        for hunt in hunts:
            try:
                data_hunt = datetime.strptime(hunt["criado_em"][:16], "%Y-%m-%d %H:%M")
                if data_hunt >= limite:
                    filtrados.append(hunt)
            except:
                filtrados.append(hunt)
        return filtrados

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

        media_hora = round((total_lucro_jogador / total_duracao) * 60) if total_duracao > 0 else 0

        for texto, valor, cor in [
            ("🗂 Hunts", str(total_hunts), CORES["texto_principal"]),
            ("⏱ Tempo total", f"{horas}h{minutos:02d}min", CORES["texto_principal"]),
            ("💰 Lucro NPC", f"${total_lucro_npc:,}", CORES["verde"] if total_lucro_npc >= 0 else CORES["vermelho"]),
            ("💰 Lucro Jogador", f"${total_lucro_jogador:,}", CORES["verde"] if total_lucro_jogador >= 0 else CORES["vermelho"]),
            ("⚡ Média/hora", f"${media_hora:,}", CORES["verde"] if media_hora >= 0 else CORES["vermelho"]),
        ]:
            frame = ctk.CTkFrame(self.resumo_labels, fg_color="transparent")
            frame.pack(side="left", expand=True)
            ctk.CTkLabel(frame, text=texto,
                font=ctk.CTkFont(size=11),
                text_color=CORES["texto_secundario"]).pack()
            ctk.CTkLabel(frame, text=valor,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=cor).pack()

    def _carregar_hunts(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
        self._hunts_selecionadas = []

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

        hunts = self._filtrar_por_periodo(hunts)

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
            ctk.CTkLabel(self.frame_lista, text="Nenhuma hunt no período selecionado.",
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

        # Checkbox para comparativo
        sel_var = ctk.BooleanVar(value=False)
        check = ctk.CTkCheckBox(body, text="", variable=sel_var, width=24,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            border_color=CORES["borda"],
            command=lambda h=dict(hunt), c=calculos, v=sel_var: self._toggle_selecao(h, c, v))
        check.pack(side="left", padx=(0, 10))

        left = ctk.CTkFrame(body, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

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
            if bonus_loot:
                nomes = ", ".join([f"{b['nome']} x{b['quantidade']}" for b in bonus_loot])
                ctk.CTkLabel(left, text=f"🍀 {nomes}",
                    font=ctk.CTkFont(size=11),
                    text_color=CORES["ouro"]).pack(anchor="w", pady=(2, 0))

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

    def _toggle_selecao(self, hunt, calculos, var):
        if var.get():
            if len(self._hunts_selecionadas) >= 2:
                var.set(False)
                self._mostrar_aviso("Selecione no máximo 2 hunts para comparar.")
                return
            self._hunts_selecionadas.append({"hunt": hunt, "calculos": calculos})
        else:
            self._hunts_selecionadas = [h for h in self._hunts_selecionadas if h["hunt"]["id"] != hunt["id"]]

    def _mostrar_aviso(self, msg):
        janela = ctk.CTkToplevel(self)
        janela.title("Atenção")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 320, 130)
        ctk.CTkLabel(janela, text=msg, font=ctk.CTkFont(size=13),
            text_color=CORES["texto_principal"], wraplength=280).pack(pady=20)
        ctk.CTkButton(janela, text="OK", width=100,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", command=janela.destroy).pack()

    def _abrir_comparativo(self):
        if len(self._hunts_selecionadas) != 2:
            self._mostrar_aviso("Selecione exatamente 2 hunts para comparar.\n\nUse os checkboxes ao lado de cada hunt.")
            return

        h1 = self._hunts_selecionadas[0]
        h2 = self._hunts_selecionadas[1]

        janela = ctk.CTkToplevel(self)
        janela.title("Comparativo de Hunts")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 700, 500)

        ctk.CTkLabel(janela, text="⚖ Comparativo de Hunts",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=CORES["ouro"]).pack(pady=(15, 10))

        content = ctk.CTkFrame(janela, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=5)

        for col, dados in enumerate([h1, h2]):
            hunt = dados["hunt"]
            calc = dados["calculos"]
            horas = hunt["duracao_minutos"] // 60
            mins = hunt["duracao_minutos"] % 60
            cor_lucro = CORES["verde"] if calc["lucro_jogador"] >= 0 else CORES["vermelho"]

            card = ctk.CTkFrame(content, fg_color=CORES["bg_card"],
                corner_radius=10, border_width=1, border_color=CORES["borda"])
            card.grid(row=0, column=col, padx=10, sticky="nsew")
            content.grid_columnconfigure(col, weight=1)

            ctk.CTkFrame(card, fg_color=cor_lucro, height=3, corner_radius=0).pack(fill="x")

            ctk.CTkLabel(card, text=f"Hunt {col + 1}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=CORES["ouro"]).pack(pady=(12, 4))

            ctk.CTkLabel(card, text=hunt["criado_em"][:16],
                font=ctk.CTkFont(size=11),
                text_color=CORES["texto_secundario"]).pack()

            ctk.CTkFrame(card, fg_color=CORES["borda"], height=1).pack(fill="x", padx=15, pady=8)

            itens = [
                ("⏱ Duração", f"{horas}h{mins:02d}min", CORES["texto_principal"]),
                ("💰 Loot NPC", f"${calc['total_npc']:,}", CORES["verde"]),
                ("💰 Loot Jogador", f"${calc['total_jogador']:,}", CORES["verde"]),
                ("💸 Gastos", f"-${calc['total_gastos']:,}", CORES["vermelho"]),
                ("✅ Lucro NPC", f"${calc['lucro_npc']:,}", CORES["verde"] if calc["lucro_npc"] >= 0 else CORES["vermelho"]),
                ("✅ Lucro Jogador", f"${calc['lucro_jogador']:,}", cor_lucro),
                ("⚡ Média/hora", f"${calc['lucro_jogador_hora']:,}/h", cor_lucro),
            ]

            for label, valor, cor in itens:
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=2)
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(size=12),
                    text_color=CORES["texto_secundario"], anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=valor, font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=cor, anchor="e").pack(side="right")

        # Vencedor
        lucro1 = h1["calculos"]["lucro_jogador"]
        lucro2 = h2["calculos"]["lucro_jogador"]
        if lucro1 > lucro2:
            vencedor = f"🏆 Hunt 1 foi mais lucrativa por ${lucro1 - lucro2:,}"
            cor_v = CORES["verde"]
        elif lucro2 > lucro1:
            vencedor = f"🏆 Hunt 2 foi mais lucrativa por ${lucro2 - lucro1:,}"
            cor_v = CORES["verde"]
        else:
            vencedor = "🤝 As duas hunts tiveram o mesmo lucro!"
            cor_v = CORES["ouro"]

        ctk.CTkLabel(janela, text=vencedor,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=cor_v).pack(pady=10)

    def _abrir_graficos(self):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hunts WHERE personagem_id = ? ORDER BY criado_em ASC",
            (self.personagem["id"],))
        hunts = list(cursor.fetchall())
        conn.close()

        hunts = self._filtrar_por_periodo(hunts)

        if len(hunts) < 2:
            self._mostrar_aviso("É necessário ter pelo menos 2 hunts para gerar gráficos.")
            return

        datas = []
        lucros_hora = []
        lucros_total = []

        for hunt in hunts:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hunt_drops WHERE hunt_id = ?", (hunt["id"],))
            drops = [dict(d) for d in cursor.fetchall()]
            cursor.execute("SELECT * FROM hunt_gastos WHERE hunt_id = ?", (hunt["id"],))
            gastos = [dict(g) for g in cursor.fetchall()]
            conn.close()

            calculos = calcular_hunt(hunt["duracao_minutos"], drops, gastos)
            try:
                data = datetime.strptime(hunt["criado_em"][:16], "%Y-%m-%d %H:%M")
            except:
                data = datetime.now()

            datas.append(data)
            lucros_hora.append(calculos["lucro_jogador_hora"])
            lucros_total.append(calculos["lucro_jogador"])

        janela = ctk.CTkToplevel(self)
        janela.title("Gráficos")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 800, 550)

        ctk.CTkLabel(janela, text="📊 Evolução das Hunts",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=CORES["ouro"]).pack(pady=(15, 5))

        fig = Figure(figsize=(7.5, 4.5), facecolor="#1a1a1a")

        ax1 = fig.add_subplot(1, 2, 1)
        ax1.set_facecolor("#242424")
        cores_barras = [CORES["verde"] if v >= 0 else CORES["vermelho"] for v in lucros_hora]
        ax1.bar(range(len(lucros_hora)), lucros_hora, color=cores_barras, width=0.6)
        ax1.set_title("Lucro/hora por Hunt", color=CORES["ouro"], fontsize=11)
        ax1.set_xlabel("Hunt #", color=CORES["texto_secundario"], fontsize=9)
        ax1.set_ylabel("$/h", color=CORES["texto_secundario"], fontsize=9)
        ax1.tick_params(colors=CORES["texto_secundario"])
        ax1.spines['bottom'].set_color(CORES["borda"])
        ax1.spines['left'].set_color(CORES["borda"])
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.axhline(y=0, color=CORES["borda"], linewidth=0.8)

        ax2 = fig.add_subplot(1, 2, 2)
        ax2.set_facecolor("#242424")
        acumulado = []
        soma = 0
        for v in lucros_total:
            soma += v
            acumulado.append(soma)
        cor_linha = CORES["verde"] if acumulado[-1] >= 0 else CORES["vermelho"]
        ax2.plot(range(len(acumulado)), acumulado, color=cor_linha, linewidth=2, marker='o', markersize=4)
        ax2.fill_between(range(len(acumulado)), acumulado, alpha=0.15, color=cor_linha)
        ax2.set_title("Lucro acumulado", color=CORES["ouro"], fontsize=11)
        ax2.set_xlabel("Hunt #", color=CORES["texto_secundario"], fontsize=9)
        ax2.set_ylabel("$", color=CORES["texto_secundario"], fontsize=9)
        ax2.tick_params(colors=CORES["texto_secundario"])
        ax2.spines['bottom'].set_color(CORES["borda"])
        ax2.spines['left'].set_color(CORES["borda"])
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.axhline(y=0, color=CORES["borda"], linewidth=0.8)

        fig.tight_layout(pad=2.0)

        canvas = FigureCanvasTkAgg(fig, master=janela)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 15))

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