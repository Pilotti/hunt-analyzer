import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio
from utils.search_box import SearchBox
from assets.theme import CORES
import json
import os
import sys

def _get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def _centralizar(janela, largura, altura):
    janela.update_idletasks()
    x = (janela.winfo_screenwidth() // 2) - (largura // 2)
    y = (janela.winfo_screenheight() // 2) - (altura // 2)
    janela.geometry(f"{largura}x{altura}+{x}+{y}")

DROPS_PATH = os.path.join(_get_base_path(), "banco", "itens_drop.json")
CONSUMIVEIS_PATH = os.path.join(_get_base_path(), "banco", "itens_consumivel.json")
INIMIGOS_PATH = os.path.join(_get_base_path(), "banco", "inimigos.json")

BONUS_LOOT = [
    {"nome": "Fortune Totem", "duracao_minutos": 60},
    {"nome": "Jade Fortune Totem", "duracao_minutos": 60},
    {"nome": "Big Fortune Totem", "duracao_minutos": 180},
    {"nome": "Majestic Fortune Totem", "duracao_minutos": 20},
    {"nome": "Bonus Calendario (drop)", "duracao_minutos": 20},
]

BONUS_GERAL = [
    {"nome": "Catcher Totem", "duracao_minutos": 60},
    {"nome": "Scientific Totem", "duracao_minutos": 15},
    {"nome": "Borage Flower", "duracao_minutos": 60},
    {"nome": "Fire Flower", "duracao_minutos": 60},
    {"nome": "Park Totem", "duracao_minutos": 20},
    {"nome": "Bonus Calendario (captura)", "duracao_minutos": 40},
    {"nome": "Bonus Calendario (experiencia)", "duracao_minutos": 60},
]

class TelaHunt(ctk.CTkFrame):
    def __init__(self, master, usuario, personagem, ao_voltar, ao_finalizar):
        super().__init__(master, fg_color=CORES["bg_principal"])
        self.usuario = usuario
        self.personagem = personagem
        self.ao_voltar = ao_voltar
        self.ao_finalizar = ao_finalizar
        self.drops = []
        self.gastos = []
        self.inimigos = []
        self.bonus_vars = {}
        self.bonus_qtd_entries = {}
        self._ultimo_calculos = {}
        self._carregar_banco()
        self._construir()

    def _carregar_banco(self):
        self._erros_banco = []

        try:
            with open(DROPS_PATH, "r", encoding="utf-8") as f:
                self.itens_drop = json.load(f)
            if not self.itens_drop:
                self._erros_banco.append("itens_drop.json está vazio.")
        except FileNotFoundError:
            self.itens_drop = []
            self._erros_banco.append("Arquivo itens_drop.json não encontrado.")
        except json.JSONDecodeError:
            self.itens_drop = []
            self._erros_banco.append("Arquivo itens_drop.json com erro de formatação.")

        try:
            with open(CONSUMIVEIS_PATH, "r", encoding="utf-8") as f:
                self.itens_consumivel = json.load(f)
            if not self.itens_consumivel:
                self._erros_banco.append("itens_consumivel.json está vazio.")
        except FileNotFoundError:
            self.itens_consumivel = []
            self._erros_banco.append("Arquivo itens_consumivel.json não encontrado.")
        except json.JSONDecodeError:
            self.itens_consumivel = []
            self._erros_banco.append("Arquivo itens_consumivel.json com erro de formatação.")

        try:
            with open(INIMIGOS_PATH, "r", encoding="utf-8") as f:
                self.inimigos_banco = json.load(f)
            if not self.inimigos_banco:
                self._erros_banco.append("inimigos.json está vazio.")
        except FileNotFoundError:
            self.inimigos_banco = []
            self._erros_banco.append("Arquivo inimigos.json não encontrado.")
        except json.JSONDecodeError:
            self.inimigos_banco = []
            self._erros_banco.append("Arquivo inimigos.json com erro de formatação.")

    def _construir(self):
        self.master.protocol("WM_DELETE_WINDOW", self._confirmar_fechar)

        if self._erros_banco:
            msg = "\n".join(self._erros_banco)
            self.after(300, lambda: self._mostrar_erro(f"Atenção nos arquivos de banco:\n\n{msg}"))

        header = ctk.CTkFrame(self, fg_color=CORES["bg_header"], corner_radius=0)
        header.pack(fill="x")

        inner = ctk.CTkFrame(header, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)

        ctk.CTkButton(inner, text="← Voltar", width=90,
            fg_color="transparent", border_width=1,
            border_color=CORES["borda"],
            text_color=CORES["texto_secundario"],
            hover_color=CORES["bg_input"],
            command=self._voltar_seguro).pack(side="left")

        ctk.CTkLabel(inner, text=f"⚔ Hunt — {self.personagem['nome']}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=CORES["texto_principal"]).pack(side="left", padx=15)

        self.resumo = ctk.CTkLabel(inner,
            text="Loot NPC: $0  |  Loot Jogador: $0",
            font=ctk.CTkFont(size=12),
            text_color=CORES["ouro"])
        self.resumo.pack(side="right", padx=10)

        ctk.CTkFrame(self, fg_color=CORES["ouro_escuro"], height=2, corner_radius=0).pack(fill="x")

        self.tabs = ctk.CTkTabview(self,
            fg_color=CORES["bg_card"],
            segmented_button_fg_color=CORES["bg_header"],
            segmented_button_selected_color=CORES["ouro"],
            segmented_button_selected_hover_color=CORES["ouro_hover"],
            segmented_button_unselected_color=CORES["bg_header"],
            segmented_button_unselected_hover_color=CORES["bg_input"],
            text_color=CORES["texto_principal"])
        self.tabs.pack(fill="both", expand=True, padx=15, pady=8)

        self.tabs.add("📦 Drops")
        self.tabs.add("🧪 Gastos")
        self.tabs.add("⚔ Inimigos")
        self.tabs.add("🍀 Bônus")
        self.tabs.add("📝 Notas")

        self._construir_aba_drops()
        self._construir_aba_gastos()
        self._construir_aba_inimigos()
        self._construir_aba_bonus()
        self._construir_aba_notas()

        footer = ctk.CTkFrame(self, fg_color=CORES["bg_header"], corner_radius=0)
        footer.pack(fill="x")

        ctk.CTkFrame(footer, fg_color=CORES["ouro_escuro"], height=2, corner_radius=0).pack(fill="x")

        inner_footer = ctk.CTkFrame(footer, fg_color="transparent")
        inner_footer.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(inner_footer, text="Duração:",
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 8))

        self.horas = ctk.CTkEntry(inner_footer, placeholder_text="Horas", width=70,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.horas.pack(side="left", padx=4)
        self.horas.bind("<KeyPress>", self._apenas_numeros)

        ctk.CTkLabel(inner_footer, text="h",
            text_color=CORES["texto_secundario"]).pack(side="left")

        self.minutos = ctk.CTkEntry(inner_footer, placeholder_text="Min", width=70,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.minutos.pack(side="left", padx=4)
        self.minutos.bind("<KeyPress>", self._apenas_numeros)

        ctk.CTkLabel(inner_footer, text="min",
            text_color=CORES["texto_secundario"]).pack(side="left")

        ctk.CTkButton(inner_footer, text="✅ Finalizar Hunt", width=160,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._finalizar).pack(side="right")

    def _construir_barra_input(self, aba, search_attr, search_valores, search_placeholder, qtd_attr, adicionar_cmd):
        row = ctk.CTkFrame(aba, fg_color=CORES["bg_header"], corner_radius=8)
        row.pack(fill="x", pady=(8, 4), padx=5)

        search = SearchBox(row,
            valores=search_valores,
            placeholder=search_placeholder,
            width=220,
            ao_selecionar=lambda v: getattr(self, qtd_attr).focus())
        search.pack(side="left", padx=10, pady=8)
        setattr(self, search_attr, search)

        entry = ctk.CTkEntry(row, placeholder_text="Quantidade", width=100,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        entry.pack(side="left", padx=4, pady=8)
        entry.bind("<Return>", lambda e: adicionar_cmd())
        entry.bind("<KeyPress>", self._apenas_numeros)
        setattr(self, qtd_attr, entry)

        ctk.CTkButton(row, text="+ Adicionar", width=110,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", font=ctk.CTkFont(size=12, weight="bold"),
            command=adicionar_cmd).pack(side="left", padx=8, pady=8)

    def _construir_cabecalho(self, aba, colunas):
        header = ctk.CTkFrame(aba, fg_color=CORES["bg_header"], corner_radius=6)
        header.pack(fill="x", padx=5, pady=(2, 0))
        for texto, w in colunas:
            ctk.CTkLabel(header, text=texto,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=CORES["ouro"], width=w,
                anchor="w").pack(side="left", padx=10, pady=6)

    def _construir_aba_drops(self):
        aba = self.tabs.tab("📦 Drops")

        self._construir_barra_input(aba,
            "drop_search", [i["nome"] for i in self.itens_drop],
            "Pesquisar item...", "drop_qtd", self._adicionar_drop)

        ord_row = ctk.CTkFrame(aba, fg_color="transparent")
        ord_row.pack(fill="x", padx=5, pady=(2, 0))
        ctk.CTkLabel(ord_row, text="Ordenar:",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_secundario"]).pack(side="left", padx=5)
        self.drop_ordem = ctk.CTkComboBox(ord_row,
            values=["Adição", "Nome (A-Z)", "Quantidade", "Valor total"],
            width=150, state="readonly",
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"],
            button_color=CORES["borda"],
            dropdown_fg_color=CORES["bg_card"],
            command=lambda v: self._atualizar_tabela_drops())
        self.drop_ordem.set("Adição")
        self.drop_ordem.pack(side="left", padx=5)

        self.erro_drop = ctk.CTkLabel(aba, text="",
            text_color=CORES["vermelho"], font=ctk.CTkFont(size=11))
        self.erro_drop.pack(anchor="w", padx=10)

        self._construir_cabecalho(aba, [
            ("Item", 160), ("Qtd", 50), ("Preço NPC", 100), ("Preço Jogador", 120), ("Total", 100), ("", 40)
        ])

        self.lista_drops = ctk.CTkScrollableFrame(aba, fg_color="transparent")
        self.lista_drops.pack(fill="both", expand=True, pady=2, padx=5)

    def _construir_aba_gastos(self):
        aba = self.tabs.tab("🧪 Gastos")

        self._construir_barra_input(aba,
            "gasto_search", [i["nome"] for i in self.itens_consumivel],
            "Pesquisar consumível...", "gasto_qtd", self._adicionar_gasto)

        ord_row = ctk.CTkFrame(aba, fg_color="transparent")
        ord_row.pack(fill="x", padx=5, pady=(2, 0))
        ctk.CTkLabel(ord_row, text="Ordenar:",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_secundario"]).pack(side="left", padx=5)
        self.gasto_ordem = ctk.CTkComboBox(ord_row,
            values=["Adição", "Nome (A-Z)", "Quantidade", "Valor total"],
            width=150, state="readonly",
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"],
            button_color=CORES["borda"],
            dropdown_fg_color=CORES["bg_card"],
            command=lambda v: self._atualizar_tabela_gastos())
        self.gasto_ordem.set("Adição")
        self.gasto_ordem.pack(side="left", padx=5)

        self.erro_gasto = ctk.CTkLabel(aba, text="",
            text_color=CORES["vermelho"], font=ctk.CTkFont(size=11))
        self.erro_gasto.pack(anchor="w", padx=10)

        self._construir_cabecalho(aba, [
            ("Item", 175), ("Qtd", 50), ("Preço NPC", 100), ("Preço Pago", 120), ("Total", 100), ("", 40)
        ])

        self.lista_gastos = ctk.CTkScrollableFrame(aba, fg_color="transparent")
        self.lista_gastos.pack(fill="both", expand=True, pady=2, padx=5)

    def _construir_aba_inimigos(self):
        aba = self.tabs.tab("⚔ Inimigos")

        self._construir_barra_input(aba,
            "inimigo_search", [i["nome"] for i in self.inimigos_banco],
            "Pesquisar inimigo...", "inimigo_qtd", self._adicionar_inimigo)

        self.erro_inimigo = ctk.CTkLabel(aba, text="",
            text_color=CORES["vermelho"], font=ctk.CTkFont(size=11))
        self.erro_inimigo.pack(anchor="w", padx=10)

        self._construir_cabecalho(aba, [
            ("Inimigo", 350), ("Quantidade", 120), ("", 40)
        ])

        self.lista_inimigos = ctk.CTkScrollableFrame(aba, fg_color="transparent")
        self.lista_inimigos.pack(fill="both", expand=True, pady=2, padx=5)

    def _construir_aba_bonus(self):
        aba = self.tabs.tab("🍀 Bônus")

        scroll = ctk.CTkScrollableFrame(aba, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=5, pady=5)

        loot_header = ctk.CTkFrame(scroll, fg_color=CORES["bg_header"], corner_radius=8)
        loot_header.pack(fill="x", pady=(5, 8))
        ctk.CTkLabel(loot_header, text="🍀  Bônus de Loot",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=CORES["ouro"]).pack(anchor="w", padx=12, pady=8)

        for bonus in BONUS_LOOT:
            self._criar_linha_bonus(scroll, bonus, "loot")

        ctk.CTkFrame(scroll, height=1, fg_color=CORES["borda"]).pack(fill="x", pady=12)

        geral_header = ctk.CTkFrame(scroll, fg_color=CORES["bg_header"], corner_radius=8)
        geral_header.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(geral_header, text="⚡  Bônus Gerais",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=CORES["ouro"]).pack(anchor="w", padx=12, pady=8)

        for bonus in BONUS_GERAL:
            self._criar_linha_bonus(scroll, bonus, "geral")

    def _construir_aba_notas(self):
        aba = self.tabs.tab("📝 Notas")

        ctk.CTkLabel(aba, text="Anotações da hunt",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=CORES["ouro"]).pack(anchor="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(aba,
            text="Use este espaço para registrar observações, eventos ou qualquer informação relevante.",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_secundario"],
            wraplength=820).pack(anchor="w", padx=10, pady=(0, 8))

        self.notas = ctk.CTkTextbox(aba,
            fg_color=CORES["bg_input"],
            border_color=CORES["borda"],
            text_color=CORES["texto_principal"],
            font=ctk.CTkFont(size=12))
        self.notas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _criar_linha_bonus(self, parent, bonus, tipo):
        nome = bonus["nome"]
        duracao = bonus["duracao_minutos"]

        var = ctk.BooleanVar(value=False)
        self.bonus_vars[nome] = var

        frame = ctk.CTkFrame(parent, fg_color=CORES["bg_card"],
            corner_radius=6, border_width=1, border_color=CORES["borda"])
        frame.pack(fill="x", pady=2)

        check = ctk.CTkCheckBox(frame, text="", variable=var, width=24,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            border_color=CORES["borda"],
            command=lambda n=nome: self._toggle_bonus(n))
        check.pack(side="left", padx=(10, 8), pady=8)

        horas = duracao // 60
        mins = duracao % 60
        duracao_txt = f"{horas}h" if mins == 0 else f"{horas}h{mins}min" if horas > 0 else f"{mins}min"

        ctk.CTkLabel(frame, text=nome, width=220, anchor="w",
            font=ctk.CTkFont(size=13),
            text_color=CORES["texto_principal"]).pack(side="left")

        ctk.CTkLabel(frame, text=f"⏱ {duracao_txt} cada", width=120,
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_secundario"]).pack(side="left", padx=8)

        entry_qtd = ctk.CTkEntry(frame, placeholder_text="Qtd", width=70,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["ouro"], state="disabled")
        entry_qtd.pack(side="left", padx=(0, 10))
        entry_qtd.bind("<KeyPress>", self._apenas_numeros)
        self.bonus_qtd_entries[nome] = entry_qtd

    def _toggle_bonus(self, nome):
        entry = self.bonus_qtd_entries[nome]
        if self.bonus_vars[nome].get():
            entry.configure(state="normal")
            entry.delete(0, "end")
            entry.insert(0, "1")
        else:
            entry.configure(state="disabled")
            entry.delete(0, "end")

    def _get_bonus_ativos(self):
        bonus_ativos = []
        for bonus in BONUS_LOOT + BONUS_GERAL:
            nome = bonus["nome"]
            if self.bonus_vars[nome].get():
                qtd_raw = self.bonus_qtd_entries[nome].get()
                qtd = int(qtd_raw) if qtd_raw.isdigit() else 1
                tipo = "loot" if bonus in BONUS_LOOT else "geral"
                bonus_ativos.append({
                    "nome": nome,
                    "quantidade": qtd,
                    "duracao_minutos": bonus["duracao_minutos"],
                    "tipo": tipo
                })
        return bonus_ativos

    def _apenas_numeros(self, event):
        if event.char and not event.char.isdigit() and event.keysym not in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return "break"

    def _ordenar_lista(self, lista, ordem, campo_nome, campo_qtd, campo_valor=None):
        if ordem == "Nome (A-Z)":
            return sorted(lista, key=lambda x: x[campo_nome].lower())
        elif ordem == "Quantidade":
            return sorted(lista, key=lambda x: x[campo_qtd], reverse=True)
        elif ordem == "Valor total" and campo_valor:
            return sorted(lista, key=lambda x: x.get(campo_valor, 0), reverse=True)
        return lista

    def _adicionar_drop(self):
        nome = self.drop_search.get()
        qtd = self.drop_qtd.get()

        if not nome:
            self.erro_drop.configure(text="Selecione um item.")
            return
        if not qtd.isdigit():
            self.erro_drop.configure(text="Quantidade inválida.")
            return

        item = next((i for i in self.itens_drop if i["nome"] == nome), None)
        if not item:
            self.erro_drop.configure(text="Item não encontrado na lista.")
            return

        self.erro_drop.configure(text="")
        existente = next((d for d in self.drops if d["item_nome"] == nome), None)
        if existente:
            existente["quantidade"] += int(qtd)
            self._flash_linha(self.lista_drops, nome)
        else:
            self.drops.append({
                "item_nome": nome,
                "quantidade": int(qtd),
                "preco_npc": item["preco_npc"],
                "preco_jogador": item["preco_npc"]
            })

        self.drop_search.clear()
        self.drop_qtd.delete(0, "end")
        self.drop_search.focus()
        self._atualizar_tabela_drops()
        self._atualizar_resumo()

    def _flash_linha(self, frame, nome):
        for widget in frame.winfo_children():
            filhos = widget.winfo_children()
            if filhos:
                try:
                    if filhos[0].cget("text") == nome:
                        widget.configure(fg_color=CORES["ouro_escuro"])
                        widget.after(600, lambda w=widget: w.configure(fg_color="transparent"))
                        break
                except:
                    pass

    def _atualizar_tabela_drops(self):
        for widget in self.lista_drops.winfo_children():
            widget.destroy()

        ordem = self.drop_ordem.get() if hasattr(self, "drop_ordem") else "Adição"
        lista = self._ordenar_lista(self.drops, ordem, "item_nome", "quantidade", "preco_jogador")

        for idx, item in enumerate(lista):
            total = item["quantidade"] * item["preco_jogador"]
            row = ctk.CTkFrame(self.lista_drops,
                fg_color=CORES["bg_card"] if idx % 2 == 0 else "transparent",
                corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=item["item_nome"], width=160, anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_principal"]).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=str(item["quantidade"]), width=50,
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_principal"]).pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"${item['preco_npc']:,}", width=100,
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_secundario"]).pack(side="left", padx=4)

            real_idx = self.drops.index(item)
            entry_jogador = ctk.CTkEntry(row, width=120,
                fg_color=CORES["bg_input"], border_color=CORES["borda"],
                text_color=CORES["ouro"], font=ctk.CTkFont(size=12))
            entry_jogador.insert(0, str(item["preco_jogador"]))
            entry_jogador.pack(side="left", padx=4)
            entry_jogador.bind("<KeyPress>", self._apenas_numeros)
            entry_jogador.bind("<FocusOut>", lambda e, i=real_idx, en=entry_jogador: self._atualizar_preco_jogador(i, en))

            ctk.CTkLabel(row, text=f"${total:,}", width=100,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=CORES["verde"]).pack(side="left", padx=4)

            ctk.CTkButton(row, text="🗑", width=36,
                fg_color="transparent", border_width=1,
                border_color=CORES["vermelho"],
                text_color=CORES["vermelho"],
                hover_color=CORES["bg_input"],
                command=lambda i=real_idx: self._remover_drop(i)).pack(side="left", padx=5, pady=4)

    def _remover_drop(self, idx):
        self.drops.pop(idx)
        self._atualizar_tabela_drops()
        self._atualizar_resumo()

    def _atualizar_preco_jogador(self, idx, entry):
        valor = entry.get()
        if valor.isdigit():
            self.drops[idx]["preco_jogador"] = int(valor)
            self._atualizar_tabela_drops()
            self._atualizar_resumo()

    def _adicionar_gasto(self):
        nome = self.gasto_search.get()
        qtd = self.gasto_qtd.get()

        if not nome:
            self.erro_gasto.configure(text="Selecione um consumível.")
            return
        if not qtd.isdigit():
            self.erro_gasto.configure(text="Quantidade inválida.")
            return

        item = next((i for i in self.itens_consumivel if i["nome"] == nome), None)
        if not item:
            self.erro_gasto.configure(text="Item não encontrado na lista.")
            return

        self.erro_gasto.configure(text="")
        existente = next((g for g in self.gastos if g["item_nome"] == nome), None)
        if existente:
            existente["quantidade"] += int(qtd)
            self._flash_linha(self.lista_gastos, nome)
        else:
            self.gastos.append({
                "item_nome": nome,
                "quantidade": int(qtd),
                "preco_npc": item["preco_npc"],
                "preco_pago": 0
            })

        self.gasto_search.clear()
        self.gasto_qtd.delete(0, "end")
        self.gasto_search.focus()
        self._atualizar_tabela_gastos()
        self._atualizar_resumo()

    def _atualizar_tabela_gastos(self):
        for widget in self.lista_gastos.winfo_children():
            widget.destroy()

        ordem = self.gasto_ordem.get() if hasattr(self, "gasto_ordem") else "Adição"
        lista = self._ordenar_lista(self.gastos, ordem, "item_nome", "quantidade", "preco_pago")

        for idx, item in enumerate(lista):
            preco_efetivo = item.get("preco_pago", 0) if item.get("preco_pago", 0) > 0 else item["preco_npc"]
            total = item["quantidade"] * preco_efetivo if item["preco_npc"] != -1 else 0

            row = ctk.CTkFrame(self.lista_gastos,
                fg_color=CORES["bg_card"] if idx % 2 == 0 else "transparent",
                corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=item["item_nome"], width=175, anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_principal"]).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=str(item["quantidade"]), width=50,
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_principal"]).pack(side="left", padx=4)

            if item["preco_npc"] == -1:
                ctk.CTkLabel(row, text="N/D", width=100,
                    font=ctk.CTkFont(size=12),
                    text_color=CORES["texto_secundario"]).pack(side="left", padx=4)
                ctk.CTkLabel(row, text="N/D", width=120,
                    font=ctk.CTkFont(size=12),
                    text_color=CORES["texto_secundario"]).pack(side="left", padx=4)
                ctk.CTkLabel(row, text="N/D", width=100,
                    font=ctk.CTkFont(size=12),
                    text_color=CORES["texto_secundario"]).pack(side="left", padx=4)
            else:
                preco_npc_txt = f"${item['preco_npc']:,}" if item["preco_npc"] > 0 else "N/A"
                ctk.CTkLabel(row, text=preco_npc_txt, width=100,
                    font=ctk.CTkFont(size=12),
                    text_color=CORES["texto_secundario"]).pack(side="left", padx=4)

                real_idx = self.gastos.index(item)
                entry_pago = ctk.CTkEntry(row, width=120,
                    fg_color=CORES["bg_input"], border_color=CORES["borda"],
                    text_color=CORES["ouro"], font=ctk.CTkFont(size=12),
                    placeholder_text="Preço pago")
                if item.get("preco_pago", 0) > 0:
                    entry_pago.insert(0, str(item["preco_pago"]))
                entry_pago.pack(side="left", padx=4)
                entry_pago.bind("<KeyPress>", self._apenas_numeros)
                entry_pago.bind("<FocusOut>", lambda e, i=real_idx, en=entry_pago: self._atualizar_preco_pago(i, en))

                total_txt = f"-${total:,}" if total > 0 else "$0"
                ctk.CTkLabel(row, text=total_txt, width=100,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=CORES["vermelho"]).pack(side="left", padx=4)

            ctk.CTkButton(row, text="🗑", width=36,
                fg_color="transparent", border_width=1,
                border_color=CORES["vermelho"],
                text_color=CORES["vermelho"],
                hover_color=CORES["bg_input"],
                command=lambda i=self.gastos.index(item): self._remover_gasto(i)).pack(side="left", padx=5, pady=4)

    def _atualizar_preco_pago(self, idx, entry):
        valor = entry.get()
        if valor.isdigit():
            self.gastos[idx]["preco_pago"] = int(valor)
            self._atualizar_tabela_gastos()
            self._atualizar_resumo()

    def _remover_gasto(self, idx):
        self.gastos.pop(idx)
        self._atualizar_tabela_gastos()
        self._atualizar_resumo()

    def _adicionar_inimigo(self):
        nome = self.inimigo_search.get()
        qtd = self.inimigo_qtd.get()

        if not nome:
            self.erro_inimigo.configure(text="Selecione um inimigo.")
            return
        if not qtd.isdigit():
            self.erro_inimigo.configure(text="Quantidade inválida.")
            return

        item = next((i for i in self.inimigos_banco if i["nome"] == nome), None)
        if not item:
            self.erro_inimigo.configure(text="Inimigo não encontrado na lista.")
            return

        self.erro_inimigo.configure(text="")
        existente = next((i for i in self.inimigos if i["inimigo_nome"] == nome), None)
        if existente:
            existente["quantidade"] += int(qtd)
        else:
            self.inimigos.append({"inimigo_nome": nome, "quantidade": int(qtd)})

        self.inimigo_search.clear()
        self.inimigo_qtd.delete(0, "end")
        self.inimigo_search.focus()
        self._atualizar_tabela_inimigos()

    def _atualizar_tabela_inimigos(self):
        for widget in self.lista_inimigos.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.inimigos):
            row = ctk.CTkFrame(self.lista_inimigos,
                fg_color=CORES["bg_card"] if idx % 2 == 0 else "transparent",
                corner_radius=4)
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=item["inimigo_nome"], width=350, anchor="w",
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_principal"]).pack(side="left", padx=10, pady=6)
            ctk.CTkLabel(row, text=str(item["quantidade"]), width=120,
                font=ctk.CTkFont(size=12),
                text_color=CORES["texto_principal"]).pack(side="left", padx=4)

            ctk.CTkButton(row, text="🗑", width=36,
                fg_color="transparent", border_width=1,
                border_color=CORES["vermelho"],
                text_color=CORES["vermelho"],
                hover_color=CORES["bg_input"],
                command=lambda i=idx: self._remover_inimigo(i)).pack(side="left", padx=5, pady=4)

    def _remover_inimigo(self, idx):
        self.inimigos.pop(idx)
        self._atualizar_tabela_inimigos()

    def _atualizar_resumo(self):
        total_npc = sum(d["quantidade"] * d["preco_npc"] for d in self.drops)
        total_jogador = sum(d["quantidade"] * d["preco_jogador"] for d in self.drops)
        self.resumo.configure(text=f"Loot NPC: ${total_npc:,}  |  Loot Jogador: ${total_jogador:,}")

    def _voltar_seguro(self):
        if self.drops or self.gastos or self.inimigos:
            self._popup_confirmacao(
                "Você tem uma hunt em andamento.\nDeseja sair sem salvar?",
                lambda: [self._restaurar_protocolo(), self.ao_voltar()]
            )
        else:
            self._restaurar_protocolo()
            self.ao_voltar()

    def _confirmar_fechar(self):
        if self.drops or self.gastos or self.inimigos:
            self._popup_confirmacao(
                "Você tem uma hunt em andamento.\nDeseja sair sem salvar?",
                lambda: self.master.destroy()
            )
        else:
            self.master.destroy()

    def _popup_confirmacao(self, mensagem, ao_confirmar):
        janela = ctk.CTkToplevel(self)
        janela.title("Atenção")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 340, 160)

        ctk.CTkLabel(janela, text=mensagem,
            font=ctk.CTkFont(size=13), wraplength=300,
            text_color=CORES["texto_principal"]).pack(pady=25)

        botoes = ctk.CTkFrame(janela, fg_color="transparent")
        botoes.pack()

        ctk.CTkButton(botoes, text="Sair sem salvar", width=140,
            fg_color=CORES["vermelho"], hover_color=CORES["vermelho_hover"],
            command=lambda: [janela.destroy(), ao_confirmar()]).pack(side="left", padx=10)

        ctk.CTkButton(botoes, text="Cancelar", width=120,
            fg_color="transparent", border_width=1, border_color=CORES["borda"],
            text_color=CORES["texto_secundario"], hover_color=CORES["bg_input"],
            command=janela.destroy).pack(side="left", padx=10)

    def _restaurar_protocolo(self):
        self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)

    def _finalizar(self):
        if not self.drops:
            self._mostrar_erro("Adicione pelo menos um drop antes de finalizar.")
            return

        horas = int(self.horas.get() or 0)
        minutos = int(self.minutos.get() or 0)
        duracao = horas * 60 + minutos

        if duracao == 0:
            self._mostrar_erro("Informe a duração da hunt.")
            return

        total_inimigos = sum(i["quantidade"] for i in self.inimigos)
        inimigos_calc = calcular_inimigos(total_inimigos, duracao)
        calculos = calcular_hunt(duracao, self.drops, self.gastos)
        bonus_ativos = self._get_bonus_ativos()
        notas = self.notas.get("1.0", "end").strip()

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO hunts (personagem_id, duracao_minutos) VALUES (?, ?)",
            (self.personagem["id"], duracao))
        hunt_id = cursor.lastrowid

        for d in self.drops:
            cursor.execute("INSERT INTO hunt_drops (hunt_id, item_nome, quantidade, preco_npc, preco_jogador) VALUES (?, ?, ?, ?, ?)",
                (hunt_id, d["item_nome"], d["quantidade"], d["preco_npc"], d["preco_jogador"]))

        for g in self.gastos:
            if g["preco_npc"] == -1:
                preco_efetivo = 0
            elif g.get("preco_pago", 0) > 0:
                preco_efetivo = g["preco_pago"]
            else:
                preco_efetivo = g["preco_npc"]
            cursor.execute("INSERT INTO hunt_gastos (hunt_id, item_nome, quantidade, preco_npc) VALUES (?, ?, ?, ?)",
                (hunt_id, g["item_nome"], g["quantidade"], preco_efetivo))

        for i in self.inimigos:
            cursor.execute("INSERT INTO hunt_inimigos (hunt_id, inimigo_nome, quantidade) VALUES (?, ?, ?)",
                (hunt_id, i["inimigo_nome"], i["quantidade"]))

        for b in bonus_ativos:
            cursor.execute("INSERT INTO hunt_bonus (hunt_id, nome, quantidade, duracao_minutos, tipo) VALUES (?, ?, ?, ?, ?)",
                (hunt_id, b["nome"], b["quantidade"], b["duracao_minutos"], b["tipo"]))

        conn.commit()
        conn.close()

        relatorio = gerar_relatorio(
            self.personagem["nome"], duracao,
            self.drops, self.gastos, self.inimigos,
            calculos, inimigos_calc, bonus_ativos, notas
        )

        self._ultimo_calculos = calculos
        self._restaurar_protocolo()
        self._mostrar_relatorio(relatorio)

    def _mostrar_erro(self, mensagem):
        janela = ctk.CTkToplevel(self)
        janela.title("Atenção")
        janela.resizable(False, False)
        janela.grab_set()
        janela.configure(fg_color=CORES["bg_principal"])
        _centralizar(janela, 320, 140)

        ctk.CTkLabel(janela, text=mensagem,
            font=ctk.CTkFont(size=13), wraplength=280,
            text_color=CORES["texto_principal"]).pack(pady=25)

        ctk.CTkButton(janela, text="OK", width=120,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a",
            command=janela.destroy).pack()

    def _mostrar_relatorio(self, relatorio):
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

        lucro_jogador = self._ultimo_calculos.get("lucro_jogador", 0)
        lucro_npc = self._ultimo_calculos.get("lucro_npc", 0)

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

            elif l.startswith("✅ Lucro NPC"):
                cor = CORES["verde"] if lucro_npc >= 0 else CORES["vermelho"]
                add(l, cor, bold=True)

            elif l.startswith("✅ Lucro Jogador") or l.startswith("❌ Lucro Jogador"):
                cor = CORES["verde"] if lucro_jogador >= 0 else CORES["vermelho"]
                add(l, cor, bold=True)

            elif l.startswith("❌ Lucro NPC"):
                add(l, CORES["vermelho"], bold=True)

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
            command=lambda: [janela.destroy(), self.ao_finalizar()]).pack(side="left", padx=5)

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
        self.clipboard_clear()
        self.clipboard_append(texto)