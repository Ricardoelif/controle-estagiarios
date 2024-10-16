import streamlit as st
import datetime
from data import (
    carregar_estagiarios,
    carregar_cronograma,
    atualizar_horario_estagiario,
    remover_horario_estagiario
)

# Função para alterar horário do estagiário
def alterar_horario(conn):
    st.markdown("### Alteração de Horário")

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
                headers = ['Horário Início', 'Horário Fim', 'Computador Alocado', 'Dias da Semana', '', '', '']
                for col, header in zip(cols, headers):
                    col.markdown(f"**{header}**")

                # Exibir registros em formato de tabela com botões
                for index, row in registros_filtrados.iterrows():
                    cols = st.columns([2, 2, 2, 2, 2, 1, 1])
                    cols[0].write(row['horario_inicio'])
                    cols[1].write(row['horario_fim'])
                    cols[2].write(row['computador_alocado'])
                    cols[3].write(row['dias_semana'])

                    editar = cols[5].button("✏️", key=f"editar_{row['id']}")
                    excluir = cols[6].button("❌", key=f"apagar_{row['id']}")

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

                    if st.button("Salvar Alterações"):
                        if novo_horario_inicio < novo_horario_fim:
                            try:
                                # Converter os horários para strings no formato 'HH:MM:SS'
                                novo_horario_inicio_str = novo_horario_inicio.strftime('%H:%M:%S')
                                novo_horario_fim_str = novo_horario_fim.strftime('%H:%M:%S')
                                # Chamar a função para atualizar apenas os campos necessários
                                atualizar_horario_estagiario(conn, registro_id, novo_horario_inicio_str, novo_horario_fim_str)
                                st.success(f"Horário de {registro['nome']} alterado com sucesso!")
                                # Limpar o estado de edição
                                del st.session_state['editar_registro']
                                del st.session_state['editar_registro_id']
                                st.session_state['updated'] = True
                            except Exception as e:
                                st.error("Ocorreu um erro ao atualizar o horário.")
                                st.stop()
                            st.rerun()
                        else:
                            st.error("O horário de início deve ser anterior ao horário de fim.")
            else:
                st.warning("Nenhum horário cadastrado para o estagiário selecionado.")
                st.stop()