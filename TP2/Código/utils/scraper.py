import json
from bs4 import BeautifulSoup
import requests


BASE_URL = "https://www.atlasdasaude.pt"

OUTPUT_PATH = "../dicts/atlas_saude.json"


def get_html_content(url):
    response = requests.get(url)
    html_content = response.text
    print(f"Obtido o conteúdo html de {response.url}")

    return html_content


def get_info_doencas(letra):
    url = f"{BASE_URL}/doencasaaz/{letra}"
    html_content = get_html_content(url)

    soup = BeautifulSoup(html_content, 'html.parser')

    doencas = {}
    for div_row in soup.find_all('div', class_="views-row"):
        designacao = div_row.div.h3.a.text

        resumo_div = div_row.find('div', class_="views-field-body")
        resumo = resumo_div.div.text.strip().replace(" ", " ")

        doencas[designacao] = resumo

    return doencas


if __name__ == "__main__":
    res = {}
    for ascii_code in range(ord('a'), ord('z') + 1):
        letra = chr(ascii_code)
        res |= get_info_doencas(letra)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=4)
