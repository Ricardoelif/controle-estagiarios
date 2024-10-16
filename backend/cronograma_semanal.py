import streamlit as st
import pandas as pd
import datetime
from data import carregar_estagiarios, inserir_cronograma_no_banco, resetar_cronograma
from utils import conectar_banco

def criar_tabela_cronograma(conn):
    st.markdown("### Cronograma Semanal")

    if 'cronograma' not in st.session_state:
        st.session_state['cronograma'] = pd.DataFrame(columns=['nome', 'horario_inicio', 'horario_fim', 'computador_alocado', 'dias_semana'])

    # Carregar estagiários do banco de dados
    estagiarios = carregar_estagiarios(conn)

    # Mapeamento dos dias para nomes completos
    dias_nome_completo = {
        'Seg': 'Segunda-Feira',
        'Ter': 'Terça-Feira',
        'Qua': 'Quarta-Feira',
        'Qui': 'Quinta-Feira',
        'Sex': 'Sexta-Feira'
    }

    if estagiarios:
        estagiario_selecionado = st.selectbox("Selecione o Estagiário", estagiarios)

        if estagiario_selecionado:
            horario_inicio = st.time_input("Horário de Início", datetime.time(8, 0), key="horario_inicio")
            horario_fim = st.time_input("Horário de Fim", datetime.time(12, 0), key="horario_fim")
            computador = st.selectbox("Computador Alocado", ['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5'], key="computador")
            dias_semana = st.multiselect("Dias da Semana", list(dias_nome_completo.values()), key="dias_semana")

            if st.button("Adicionar"):
                if horario_inicio < horario_fim and dias_semana:
                    dias_abreviados = [k for k, v in dias_nome_completo.items() if v in dias_semana]
                    novo_registro = pd.DataFrame({
                        'nome': [estagiario_selecionado],
                        'horario_inicio': [horario_inicio],
                        'horario_fim': [horario_fim],
                        'computador_alocado': [computador],
                        'dias_semana': [','.join(dias_abreviados)]
                    })

                    st.session_state['cronograma'] = pd.concat([st.session_state['cronograma'], novo_registro], ignore_index=True)
                    st.success("Registro adicionado ao cronograma!")
                else:
                    st.error("Verifique os horários e dias da semana antes de adicionar.")

            st.markdown("#### Cronograma Atual:")
            if not st.session_state['cronograma'].empty:
                for index, row in st.session_state['cronograma'].iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                    col1.write(row['nome'])
                    col2.write(row['horario_inicio'])
                    col3.write(row['horario_fim'])
                    col4.write(row['computador_alocado'])
                    col5.write(', '.join([dias_nome_completo[d] for d in row['dias_semana'].split(',')]))
                    if col6.button("❌", key=f"delete_{index}"):
                        st.session_state['cronograma'].drop(index, inplace=True)
                        st.session_state['cronograma'].reset_index(drop=True, inplace=True)

            if st.button("Lançar Cronograma"):
                cronograma_df = st.session_state['cronograma']
                inserir_cronograma_no_banco(conn, cronograma_df)
                st.success("Cronograma lançado com sucesso no banco de dados!")

            if st.button("Resetar Cronograma"):
                resetar_cronograma(conn)
                st.success("Cronograma resetado com sucesso!")
                st.session_state['cronograma'] = pd.DataFrame(columns=['nome', 'horario_inicio', 'horario_fim', 'computador_alocado', 'dias_semana'])

def main():
    conn = conectar_banco()
    criar_tabela_cronograma(conn)

if __name__ == "__main__":
    main()