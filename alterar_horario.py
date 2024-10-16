import streamlit as st
import datetime
from data import (
    carregar_estagiarios,
    carregar_cronograma,
    atualizar_horario_estagiario,
    remover_horario_estagiario
)

def alterar_horario(conn):
    st.markdown("### Alteração de Horário e Computador")

    # Carregar estagiários do banco de dados
    estagiarios = carregar_estagiarios(conn)

    if estagiarios:
        estagiario = st.selectbox("Selecione o Estagiário", ["Selecione"] + estagiarios)

        if estagiario != "Selecione":
            # Carregar cronograma e filtrar pelo estagiário selecionado
            cronograma_df = carregar_cronograma(conn)
            registros_filtrados = cronograma_df[cronograma_df['nome'] == estagiario]

            if not registros_filtrados.empty:
                st.markdown("### Registros Cadastrados para o Estagiário Selecionado")
                # Criar cabeçalhos da tabela
                cols = st.columns([2, 2, 2, 2, 2, 1, 1])
                headers = ['Horário Início', 'Horário Fim', 'Computador Alocado', 'Dias da Semana', '', '']
                for col, header in zip(cols, headers):
                    col.markdown(f"**{header}**")

                # Exibir registros em formato de tabela com botões
                for index, row in registros_filtrados.iterrows():
                    cols = st.columns([2, 2, 2, 2, 2, 1, 1])
                    cols[0].write(row['horario_inicio'])
                    cols[1].write(row['horario_fim'])
                    cols[2].write(row['computador_alocado'])
                    cols[3].write(row['dias_semana'])

                    editar = cols[4].button("✏️", key=f"editar_{row['id']}")
                    excluir = cols[5].button("❌", key=f"apagar_{row['id']}")

                    if editar:
                        # Armazenar o ID e os dados do registro selecionado
                        st.session_state['editar_registro_id'] = row['id']
                        st.session_state['editar_registro'] = row.copy()
                    if excluir:
                        remover_horario_estagiario(conn, row['id'])
                        st.success(f"Horário de {estagiario} removido com sucesso!")
                        st.session_state['updated'] = True
                        st.rerun()

                # Se um registro estiver em edição
                if 'editar_registro' in st.session_state:
                    registro = st.session_state['editar_registro']
                    registro_id = st.session_state['editar_registro_id']
                    st.markdown("### Editar Registro")

                    # Converter strings de horário para objetos datetime.time, se necessário
                    if isinstance(registro['horario_inicio'], str):
                        horario_inicio_obj = datetime.datetime.strptime(registro['horario_inicio'], '%H:%M:%S').time()
                    else:
                        horario_inicio_obj = registro['horario_inicio']

                    if isinstance(registro['horario_fim'], str):
                        horario_fim_obj = datetime.datetime.strptime(registro['horario_fim'], '%H:%M:%S').time()
                    else:
                        horario_fim_obj = registro['horario_fim']

                    novo_horario_inicio = st.time_input("Novo Horário de Início", horario_inicio_obj, key="novo_inicio")
                    novo_horario_fim = st.time_input("Novo Horário de Fim", horario_fim_obj, key="novo_fim")

                    # Campo para selecionar o novo computador alocado
                    computadores_disponiveis = ['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5', 'PC Externo']
                    computador_atual = registro['computador_alocado']
                    if computador_atual not in computadores_disponiveis:
                        computadores_disponiveis.append(computador_atual)
                    novo_computador = st.selectbox("Novo Computador Alocado", computadores_disponiveis, index=computadores_disponiveis.index(computador_atual), key="novo_computador")

                    if st.button("Salvar Alterações"):
                        if novo_horario_inicio < novo_horario_fim:
                            # Verificar conflitos antes de atualizar
                            conflito = verifica_conflito_edicao(
                                conn,
                                registro_id,
                                novo_horario_inicio,
                                novo_horario_fim,
                                novo_computador,
                                registro['dias_semana']
                            )
                            if conflito:
                                st.error(f"Conflito de horário com o estagiário {conflito['nome']} no computador {novo_computador} nos dias {', '.join(conflito['dias_conflito'])}.")
                            else:
                                try:
                                    # Converter os horários para strings no formato 'HH:MM:SS'
                                    novo_horario_inicio_str = novo_horario_inicio.strftime('%H:%M:%S')
                                    novo_horario_fim_str = novo_horario_fim.strftime('%H:%M:%S')
                                    # Chamar a função para atualizar os campos necessários, incluindo o computador alocado
                                    atualizar_horario_estagiario(conn, registro_id, novo_horario_inicio_str, novo_horario_fim_str, novo_computador)
                                    st.success(f"Horário e computador de {registro['nome']} alterados com sucesso!")
                                    # Limpar o estado de edição
                                    del st.session_state['editar_registro']
                                    del st.session_state['editar_registro_id']
                                    st.session_state['updated'] = True
                                except Exception as e:
                                    st.error("Ocorreu um erro ao atualizar o horário e o computador.")
                                    st.error(str(e))
                                    st.stop()
                                st.rerun()
                        else:
                            st.error("O horário de início deve ser anterior ao horário de fim.")
            else:
                st.warning("Nenhum horário cadastrado para o estagiário selecionado.")
                st.stop()

def verifica_conflito_edicao(conn, registro_id, novo_inicio, novo_fim, novo_computador, dias_semana):
    # Carregar cronograma e excluir o registro que está sendo editado
    cronograma_df = carregar_cronograma(conn)
    cronograma_df = cronograma_df[cronograma_df['id'] != registro_id]

    novos_dias = set(dias_semana.split(','))

    for _, row in cronograma_df.iterrows():
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
                # Converter horários para datetime.time, se necessário
                if isinstance(existente_inicio, str):
                    existente_inicio = datetime.datetime.strptime(existente_inicio, '%H:%M:%S').time()
                if isinstance(existente_fim, str):
                    existente_fim = datetime.datetime.strptime(existente_fim, '%H:%M:%S').time()
                # Verificar se os horários se sobrepõem
                if not (novo_fim <= existente_inicio or novo_inicio >= existente_fim):
                    return {
                        'nome': existente_nome,
                        'dias_conflito': list(dias_comuns)
                    }
    return None
