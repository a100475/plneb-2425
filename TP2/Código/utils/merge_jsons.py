import json


TRADS = {"ca", "oc", "eu", "gl", "es", "en", "fr", "nl", "ar"}

CODS = {"sbl", "nc", "CAS"}

LEX_CAT_MAP = {"s.f.": "n f", "s.m.": "n m"}


OLD_COVID_19_PATH = "./dicts/old/old_covid_19.json"

NEW_COVID_19_PATH = "./dicts/in/new_covid_19.json"
MIN_SAUDE_PATH = "./dicts/in/ministerio_saude.json"
NEO_SAUDE_PATH = "./dicts/in/neologismos_saude.json"
TERM_MED_PATH = "./dicts/in/termos_medicos_populares.json"
ATLAS_SAUDE_PATH = "./dicts/in/atlas_saude.json"

OUTPUT_PATH = "./dicts/out/merged_dict.json"


# Percorre o dicionário original e reformata-o para o contexto em português
def reformat_covid_dict(dict):
    new_dict = {}
    for sub_dict in dict:    
        if "pt-PT" in sub_dict.keys():
            pt_vals = sub_dict["pt-PT"]
        elif "pt" in sub_dict.keys():
            pt_vals = sub_dict["pt"]
        elif "pt-BR" in sub_dict.keys():
            pt_vals = sub_dict["pt-BR"]
        else:
            continue

        value_dict = {}

        key = pt_vals[0]["term"]
        value_dict["lex_cat"] = pt_vals[0]["lex_cat"]
        if len(pt_vals) > 1:
            value_dict["sinonimos"] = pt_vals[1:]

        for k, v in sub_dict.items():
            if k in TRADS:
                value_dict[f"traducao_{k}"] = v
            elif k in CODS or k == "sigla":
                value_dict[k] = v
            elif k in {"desc", "note"}:
                value_dict[f"{k}_ca"] = v  # ca = catalão
            elif k in {"sin_compl", "sin"}:
                value_dict[f"sinonimos_ca"] = v  # ca = catalão
            elif k == "den_com":
                value_dict[f"den_com_ca"] = v  # ca = catalão
            
        new_dict[key] = value_dict

    return new_dict


# Junta o conteúdo dos dicionários construídos
def merge_dicts(merge_min_saude=False):
    with open(NEW_COVID_19_PATH, "r", encoding="utf-8") as f:
        covid = json.load(f)

    with open(NEO_SAUDE_PATH, "r", encoding="utf-8") as f:
        neo_saude = json.load(f)

    with open(TERM_MED_PATH, "r", encoding="utf-8") as f:
        term_med = json.load(f)

    with open(MIN_SAUDE_PATH, "r", encoding="utf-8") as f:
        min_saude = json.load(f)
    
    with open(ATLAS_SAUDE_PATH, "r", encoding="utf-8") as f:
        atlas_saude = json.load(f)

    covneo = merge_covid_with_neo(covid, neo_saude)

    cnpop = merge_covneo_with_term_med(covneo, term_med)

    if merge_min_saude:
        cnpop = merge_covneopop_with_min_saude(cnpop, min_saude)

    return merge_new_content(cnpop, atlas_saude)


# Junta os conteúdos dos dois dicionários principais (Covid-19 e Neologismos de Saúde)
def merge_covid_with_neo(covid, neo):
    for concept in neo["termos"]:
        cname = concept["entrada"]

        matched_key = next((k for k in covid if k.lower() == cname.lower()), None)

        if matched_key:
            print(f"[INFO] Found hit between covid dict and neo dict: {cname}")
            covid[matched_key] = __process_matched_covid_neo(covid[matched_key], concept)
        else:
            covid[cname] = __process_unmatched_covid_neo(concept)

    return covid


# Processa a junção de items com match entre o dicionário do covid-19 e o de neologismos
def __process_matched_covid_neo(covid_entry, neo_entry):
    for k, v in neo_entry.items():
        # Classe gramatical
        if k == "classe_gramatical" and "lex_cat" not in covid_entry.keys():
            covid_entry["lex_cat"] = LEX_CAT_MAP[v]

        # Traduções
        elif k == "traducao_ing" and "traducao_en" not in covid_entry.keys():
            covid_entry["traducao_en"] = [{"term": v, "lex_cat": None}]
        elif k == "traducao_ing":
            append_trad = True
            for sub_dict in covid_entry["traducao_en"]:
                if sub_dict["term"] == v:
                    append_trad = False
                    break
            if append_trad:
                covid_entry["traducao_en"].append({"term": v, "lex_cat": None})
        elif k == "traducao_esp" and "traducao_es" not in covid_entry.keys():
            covid_entry["traducao_es"] = [{"term": v, "lex_cat": None}]
        elif k == "traducao_esp":
            append_trad = True
            for sub_dict in covid_entry["traducao_es"]:
                if sub_dict["term"] == v:
                    append_trad = False
                    break
            if append_trad:
                covid_entry["traducao_es"].append({"term": v, "lex_cat": None})

        # Sigla
        elif k == "sigla" and v and "sigla" in covid_entry.keys():  # Já existe uma lista de siglas
            append_sigla = True
            for term in covid_entry["sigla"]:
                if term == v:
                    append_sigla = False  # A sigla já está incluída no dicionário do covid-19
                    break
            if append_sigla:
                covid_entry["sigla"].append({"term": v, "lex_cat": None})  # Caso não esteja na lista, junta-se, mas sem classe gramatical
        elif k == "sigla" and v:  # Ainda não existe uma lista de siglas
            covid_entry["sigla"] = [{"term": v, "lex_cat": None}]

        # Definição (Troca o nome para ser consistente e deixa como lista para possíveis descrições alternativas dos outros dicionários)
        elif k == "definicao":
            covid_entry["desc"] = [v]

        # Entradas restantes (Não estão presentes no dicionário do covid-19)
        elif k != "entrada" and v:
            covid_entry[k] = v

    return covid_entry


# Processa a adição de um item do dicionário de neologismos ao dicionário do covid-19 quando não há match
def __process_unmatched_covid_neo(entry):
    modded_entry = {}
    for k, v in entry.items():
        if k == "classe_gramatical":
            modded_entry["lex_cat"] = LEX_CAT_MAP[v]
        elif k == "traducao_ing":
            modded_entry["traducao_en"] = [{"term": v, "lex_cat": None}]
        elif k == "traducao_esp":
            modded_entry["traducao_es"] = [{"term": v, "lex_cat": None}]
        elif k == "sigla" and v:
            modded_entry["sigla"] = [{"term": v, "lex_cat": None}]
        elif k == "definicao":
            modded_entry["desc"] = [v]
        elif k != "entrada" and v:
            modded_entry[k] = v
    
    return modded_entry


# Junta os conteúdos do dicionário "merged" principal com o dicionário de termos médicos populares
def merge_covneo_with_term_med(covneo, term_med):
    for k, v in term_med["Termos"].items():
        matched_key = next((existing_k for existing_k in covneo if existing_k.lower() == k.lower()), None)

        if matched_key:
            print(f"[INFO] Found hit between covneo dict and term_med dict: {k}")
            if "desc" in covneo[matched_key]:
                covneo[matched_key]["desc"].append(v)
            else:
                covneo[matched_key]["desc"] = [v]
        else:
            covneo[k] = {"desc": [v]}
    
    return covneo


# Junta os conteúdos do dicionário "merged" dos três principais dicionários com o dicionário do ministério da saúde
def merge_covneopop_with_min_saude(cnpop, min_saude):
    for dic in min_saude["Termos"].values():
        for k, v in dic.items():
            matched_key = next((existing_k for existing_k in cnpop if existing_k.lower() == k.lower()), None)

            if matched_key:
                print(f"[INFO] Found hit between cnpop dict and min_saude dict: {k}")
                if "desc" in cnpop[matched_key]:
                    cnpop[matched_key]["desc"].append(v)
                else:
                    cnpop[matched_key]["desc"] = [v]
            else:
                cnpop[k] = {"desc": [v]}

    for dic in min_saude["Siglas"].values():
        for k, v in dic.items():
            matched_key = next((existing_k for existing_k in cnpop if existing_k.lower() == v.lower()), None)

            if matched_key:
                print(f"[INFO] Found hit between cnpop dict and min_saude dict through acronym: {k}")
                if "sigla" in cnpop[matched_key]:
                    cnpop[matched_key]["sigla"].append({"term": k, "lex_cat": None})
                else:
                    cnpop[matched_key]["sigla"] = [{"term": k, "lex_cat": None}]
    
    return cnpop


# Adiciona o conteúdo proveniente do scraper ao dicionário final
def merge_new_content(base_dict, new_dict):
    for k, v in new_dict.items():
        matched_key = next((existing_k for existing_k in base_dict if existing_k.lower() == k.lower()), None)

        if matched_key:
            print(f"[INFO] Found hit between final dict and atlas_saude dict: {k}")
            if "desc" in base_dict[matched_key]:
                base_dict[matched_key]["desc"].append(v)
            else:
                base_dict[matched_key]["desc"] = [v]
        else:
            base_dict[k] = {"desc": [v]}
    
    return base_dict


if __name__ == "__main__":
    with open(OLD_COVID_19_PATH, "r", encoding="utf-8") as f:
        covid_dict = json.load(f)

    with open(NEW_COVID_19_PATH, "w", encoding="utf-8") as f:
        json.dump(reformat_covid_dict(covid_dict), f, ensure_ascii=False, indent=4)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(merge_dicts(merge_min_saude=False), f, ensure_ascii=False, indent=4)
