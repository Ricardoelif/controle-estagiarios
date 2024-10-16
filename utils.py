import psycopg2

def conectar_banco():
    try:
        conn = psycopg2.connect(
            host="aws-0-sa-east-1.pooler.supabase.com",
            database="postgres",
            user="postgres.iykkmaqmyterupyxzdej",
            password="4UJzihawH1bEFjna",
            port="6543"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None