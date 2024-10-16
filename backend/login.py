import streamlit as st
import psycopg2
from utils import conectar_banco
import os
import base64

def tela_login(conn):
    # Removemos o título "Login" para um visual mais limpo
    # st.title("Login")  # Esta linha foi removida

    # Exibir a imagem acima dos campos de login, centralizada e ampliada
    # Obter o diretório atual onde o script está sendo executado
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, 'img', 'estagio.png')
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <img src='data:image/png;base64,{encoded_image}' alt='Estagio' style='width:70%; height:auto;'/>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error(f"Imagem não encontrada: {image_path}")

    login = st.text_input("Login")
    senha = st.text_input("Senha", type="password")

    # Novo campo para a troca de senha
    trocar_senha = st.checkbox("Desejo trocar minha senha")

    if trocar_senha:
        nova_senha = st.text_input("Nova Senha", type="password")
        confirmar_senha = st.text_input("Confirme a Nova Senha", type="password")

    if st.button("Entrar"):
        try:
            # Conectar ao banco de dados e verificar se há um administrador correspondente
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM administradores WHERE login = %s AND senha = %s", (login, senha))
                resultado = cursor.fetchone()
                
                if resultado:
                    # Se o login for bem-sucedido, definir a sessão como logada
                    st.session_state['logado'] = True
                    st.session_state['nivel_acesso'] = resultado[3]  # Ajuste o índice conforme a estrutura da sua tabela
                    st.success("Login efetuado com sucesso!")
                    st.session_state['updated'] = True

                    # Verificar se o usuário deseja trocar a senha
                    if trocar_senha:
                        if nova_senha and confirmar_senha:
                            if nova_senha == confirmar_senha:
                                cursor.execute("UPDATE administradores SET senha = %s WHERE login = %s", (nova_senha, login))
                                conn.commit()
                                st.success("Senha alterada com sucesso!")
                            else:
                                st.error("As senhas não coincidem. Por favor, tente novamente.")
                                # Manter o usuário na tela de login para tentar novamente
                                st.session_state['logado'] = False
                                return
                        else:
                            st.error("Por favor, preencha os campos de nova senha.")
                            # Manter o usuário na tela de login para tentar novamente
                            st.session_state['logado'] = False
                            return
                    st.rerun()  # Para atualizar a tela e redirecionar ao menu
                else:
                    st.error("Login ou senha incorretos.")
        except Exception as e:
            st.error("Erro ao conectar ao banco de dados.")
            st.error(str(e))  # Mostrar detalhes do erro para debug
