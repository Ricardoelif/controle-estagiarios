import streamlit as st
import pandas as pd
import datetime
from data import (
    carregar_estagiarios,
    inserir_cronograma_no_banco,
    resetar_cronograma,
    carregar_cronograma
)
from utils import conectar_banco

def criar_tabela_cronograma(conn):
    st.markdown("### Cronograma Semanal")

    if 'cronograma' not in st.session_state:
        st.session_state['cronograma'] = pd.DataFrame(columns=['nome', 'horario_inicio', 'horario_fim', 'computador_alocado', 'dias_semana'])

    # Carregar estagiários do banco de dados
    estagiarios = carregar_estagiarios(conn)

    # Carregar cronograma existente do banco de dados
    cronograma_existente = carregar_cronograma(conn)  # Esta função deve retornar um DataFrame

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
            computador = st.selectbox("Computador Alocado", ['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5', 'PC Externo'], key="computador")
            dias_semana = st.multiselect("Dias da Semana", list(dias_nome_completo.values()), key="dias_semana")

            if st.button("Adicionar"):
                if horario_inicio < horario_fim and dias_semana:
                    dias_abreviados = [k for k, v in dias_nome_completo.items() if v in dias_semana]

                    # Criar novo registro
                    novo_registro = pd.DataFrame({
                        'nome': [estagiario_selecionado],
                        'horario_inicio': [horario_inicio],
                        'horario_fim': [horario_fim],
                        'computador_alocado': [computador],
                        'dias_semana': [','.join(dias_abreviados)]
                    })

                    # Combinar cronograma existente e o novo para verificação
                    cronograma_total = pd.concat([st.session_state['cronograma'], cronograma_existente], ignore_index=True)

                    # Verificar conflitos
                    conflito = verifica_conflito(
                        novo_registro,
                        cronograma_total
                    )

                    if conflito:
                        if conflito['nome'] != estagiario_selecionado:
                            st.error(f"Conflito de horário com o estagiário {conflito['nome']} no computador {computador} nos dias {', '.join(conflito['dias_conflito'])}.")
                        else:
                            # Substituir o horário existente do mesmo estagiário
                            st.session_state['cronograma'] = atualiza_horario(
                                st.session_state['cronograma'],
                                novo_registro
                            )
                            st.success("Horário do estagiário atualizado com sucesso!")
                    else:
                        # Adicionar novo registro
                        st.session_state['cronograma'] = pd.concat([st.session_state['cronograma'], novo_registro], ignore_index=True)
                        st.success("Registro adicionado ao cronograma!")
                else:
                    st.error("Verifique os horários e dias da semana antes de adicionar.")

            st.markdown("#### Cronograma Atual:")
            if not st.session_state['cronograma'].empty:
                for index, row in st.session_state['cronograma'].iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 1])
                    col1.write(row['nome'])
                    col2.write(row['horario_inicio'].strftime('%H:%M'))
                    col3.write(row['horario_fim'].strftime('%H:%M'))
                    col4.write(row['computador_alocado'])
                    col5.write(', '.join([dias_nome_completo[d] for d in row['dias_semana'].split(',')]))
                    if col6.button("❌", key=f"delete_{index}"):
                        st.session_state['cronograma'].drop(index, inplace=True)
                        st.session_state['cronograma'].reset_index(drop=True, inplace=True)

            if st.button("Lançar Cronograma"):
                cronograma_df = st.session_state['cronograma']
                inserir_cronograma_no_banco(conn, cronograma_df)
                st.success("Cronograma lançado com sucesso no banco de dados!")
                # Limpar o cronograma após inserir
                st.session_state['cronograma'] = pd.DataFrame(columns=['nome', 'horario_inicio', 'horario_fim', 'computador_alocado', 'dias_semana'])

            if st.button("Resetar Cronograma"):
                resetar_cronograma(conn)
                st.success("Cronograma resetado com sucesso!")
                st.session_state['cronograma'] = pd.DataFrame(columns=['nome', 'horario_inicio', 'horario_fim', 'computador_alocado', 'dias_semana'])

def verifica_conflito(novo_registro, cronograma_total):
    novo_inicio = novo_registro['horario_inicio'].iloc[0]
    novo_fim = novo_registro['horario_fim'].iloc[0]
    novo_computador = novo_registro['computador_alocado'].iloc[0]
    novo_nome = novo_registro['nome'].iloc[0]
    novos_dias = set(novo_registro['dias_semana'].iloc[0].split(','))

    for _, row in cronograma_total.iterrows():
        existente_inicio = row['horario_inicio']
        existente_fim = row['horario_fim']
        existente_computador = row['computador_alocado']
        existente_nome = row['nome']
        existentes_dias = set(row['dias_semana'].split(','))

        # Verificar se os computadores são os mesmos
        if existente_computador == novo_computador:
            # Verificar se os dias se sobrepõem
            dias_comuns = novos_dias & existentes_dias
            if dias_comuns:
                # Verificar se os horários se sobrepõem
                if not (novo_fim <= existente_inicio or novo_inicio >= existente_fim):
                    return {
                        'nome': existente_nome,
                        'dias_conflito': [dia for dia in dias_comuns]
                    }
    return None

def atualiza_horario(cronograma, novo_registro):
    nome = novo_registro['nome'].iloc[0]
    computador = novo_registro['computador_alocado'].iloc[0]
    dias_novos = set(novo_registro['dias_semana'].iloc[0].split(','))

    # Remover entradas que têm o mesmo nome, computador e dias em comum
    indices_para_remover = []
    for index, row in cronograma.iterrows():
        if row['nome'] == nome and row['computador_alocado'] == computador:
            dias_existentes = set(row['dias_semana'].split(','))
            if dias_novos & dias_existentes:
                indices_para_remover.append(index)

    cronograma.drop(indices_para_remover, inplace=True)
    cronograma.reset_index(drop=True, inplace=True)

    # Adicionar o novo registro
    cronograma = pd.concat([cronograma, novo_registro], ignore_index=True)
    return cronograma
