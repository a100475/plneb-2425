import json

GLOSS_TERM_MED = "Glossario_de_Termos_Medicos_Tecnicos_e_Populares.json"
GLOSS_NEO_SAUDE = "glossario_neologismos_saude.json"
DICT_MULTI_COVID = "multi_covid_19.json"
GLOSS_MIN_SAUDE = "glossario_ministerio_saude.json"


def merge_dicts():
    with open(GLOSS_TERM_MED, "r", encoding="utf-8") as f:
        dict_term_med = json.load(f)

    with open(GLOSS_NEO_SAUDE, "r", encoding="utf-8") as f:
        dict_neo_saude = json.load(f)
    
    with open(DICT_MULTI_COVID, "r", encoding="utf-8") as f:
        dict_multi_covid = json.load(f)
    
    with open(GLOSS_MIN_SAUDE, "r", encoding="utf-8") as f:
        dict_min_saude = json.load(f)
    
    final_dict = dict_term_med
    final_dict["siglas"] = dict_min_saude["Siglas"]

    for key, value in dict_min_saude["Termos"].items():
        for sub_key, sub_value in value.items():
            sub_key = sub_key.lower()
            if sub_key not in final_dict["Termos"]:
                final_dict["Termos"][sub_key] = sub_value

    for termo in dict_neo_saude["termos"]:
        key = termo["entrada"]
        termo.pop("entrada")
        vals = termo
        final_dict["Termos"][key] = vals

    for entry in dict_multi_covid:
        pt_terms = []
        for pt_key in ['pt', 'pt-PT', 'pt-BR']:
            if pt_key in entry:
                pt_terms.extend(entry[pt_key])

        if pt_terms:
            for pt_item in pt_terms:
                pt_term = pt_item['term']


                if pt_term not in final_dict["Termos"]:

                    new_entry = {
                        "classe_gramatical": pt_item.get('lex_cat', 'n/a'),
                    }


                    if 'desc' in entry:
                        new_entry["definicao"] = entry['desc']


                    for lang in ['ca', 'sigla', 'oc', 'eu', 'gl', 'es', 'en', 'fr', 'nl', 'ar']:
                        if lang in entry:
                            new_entry[f'traducao_{lang}'] = [item['term'] for item in entry[lang]]


                    if 'note' in entry:
                        new_entry['notas'] = entry['note']


                    if 'CAS' in entry:
                        new_entry['cas'] = entry['CAS']

                    final_dict["Termos"][pt_term] = new_entry
                else:

                    if isinstance(final_dict["Termos"][pt_term], str):

                        original_def = final_dict["Termos"][pt_term]
                        final_dict["Termos"][pt_term] = {
                            "definicao": original_def,
                            "classe_gramatical": pt_item.get('lex_cat', 'n/a')
                        }
                        existing_entry = final_dict["Termos"][pt_term]
                    else:
                        existing_entry = final_dict["Termos"][pt_term]
                        if "classe_gramatical" not in existing_entry:
                            existing_entry["classe_gramatical"] = pt_item.get('lex_cat', 'n/a')


                    for lang in ['ca', 'sigla', 'oc', 'eu', 'gl', 'es', 'en', 'fr', 'nl', 'ar']:
                        if lang in entry:
                            trad_key = f'traducao_{lang}'
                            if trad_key not in existing_entry:
                                existing_entry[trad_key] = [item['term'] for item in entry[lang]]


                    if 'note' in entry and 'notas' not in existing_entry:
                        existing_entry['notas'] = entry['note']


        if 'veg' in entry and isinstance(entry['veg'], dict):
            veg_term = entry['veg'].get('term')
            if veg_term:
                if veg_term not in final_dict["Termos"]:
                    veg_entry = {
                        "classe_gramatical": entry['veg'].get('lex_cat', 'n/a'),
                    }


                    if 'desc' in entry:
                        veg_entry["definicao"] = entry['desc']


                    for lang in ['ca', 'sigla', 'oc', 'eu', 'gl', 'es', 'en', 'fr', 'nl', 'ar']:
                        if lang in entry:
                            veg_entry[f'traducao_{lang}'] = [item['term'] for item in entry[lang]]


                    if 'note' in entry:
                        veg_entry['notas'] = entry['note']


                    if 'CAS' in entry:
                        veg_entry['cas'] = entry['CAS']

                    final_dict["Termos"][veg_term] = veg_entry
                else:

                    if isinstance(final_dict["Termos"][veg_term], str):

                        original_def = final_dict["Termos"][veg_term]
                        final_dict["Termos"][veg_term] = {
                            "definicao": original_def,
                            "classe_gramatical": entry['veg'].get('lex_cat', 'n/a')
                        }
                        veg_existing_entry = final_dict["Termos"][veg_term]
                    else:
                        veg_existing_entry = final_dict["Termos"][veg_term]
                        if "classe_gramatical" not in veg_existing_entry:
                            veg_existing_entry["classe_gramatical"] = entry['veg'].get('lex_cat', 'n/a')


                    for lang in ['ca', 'sigla', 'oc', 'eu', 'gl', 'es', 'en', 'fr', 'nl', 'ar']:
                        if lang in entry:
                            trad_key = f'traducao_{lang}'
                            if trad_key not in veg_existing_entry:
                                veg_existing_entry[trad_key] = [item['term'] for item in entry[lang]]


                    if 'note' in entry and 'notas' not in veg_existing_entry:
                        veg_existing_entry['notas'] = entry['note']


    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(final_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    merge_dicts()