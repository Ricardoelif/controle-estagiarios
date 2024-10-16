import streamlit as st
from data import adicionar_estagiario_banco, remover_estagiario_banco, carregar_estagiarios

# Função para adicionar e remover estagiários
def adicionar_estagiario(conn):
    st.markdown("### Adicionar Estagiário")

    nome = st.text_input("Nome do Estagiário")

    if st.button("Cadastrar Estagiário"):
        if nome:
            # Adicionar estagiário ao banco de dados
            adicionar_estagiario_banco(conn, nome)
            st.success(f"Estagiário {nome} cadastrado com sucesso!")
        else:
            st.error("Por favor, insira um nome válido para o estagiário.")

    st.markdown("### Remover Estagiário")
    estagiarios = carregar_estagiarios(conn)

    if estagiarios:
        estagiario_selecionado = st.selectbox("Selecione o Estagiário para Remover", estagiarios)

        if st.button("Remover Estagiário"):
            remover_estagiario_banco(conn, estagiario_selecionado)
            st.success(f"Estagiário {estagiario_selecionado} removido com sucesso!")
