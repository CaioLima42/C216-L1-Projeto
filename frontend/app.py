from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = "chave_secreta"  # Para mensagens flash

API_URL = "http://backend:8000/api/v1"   # URL da API FastAPI

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
        #nota_final = request.form.get("nota_final")
        nota_final = (float(nota1) + float(nota2))/2
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

@app.route("/resetar", methods=["POST"])
def resetar_dataset():
    try:
        response = requests.delete(f"{API_URL}/reset/")
        if response.status_code == 200:
            flash("Dataset resetado com sucesso!", "success")
        else:
            flash(response.json().get("detail", "Erro ao resetar dataset"), "danger")
    except Exception as e:
        flash(f"Erro ao conectar à API: {str(e)}", "danger")
    return redirect(url_for("index"))




@app.route("/notas/<int:nota_id>/editar", methods=["GET", "POST"])
def editar_nota(nota_id):
    if request.method == "POST":
        nota1 = request.form.get("nota1")
        nota2 = request.form.get("nota2")

        data = {
            "nota1": float(nota1) if nota1 else None,
            "nota2": float(nota2) if nota2 else None
        }
        try:
            response = requests.patch(f"{API_URL}/notas/{nota_id}", json=data)
            if response.status_code == 200:
                flash("Nota atualizada com sucesso!", "success")
            else:
                flash(response.json().get("detail", "Erro ao atualizar nota"), "danger")
        except Exception as e:
            flash(f"Erro ao conectar à API: {str(e)}", "danger")
        return redirect(url_for("listar_notas"))

    # Obter dados do aluno
    response = requests.get(f"{API_URL}/notas/{nota_id}")
    if response.status_code == 200:
        nota = response.json()
        return render_template("editar_nota.html", nota=nota)
    flash("Erro ao buscar nota!", "danger")
    return redirect(url_for("listar_notas"))

@app.route("/alunos/<int:aluno_id>/deletar", methods=["POST"])
def deletar_aluno(aluno_id):
    try:
        response = requests.delete(f"{API_URL}/alunos/{aluno_id}")
        if response.status_code == 200:
            flash("Aluno e suas notas foram deletados com sucesso!", "success")
        else:
            flash(response.json().get("detail", "Erro ao deletar aluno"), "danger")
    except Exception as e:
        flash(f"Erro ao conectar à API: {str(e)}", "danger")
    return redirect(url_for("listar_alunos"))

@app.route("/notas/<int:nota_id>/deletar", methods=["POST"])
def deletar_nota(nota_id):
    try:
        response = requests.delete(f"{API_URL}/notas/{nota_id}")
        if response.status_code == 200:
            flash("Nota deletada com sucesso!", "success")
        else:
            flash(response.json().get("detail", "Erro ao deletar nota"), "danger")
    except Exception as e:
        flash(f"Erro ao conectar à API: {str(e)}", "danger")
    return redirect(url_for("listar_notas"))


@app.route("/alunos/<int:aluno_id>/editar", methods=["GET", "POST"])
def editar_aluno(aluno_id):
    if request.method == "POST":
        nome = request.form.get("nome")
        idade = request.form.get("idade")
        mae = request.form.get("mae")
        pai = request.form.get("pai")
        data = {
            "nome": nome if nome else None,
            "idade": int(idade) if idade else None,
            "mae": mae if mae else None,
            "pai": pai if pai else None,
        }
        try:
            response = requests.patch(f"{API_URL}/alunos/{aluno_id}", json=data)
            if response.status_code == 200:
                flash("Aluno atualizado com sucesso!", "success")
            else:
                flash(response.json().get("detail", "Erro ao atualizar aluno"), "danger")
        except Exception as e:
            flash(f"Erro ao conectar à API: {str(e)}", "danger")
        return redirect(url_for("listar_alunos"))

    # Obter dados do aluno
    response = requests.get(f"{API_URL}/alunos/{aluno_id}")
    if response.status_code == 200:
        aluno = response.json()
        return render_template("editar_aluno.html", aluno=aluno)
    flash("Erro ao buscar aluno!", "danger")
    return redirect(url_for("listar_alunos"))



if __name__ == '__main__':
    app.run(debug=True, port=3000, host='0.0.0.0')
