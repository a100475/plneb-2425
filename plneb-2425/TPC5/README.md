# TPC5

O objetivo do trabalho de casa é a criação de um path entre a lista de conceitos e as suas definições.
Para tal, foi estabelecida uma hiperligação entre cada conceito na lista e a sua definição

```python
@app.route("/conceitos/<designacao>")
def conceito_unico(designacao):
    if designacao in db:
        return render_template(
            "conceitos.html",
            designacoes=[], 
            single_concept=designacao, 
            descricao=db[designacao], 
            title=f"Conceito: {designacao}"
        )
    else:
        return render_template("404.html", title="Erro 404 - Não encontrado"), 404
```

## conceitos.html

```python
@app.route("/conceitos/<designacao>")
def conceito_unico(designacao):
    if designacao in db:
        return render_template(
            "conceitos.html",
            designacoes=[], 
            single_concept=designacao, 
            descricao=db[designacao], 
            title=f"Conceito: {designacao}"
        )
    else:
        return render_template("404.html", title="Erro 404 - Não encontrado"), 404
```
