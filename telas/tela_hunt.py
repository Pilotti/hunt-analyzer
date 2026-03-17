import customtkinter as ctk
from utils.database import conectar
from utils.calculos import calcular_hunt, calcular_inimigos
from utils.exportar import gerar_relatorio
import json
import os

DROPS_PATH = os.path.join(os.path.dirname(__file__), "..", "banco", "itens_drop.json")
CONSUMIVEIS_PATH = os.path.join(os.path.dirname(__file__), "..", "banco", "itens_consumivel.json")
INIMIGOS_PATH = os.path.join(os.path.dirname(__file__), "..", "banco", "inimigos.json")

class TelaHunt(ctk.CTk):
    def __init__(self, usuario, personagem, ao_voltar):
        super().__init__()
        self.usuario = usuario
        self.personagem = personagem
        self.ao_voltar = ao_voltar
        self.drops = []
        self.gastos = []
        self.inimigos = []
        self.title(f"Hunt Analyzer — {personagem['nome']}")
        self.geometry("800x700")
        self.resizable(False, False)
        self._carregar_banco()
        self._construir()

    def _carregar_banco(self):
        try:
            with open(DROPS_PATH, "r", encoding="utf-8") as f:
                self.itens_drop = json.load(f)
        except:
            self.itens_drop = []

        try:
            with open(CONSUMIVEIS_PATH, "r", encoding="utf-8") as f:
                self.itens_consumivel = json.load(f)
        except:
            self.itens_consumivel = []

        try:
            with open(INIMIGOS_PATH, "r", encoding="utf-8") as f:
                self.inimigos_banco = json.load(f)
        except:
            self.inimigos_banco = []

    def _construir(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 0))

        ctk.CTkLabel(header, text=f"Hunt — {self.personagem['nome']}",
            font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="← Voltar", width=100, fg_color="transparent",
            border_width=1, command=self._voltar).pack(side="right")

        self.tabs = ctk.CTkTabview(self, width=760, height=480)
        self.tabs.pack(padx=20, pady=10)

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

        ctk.CTkButton(footer, text="Finalizar Hunt", width=200,
            command=self._finalizar).pack(side="right", padx=5)

    def _construir_aba_drops(self):
        aba = self.tabs.tab("Drops")

        row = ctk.CTkFrame(aba, fg_color="transparent")
        row.pack(fill="x", pady=10)

        self.drop_item = ctk.CTkComboBox(row, values=[i["nome"] for i in self.itens_drop], width=220)
        self.drop_item.pack(side="left", padx=5)

        self.drop_qtd = ctk.CTkEntry(row, placeholder_text="Quantidade", width=120)
        self.drop_qtd.pack(side="left", padx=5)

        ctk.CTkButton(row, text="Adicionar", width=100, command=self._adicionar_drop).pack(side="left", padx=5)

        self.lista_drops = ctk.CTkScrollableFrame(aba, width=700, height=300)
        self.lista_drops.pack(pady=5)

    def _construir_aba_gastos(self):
        aba = self.tabs.tab("Gastos")

        row = ctk.CTkFrame(aba, fg_color="transparent")
        row.pack(fill="x", pady=10)

        self.gasto_item = ctk.CTkComboBox(row, values=[i["nome"] for i in self.itens_consumivel], width=220)
        self.gasto_item.pack(side="left", padx=5)

        self.gasto_qtd = ctk.CTkEntry(row, placeholder_text="Quantidade", width=120)
        self.gasto_qtd.pack(side="left", padx=5)

        ctk.CTkButton(row, text="Adicionar", width=100, command=self._adicionar_gasto).pack(side="left", padx=5)

        self.lista_gastos = ctk.CTkScrollableFrame(aba, width=700, height=300)
        self.lista_gastos.pack(pady=5)

    def _construir_aba_inimigos(self):
        aba = self.tabs.tab("Inimigos")

        row = ctk.CTkFrame(aba, fg_color="transparent")
        row.pack(fill="x", pady=10)

        self.inimigo_item = ctk.CTkComboBox(row, values=[i["nome"] for i in self.inimigos_banco], width=220)
        self.inimigo_item.pack(side="left", padx=5)

        self.inimigo_qtd = ctk.CTkEntry(row, placeholder_text="Quantidade", width=120)
        self.inimigo_qtd.pack(side="left", padx=5)

        ctk.CTkButton(row, text="Adicionar", width=100, command=self._adicionar_inimigo).pack(side="left", padx=5)

        self.lista_inimigos = ctk.CTkScrollableFrame(aba, width=700, height=300)
        self.lista_inimigos.pack(pady=5)

    def _adicionar_drop(self):
        nome = self.drop_item.get()
        qtd = self.drop_qtd.get()
        if not nome or not qtd.isdigit():
            return

        item = next((i for i in self.itens_drop if i["nome"] == nome), None)
        if not item:
            return

        self.drops.append({
            "item_nome": nome,
            "quantidade": int(qtd),
            "preco_npc": item["preco_npc"],
            "preco_jogador": item.get("preco_jogador", item["preco_npc"])
        })
        self.drop_qtd.delete(0, "end")
        self._atualizar_lista(self.lista_drops, self.drops, "item_nome")

    def _adicionar_gasto(self):
        nome = self.gasto_item.get()
        qtd = self.gasto_qtd.get()
        if not nome or not qtd.isdigit():
            return

        item = next((i for i in self.itens_consumivel if i["nome"] == nome), None)
        if not item:
            return

        self.gastos.append({
            "item_nome": nome,
            "quantidade": int(qtd),
            "preco_npc": item["preco_npc"]
        })
        self.gasto_qtd.delete(0, "end")
        self._atualizar_lista(self.lista_gastos, self.gastos, "item_nome")

    def _adicionar_inimigo(self):
        nome = self.inimigo_item.get()
        qtd = self.inimigo_qtd.get()
        if not nome or not qtd.isdigit():
            return

        self.inimigos.append({"inimigo_nome": nome, "quantidade": int(qtd)})
        self.inimigo_qtd.delete(0, "end")
        self._atualizar_lista(self.lista_inimigos, self.inimigos, "inimigo_nome")

    def _atualizar_lista(self, frame, lista, campo_nome):
        for widget in frame.winfo_children():
            widget.destroy()
        for item in lista:
            ctk.CTkLabel(frame, text=f"{item[campo_nome]} x{item['quantidade']}").pack(anchor="w", padx=10, pady=2)

    def _finalizar(self):
        horas = int(self.horas.get() or 0)
        minutos = int(self.minutos.get() or 0)
        duracao = horas * 60 + minutos

        if duracao == 0:
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
        self._mostrar_relatorio(relatorio)

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
            command=janela.destroy).pack(pady=5)

    def _copiar(self, texto):
        self.clipboard_clear()
        self.clipboard_append(texto)

    def _voltar(self):
        self.destroy()
        self.ao_voltar()