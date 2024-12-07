-- Criação da tabela Alunos
CREATE TABLE Alunos (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Identificador único para cada aluno
    nome VARCHAR(100) NOT NULL,        -- Nome do aluno
    idade INT NOT NULL,                -- Idade do aluno
    mae VARCHAR(100),                  -- Nome da mãe
    pai VARCHAR(100)                   -- Nome do pai
);

-- Criação da tabela Notas
CREATE TABLE Notas (
    id INT AUTO_INCREMENT PRIMARY KEY, -- Identificador único para cada registro de nota
    id_aluno INT NOT NULL,             -- Referência para o aluno (chave estrangeira)
    nota1 DECIMAL(5,2),                -- Nota 1
    nota2 DECIMAL(5,2),                -- Nota 2
    nota_final DECIMAL(5,2),           -- Nota final
    FOREIGN KEY (id_aluno) REFERENCES Alunos(id) ON DELETE CASCADE -- Chave estrangeira
);


INSERT INTO Alunos (nome, idade, mae, pai)
VALUES ('Maria Clara Silva', 14, 'Ana Paula Silva', 'Carlos Alberto Silva');
INSERT INTO Alunos (nome, idade, mae, pai)
VALUES ('João Pedro Oliveira', 16, 'Mariana Oliveira', 'Rafael Oliveira');