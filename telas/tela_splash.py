import customtkinter as ctk
from assets.theme import CORES
import threading

class TelaSplash(ctk.CTkToplevel):
    def __init__(self, master, ao_finalizar):
        super().__init__(master)
        self.ao_finalizar = ao_finalizar
        self.overrideredirect(True)
        self.configure(fg_color=CORES["bg_principal"])

        largura = 400
        altura = 300
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

        self._construir()
        self.after(100, self._iniciar_progresso)

    def _construir(self):
        ctk.CTkFrame(self, fg_color=CORES["borda_ouro"], height=3, corner_radius=0).pack(fill="x")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(content, text="⚔",
            font=ctk.CTkFont(size=52),
            text_color=CORES["ouro"]).pack(pady=(0, 10))

        ctk.CTkLabel(content, text="Hunt Analyzer",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=CORES["texto_principal"]).pack()

        ctk.CTkLabel(content, text="PokéXGames",
            font=ctk.CTkFont(size=14),
            text_color=CORES["ouro"]).pack(pady=(4, 0))

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.place(relx=0.5, rely=0.85, anchor="center")

        self.progresso = ctk.CTkProgressBar(footer, width=300,
            fg_color=CORES["bg_card"],
            progress_color=CORES["ouro"])
        self.progresso.pack()
        self.progresso.set(0)

        self.label_status = ctk.CTkLabel(footer, text="Inicializando...",
            font=ctk.CTkFont(size=11),
            text_color=CORES["texto_secundario"])
        self.label_status.pack(pady=(8, 0))

        ctk.CTkFrame(self, fg_color=CORES["borda_ouro"], height=3, corner_radius=0).pack(side="bottom", fill="x")

    def _iniciar_progresso(self):
        etapas = [
            (0.2, "Carregando banco de dados..."),
            (0.5, "Carregando itens e inimigos..."),
            (0.8, "Preparando interface..."),
            (1.0, "Pronto!"),
        ]
        self._animar(etapas, 0)

    def _animar(self, etapas, idx):
        if idx >= len(etapas):
            self.after(300, self._finalizar)
            return

        valor, texto = etapas[idx]
        self.progresso.set(valor)
        self.label_status.configure(text=texto)
        self.after(500, lambda: self._animar(etapas, idx + 1))

    def _finalizar(self):
        self.destroy()
        self.ao_finalizar()