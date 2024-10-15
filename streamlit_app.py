import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import psycopg2
import os
import streamlit.components.v1 as components

# Conexão com o Supabase (string completa)
DATABASE_URL = 'postgresql://postgres.iykkmaqmyterupyxzdej:4UJzihawH1bEFjna@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'

def conectar_banco():
    """Conecta ao banco de dados Supabase."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para inicializar a base de dados
def inicializar_db():
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS estagiarios (
                                id SERIAL PRIMARY KEY,
                                nome VARCHAR NOT NULL,
                                horario_inicio TIME NOT NULL,
                                horario_fim TIME NOT NULL,
                                computador_alocado VARCHAR NOT NULL)''')
                conn.commit()
        except Exception as e:
            st.error(f"Erro ao inicializar o banco de dados: {e}")
        finally:
            conn.close()

# Função para adicionar um novo estagiário no sistema
def adicionar_estagiario(nome, horario_inicio, horario_fim, computador):
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO estagiarios (nome, horario_inicio, horario_fim, computador_alocado) VALUES (%s, %s, %s, %s)",
                               (nome, horario_inicio, horario_fim, computador))
                conn.commit()
        except Exception as e:
            st.error(f"Erro ao adicionar estagiário: {e}")
        finally:
            conn.close()

# Função para atualizar o horário de um estagiário
def atualizar_horario_estagiario(id, horario_inicio, horario_fim, computador):
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE estagiarios SET horario_inicio = %s, horario_fim = %s, computador_alocado = %s WHERE id = %s",
                               (horario_inicio, horario_fim, computador, id))
                conn.commit()
        except Exception as e:
            st.error(f"Erro ao atualizar horário do estagiário: {e}")
        finally:
            conn.close()

# Função para excluir um estagiário e reordenar os IDs
def excluir_estagiario(id):
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM estagiarios WHERE id = %s", (id,))
                conn.commit()

                # Reordenar os IDs após exclusão
                cursor.execute("""
                    WITH RECURSIVE cte AS (
                        SELECT id, ROW_NUMBER() OVER (ORDER BY id) AS new_id
                        FROM estagiarios
                    )
                    UPDATE estagiarios
                    SET id = cte.new_id
                    FROM cte
                    WHERE estagiarios.id = cte.id;
                """)
                conn.commit()
        except Exception as e:
            st.error(f"Erro ao excluir estagiário: {e}")
        finally:
            conn.close()

# Função para visualizar os estagiários e horários
def visualizar_estagiarios():
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM estagiarios ORDER BY id")
                rows = cursor.fetchall()
                colunas = [desc[0] for desc in cursor.description]
                return pd.DataFrame(rows, columns=colunas)
        except Exception as e:
            st.error(f"Erro ao visualizar estagiários: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    else:
        return pd.DataFrame()

# Função para verificar se há conflitos de horário, ignorando o próprio estagiário
def verificar_conflito(horario_inicio, horario_fim, computador, estagiario_id=None):
    conn = conectar_banco()
    if conn:
        try:
            with conn.cursor() as cursor:
                query = """
                SELECT * FROM estagiarios
                WHERE computador_alocado = %s
                AND id != %s
                AND (
                    (horario_inicio <= %s AND horario_fim > %s) OR
                    (horario_inicio < %s AND horario_fim >= %s)
                )
                """
                cursor.execute(query, (computador, estagiario_id, horario_inicio, horario_inicio, horario_fim, horario_fim))
                result = cursor.fetchall()
                return len(result) > 0
        except Exception as e:
            st.error(f"Erro ao verificar conflito de horário: {e}")
            return False
        finally:
            conn.close()
    else:
        return False

# Inicializando a base de dados
inicializar_db()

# Interface com Streamlit
st.set_page_config(page_title="Controle de Estagiários", page_icon="📊", layout="centered")
st.title('📊 Controle de Computadores para Estagiários')

# Estilo CSS customizado
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
        margin: 5px;
        cursor: pointer;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .st-expander {
        background-color: #f1f1f1;
        border-radius: 10px;
        padding: 20px;
    }
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 10px;
    }
    .plotly-chart {
        border: 2px solid #444;
        border-radius: 15px;
        padding: 10px;
        background-color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# Visualizar horários e disponibilidade
st.header('🖥️ Visualizar Disponibilidade de Computadores')
st.write('Os horários e os computadores alocados atualmente são exibidos abaixo:')

estagiarios_df = visualizar_estagiarios()
if not estagiarios_df.empty:
    # Preparar os dados para visualização
    estagiarios_df['horario_inicio_dt'] = estagiarios_df['horario_inicio'].apply(lambda x: datetime.datetime.combine(datetime.date.today(), x))
    estagiarios_df['horario_fim_dt'] = estagiarios_df['horario_fim'].apply(lambda x: datetime.datetime.combine(datetime.date.today(), x))
    estagiarios_df['duracao_horas'] = (estagiarios_df['horario_fim_dt'] - estagiarios_df['horario_inicio_dt']).dt.total_seconds() / 3600

    for index, row in estagiarios_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        col1.write(f"**ID:** {row['id']}")
        col2.write(f"**Nome:** {row['nome']}")
        col3.write(f"**Início:** {row['horario_inicio']}")
        col4.write(f"**Fim:** {row['horario_fim']}")
        if col5.button('Excluir', key=f"excluir_{row['id']}"):
            excluir_estagiario(row['id'])
            st.experimental_rerun()
else:
    st.warning('Nenhum estagiário registrado ainda.')

# Criar gráfico com Plotly
if not estagiarios_df.empty:
    fig = px.timeline(estagiarios_df, x_start='horario_inicio_dt', x_end='horario_fim_dt', y='computador_alocado', color='nome',
                      title='Ocupação dos Computadores', labels={'computador_alocado': 'Computador', 'nome': 'Estagiário'})
    fig.update_layout(xaxis_title='Horário', yaxis_title='Computador', showlegend=True, plot_bgcolor='#333', paper_bgcolor='#333', font_color='white')

    st.markdown("<div class='plotly-chart'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Adicionando novo estagiário
with st.expander('➕ Adicionar novo estagiário'):
    st.markdown("### Adicionar Estagiário")
    nome = st.text_input('Nome do Estagiário', placeholder="Digite o nome do estagiário...")
    horario_inicio = st.time_input('Horário de Início', datetime.time(8, 0))
    horario_fim = st.time_input('Horário de Fim', datetime.time(12, 0))
    computador = st.selectbox('Computador Alocado', ['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5'])

    if st.button('Adicionar Estagiário'):
        if nome:
            if verificar_conflito(horario_inicio, horario_fim, computador):
                st.error('Horário já ocupado por outro estagiário. Escolha outro horário ou computador.')
            else:
                adicionar_estagiario(nome, horario_inicio, horario_fim, computador)
                st.success(f'Estagiário {nome} adicionado com sucesso!')
        else:
            st.error('Por favor, insira um nome válido.')

# Visualizando e atualizando os estagiários
with st.expander('✏️ Atualizar Horário de Estagiários'):
    if not estagiarios_df.empty:
        st.markdown("### Atualizar Horário")
        st.dataframe(estagiarios_df.style.set_properties(**{'text-align': 'left'}), height=300)
        estagiario_id = st.number_input('ID do Estagiário para Atualizar', min_value=1, step=1)

        # Preencher automaticamente os campos com os dados do estagiário selecionado
        if estagiario_id in estagiarios_df['id'].values:
            estagiario_selecionado = estagiarios_df[estagiarios_df['id'] == estagiario_id].iloc[0]
            novo_horario_inicio = st.time_input('Novo Horário de Início', estagiario_selecionado['horario_inicio'])
            novo_horario_fim = st.time_input('Novo Horário de Fim', estagiario_selecionado['horario_fim'])
            novo_computador = st.selectbox('Novo Computador Alocado', ['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5'], index=['PC-1', 'PC-2', 'PC-3', 'PC-4', 'PC-5'].index(estagiario_selecionado['computador_alocado']))

            if st.button('Atualizar Horário'):
                if verificar_conflito(novo_horario_inicio, novo_horario_fim, novo_computador, estagiario_id):
                    st.error('Horário já ocupado por outro estagiário. Escolha outro horário ou computador.')
                else:
                    atualizar_horario_estagiario(estagiario_id, novo_horario_inicio, novo_horario_fim, novo_computador)
                    st.success(f'Horário do Estagiário ID {estagiario_id} atualizado com sucesso!')
    else:
        st.warning('Nenhum estagiário registrado ainda.')