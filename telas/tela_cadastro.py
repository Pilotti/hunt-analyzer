import customtkinter as ctk
from utils.auth import cadastrar_usuario

class TelaCadastro(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Hunt Analyzer — Cadastro")
        self.geometry("400x500")
        self.resizable(False, False)
        self.grab_set()
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="Criar conta", font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(40, 5))
        ctk.CTkLabel(self, text="Preencha os dados abaixo", font=ctk.CTkFont(size=14)).pack(pady=(0, 30))

        self.email = ctk.CTkEntry(self, placeholder_text="E-mail", width=300)
        self.email.pack(pady=8)

        self.senha = ctk.CTkEntry(self, placeholder_text="Senha", show="*", width=300)
        self.senha.pack(pady=8)

        self.confirmar_senha = ctk.CTkEntry(self, placeholder_text="Confirmar senha", show="*", width=300)
        self.confirmar_senha.pack(pady=8)

        self.mensagem = ctk.CTkLabel(self, text="", text_color="red")
        self.mensagem.pack(pady=5)

        ctk.CTkButton(self, text="Cadastrar", width=300, command=self._cadastrar).pack(pady=8)
        ctk.CTkButton(self, text="Voltar", width=300, fg_color="transparent",
            border_width=1, command=self.destroy).pack(pady=4)

    def _cadastrar(self):
        email = self.email.get()
        senha = self.senha.get()
        confirmar = self.confirmar_senha.get()

        if not email or not senha or not confirmar:
            self.mensagem.configure(text="Preencha todos os campos.")
            return

        if senha != confirmar:
            self.mensagem.configure(text="As senhas não coincidem.")
            return

        if len(senha) < 6:
            self.mensagem.configure(text="Senha deve ter no mínimo 6 caracteres.")
            return

        if cadastrar_usuario(email, senha):
            self.mensagem.configure(text_color="green", text="Conta criada com sucesso!")
            self.after(1500, self.destroy)
        else:
            self.mensagem.configure(text_color="red", text="E-mail já cadastrado.")