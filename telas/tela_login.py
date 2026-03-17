import customtkinter as ctk
from utils.auth import login_usuario
from assets.theme import CORES

class TelaLogin(ctk.CTkFrame):
    def __init__(self, master, ao_logar):
        super().__init__(master, fg_color=CORES["bg_principal"])
        self.ao_logar = ao_logar
        self._construir()

    def _construir(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        ctk.CTkLabel(center, text="⚔",
            font=ctk.CTkFont(size=48),
            text_color=CORES["ouro"]).pack(pady=(0, 5))

        ctk.CTkLabel(center, text="Hunt Analyzer",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=CORES["texto_principal"]).pack(pady=(0, 4))

        ctk.CTkLabel(center, text="PokéXGames",
            font=ctk.CTkFont(size=13),
            text_color=CORES["ouro"]).pack(pady=(0, 35))

        # Card
        card = ctk.CTkFrame(center, fg_color=CORES["bg_card"],
            corner_radius=12, border_width=1, border_color=CORES["borda"])
        card.pack(padx=20, pady=5, ipadx=20, ipady=20)

        ctk.CTkLabel(card, text="Entrar na sua conta",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=CORES["texto_principal"]).pack(pady=(20, 15))

        self.email = ctk.CTkEntry(card, placeholder_text="E-mail", width=300,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.email.pack(pady=6)

        self.senha = ctk.CTkEntry(card, placeholder_text="Senha", show="*", width=300,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.senha.pack(pady=6)
        self.senha.bind("<Return>", lambda e: self._login())

        self.mensagem = ctk.CTkLabel(card, text="", text_color=CORES["vermelho"],
            font=ctk.CTkFont(size=12))
        self.mensagem.pack(pady=4)

        ctk.CTkButton(card, text="Entrar", width=300,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._login).pack(pady=(4, 8))

        ctk.CTkFrame(card, height=1, fg_color=CORES["borda"]).pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(card, text="Não tem conta?",
            font=ctk.CTkFont(size=12),
            text_color=CORES["texto_secundario"]).pack()

        ctk.CTkButton(card, text="Criar conta", width=300,
            fg_color="transparent", border_width=1, border_color=CORES["borda_ouro"],
            text_color=CORES["ouro"], hover_color=CORES["bg_input"],
            command=self._abrir_cadastro).pack(pady=(4, 20))

    def _login(self):
        usuario = login_usuario(self.email.get(), self.senha.get())
        if usuario:
            self.ao_logar(usuario)
        else:
            self.mensagem.configure(text="E-mail ou senha incorretos.")

    def _abrir_cadastro(self):
        from telas.tela_cadastro import TelaCadastro
        TelaCadastro(self)