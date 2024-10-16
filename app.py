import streamlit as st
from streamlit_option_menu import option_menu
from utils import conectar_banco
from cronograma_semanal import criar_tabela_cronograma
from visualizar_cronograma import visualizar_cronograma
from adicionar_estagiario import adicionar_estagiario
from alterar_horario import alterar_horario
from login import tela_login
import logging

# Configurar logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Configurar a página
st.set_page_config(page_title="Controle de Estagiários", layout="wide")

# Função principal
def main():
    conn = conectar_banco()
    logger.debug("Conexão com o banco de dados estabelecida.")

    # Verificar se o usuário já está logado
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        logger.debug("Usuário não está logado.")

    if not st.session_state['logado']:
        # Mostrar tela de login se não estiver logado
        tela_login(conn)
    else:
        # Mostrar o menu principal se o usuário estiver logado
        criar_menu(conn)

# Função para criar o menu principal
def criar_menu(conn):
    logger.debug("Criando o menu principal.")
    # Definir o menu usando streamlit-option-menu
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=["Visualização do Cronograma", "Cronograma Semanal", "Adicionar Estagiário", "Alterar Horário"],
            icons=["eye", "calendar", "person-plus", "clock"],
            menu_icon="cast",
            default_index=0,
            orientation="vertical",
            styles={
                "container": {"padding": "0!important", "background-color": "#000000"},
                "icon": {"color": "#FFFFFF", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "--hover-color": "#333333",
                    "color": "#FFFFFF",
                },
                "nav-link-selected": {"background-color": "#444444", "font-weight": "bold", "color": "#FFFFFF"},
            }
        )

    # Chamar a função correspondente à opção selecionada
    if selected == "Visualização do Cronograma":
        visualizar_cronograma(conn)
    elif selected == "Cronograma Semanal":
        criar_tabela_cronograma(conn)
    elif selected == "Adicionar Estagiário":
        adicionar_estagiario(conn)
    elif selected == "Alterar Horário":
        alterar_horario(conn)

if __name__ == "__main__":
    main()
