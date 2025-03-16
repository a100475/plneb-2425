from flask import Flask, request, render_template
import json
app = Flask(__name__)

#db_file = open("../Aula4/conceitos.json")
db_file = open("conceitos_.json",encoding="utf-8")

db = json.load(db_file)
db_file.close()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/conceitos")
def conceitos():
    designacoes = list(db.keys())
    return render_template("conceitos.html", designacoes=designacoes, title="Lista de Conceitos")

@app.route("/api/conceitos")
def api_conceitos():
    return db

@app.route("/api/conceitos/<designacao>")
def api_conceito(designacao):

    return {"designacao":designacao, "descricao":db[designacao]}

@app.post("/api/conceitos")
def adicionar_conceito():
    #json
    data = request.get_json()
    #{"designacao":"vida", "descricao": "a vida é ..."}
    db[data["designacao"]] = data["descricao"]
    f_out = open("conceitos_.json", "w")
    json.dump(db,f_out, indent=4, ensure_ascii=False)
    f_out.close()
    #form data
    return data

@app.route("/conceitos/<designacao>")
def conceito_unico(designacao):
    if designacao in db:
        return render_template("conceitos.html", designacoes=[designacao], descricao=db[designacao], title=f"Conceito: {designacao}")
    else:
        return render_template("404.html", title="Erro 404 - Não encontrado"), 404
    
    
app.run(host="localhost", port=4002, debug=True)
