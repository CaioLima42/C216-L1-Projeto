from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/school")
    return await asyncpg.connect(DATABASE_URL)


# Inicializar a aplicação FastAPI
app = FastAPI()

# Modelo para Alunos
class Aluno(BaseModel):
    id: Optional[int] = None
    nome: str
    idade: int
    mae: str
    pai: str

# Modelo para adicionar Alunos
class AlunoBase(BaseModel):
    nome: str
    idade: int
    mae: str
    pai: str

# Modelo para Notas
class Nota(BaseModel):
    id: Optional[int] = None
    id_aluno: int
    nota1: float
    nota2: float
    nota_final: float

# Modelo para adicionar Notas
class NotaBase(BaseModel):
    id_aluno: int
    nota1: float
    nota2: float
    nota_final: float

# Middleware para logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Path: {request.url.path}, Method: {request.method}, Process Time: {process_time:.4f}s")
    return response

# 1. Adicionar um novo aluno
@app.post("/api/v1/alunos/", status_code=201)
async def adicionar_aluno(aluno: AlunoBase):
    conn = await get_database()
    try:
        query = "INSERT INTO Alunos (nome, idade, mae, pai) VALUES ($1, $2, $3, $4) RETURNING id"
        aluno_id = await conn.fetchval(query, aluno.nome, aluno.idade, aluno.mae, aluno.pai)
        return {"message": "Aluno adicionado com sucesso!", "id": aluno_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar o aluno: {str(e)}")
    finally:
        await conn.close()

# 2. Listar todos os alunos
@app.get("/api/v1/alunos/", response_model=List[Aluno])
async def listar_alunos():
    conn = await get_database()
    try:
        query = "SELECT * FROM Alunos"
        rows = await conn.fetch(query)
        alunos = [dict(row) for row in rows]
        return alunos
    finally:
        await conn.close()

# 3. Buscar aluno por ID
@app.get("/api/v1/alunos/{aluno_id}")
async def listar_aluno_por_id(aluno_id: int):
    conn = await get_database()
    try:
        query = "SELECT * FROM Alunos WHERE id = $1"
        aluno = await conn.fetchrow(query, aluno_id)
        if aluno is None:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        return dict(aluno)
    finally:
        await conn.close()

# 4. Adicionar notas para um aluno
@app.post("/api/v1/notas/", status_code=201)
async def adicionar_nota(nota: NotaBase):
    conn = await get_database()
    try:
        # Verificar se o aluno existe
        aluno_query = "SELECT id FROM Alunos WHERE id = $1"
        aluno = await conn.fetchval(aluno_query, nota.id_aluno)
        if aluno is None:
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")

        # Inserir as notas
        query = "INSERT INTO notas (id_aluno, nota1, nota2, nota_final) VALUES ($1, $2, $3, $4)"
        await conn.execute(query, nota.id_aluno, nota.nota1, nota.nota2, nota.nota_final)
        return {"message": "Notas adicionadas com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao adicionar as notas: {str(e)}")
    finally:
        await conn.close()

# 5. Listar todas as notas
@app.get("/api/v1/notas/", response_model=List[Nota])
async def listar_notas():
    conn = await get_database()
    try:
        query = "SELECT * FROM notas"
        rows = await conn.fetch(query)
        notas = [dict(row) for row in rows]
        return notas
    finally:
        await conn.close()

# 6. Buscar notas por ID do aluno
@app.get("/api/v1/notas/{aluno_id}")
async def listar_notas_por_aluno(aluno_id: int):
    conn = await get_database()
    try:
        query = "SELECT * FROM notas WHERE id_aluno = $1"
        rows = await conn.fetch(query, aluno_id)
        if not rows:
            raise HTTPException(status_code=404, detail="Notas não encontradas para o aluno.")
        notas = [dict(row) for row in rows]
        return notas
    finally:
        await conn.close()
        
# 7. Resetar dataset
@app.delete("/api/v1/reset/")
async def resetar_dataset():
    init_sql = os.getenv("INIT_SQL", "db/init.sql")  # Caminho para o arquivo SQL
    conn = await get_database()
    try:
        # Ler comandos SQL do arquivo
        with open(init_sql, 'r') as file:
            sql_commands = file.read()
        # Executar comandos SQL
        await conn.execute(sql_commands)
        return {"message": "Dataset resetado com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao resetar o dataset: {str(e)}")
    finally:
        await conn.close()