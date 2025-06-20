import json
import requests
from bs4 import BeautifulSoup
import os

url_start = "https://www.atlasdasaude.pt"
all_doencas = {}

section_map = {
    "causas": "causes",
    "sintomas": "symptoms",
    "diagnóstico": "diagnosis",
    "tratamento": "treatment",
    "nota": "note"
}

for ascii_code in range(ord('a'), ord('z') + 1):
    letra = chr(ascii_code)
    list_url = f"{url_start}/doencasaaz/{letra}"
    list_response = requests.get(list_url)
    list_soup = BeautifulSoup(list_response.text, 'html.parser')

    for div_row in list_soup.find_all('div', class_="views-row"):

        a_tag = div_row.div.h3.a
        nome = a_tag.text.strip()
        link = url_start + a_tag['href']

        page_response = requests.get(link)
        page_soup = BeautifulSoup(page_response.text, 'html.parser')

        disease_data = {
            "description": "",
            "causes": "",
            "symptoms": "",
            "diagnosis": "",
            "treatment": "",
            "note": ""
        }

        content_div = page_soup.find("div", class_="field-name-body")
        if content_div:
            current_section = "description"
            for el in content_div.find_all(["h2", "p", "ul", "ol"]):
                if el.name == "h2":
                    section_title = el.get_text().strip().lower()
                    for key in section_map:
                        if key in section_title:
                            current_section = section_map[key]
                            break
                    else:
                        current_section = "description"
                else:
                    text = el.get_text(separator=" ", strip=True)
                    if text:
                        disease_data[current_section] += text + "\n"

        nota_div = page_soup.find("div", class_="field-name-field-nota")
        if nota_div:
            nota_text = nota_div.get_text(separator=" ", strip=True).replace("Nota:", "").strip()
            disease_data["note"] = nota_text

        for key in disease_data:
            disease_data[key] = disease_data[key].strip()
            if not disease_data[key]:
                disease_data[key] = "N/A"

        all_doencas[nome] = disease_data



script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "termos.json")

with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(all_doencas, f_out, indent=4, ensure_ascii=False)
    