import customtkinter as ctk
from utils.auth import cadastrar_usuario, email_valido
from assets.theme import CORES

class TelaCadastro(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Hunt Analyzer — Cadastro")
        self.geometry("420x520")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color=CORES["bg_principal"])
        self.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() // 2) - 210
        y = master.winfo_rooty() + (master.winfo_height() // 2) - 260
        self.geometry(f"+{x}+{y}")
        self._construir()

    def _construir(self):
        ctk.CTkLabel(self, text="⚔",
            font=ctk.CTkFont(size=32),
            text_color=CORES["ouro"]).pack(pady=(30, 0))

        ctk.CTkLabel(self, text="Criar conta",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=CORES["texto_principal"]).pack(pady=(5, 2))

        ctk.CTkLabel(self, text="Preencha os dados abaixo",
            font=ctk.CTkFont(size=13),
            text_color=CORES["texto_secundario"]).pack(pady=(0, 20))

        card = ctk.CTkFrame(self, fg_color=CORES["bg_card"],
            corner_radius=12, border_width=1, border_color=CORES["borda"])
        card.pack(padx=30, fill="x", ipadx=10, ipady=10)

        self.email = ctk.CTkEntry(card, placeholder_text="E-mail", width=320,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.email.pack(pady=(20, 6))

        self.senha = ctk.CTkEntry(card, placeholder_text="Senha", show="*", width=320,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.senha.pack(pady=6)

        self.confirmar_senha = ctk.CTkEntry(card, placeholder_text="Confirmar senha", show="*", width=320,
            fg_color=CORES["bg_input"], border_color=CORES["borda"],
            text_color=CORES["texto_principal"])
        self.confirmar_senha.pack(pady=6)

        self.mensagem = ctk.CTkLabel(card, text="", text_color=CORES["vermelho"],
            font=ctk.CTkFont(size=12))
        self.mensagem.pack(pady=4)

        ctk.CTkButton(card, text="Cadastrar", width=320,
            fg_color=CORES["ouro"], hover_color=CORES["ouro_hover"],
            text_color="#1a1a1a", font=ctk.CTkFont(size=13, weight="bold"),
            command=self._cadastrar).pack(pady=(4, 8))

        ctk.CTkButton(card, text="Voltar", width=320,
            fg_color="transparent", border_width=1, border_color=CORES["borda"],
            text_color=CORES["texto_secundario"], hover_color=CORES["bg_input"],
            command=self.destroy).pack(pady=(0, 20))

    def _cadastrar(self):
        email = self.email.get().strip()
        senha = self.senha.get()
        confirmar = self.confirmar_senha.get()

        if not email or not senha or not confirmar:
            self.mensagem.configure(text="Preencha todos os campos.")
            return

        if not email_valido(email):
            self.mensagem.configure(text="E-mail inválido.")
            return

        if senha != confirmar:
            self.mensagem.configure(text="As senhas não coincidem.")
            return

        if len(senha) < 6:
            self.mensagem.configure(text="Senha deve ter no mínimo 6 caracteres.")
            return

        if cadastrar_usuario(email, senha):
            self.mensagem.configure(text_color=CORES["verde"], text="Conta criada com sucesso!")
            self.after(1500, self.destroy)
        else:
            self.mensagem.configure(text_color=CORES["vermelho"], text="E-mail já cadastrado.")