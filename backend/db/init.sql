-- Deletar tabelas existentes
DROP TABLE IF EXISTS "notas" CASCADE;
DROP TABLE IF EXISTS "alunos" CASCADE;

-- Criação da tabela Alunos
CREATE TABLE "alunos" (
    "id" SERIAL PRIMARY KEY, -- Identificador único para cada aluno
    "nome" VARCHAR(100) NOT NULL, -- Nome do aluno
    "idade" INT NOT NULL, -- Idade do aluno
    "mae" VARCHAR(100), -- Nome da mãe
    "pai" VARCHAR(100) -- Nome do pai
);

-- Criação da tabela Notas
CREATE TABLE "notas" (
    "id" SERIAL PRIMARY KEY, -- Identificador único para cada registro de nota
    "id_aluno" INTEGER REFERENCES alunos(id) ON DELETE CASCADE, -- Referência para o aluno (chave estrangeira)
    "nota1" DECIMAL(5,2), -- Nota 1
    "nota2" DECIMAL(5,2), -- Nota 2
    "nota_final" DECIMAL(5,2) -- Nota final
);

-- Inserir dados iniciais
INSERT INTO "alunos" (nome, idade, mae, pai) VALUES ('Maria Clara Silva', 14, 'Ana Paula Silva', 'Carlos Alberto Silva');
INSERT INTO "alunos" (nome, idade, mae, pai) VALUES ('João Pedro Oliveira', 16, 'Mariana Oliveira', 'Rafael Oliveira');

INSERT INTO "notas" (id_aluno, nota1, nota2, nota_final) VALUES ('2', 10, 10, 10);
