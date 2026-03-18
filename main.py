import customtkinter as ctk
from utils.database import inicializar
from assets.theme import CORES, VERSAO

class App:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title(f"Hunt Analyzer {VERSAO}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=CORES["bg_principal"])
        self.root.withdraw()

        largura = 900
        altura = 620
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")

        self._usuario = None
        self._frame_atual = None
        inicializar()

        from telas.tela_splash import TelaSplash
        TelaSplash(self.root, self._apos_splash)
        self.root.mainloop()

    def _apos_splash(self):
        self.root.deiconify()
        self._mostrar_login()

    def _limpar(self):
        if self._frame_atual:
            self._frame_atual.destroy()

    def _construir_rodape(self):
        rodape = ctk.CTkFrame(self.root, fg_color=CORES["bg_header"],
            corner_radius=0, height=24)
        rodape.pack(side="bottom", fill="x")
        rodape.pack_propagate(False)

        ctk.CTkLabel(rodape, text=f"Hunt Analyzer {VERSAO}  •  PokéXGames",
            font=ctk.CTkFont(size=10),
            text_color=CORES["texto_desabilitado"]).pack(side="right", padx=12)

    def _mostrar_login(self):
        from telas.tela_login import TelaLogin
        self._limpar()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._frame_atual = TelaLogin(self.root, ao_logar=self._ao_logar)
        self._frame_atual.pack(fill="both", expand=True)

    def _ao_logar(self, usuario):
        self._usuario = usuario
        self._mostrar_personagens()

    def _mostrar_personagens(self):
        from telas.tela_personagens import TelaPersonagens
        self._limpar()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._frame_atual = TelaPersonagens(self.root,
            usuario=self._usuario,
            ao_selecionar=self._ao_selecionar_personagem,
            ao_historico=self._mostrar_historico,
            ao_sair=self._mostrar_login)
        self._frame_atual.pack(fill="both", expand=True)

    def _ao_selecionar_personagem(self, personagem):
        self._mostrar_hunt(personagem)

    def _mostrar_hunt(self, personagem):
        from telas.tela_hunt import TelaHunt
        self._limpar()
        self._frame_atual = TelaHunt(self.root,
            usuario=self._usuario,
            personagem=personagem,
            ao_voltar=self._mostrar_personagens,
            ao_finalizar=self._mostrar_personagens)
        self._frame_atual.pack(fill="both", expand=True)

    def _mostrar_historico(self, personagem):
        from telas.tela_historico import TelaHistorico
        self._limpar()
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._frame_atual = TelaHistorico(self.root,
            personagem=personagem,
            ao_voltar=self._mostrar_personagens)
        self._frame_atual.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()