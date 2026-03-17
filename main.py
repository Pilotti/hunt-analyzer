import customtkinter as ctk
from utils.database import inicializar

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hunt Analyzer")
        self.geometry("900x600")
        self.minsize(800, 500)
        self._usuario = None
        self._frame_atual = None
        inicializar()
        self._mostrar_login()

    def _limpar(self):
        if self._frame_atual:
            self._frame_atual.destroy()

    def _mostrar_login(self):
        from telas.tela_login import TelaLogin
        self._limpar()
        self._frame_atual = TelaLogin(self, ao_logar=self._ao_logar)
        self._frame_atual.pack(fill="both", expand=True)

    def _ao_logar(self, usuario):
        self._usuario = usuario
        self._mostrar_personagens()

    def _mostrar_personagens(self):
        from telas.tela_personagens import TelaPersonagens
        self._limpar()
        self._frame_atual = TelaPersonagens(self, usuario=self._usuario,
            ao_selecionar=self._ao_selecionar_personagem,
            ao_historico=self._mostrar_historico)
        self._frame_atual.pack(fill="both", expand=True)

    def _ao_selecionar_personagem(self, personagem):
        self._mostrar_hunt(personagem)

    def _mostrar_hunt(self, personagem):
        from telas.tela_hunt import TelaHunt
        self._limpar()
        self._frame_atual = TelaHunt(self, usuario=self._usuario,
            personagem=personagem,
            ao_voltar=self._mostrar_personagens,
            ao_finalizar=self._mostrar_personagens)
        self._frame_atual.pack(fill="both", expand=True)

    def _mostrar_historico(self, personagem):
        from telas.tela_historico import TelaHistorico
        self._limpar()
        self._frame_atual = TelaHistorico(self, personagem=personagem,
            ao_voltar=self._mostrar_personagens)
        self._frame_atual.pack(fill="both", expand=True)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()