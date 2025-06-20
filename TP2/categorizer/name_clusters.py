import pandas as pd
import json
import os

def process_clusters():
    df = pd.read_csv("medical_categories_analysis.csv")

    cluster_names = {
        10: "Doenças e Síndromes",
        2: "Fármacos e Terapêuticas",
        8: "Saúde Pública e Epidemiologia",
        9: "Conceitos Gerais de Fisiologia e Patologia",
        7: "Condições Inflamatórias",
        3: "Sintomas Clínicos",
        16: "Bioquímica, Proteínas e Técnicas Laboratoriais",
        5: "Desequilíbrios Metabólicos e Sistémicos",
        4: "Condições Clínicas",
        0: "Distúrbios de Função",
        14: "Anatomia",
        13: "Doenças Infeciosas",
        15: "Conceitos de Processo",
        11: "Classes de Fármacos",
        1: "Farmacologia",
        12: "Processos Fisiológicos e Patológicos",
        17: "Patologia Cardiovascular e Vascular",
        6: "Ginecologia e Obstetrícia"
    }
    

    merge_groups = {
        "Farmacologia e Terapêutica": [2, 11, 1],
        "Processos e Conceitos Fisiopatológicos": [9, 12],
        "Sintomas e Distúrbios Funcionais": [3, 0]
    }
    
    final_clusters = {}
    used_clusters = set()

    for merged_name, cluster_ids in merge_groups.items():
        all_terms = []
        for cluster_id in cluster_ids:
            if cluster_id in df['Cluster_ID'].values:
                cluster_row = df[df['Cluster_ID'] == cluster_id]
                terms = eval(cluster_row['All_Terms'].iloc[0])
                all_terms.extend(terms)
                used_clusters.add(cluster_id)
        
        if all_terms:
            final_clusters[merged_name] = {"termos": sorted(list(set(all_terms)))}
    
    for _, row in df.iterrows():
        cluster_id = row['Cluster_ID']
        if cluster_id not in used_clusters:
            cluster_name = cluster_names.get(cluster_id, f"Cluster {cluster_id}")
            terms = eval(row['All_Terms'])
            final_clusters[cluster_name] = {"termos": sorted(terms)}
    
    return final_clusters

def verify_all_terms_categorized():
    with open("dicts/out/merged_dict.json", 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    final_clusters = process_clusters()
    categorized_terms = set()
    for cluster_data in final_clusters.values():
        categorized_terms.update(cluster_data["termos"])
    
    # Check for missing terms
    original_terms = set(original_data.keys())
    missing_terms = original_terms - categorized_terms
    
    print(f"Original terms: {len(original_terms)}")
    print(f"Categorized terms: {len(categorized_terms)}")
    print(f"Missing terms: {len(missing_terms)}")
    
    if missing_terms:
        print("Some missing terms:", list(missing_terms)[:10])
    
    return missing_terms

def save_clustered_terms(path=None):
    print("Processing clusters...")
    final_clusters = process_clusters()
    
    print("\nFinal clusters summary:")
    print("=" * 60)
    total_terms = 0
    for cluster_name, data in final_clusters.items():
        term_count = len(data["termos"])
        total_terms += term_count
        print(f"{cluster_name}: {term_count} terms")
    
    print(f"\nTotal terms: {total_terms}")
    
    # Verify all terms are categorized
    print("\nVerifying all terms are categorized...")
    missing_terms = verify_all_terms_categorized()
    
    if path is None:
        path = "."
    
    output_file = os.path.join(path, "categorized_medical_terms.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_clusters, f, ensure_ascii=False, indent=2)
    
    print(f"\nCategorized terms saved to {output_file}")
    
    return final_clusters

if __name__ == "__main__":
    clustered_terms = save_clustered_terms('dicts/out')