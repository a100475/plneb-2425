import json
import re

import unicodedata


def limpar_marcar(texto):
    #Limpeza
    texto = re.sub(r'\n+', '\n', texto)
    texto = re.sub(r'\f', '', texto)

    #Marcarcao
    texto = re.sub(r'(((?<=\n\b[A-Z]\b\n))|(\n(?=\b[A-Z]\b\n)))', '\n###\n', texto)
    
    return texto


def normalizar_first_letter(term):
    cleaned_term = re.sub(r'^[\'"\(\)\[\]\{\}]+', '', term.strip())

    if not cleaned_term:
        return '_'

    first_letter = cleaned_term[0].upper()

    # Normalizar caracteres com acento (á -> a, etc.)
    first_letter = unicodedata.normalize('NFKD', first_letter).encode('ASCII', 'ignore').decode('utf-8')

    if not first_letter:
        return '_'

    return first_letter


def processar_blocks(blocks):
    processed_blocks = []

    for block in blocks:
        if not block.strip():
            continue

        processed_lines = []
        lines = block.splitlines()
        i = 0

        while i < len(lines):
            current_line = lines[i].strip()

            if i == len(lines) - 1:
                processed_lines.append(current_line)
                break

            next_line = lines[i + 1].strip()

            # If line não tem "(pop)" && >35 chars
            if "(pop)" not in current_line and len(current_line) > 35:
                # Add para a proxima linha
                lines[i + 1] = current_line + " " + next_line
                i += 1

            # If line tem "(pop)" && <35 char
            elif "(pop)" not in current_line and len(current_line) <= 35 and i > 0:
                # Add à linha anterior
                processed_lines[-1] = processed_lines[-1] + " " + current_line
                i += 1
            else:
                processed_lines.append(current_line)
                i += 1

        processed_blocks.append('\n'.join(processed_lines))

    return processed_blocks

def extract_termos():

    with open('data_txt/Glossario de Termos Medicos Tecnicos e Populares.txt', 'r', encoding='utf-8') as f:
        texto = f.read()

    texto = limpar_marcar(texto)

    blocks = re.findall(r'###\s*(.*?)\s*(?=###|$)', texto, re.DOTALL)

    result_dict = {"Termos": {}}

    term_dict = result_dict["Termos"]

    blocks = processar_blocks(blocks)

    for block in blocks:
        # desc (pop), term  AND  term, desc (pop)
        entries = re.findall(
            r'^(?:(.*)\s*\(pop\)\s*,\s*(.+)|(.*?)\s*,\s*(.+)\s*\(pop\))$',
            block,
            re.MULTILINE
        )

        for left_desc, left_term, right_term, right_desc in entries:
            if left_desc and left_term:
                term = left_term
                desc = left_desc.strip()
                #first_letter = normalizar_first_letter(term)
            elif right_term and right_desc:
                term = right_term
                desc = right_desc.strip()
                #first_letter = normalizar_first_letter(term)
            else:
                continue

            #if first_letter not in term_dict:
                #term_dict[first_letter] = {}

            #term_dict[first_letter][term] = desc
            term_dict[term.lower()] = desc


    with open('Glossario_de_Termos_Medicos_Tecnicos_e_Populares.json', 'w', encoding='utf-8') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    extract_termos()