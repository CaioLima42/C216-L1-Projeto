from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "chave_secreta"  # Para mensagens flash

API_URL = "http://127.0.0.1:8000/api/v1"  # URL da API FastAPI

# Rota para a página inicial
@app.route("/")
def index():
    return render_template("index.html")

# Rota para listar alunos
@app.route("/alunos/")
def listar_alunos():
    response = requests.get(f"{API_URL}/alunos/")
    if response.status_code == 200:
        alunos = response.json()
        return render_template("alunos.html", alunos=alunos)
    flash("Erro ao buscar alunos!", "error")
    return redirect(url_for("index"))

# Rota para adicionar aluno
@app.route("/alunos/adicionar", methods=["GET", "POST"])
def adicionar_aluno():
    if request.method == "POST":
        nome = request.form.get("nome")
        idade = request.form.get("idade")
        mae = request.form.get("mae")
        pai = request.form.get("pai")
        data = {"nome": nome, "idade": int(idade), "mae": mae, "pai": pai}
        response = requests.post(f"{API_URL}/alunos/", json=data)
        if response.status_code == 201:
            flash("Aluno adicionado com sucesso!", "success")
            return redirect(url_for("listar_alunos"))
        flash("Erro ao adicionar aluno!", "error")
    return render_template("adicionar_aluno.html")

# Rota para listar notas
@app.route("/notas/")
def listar_notas():
    response = requests.get(f"{API_URL}/notas/")
    if response.status_code == 200:
        notas = response.json()
        return render_template("notas.html", notas=notas)
    flash("Erro ao buscar notas!", "error")
    return redirect(url_for("index"))

# Rota para adicionar nota
@app.route("/notas/adicionar", methods=["GET", "POST"])
def adicionar_nota():
    if request.method == "POST":
        id_aluno = request.form.get("id_aluno")
        nota1 = request.form.get("nota1")
        nota2 = request.form.get("nota2")
        nota_final = request.form.get("nota_final")
        data = {
            "id_aluno": int(id_aluno),
            "nota1": float(nota1),
            "nota2": float(nota2),
            "nota_final": float(nota_final),
        }
        response = requests.post(f"{API_URL}/notas/", json=data)
        if response.status_code == 201:
            flash("Nota adicionada com sucesso!", "success")
            return redirect(url_for("listar_notas"))
        flash("Erro ao adicionar nota!", "error")
    return render_template("adicionar_nota.html")

if __name__ == "__main__":
    app.run(debug=True)
