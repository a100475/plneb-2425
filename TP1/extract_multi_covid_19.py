import json
import re

from bs4 import BeautifulSoup


XML_PATH = r"data_txt\diccionari-multilinguee-de-la-covid-19\diccionari-multilinguee-de-la-covid-19.xml"


PAG_INICIO_CONCEITOS = 30
PAG_FIM_CONCEITOS = 182

RIGHT_PAGE_MID_POINT = 502
LEFT_PAGE_MID_POINT = 442


TRADS = {"oc", "eu", "gl", "es", "en", "fr", "pt", "pt [PT]", "pt [BR]", "nl", "ar"}

CAT_LEX = {"n", "n pl", "n m", "n m", "n f", "n m pl", "n f pl", "n m, f", "n m/f", "adj", "v tr", "v tr/intr", "v intr"}

INFO = {"sin.", "sin. compl.", "den. com.", "veg.", "sigla"}

CODS = {"sbl", "nc", "CAS"}

DEFS = {
    "CONCEPTES GENERALS",
    "EPIDEMIOLOGIA",
    "ETIOPATOGÈNIA",
    "DIAGNÒSTIC",
    "CLÍNICA",
    "PREVENCIÓ",
    "TRACTAMENT",
    "PRINCIPIS ACTIUS",
    "ENTORN SOCIAL"
}


def extract_page_interval(xml_soup, pagina_inicio, pagina_fim):
    paginas = xml_soup.find_all("page")
    resultado = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE pdf2xml SYSTEM "pdf2xml.dtd">\n\n<pdf2xml producer="poppler" version="24.08.0">\n'

    for pagina in paginas:
        numero = int(pagina.get("number", 0))
        if pagina_inicio <= numero <= pagina_fim:
            resultado += (str(pagina) + "\n")

    return resultado + "</pdf2xml>"


def prepare_text(xml_text):
    soup = BeautifulSoup(xml_text, 'xml')
    pages = soup.find_all('page')
    final_text = ""

    pag_direita = True
    for page in pages:
        right_stack = ""

        mid_point = RIGHT_PAGE_MID_POINT if pag_direita else LEFT_PAGE_MID_POINT

        for text_tag in page.find_all('text'):
            if int(text_tag['top']) <= 285 or int(text_tag['font']) == 6:  # filtra o texto do cabeçalho e os números das páginas
                continue

            if int(text_tag['left']) < mid_point:
                final_text += apply_marks(re.sub(r" {2,}", " ", text_tag.text.strip())) + "\n"
            else:
                right_stack += apply_marks(re.sub(r" {2,}", " ", text_tag.text.strip())) + "\n"

        final_text += right_stack
        pag_direita = not pag_direita

    return final_text


def apply_marks(text):
    text = text.strip()

    if text in CAT_LEX or re.match(rf"({'|'.join(CAT_LEX)});", text):
        return f"##{text}"
    elif text in TRADS:
        return f"§§{text}"
    elif text in CODS:
        return f"@@{text}"
    elif text in INFO:
        return f"€€{text}"
    else:
        return text


def parse_text(conceitos_texto):
    result = []

    concept_pattern = r"^\d+\n{1,2}[^\n]*(?:\n[^\n]*)?\n##.+?"
    concepts = re.findall(rf"({concept_pattern})(?={concept_pattern})", conceitos_texto, re.DOTALL|re.MULTILINE)

    last_concept_pattern = r".*(^\d+\n{1,2}[\s\S]+?##[\s\S]*)$"
    concepts.append(re.search(last_concept_pattern, conceitos_texto, re.DOTALL|re.MULTILINE).group(1))

    current_concept = {}
    for concept in concepts:
        match_inicial = re.match(r'(\d+)\n{1,2}([\s\S]+?)##(.+?)\n', concept, flags=re.DOTALL)
        current_concept['id'] = int(match_inicial.group(1).strip())
        current_concept['ca'] = [{
            "term": match_inicial.group(2).strip().replace("\n", " "),
            "lex_cat": match_inicial.group(3).strip().replace("\n", " ")
        }]

        info_matches = re.findall(rf"€€(.+?)\n(.+?)(?=§§|$|€€)", concept, flags=re.DOTALL)

        if info_matches:
            for match in info_matches:
                info_key = match[0].strip().replace(".", "").replace(" ", "_")
                term_clex_pairs = re.split(r'[;|]', match[1].strip())
                value_list = []
                for pair in term_clex_pairs:
                    term, lex_class = pair.split('##') if '##' in pair else (pair.strip(), None)
                    if term: term = term.strip().replace("\n", " ")
                    if lex_class: lex_class = lex_class.strip().replace("\n", " ")
                    value_list.append({'term': term, 'lex_cat': lex_class})
                if (info_key == "veg" or info_key == "den_com") and value_list:
                    current_concept[info_key] = value_list[0]
                else:
                    current_concept[info_key] = value_list

        match_trads = re.findall(rf"§§(.+?)\n(.+?)(?=§§|@@|nc |{'|'.join(DEFS)})", concept, re.DOTALL)

        for trad_match in match_trads:
            lang_code_raw = trad_match[0].strip()
            lang_code = re.sub(r'\s*\[(.*?)\]', r'-\1', lang_code_raw)
            term_clex_pairs = re.split(r'[;|]', trad_match[1].strip())
            res = []
            for pair in term_clex_pairs:
                term, lex_class = pair.split('##') if '##' in pair else (pair.strip(), None)
                if term: term = term.strip().replace("\n", " ")
                if lex_class: lex_class = lex_class.strip().replace("\n", " ")
                res.append({'term': term, 'lex_cat': lex_class})

            current_concept[lang_code] = res

        cods_match = re.findall(rf"@@(.+?)\n(.+?)(@@|nc |{'|'.join(DEFS)})", concept, re.DOTALL)

        for cod_match in cods_match:
            cod = cod_match[0].strip()
            content = cod_match[1].replace("\n", " ").strip()
            current_concept[cod] = content

        nc_match = re.search(rf'nc (.+?)(?=@@|{'|'.join(DEFS)})', concept, flags=re.DOTALL)
        if nc_match:
            current_concept["nc"] = (nc_match.group(1)).replace("\n", " ").strip()

        desc_match = re.search(rf"({'|'.join(DEFS)})(.+?)(Nota:|$)", concept, re.DOTALL)
        if desc_match:
            current_concept['desc'] = (desc_match.group(1) + desc_match.group(2)).replace("\n", " ").strip()

        nota_match = re.search(r"Nota:\s*(.*?)$", concept, re.DOTALL)
        if nota_match:
            notes_text = nota_match.group(0).replace("Nota:", "", 1).strip()

            if re.search(r"^\s*1\.", notes_text):
                notes = re.findall(r"(?:^|\n)\s*(\d+)\.\s*([\s\S]*?)(?=(?:\n\s*\d+\.)|$)", notes_text)

                current_concept["note"] = [
                    re.sub(r"\s+", " ", note[1].strip()) 
                    for note in notes if note[1].strip()
                ]
            else:
                current_concept["note"] = [re.sub(r"\s+", " ", notes_text.strip())] if notes_text.strip() else []

        result.append(current_concept)
        current_concept = {}

    return result



if __name__ == "__main__":
    with open(XML_PATH, "r", encoding="utf-8") as f:
        xml_content = f.read()

    xml_soup = BeautifulSoup(xml_content, 'xml')

    """
    pags_conceitos = extract_page_interval(xml_soup, PAG_INICIO_CONCEITOS, PAG_FIM_CONCEITOS)
    with open("pags_conceitos.xml", "w", encoding="utf-8") as f:
        f.write(pags_conceitos)
    """

    with open("data_txt/diccionari-multilinguee-de-la-covid-19/pags_conceitos.xml", "r", encoding="utf-8") as f:
        pags_conceitos = f.read()

    text = prepare_text(pags_conceitos)
    with open("texto_dict.txt", "w", encoding="utf-8") as f:
        f.write(text)

    parsed_text = parse_text(text)
    with open("multi_covid_19.json", "w", encoding="utf-8") as f:
        json.dump(parsed_text, f, indent=4, ensure_ascii=False)
