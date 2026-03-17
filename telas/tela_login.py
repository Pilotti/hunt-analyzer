import customtkinter as ctk
from utils.auth import login_usuario

class TelaLogin(ctk.CTkFrame):
    def __init__(self, master, ao_logar):
        super().__init__(master, fg_color="transparent")
        self.ao_logar = ao_logar
        self._construir()

    def _construir(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center, text="Hunt Analyzer",
            font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(0, 5))
        ctk.CTkLabel(center, text="Faça login para continuar",
            font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        self.email = ctk.CTkEntry(center, placeholder_text="E-mail", width=300)
        self.email.pack(pady=8)

        self.senha = ctk.CTkEntry(center, placeholder_text="Senha", show="*", width=300)
        self.senha.pack(pady=8)
        self.senha.bind("<Return>", lambda e: self._login())

        self.mensagem = ctk.CTkLabel(center, text="", text_color="red")
        self.mensagem.pack(pady=5)

        ctk.CTkButton(center, text="Entrar", width=300, command=self._login).pack(pady=8)

        ctk.CTkLabel(center, text="Não tem conta?",
            font=ctk.CTkFont(size=12)).pack(pady=(20, 0))
        ctk.CTkButton(center, text="Cadastre-se", width=300,
            fg_color="transparent", border_width=1,
            command=self._abrir_cadastro).pack(pady=4)

    def _login(self):
        usuario = login_usuario(self.email.get(), self.senha.get())
        if usuario:
            self.ao_logar(usuario)
        else:
            self.mensagem.configure(text="E-mail ou senha incorretos.")

    def _abrir_cadastro(self):
        from telas.tela_cadastro import TelaCadastro
        TelaCadastro(self)