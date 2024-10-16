import psycopg2
import pandas as pd

# Função para carregar estagiários do banco de dados
def carregar_estagiarios(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nome FROM estagiarios")
            result = cursor.fetchall()
            return [row[0] for row in result]
    except Exception as e:
        print(f"Erro ao carregar estagiários: {e}")
        return []

# Função para adicionar estagiário ao banco de dados
def adicionar_estagiario_banco(conn, nome):
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO estagiarios (nome)
                VALUES (%s)
                """,
                (nome,)
            )
            conn.commit()
    except Exception as e:
        print(f"Erro ao adicionar estagiário: {e}")
        conn.rollback()

# Função para remover estagiário do banco de dados
def remover_estagiario_banco(conn, nome):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM estagiarios WHERE nome = %s", (nome,))
            conn.commit()
    except Exception as e:
        print(f"Erro ao remover estagiário: {e}")
        conn.rollback()

# Função para carregar cronograma do banco de dados
def carregar_cronograma(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, nome, horario_inicio, horario_fim, computador_alocado, dias_semana
                FROM cronograma
            """)
            rows = cursor.fetchall()
            colunas = [desc[0] for desc in cursor.description]
            cronograma_df = pd.DataFrame(rows, columns=colunas)
            return cronograma_df
    except Exception as e:
        print(f"Erro ao carregar cronograma: {e}")
        return pd.DataFrame()

# Função para inserir cronograma no banco de dados
def inserir_cronograma_no_banco(conn, cronograma_df):
    try:
        with conn.cursor() as cursor:
            for _, row in cronograma_df.iterrows():
                cursor.execute("""
                    INSERT INTO cronograma (nome, horario_inicio, horario_fim, computador_alocado, dias_semana)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    row['nome'],
                    row['horario_inicio'],
                    row['horario_fim'],
                    row['computador_alocado'],
                    row['dias_semana']
                ))
            conn.commit()
    except Exception as e:
        print(f"Erro ao inserir cronograma: {e}")
        conn.rollback()

# Função para atualizar horário de estagiário no banco de dados
def atualizar_horario_estagiario(conn, registro_id, novo_horario_inicio, novo_horario_fim):
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE cronograma
                SET horario_inicio = %s,
                    horario_fim = %s
                WHERE id = %s
            """, (
                novo_horario_inicio,
                novo_horario_fim,
                registro_id
            ))
            conn.commit()
    except Exception as e:
        print(f"Erro ao atualizar registro ID {registro_id}: {e}")
        conn.rollback()

# Função para remover horário de estagiário do banco de dados
def remover_horario_estagiario(conn, id_estagiario):
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM cronograma WHERE id = %s", (id_estagiario,))
            conn.commit()
    except Exception as e:
        print(f"Erro ao remover horário do estagiário: {e}")
        conn.rollback()

# Função para resetar o cronograma semanal
def resetar_cronograma(conn):
    try:
        with conn.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE cronograma")
            conn.commit()
    except Exception as e:
        print(f"Erro ao resetar cronograma: {e}")
        conn.rollback()