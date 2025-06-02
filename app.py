
from google import genai

client = genai.Client(api_key="AIzaSyBub0nEbWIC16FEBhG5w5DV9Oj2KV9km08")

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Explain how AI works in a few words",
)

print(response.text)

def carregar_termos():
    termos = {}
    try:
        with open("/DATA/dicionario.txt", "r", encoding="utf-8") as f:
            for linha in f:
                if '|' in linha:
                    termo, definicao = linha.strip().split('|', 1)
                    termos[termo] = definicao
    except FileNotFoundError:
        pass
    return termos

def salvar_termos(termos):
    with open("/DATA/dicionario.txt ", "w", encoding="utf-8") as f:
        for termo, definicao in termos.items():
            f.write(f"{termo}|{definicao}\n")
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/dicionario")
def dicionario():
    termos = carregar_termos()
    return render_template("dicionario.html", termos=termos)

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():
    if request.method == "POST":
        termo = request.form["termo"].strip()
        definicao = request.form["definicao"].strip()
        termos = carregar_termos()
        termos[termo] = definicao
        salvar_termos(termos)
        return redirect(url_for("dicionario"))
    return render_template("adicionar.html")

@app.route("/editar/<termo>", methods=["GET", "POST"])
def editar(termo):
    termos = carregar_termos()
    if request.method == "POST":
        nova_definicao = request.form["definicao"]
        termos[termo] = nova_definicao
        salvar_termos(termos)
        return redirect(url_for("dicionario"))
    definicao = termos.get(termo, "")
    return render_template("editar.html", termo=termo, definicao=definicao)

@app.route("/deletar/<termo>")
def deletar(termo):
    termos = carregar_termos()
    if termo in termos:
        del termos[termo]
        salvar_termos(termos)
    return redirect(url_for("dicionario"))

