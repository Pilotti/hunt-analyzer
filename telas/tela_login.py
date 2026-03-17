import customtkinter as ctk
from utils.auth import login_usuario

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TelaLogin(ctk.CTk):
    def __init__(self, ao_logar):
        super().__init__()
        self.ao_logar = ao_logar
        self.title("Hunt Analyzer — Login")
        self.geometry("400x500")
        self.resizable(False, False)
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="Hunt Analyzer", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Faça login para continuar", font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        self.email = ctk.CTkEntry(self, placeholder_text="E-mail", width=300)
        self.email.pack(pady=8)

        self.senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=300)
        self.senha.pack(pady=8)

        self.mensagem = ctk.CTkLabel(self, text="", text_color="red")
        self.mensagem.pack(pady=5)

        ctk.CTkButton(self, text="Entrar", width=300, command=self._login).pack(pady=8)

        ctk.CTkLabel(self, text="Não tem conta?", font=ctk.CTkFont(size=12)).pack(pady=(20, 0))
        ctk.CTkButton(self, text="Cadastre-se", width=300, fg_color="transparent",
            border_width=1, command=self._abrir_cadastro).pack(pady=4)

    def _login(self):
        usuario = login_usuario(self.email.get(), self.senha.get())
        if usuario:
            self.destroy()
            self.ao_logar(usuario)
        else:
            self.mensagem.configure(text="E-mail ou senha incorretos.")

    def _abrir_cadastro(self):
        from telas.tela_cadastro import TelaCadastro
        TelaCadastro(self)