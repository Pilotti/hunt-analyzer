from utils.database import inicializar
from telas.tela_login import TelaLogin

def ao_logar(usuario):
    print(f"Logado como: {usuario['email']}")

if __name__ == "__main__":
    inicializar()
    app = TelaLogin(ao_logar)
    app.mainloop()