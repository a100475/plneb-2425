import json
import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
import torch
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import re

class MedicalTermCategorizer:
    def __init__(self, model_name='neuralmind/bert-base-portuguese-cased'):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        
        self.terms = {}
        self.original_data = {}
        self.embeddings = None
        self.cluster_labels = None
        
    def load_terms(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.original_data = data
        processed_terms = {}
        terms_without_description = []
        
        for term, content in data.items():
            description = self._extract_description(content)
            if description:
                processed_terms[term] = description
            else:
                processed_terms[term] = term
                terms_without_description.append(term)
        
        self.terms = processed_terms
        print(f"Loaded {len(processed_terms)} terms")
        return processed_terms
    
    def _extract_description(self, content):
        if isinstance(content, dict):
            if 'desc' in content:
                desc = content['desc']
                if isinstance(desc, list) and desc:
                    return desc[0] 
                elif isinstance(desc, str):
                    return desc
            
            if 'desc_ca' in content:
                desc_ca = content['desc_ca']
                if isinstance(desc_ca, dict) and 'text' in desc_ca:
                    return desc_ca['text']
                elif isinstance(desc_ca, str):
                    return desc_ca
        
        return None
    
    def get_bert_embeddings(self, texts, batch_size=8):
        embeddings = []
        
        processed_texts = []
        for text in texts:
            clean_text = re.sub(r'[^\w\s]', ' ', text.lower())
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            processed_texts.append(clean_text)
        
        with torch.no_grad():
            for i in range(0, len(processed_texts), batch_size):
                batch_texts = processed_texts[i:i + batch_size]
                
                encoded = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=256,
                    return_tensors='pt'
                )
                
                input_ids = encoded['input_ids'].to(self.device)
                attention_mask = encoded['attention_mask'].to(self.device)
                
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                
                token_embeddings = outputs.last_hidden_state
                input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                mean_embeddings = sum_embeddings / sum_mask
                
                embeddings.append(mean_embeddings.cpu().numpy())
        
        return np.vstack(embeddings)
    
    def create_embeddings(self):
        if not self.terms:
            raise ValueError("Load terms first.")
            
        print("Creating BERT embeddings...")
        combined_texts = [f"{term}: {desc}" for term, desc in self.terms.items()]
        self.embeddings = self.get_bert_embeddings(combined_texts)
        print(f"Created embeddings with shape: {self.embeddings.shape}")

    def cluster_terms(self, n_clusters: int = 20):
        if self.embeddings is None:
            raise ValueError("Create embeddings first.")
            
        print(f"Clustering terms into {n_clusters} clusters...")
        
        kmeans = KMeans(
            n_clusters=n_clusters, 
            random_state=42, 
            n_init=20,
            max_iter=500,
            init='k-means++'
        )
        self.cluster_labels = kmeans.fit_predict(self.embeddings)
        
        print("Clustering Done")
        
        unique, counts = np.unique(self.cluster_labels, return_counts=True)
        print(f"Cluster distribution: {dict(zip(unique, counts))}")
    
    def _find_cluster_representatives(self, n_representatives=10):
        if self.embeddings is None or self.cluster_labels is None:
            raise ValueError("Embeddings and clustering must be completed first.")
            
        cluster_representatives = {}
        terms_list = list(self.terms.keys())
        
        for cluster_id in set(self.cluster_labels):
            cluster_mask = self.cluster_labels == cluster_id
            cluster_embeddings = self.embeddings[cluster_mask]
            cluster_terms = [terms_list[i] for i, mask in enumerate(cluster_mask) if mask]
            
            centroid = np.mean(cluster_embeddings, axis=0)
            
            distances = []
            for i, embedding in enumerate(cluster_embeddings):
                distance = np.linalg.norm(embedding - centroid)
                distances.append((distance, cluster_terms[i]))
            
            distances.sort(key=lambda x: x[0])
            representatives = [term for _, term in distances[:n_representatives]]
            cluster_representatives[cluster_id] = representatives
        
        return cluster_representatives

    def print_cluster_representatives(self, n_representatives=10):
        representatives = self._find_cluster_representatives(n_representatives)
        cluster_results = self.get_cluster_results()
        
        print("\n" + "="*80)
        print("CLUSTER REPRESENTATIVES")
        print("="*80)
        
        sorted_clusters = sorted(cluster_results.items(), key=lambda x: len(x[1]), reverse=True)
        
        for cluster_id, cluster_terms in sorted_clusters:
            cluster_size = len(cluster_terms)
            cluster_reps = representatives[cluster_id]
            
            print(f"\nCluster {cluster_id} - Size: {cluster_size} ({cluster_size/len(self.terms)*100:.1f}%)")
            print("-" * 60)
            print("Most representative terms:")
            for i, term in enumerate(cluster_reps, 1):
                print(f"  {i:2d}. {term}")
    
    def get_cluster_results(self):
        if self.cluster_labels is None:
            raise ValueError("Please cluster terms first.")
            
        cluster_results = defaultdict(list)
        terms_list = list(self.terms.keys())
        
        for i, label in enumerate(self.cluster_labels):
            cluster_results[label].append(terms_list[i])
        
        return dict(cluster_results)
    
    def analyze_clusters(self):
        cluster_results = self.get_cluster_results()
        representatives = self._find_cluster_representatives(10)
        
        analysis_data = []
        
        for cluster_id, cluster_terms in cluster_results.items():
            cluster_size = len(cluster_terms)
            representative_terms = ', '.join(representatives[cluster_id])
            
            analysis_data.append({
                'Cluster_ID': cluster_id,
                'Size': cluster_size,
                'Representative_Terms': representative_terms,
                'All_Terms': cluster_terms
            })
        
        df = pd.DataFrame(analysis_data)
        df = df.sort_values('Size', ascending=False).reset_index(drop=True)
        
        return df
    
    def visualize_clusters(self, save_path=None):
        if self.embeddings is None or self.cluster_labels is None:
            raise ValueError("Embeddings and clustering must be completed first.")
            
        pca = PCA(n_components=2, random_state=42)
        embeddings_2d = pca.fit_transform(self.embeddings)
        
        plt.figure(figsize=(18, 14))
        
        n_clusters = len(set(self.cluster_labels))
        colors = plt.cm.tab20(np.linspace(0, 1, n_clusters))
        
        for i, cluster_id in enumerate(set(self.cluster_labels)):
            mask = self.cluster_labels == cluster_id
            plt.scatter(
                embeddings_2d[mask, 0], 
                embeddings_2d[mask, 1], 
                c=[colors[i]], 
                label=f"Cluster {cluster_id}",
                alpha=0.6,
                s=20
            )
        
        cluster_results = self.get_cluster_results()
        for cluster_id in cluster_results.keys():
            mask = self.cluster_labels == cluster_id
            center_x = embeddings_2d[mask, 0].mean()
            center_y = embeddings_2d[mask, 1].mean()
            
            cluster_size = sum(mask)
            
            plt.annotate(f'C{cluster_id}\n({cluster_size})', 
                        (center_x, center_y), 
                        fontsize=8, fontweight='bold',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                        ha='center', va='center')
        
        plt.title('Categorização de Termos Médicos', fontsize=16, fontweight='bold')
        plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variância)', fontsize=12)
        plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variância)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Gráfico salvo em {save_path}")
        
        plt.tight_layout()
        plt.show()
    
    def find_optimal_clusters_elbow(self, max_clusters=20):
        if self.embeddings is None:
            raise ValueError("Create embeddings first.")
            
        wcss = []
        cluster_range = range(2, max_clusters + 1)
        
        print("Finding optimal clusters using elbow method...")
        for k in cluster_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(self.embeddings)
            wcss.append(kmeans.inertia_)
            print(f"K={k}, WCSS={kmeans.inertia_:.2f}")
        
        plt.figure(figsize=(10, 6))
        plt.plot(cluster_range, wcss, 'bo-')
        plt.title('Elbow Method for Optimal Clusters')
        plt.xlabel('Number of Clusters (k)')
        plt.ylabel('Within-Cluster Sum of Squares (WCSS)')
        plt.grid(True, alpha=0.3)
        plt.show()
        
        differences = np.diff(wcss)
        elbow_point = cluster_range[np.argmax(differences)] + 1
        print(f"Suggested elbow point: {elbow_point} clusters")
        
        return wcss, elbow_point


def main():
    categorizer = MedicalTermCategorizer()
    
    json_path = "dicts/out/merged_dict.json"
    categorizer.load_terms(json_path)
    
    categorizer.create_embeddings()

    wcss, recommended_k = categorizer.find_optimal_clusters_elbow()

    categorizer.cluster_terms(n_clusters=recommended_k)
    
    categorizer.print_cluster_representatives(n_representatives=15)

    analysis_df = categorizer.analyze_clusters()
    print("\nAnálise de Categorias:")
    print(analysis_df[['Cluster_ID', 'Size', 'Representative_Terms']])
    
    categorizer.visualize_clusters(save_path="medical_categories_improved.png")
    
    analysis_df.to_csv("medical_categories_analysis.csv", index=False, encoding='utf-8')
    print("\nAnálise salva em medical_categories_analysis.csv")

if __name__ == "__main__":
    main()