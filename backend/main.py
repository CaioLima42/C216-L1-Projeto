from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import time
import asyncpg
import os

# Função para obter a conexão com o banco de dados PostgreSQL
async def get_database():
    DATABASE_URL = os.environ.get("PGURL", "postgres://postgres:postgres@db:5432/alunos")
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


class NotaBase(BaseModel):
    nota1: float
    nota2: float
    id_aluno: Optional[int] = None  # Tornando opcional
    nota_final: Optional[float] = None  # Tornando opcional


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
        query = "INSERT INTO alunos (nome, idade, mae, pai) VALUES ($1, $2, $3, $4) RETURNING id"
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
        query = "SELECT * FROM alunos"
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
        query = "SELECT * FROM alunos WHERE id = $1"
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
        aluno_query = "SELECT id FROM alunos WHERE id = $1"
        
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


@app.patch("/api/v1/notas/{nota_id}")
async def atualizar_nota(nota_id: int, nota_atualizacao: NotaBase):
    conn = await get_database()
    try:
        # Verificar se a nota existe e obter o id_aluno
        nota_query = "SELECT id_aluno FROM notas WHERE id = $1"
        id_aluno = await conn.fetchval(nota_query, nota_id)
        if id_aluno is None:
            raise HTTPException(status_code=404, detail="Nota não encontrada.")

        # Calcular a nova nota final como a soma de nota1 e nota2
        nota_final = (nota_atualizacao.nota1 + nota_atualizacao.nota2) / 2

        # Atualizar as notas no banco de dados
        update_query = """
            UPDATE notas
            SET nota1 = $1, nota2 = $2, nota_final = $3
            WHERE id = $4
        """
        await conn.execute(update_query, nota_atualizacao.nota1, nota_atualizacao.nota2, nota_final, nota_id)

        return {"message": "Notas atualizadas com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Falha ao atualizar as notas: {str(e)}")
    finally:
        await conn.close()



@app.delete("/api/v1/alunos/{aluno_id}", status_code=200)
async def deletar_aluno(aluno_id: int):
    conn = await get_database()
    try:
        # Deletar notas do aluno
        await conn.execute("DELETE FROM notas WHERE id_aluno = $1", aluno_id)
        # Deletar aluno
        result = await conn.execute("DELETE FROM Alunos WHERE id = $1", aluno_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="Aluno não encontrado.")
        return {"message": "Aluno e suas notas foram deletados com sucesso!"}
    finally:
        await conn.close()



# Modelo para atualizar Aluno
class AlunoUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None
    mae: Optional[str] = None
    pai: Optional[str] = None

@app.patch("/api/v1/alunos/{aluno_id}", status_code=200)
async def atualizar_aluno(aluno_id: int, aluno: AlunoUpdate):
    conn = await get_database()
    try:
        # Atualizar apenas os campos fornecidos
        query = """
            UPDATE Alunos
            SET 
                nome = COALESCE($1, nome),
                idade = COALESCE($2, idade),
                mae = COALESCE($3, mae),
                pai = COALESCE($4, pai)
            WHERE id = $5
        """
        await conn.execute(query, aluno.nome, aluno.idade, aluno.mae, aluno.pai, aluno_id)
        return {"message": "Aluno atualizado com sucesso!"}
    finally:
        await conn.close()

class NotaUpdate(BaseModel):
    nota1: Optional[float] = None
    nota2: Optional[float] = None

@app.patch("/api/v1/notas/{nota_id}", status_code=200)
async def atualizar_nota(nota_id: int, nota: NotaUpdate):
    conn = await get_database()
    try:
        # Calcular nota final se necessário
        existing_nota_query = "SELECT nota1, nota2 FROM notas WHERE id = $1"
        existing_nota = await conn.fetchrow(existing_nota_query, nota_id)

        if not existing_nota:
            raise HTTPException(status_code=404, detail="Nota não encontrada.")

        nota1 = nota.nota1 if nota.nota1 is not None else existing_nota['nota1']
        nota2 = nota.nota2 if nota.nota2 is not None else existing_nota['nota2']
        nota_final = (nota1 + nota2) / 2

        # Atualizar as notas
        query = """
            UPDATE notas
            SET 
                nota1 = $1,
                nota2 = $2,
                nota_final = $3
            WHERE id = $4
        """
        await conn.execute(query, nota1, nota2, nota_final, nota_id)
        return {"message": "Nota atualizada com sucesso!"}
    finally:
        await conn.close()

