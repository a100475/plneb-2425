import json
import re




# Limpeza e Marcação de texto
def limpar_marcar(conteudo):
    #Limpeza
    conteudo = re.sub(r'', '\n', conteudo)
    conteudo = re.sub(r'\n+', '\n', conteudo)

    #Marcarcao
    # Marcar o autor
    conteudo = re.sub(r'(AURI CLAUDIONEI MATOS FRÜBEL)', r'##AUTOR##\1##AUTOR##', conteudo)

    # Marcar o título
    conteudo = re.sub(r'(^(GLOSSÁRIO).+?(BRASIL)$)', r'##TITULO##\1##TITULO##', conteudo, flags=re.DOTALL | re.MULTILINE)

    # Marcar o ano de publicação
    conteudo = re.sub(r'ARARAQUARA\n(^(\d{4})$)', r'ARARAQUARA\n##ANO_PUBLICACAO##\1##ANO_PUBLICACAO##', conteudo, flags=re.MULTILINE)

    # Marcar o resumo
    conteudo = re.sub(r'^RESUMO\n(.+?)\nPalavras-chave', r'RESUMO\n##RESUMO##\1##RESUMO##\nPalavras-chave', conteudo, flags=re.MULTILINE | re.DOTALL) 

    # Marcar as palavras-chave
    conteudo = re.sub(r'Palavras-chave:(\s(.+?)(?=\n|$))', r'Palavras-chave: ##PALAVRAS-CHAVE##\1##PALAVRAS-CHAVE##', conteudo, flags=re.MULTILINE)

    # Marcar as entradas do glossário
    # Início
    conteudo = re.sub(r'(?<=\d\)\n)^(\w[^()]+?\s(s\.f\.|s\.m\.)\n)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    conteudo = re.sub(r'(?<=\d\)\)\n)^(\w[^()]+?\s(s\.f\.|s\.m\.)\n)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    conteudo = re.sub(r'(?<=\d\)"\n)^(\w[^()]+?\s(s\.f\.|s\.m\.)\n)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    conteudo = re.sub(r'(?<=3\.2\. O glossário\n)^(\w[^()]+?\s(s\.f\.|s\.m\.)\n)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    
    # Fim
    conteudo = re.sub(r'(?<=\)\))(\n)(?=##ENTRADA##)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    conteudo = re.sub(r'(?<=\d\))(\n)(?=##ENTRADA##)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    conteudo = re.sub(r'(?<=\)")(\n)(?=##ENTRADA##)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    conteudo = re.sub(r'(?<=\d\))(\n)(?=3\.3\. Equivalências)', r'##ENTRADA##\1', conteudo, flags=re.MULTILINE | re.DOTALL)
    
    
    return conteudo


def extrair_metadata(conteudo_limpo):
    metadata = {}

    # Extrair o autor
    autor = re.search(r'##AUTOR##(.*?)##AUTOR##', conteudo_limpo)
    metadata['autor'] = autor.group(1) if autor else None

    # Extrair o título
    titulo = re.search(r'##TITULO##(.+?)##TITULO##', conteudo_limpo, flags=re.DOTALL)
    if titulo:
        titulo = re.sub(r'\n', ' ', titulo.group(1))
        metadata['titulo'] = titulo
    else:
        metadata['titulo'] = None
    
    # Extair a data de publicacao
    data = re.search(r'##ANO_PUBLICACAO##(.+?)##ANO_PUBLICACAO##', conteudo_limpo)
    metadata['data_publicacao'] = data.group(1) if data else None

    # Extrair o resumo
    resumo = re.search(r'##RESUMO##(.+?)##RESUMO##', conteudo_limpo, flags=re.DOTALL)
    if resumo:
        resumo = re.sub(r'\n', ' ', resumo.group(1))
        metadata['resumo'] = resumo
    else:
        metadata['resumo'] = None

    # Extrair as palavras-chave
    p_chaves = re.search(r'##PALAVRAS-CHAVE##(.+?)##PALAVRAS-CHAVE##', conteudo_limpo, flags=re.DOTALL)
    metadata['palavras-chave'] = []

    if p_chaves:
        palavras = [p.strip() for p in re.split('[,;]', p_chaves.group(1))]
        for i in range(len(palavras)):
            metadata['palavras-chave'].append(palavras[i])
    else:
        metadata['palavras-chave'] = None


    return metadata

    

def extrair_conteudo(conteudo_limpo):
    lista_termos = []
    
    conceitos = re.findall(r'##ENTRADA##(.+?)##ENTRADA##', conteudo_limpo, flags=re.DOTALL)
    for conceito in conceitos:
        info = {}

        # Extrair a entrada e classe
        entrada = re.findall(r'(^\w.+?(?:s\.f\.|s\.m\.)$)', conceito, flags=re.MULTILINE)

        palavra = re.search(r'^\w.+?(?=\s(?:s\.f\.|s\.m\.))', entrada[0]) if entrada else None
        info["entrada"] = palavra.group(0) if palavra else None

        classe = re.search(r'(s\.f\.|s\.m\.)', entrada[0]) if entrada else None
        info["classe_gramatical"] = classe.group(0) if classe else None

        # Extrair as traducoes       
        traducao = re.findall(r'(?<=\.\n)(^\w.+?\[ing\];.+?\.?)(?=\[esp\]\n|\[es\n|\n[A-ZÁÉÍÓÚÂÊÎÔÛÃÕ])', conceito, flags=re.MULTILINE | re.DOTALL)
        
        if traducao:
            traducao = traducao[0].split("; ")
            info["traducao_ing"] = traducao[0].replace(" [ing]", "").replace("\n", " ")
            if traducao and len(traducao) > 1:
                trad_esp = re.sub(r'\.', "", traducao[1])
                info["traducao_esp"] = trad_esp.replace("\n", " ").strip()
            else:
                info["traducao_esp"] = None
        else:
            info["traducao_ing"] = None
            info["traducao_esp"] = None
        
        # Extrair sigla
        sigla = re.search(r'^Sigla:\s([A-Z]{1,})', conceito, flags=re.MULTILINE)
        info["sigla"] = sigla.group(1) if sigla else None

        # Extrair a definicao       
        definicao = re.search(r'(?:\[esp\]|\[es|;\s\w+\s\w+)\n(\w.+?)(?=Inf\.|\“|\")', conceito, flags=re.MULTILINE | re.DOTALL)

        if definicao:
            if re.search(r'.+?\nSigla:\s.+', definicao.group(1)):
                definicao = re.sub(r'(.+?\nSigla:\s[A-Z]+\n)(?=[A-ZÁÉÍÓÚÂÊÎÔÛÃÕ])', '', definicao.group(1))
                definicao = definicao.strip().replace("\n", " ")

                if re.match(r'Ver este termo\s', definicao):
                    definicao = re.sub(r'(Ver este termo\s)(?=\w+?)', '', definicao)
                    info["ver"] = definicao
                else:
                    info["definicao"] = definicao
            
            elif re.search(r'Sigla:\s.+', definicao.group(1)):
                definicao = re.sub(r'(Sigla:\s[A-Z]+\n)(?=[A-ZÁÉÍÓÚÂÊÎÔÛÃÕ])', '', definicao.group(1))
                definicao = definicao.strip().replace("\n", " ")

                if re.match(r'Ver este termo\s', definicao):
                    definicao = re.sub(r'(Ver este termo\s)(?=\w+?)', '', definicao)
                    info["ver"] = definicao
                else:
                    info["definicao"] = definicao

            elif re.search(r'\[esp\]', definicao.group(1)):
                definicao = re.sub(r'(.+?\[esp\]\n)(?=[A-ZÁÉÍÓÚÂÊÎÔÛÃÕ])', '', definicao.group(1))
                definicao = definicao.strip().replace("\n", " ")

                if re.match(r'Ver este termo\s', definicao):
                    definicao = re.sub(r'(Ver este termo\s)(?=\w+?)', '', definicao)
                    info["ver"] = definicao
                else:
                    info["definicao"] = definicao           

            else:
                definicao = definicao.group(1).strip().replace("\n", " ")

                if re.match(r'Ver este termo\s', definicao):
                    definicao = re.sub(r'(Ver este termo\s)(?=\w+?)', '', definicao)
                    info["ver"] = definicao
                else:
                    info["definicao"] = definicao

        else:
            info["definicao"] = None

        # Extrair a informacao enciclopedia
        inf_encicl = re.search(r'(?:Inf\. encicl\.:?\s)(.*?)\“', conceito, flags=re.MULTILINE | re.DOTALL)
        info["informacao_enciclopedia"] = inf_encicl.group(1).strip().replace("\n", " ") if inf_encicl else None

        # Extair abonacoes
        abonacoes = re.search(r'(?<=“|")(?:\.{3}|…)(.*?)(?=\.{2,4}|…)”?', conceito, flags=re.MULTILINE | re.DOTALL)
        info["abonacoes"] = re.sub(r'^\.\s?', '', abonacoes.group(1).strip().replace("\n", " ")) if abonacoes else None
        

        lista_termos.append(info)

    
    return lista_termos



if __name__ == "__main__":
    with open(r'data_txt/glossario_neologismos_saude.txt', "r", encoding="utf-8") as f:
        conteudo = f.read()

    conteudo_limpo = limpar_marcar(conteudo)
    metadata = extrair_metadata(conteudo_limpo)
    termos = extrair_conteudo(conteudo_limpo)

    conteudo_final = {
        'metadata': metadata,
        'termos': termos
    }
    
    with open(r'glossario_neologismos_saude.json', "w", encoding="utf-8") as file:
        json.dump(conteudo_final, file, ensure_ascii=False, indent=4)
