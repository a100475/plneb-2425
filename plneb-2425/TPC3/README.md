# TPC3 - Pedro Flores

## Procedimento

## Leitura do ficheiro

```python
file = open("dicionario_medico.txt", encoding="utf-8")
print(file)
texto = file.read()
```


## Limpeza do Texto e adicionar marcadores

```python
texto = re.sub(r"\f", "", texto)
texto = re.sub(r"\n\n", "\n\n@", texto)
```


## Função para limpar descrições


```python
def limpa_descricao(descricao):
    descricao = descricao.strip()
    descricao = re.sub(r"\n", "", descricao)
    return descricao

```


## Extração e organização conceitos


```python
conceitos_raw = re.findall(r'@(.*)\n([^@]*)', texto)
conceitos = [(descricao, limpa_descricao(descricao)) for designacao, descricao in conceitos_raw]
```


## Gerar ficheiro HTML

```python
def gera_html(conceitos):
    html = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<meta charset="UTF-8"/>',
        '<style>',
        'body { font-family: Arial, sans-serif; margin: 20px; padding: 0; }',
        'h3 { color: #2c3e50; }',
        'div { margin-bottom: 15px; }',
        'p { margin: 5px 0; }',
        'hr { border: none; border-top: 1px solid #bdc3c7; margin: 10px 0; }',
        '</style>',
        '</head>',
        '<body>',
        '<h3>Dicionário De Conceitos Médicos</h3>',
        '<p>Este dicionário foi desenvolvido para a aula de PLNEB 2024/2025</p>'
    ]

    for designacao, descricao in conceitos:
        html.append(f"""
            <div>
                <p><strong>{designacao}</strong></p>
                <p>{descricao}</p>
            </div>
            <hr/>
        """)

    html.append('</body></html>')
    return ''.join(html)
```
