import streamlit as st
from streamlit_option_menu import option_menu
from utils import conectar_banco
from cronograma_semanal import criar_tabela_cronograma
from visualizar_cronograma import visualizar_cronograma
from adicionar_estagiario import adicionar_estagiario
from alterar_horario import alterar_horario
from login import tela_login
import logging

# Set the root logger to WARNING to suppress DEBUG messages from libraries
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Função principal
def main():
    conn = conectar_banco()
    logger.debug("Database connection established.")

    # Verificar se o usuário já está logado
    if 'logado' not in st.session_state:
        st.session_state['logado'] = False
        logger.debug("User not logged in.")

    if not st.session_state['logado']:
        # Mostrar tela de login se não estiver logado
        tela_login(conn)
    else:
        # Mostrar o menu principal se o usuário estiver logado
        criar_menu(conn)

# Função para criar o menu principal
def criar_menu(conn):
    logger.debug("Creating main menu.")
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
