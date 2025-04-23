import json
import re
import unicodedata
from collections import defaultdict
from xml.etree import ElementTree as ET

def limpar(texto):
    texto = re.sub(r'\s?–\s?', '', texto)
    return texto


def delimitar_texto(texto):
    texto = limpar(texto)

    #Inicio
    match_ab = re.search(r'<b[^>]*>AB</b>', texto)
    if not match_ab:
        return {}

    #Fim
    match_ups = re.search(r'<b[^>]*>UPS\s*[–—-]?</b>', texto)
    if match_ups:
        restante = texto[match_ups.end():]
        match_fim = re.search(r'</page>', restante)
        if match_fim:
            end_pos = match_ups.end() + match_fim.end()
            texto = texto[match_ab.start():end_pos]
        else:
            texto = texto[match_ab.start():]
    else:
        texto = texto[match_ab.start():]

    return texto


def extract_siglas(texto_raw):
    texto = delimitar_texto(texto_raw)

    #Find siglas
    sigla_matches = list(re.finditer(r'<b>([A-Z][\s\S]*?)</b>', texto))

    siglas_dict = defaultdict(dict)

    for i, match in enumerate(sigla_matches):
        sigla = match.group(1)
        start = match.end()
        end = sigla_matches[i + 1].start() if i + 1 < len(sigla_matches) else len(texto)

        segmento_definicao = texto[start:end]

        #Extract non-bold text content within <text> elements
        definicoes = re.findall(r'>([^<>]+)</text>', segmento_definicao)
        definicao_limpa = ' '.join([d.strip() for d in definicoes if d.strip()])

        #Skip if the description starts with a number
        if definicao_limpa and not definicao_limpa[0].isdigit():
            letra = sigla[0]
            if letra.isalpha():
                siglas_dict[letra][sigla] = definicao_limpa

    return dict(siglas_dict)


def extract_terms(root):
    termos_dict = {}
    elements = list(root.iter("text"))
    i = 0
    started = False

    #Find start or terms
    while i < len(elements) - 3:
        first = elements[i]
        second = elements[i + 1]
        third = elements[i + 2]

        if (
            any(child.tag == "b" for child in first)
            and any(child.tag == "b" for child in second)
            and any(child.tag == "i" for child in third)
            and "Categoria:" in "".join(third.itertext())
        ):
            started = True
            break
        i += 1

    if not started:
        return {}


    while i < len(elements):
        elem = elements[i]

        #Name
        name_lines = []
        while i < len(elements):
            elem = elements[i]
            if any(child.tag == "b" for child in elem):
                name_lines.append("".join(elem.itertext()).strip())
                i += 1
            else:
                break
        if not name_lines:
            continue
        full_name = " ".join(name_lines).strip()

        #Categoria
        categoria = None
        categoria_found = False
        desc_start_index = i

        while i < len(elements):
            elem = elements[i]
            text = "".join(elem.itertext()).strip()
            is_italic = any(child.tag == "i" for child in elem)

            if is_italic and "Categoria:" in text:
                if i + 1 < len(elements):
                    categoria = "".join(elements[i + 1].itertext()).strip()
                    i += 2
                    categoria_found = True
                    break
            elif any(child.tag == "b" for child in elem):
                break  #Next term found, no category
            else:
                i += 1

        if not categoria_found:
            categoria = "Sem Categoria"
            i = desc_start_index  #rewind to start of description
            if i < len(elements):
                preview_text = "".join(elements[i].itertext()).strip()
                if not preview_text.startswith("Ver"):
                    #Skip this term and advance to next <b> or the next line
                    while i < len(elements) and not any(child.tag == "b" for child in elements[i]):
                        i += 1
                    continue  #continue outer loop



        #Descricao
        description_lines = []
        while i < len(elements):
            elem = elements[i]
            if any(child.tag == "b" for child in elem):
                break  #Start of next term
            text = "".join(elem.itertext()).strip()
            if text:
                description_lines.append(text)
            i += 1

        full_description = " ".join(description_lines).strip()
        full_description = full_description.replace("- ", "")  #Remove all "- " from the description

        #guardar termo
        if categoria not in termos_dict:
            termos_dict[categoria] = {}
        termos_dict[categoria][full_name] = full_description

    return termos_dict

def extract_info():
    xml_path = 'data_txt/glossario_ministerio_saude.xml'

    #Siglas
    with open(xml_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()
    siglas_dict = extract_siglas(raw_text)

    #Termos
    tree = ET.ElementTree(ET.fromstring(raw_text))
    root = tree.getroot()
    termos_dict = extract_terms(root)

    #Organizar alphabeticamente (Sem categoria no final para termos)
    termos_ordenados = dict(
        sorted(
            termos_dict.items(),
            key=lambda item: (item[0] == "Sem Categoria", item[0])
        )
    )


    output = {
        "Siglas": siglas_dict,
        "Termos": termos_ordenados
    }

    with open('glossario_ministerio_saude.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    extract_info()