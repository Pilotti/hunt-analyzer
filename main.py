from utils.database import inicializar
from telas.tela_login import TelaLogin
from telas.tela_personagens import TelaPersonagens
from telas.tela_hunt import TelaHunt

def ao_iniciar_hunt(usuario, personagem):
    app = TelaHunt(usuario, personagem, lambda: ao_logar(usuario))
    app.mainloop()

def ao_selecionar_personagem(usuario, personagem):
    ao_iniciar_hunt(usuario, personagem)

def ao_logar(usuario):
    app = TelaPersonagens(usuario, lambda p: ao_selecionar_personagem(usuario, p))
    app.mainloop()

if __name__ == "__main__":
    inicializar()
    app = TelaLogin(ao_logar)
    app.mainloop()