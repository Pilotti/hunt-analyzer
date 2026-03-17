from utils.database import inicializar
from telas.tela_login import TelaLogin
from telas.tela_personagens import TelaPersonagens

def ao_selecionar_personagem(personagem):
    print(f"Personagem selecionado: {personagem['nome']}")

def ao_logar(usuario):
    app = TelaPersonagens(usuario, ao_selecionar_personagem)
    app.mainloop()

if __name__ == "__main__":
    inicializar()
    app = TelaLogin(ao_logar)
    app.mainloop()