from db_utils import try_open_with_key
import tela_login
import tela_alterar

if __name__ == "__main__":
    if try_open_with_key("1234"):
        tela_alterar.tela_forcar_alteracao()
    else:
        tela_login.criar_tela_login()
