import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio
from utils.search_box import SearchBox
import json
import os

DROPS_PATH = os.path.join(os.path.dirname(__file__), "..", "banco", "itens_drop.json")
CONSUMIVEIS_PATH = os.path.join(os.path.dirname(__file__), "..", "banco", "itens_consumivel.json")
INIMIGOS_PATH = os.path.join(os.path.dirname(__file__), "..", "banco", "inimigos.json")

class TelaHunt(ctk.CTkFrame):
    def __init__(self, master, usuario, personagem, ao_voltar, ao_finalizar):
        super().__init__(master, fg_color="transparent")
        self.usuario = usuario
        self.personagem = personagem
        self.ao_voltar = ao_voltar
        self.ao_finalizar = ao_finalizar
        self.drops = []
        self.gastos = []
        self.inimigos = []
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

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(header, text=f"Hunt — {self.personagem['nome']}",
            font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="← Voltar", width=100, fg_color="transparent",
            border_width=1, command=self._voltar_seguro).pack(side="right")

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=10)

        self.tabs.add("Drops")
        self.tabs.add("Gastos")
        self.tabs.add("Inimigos")

        self._construir_aba_drops()
        self._construir_aba_gastos()
        self._construir_aba_inimigos()

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(footer, text="Duração:").pack(side="left", padx=5)
        self.horas = ctk.CTkEntry(footer, placeholder_text="Horas", width=80)
        self.horas.pack(side="left", padx=5)
        self.minutos = ctk.CTkEntry(footer, placeholder_text="Minutos", width=80)
        self.minutos.pack(side="left", padx=5)

        self.resumo = ctk.CTkLabel(footer, text="Loot NPC: 0 gp  |  Loot Jogador: 0 gp")
        self.resumo.pack(side="left", padx=20)

        ctk.CTkButton(footer, text="Finalizar Hunt", width=160,
            command=self._finalizar).pack(side="right", padx=5)

    def _construir_aba_drops(self):
        aba = self.tabs.tab("Drops")

        row = ctk.CTkFrame(aba, fg_color="transparent")
        row.pack(fill="x", pady=10)

        self.drop_search = SearchBox(row,
            valores=[i["nome"] for i in self.itens_drop],
            placeholder="Pesquisar item...",
            width=220,
            ao_selecionar=lambda v: self.drop_qtd.focus())
        self.drop_search.pack(side="left", padx=5)

        self.drop_qtd = ctk.CTkEntry(row, placeholder_text="Quantidade", width=100)
        self.drop_qtd.pack(side="left", padx=5)
        self.drop_qtd.bind("<Return>", lambda e: self._adicionar_drop())

        ctk.CTkButton(row, text="Adicionar", width=100,
            command=self._adicionar_drop).pack(side="left", padx=5)

        self.erro_drop = ctk.CTkLabel(aba, text="", text_color="red")
        self.erro_drop.pack(anchor="w", padx=5)

        header = ctk.CTkFrame(aba, fg_color="#2b2b2b")
        header.pack(fill="x", padx=5, pady=(5, 0))

        for texto, w in [("Item", 180), ("Qtd", 60), ("Preço NPC", 110), ("Preço Jogador", 130), ("", 50)]:
            ctk.CTkLabel(header, text=texto, font=ctk.CTkFont(weight="bold"), width=w).pack(side="left", padx=5, pady=4)

        self.lista_drops = ctk.CTkScrollableFrame(aba)
        self.lista_drops.pack(fill="both", expand=True, pady=2)

    def _construir_aba_gastos(self):
        aba = self.tabs.tab("Gastos")

        row = ctk.CTkFrame(aba, fg_color="transparent")
        row.pack(fill="x", pady=10)

        self.gasto_search = SearchBox(row,
            valores=[i["nome"] for i in self.itens_consumivel],
            placeholder="Pesquisar consumível...",
            width=220,
            ao_selecionar=lambda v: self.gasto_qtd.focus())
        self.gasto_search.pack(side="left", padx=5)

        self.gasto_qtd = ctk.CTkEntry(row, placeholder_text="Quantidade", width=120)
        self.gasto_qtd.pack(side="left", padx=5)
        self.gasto_qtd.bind("<Return>", lambda e: self._adicionar_gasto())

        ctk.CTkButton(row, text="Adicionar", width=100,
            command=self._adicionar_gasto).pack(side="left", padx=5)

        header = ctk.CTkFrame(aba, fg_color="#2b2b2b")
        header.pack(fill="x", padx=5, pady=(5, 0))

        for texto, w in [("Item", 260), ("Qtd", 80), ("Preço NPC", 120), ("", 50)]:
            ctk.CTkLabel(header, text=texto, font=ctk.CTkFont(weight="bold"), width=w).pack(side="left", padx=5, pady=4)

        self.lista_gastos = ctk.CTkScrollableFrame(aba)
        self.lista_gastos.pack(fill="both", expand=True, pady=2)

    def _construir_aba_inimigos(self):
        aba = self.tabs.tab("Inimigos")

        row = ctk.CTkFrame(aba, fg_color="transparent")
        row.pack(fill="x", pady=10)

        self.inimigo_search = SearchBox(row,
            valores=[i["nome"] for i in self.inimigos_banco],
            placeholder="Pesquisar inimigo...",
            width=220,
            ao_selecionar=lambda v: self.inimigo_qtd.focus())
        self.inimigo_search.pack(side="left", padx=5)

        self.inimigo_qtd = ctk.CTkEntry(row, placeholder_text="Quantidade", width=120)
        self.inimigo_qtd.pack(side="left", padx=5)
        self.inimigo_qtd.bind("<Return>", lambda e: self._adicionar_inimigo())

        ctk.CTkButton(row, text="Adicionar", width=100,
            command=self._adicionar_inimigo).pack(side="left", padx=5)

        header = ctk.CTkFrame(aba, fg_color="#2b2b2b")
        header.pack(fill="x", padx=5, pady=(5, 0))

        for texto, w in [("Inimigo", 340), ("Quantidade", 120), ("", 50)]:
            ctk.CTkLabel(header, text=texto, font=ctk.CTkFont(weight="bold"), width=w).pack(side="left", padx=5, pady=4)

        self.lista_inimigos = ctk.CTkScrollableFrame(aba)
        self.lista_inimigos.pack(fill="both", expand=True, pady=2)

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

    def _atualizar_tabela_drops(self):
        for widget in self.lista_drops.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.drops):
            row = ctk.CTkFrame(self.lista_drops, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=item["item_nome"], width=180, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(item["quantidade"]), width=60).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{item['preco_npc']:,}", width=110).pack(side="left", padx=5)

            entry_jogador = ctk.CTkEntry(row, width=130)
            entry_jogador.insert(0, str(item["preco_jogador"]))
            entry_jogador.pack(side="left", padx=5)
            entry_jogador.bind("<FocusOut>", lambda e, i=idx, en=entry_jogador: self._atualizar_preco_jogador(i, en))

            ctk.CTkButton(row, text="🗑", width=40, fg_color="transparent",
                border_width=1, text_color="red",
                command=lambda i=idx: self._remover_drop(i)).pack(side="left", padx=5)

    def _remover_drop(self, idx):
        self.drops.pop(idx)
        self._atualizar_tabela_drops()
        self._atualizar_resumo()

    def _atualizar_preco_jogador(self, idx, entry):
        valor = entry.get()
        if valor.isdigit():
            self.drops[idx]["preco_jogador"] = int(valor)
            self._atualizar_resumo()

    def _adicionar_gasto(self):
        nome = self.gasto_search.get()
        qtd = self.gasto_qtd.get()

        if not nome or not qtd.isdigit():
            return

        item = next((i for i in self.itens_consumivel if i["nome"] == nome), None)
        if not item:
            return

        existente = next((g for g in self.gastos if g["item_nome"] == nome), None)
        if existente:
            existente["quantidade"] += int(qtd)
        else:
            self.gastos.append({
                "item_nome": nome,
                "quantidade": int(qtd),
                "preco_npc": item["preco_npc"]
            })

        self.gasto_search.clear()
        self.gasto_qtd.delete(0, "end")
        self.gasto_search.focus()
        self._atualizar_tabela_gastos()
        self._atualizar_resumo()

    def _atualizar_tabela_gastos(self):
        for widget in self.lista_gastos.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.gastos):
            row = ctk.CTkFrame(self.lista_gastos, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=item["item_nome"], width=260, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(item["quantidade"]), width=80).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{item['preco_npc']:,}", width=120).pack(side="left", padx=5)

            ctk.CTkButton(row, text="🗑", width=40, fg_color="transparent",
                border_width=1, text_color="red",
                command=lambda i=idx: self._remover_gasto(i)).pack(side="left", padx=5)

    def _remover_gasto(self, idx):
        self.gastos.pop(idx)
        self._atualizar_tabela_gastos()
        self._atualizar_resumo()

    def _adicionar_inimigo(self):
        nome = self.inimigo_search.get()
        qtd = self.inimigo_qtd.get()

        if not nome or not qtd.isdigit():
            return

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
            row = ctk.CTkFrame(self.lista_inimigos, fg_color="transparent")
            row.pack(fill="x", pady=2)

            ctk.CTkLabel(row, text=item["inimigo_nome"], width=340, anchor="w").pack(side="left", padx=5)
            ctk.CTkLabel(row, text=str(item["quantidade"]), width=120).pack(side="left", padx=5)

            ctk.CTkButton(row, text="🗑", width=40, fg_color="transparent",
                border_width=1, text_color="red",
                command=lambda i=idx: self._remover_inimigo(i)).pack(side="left", padx=5)

    def _remover_inimigo(self, idx):
        self.inimigos.pop(idx)
        self._atualizar_tabela_inimigos()

    def _atualizar_resumo(self):
        total_npc = sum(d["quantidade"] * d["preco_npc"] for d in self.drops)
        total_jogador = sum(d["quantidade"] * d["preco_jogador"] for d in self.drops)
        self.resumo.configure(text=f"Loot NPC: {total_npc:,} gp  |  Loot Jogador: {total_jogador:,} gp")

    def _voltar_seguro(self):
        if self.drops or self.gastos or self.inimigos:
            janela = ctk.CTkToplevel(self)
            janela.title("Atenção")
            janela.geometry("320x150")
            janela.grab_set()
            janela.resizable(False, False)

            ctk.CTkLabel(janela, text="Você tem uma hunt em andamento.\nDeseja sair sem salvar?",
                font=ctk.CTkFont(size=13), wraplength=280).pack(pady=25)

            botoes = ctk.CTkFrame(janela, fg_color="transparent")
            botoes.pack()

            ctk.CTkButton(botoes, text="Sair sem salvar", width=130, fg_color="red",
                command=lambda: [janela.destroy(), self._restaurar_protocolo(), self.ao_voltar()]).pack(side="left", padx=10)

            ctk.CTkButton(botoes, text="Cancelar", width=120, fg_color="transparent",
                border_width=1, command=janela.destroy).pack(side="left", padx=10)
        else:
            self._restaurar_protocolo()
            self.ao_voltar()

    def _confirmar_fechar(self):
        if self.drops or self.gastos or self.inimigos:
            janela = ctk.CTkToplevel(self)
            janela.title("Atenção")
            janela.geometry("320x150")
            janela.grab_set()
            janela.resizable(False, False)

            ctk.CTkLabel(janela, text="Você tem uma hunt em andamento.\nDeseja sair sem salvar?",
                font=ctk.CTkFont(size=13), wraplength=280).pack(pady=25)

            botoes = ctk.CTkFrame(janela, fg_color="transparent")
            botoes.pack()

            ctk.CTkButton(botoes, text="Sair sem salvar", width=130, fg_color="red",
                command=lambda: [janela.destroy(), self.master.destroy()]).pack(side="left", padx=10)

            ctk.CTkButton(botoes, text="Cancelar", width=120, fg_color="transparent",
                border_width=1, command=janela.destroy).pack(side="left", padx=10)
        else:
            self.master.destroy()

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

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO hunts (personagem_id, duracao_minutos) VALUES (?, ?)",
            (self.personagem["id"], duracao))
        hunt_id = cursor.lastrowid

        for d in self.drops:
            cursor.execute("INSERT INTO hunt_drops (hunt_id, item_nome, quantidade, preco_npc, preco_jogador) VALUES (?, ?, ?, ?, ?)",
                (hunt_id, d["item_nome"], d["quantidade"], d["preco_npc"], d["preco_jogador"]))

        for g in self.gastos:
            cursor.execute("INSERT INTO hunt_gastos (hunt_id, item_nome, quantidade, preco_npc) VALUES (?, ?, ?, ?)",
                (hunt_id, g["item_nome"], g["quantidade"], g["preco_npc"]))

        for i in self.inimigos:
            cursor.execute("INSERT INTO hunt_inimigos (hunt_id, inimigo_nome, quantidade) VALUES (?, ?, ?)",
                (hunt_id, i["inimigo_nome"], i["quantidade"]))

        conn.commit()
        conn.close()

        relatorio = gerar_relatorio(
            self.personagem["nome"], duracao,
            self.drops, self.gastos, self.inimigos,
            calculos, inimigos_calc
        )
        self._restaurar_protocolo()
        self._mostrar_relatorio(relatorio)

    def _mostrar_erro(self, mensagem):
        janela = ctk.CTkToplevel(self)
        janela.title("Atenção")
        janela.geometry("300x130")
        janela.grab_set()
        janela.resizable(False, False)

        ctk.CTkLabel(janela, text=mensagem,
            font=ctk.CTkFont(size=13), wraplength=260).pack(pady=25)
        ctk.CTkButton(janela, text="OK", width=120,
            command=janela.destroy).pack()

    def _mostrar_relatorio(self, relatorio):
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
            command=lambda: [janela.destroy(), self.ao_finalizar()]).pack(pady=5)

    def _copiar(self, texto):
        self.clipboard_clear()
        self.clipboard_append(texto)