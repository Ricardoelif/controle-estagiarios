import streamlit as st
import pandas as pd
import plotly.express as px
from data import carregar_cronograma

def visualizar_cronograma(conn):
    st.title("Visualização do Cronograma")

    # Carregar cronograma do banco de dados
    cronograma_df = carregar_cronograma(conn)

    if cronograma_df.empty:
        st.warning("Nenhum cronograma encontrado no banco de dados.")
    else:
        # Converter os horários para datetime compatível
        cronograma_df['horario_inicio'] = pd.to_datetime(cronograma_df['horario_inicio'], format='%H:%M:%S')
        cronograma_df['horario_fim'] = pd.to_datetime(cronograma_df['horario_fim'], format='%H:%M:%S')

        # Remover duplicatas e combinar dias da semana em ordem lógica
        dias_ordem = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex']
        cronograma_df = cronograma_df.groupby(['nome', 'horario_inicio', 'horario_fim', 'computador_alocado']).agg({
            'dias_semana': lambda x: ','.join(sorted(set(
                day.strip() for days in x for day in days.split(',')), key=lambda d: dias_ordem.index(d)))
        }).reset_index()

        # Mapeamento dos dias para nomes completos
        dias_nome_completo = {
            'Seg': 'Segunda-Feira',
            'Ter': 'Terça-Feira',
            'Qua': 'Quarta-Feira',
            'Qui': 'Quinta-Feira',
            'Sex': 'Sexta-Feira'
        }

        # Dropdown para selecionar o dia da semana
        dias_da_semana = cronograma_df['dias_semana'].str.split(',').explode().unique()
        dias_da_semana_completo = [dias_nome_completo[d] for d in dias_da_semana if d in dias_nome_completo]
        dia_selecionado = st.selectbox("Selecione o Dia da Semana", sorted(dias_da_semana_completo, key=lambda d: list(dias_nome_completo.values()).index(d)))

        # Filtrar o DataFrame pelo dia selecionado
        dia_abreviado = [k for k, v in dias_nome_completo.items() if v == dia_selecionado][0]
        cronograma_filtrado = cronograma_df[cronograma_df['dias_semana'].str.contains(dia_abreviado)]

        # Criar gráfico para visualização do cronograma filtrado
        fig = px.timeline(
            cronograma_filtrado,
            x_start='horario_inicio',
            x_end='horario_fim',
            y='computador_alocado',
            color='nome',
            title=f'Ocupação dos Computadores - {dia_selecionado}',
            labels={'computador_alocado': 'Computador', 'nome': 'Estagiário'},
            text='nome'
        )
        fig.update_layout(
            xaxis_title='Horário',
            yaxis_title='Computador',
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        fig.update_traces(textposition='inside', textfont_size=12, textfont=dict(weight='bold'))

        st.plotly_chart(fig, use_container_width=True)

        # Exibir o cronograma filtrado em formato de tabela
        st.markdown(f"#### Cronograma Atual do Banco de Dados para {dia_selecionado}:")
        st.dataframe(cronograma_filtrado)