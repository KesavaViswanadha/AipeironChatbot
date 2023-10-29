import numpy as np
import spacy
from PyPDF2 import PdfReader
import nltk
import sys
import json
import os
import openai
from scipy.spatial import distance
import plotly.express as px
from sklearn.cluster import KMeans
from umap import UMAP
import pinecone

class DocChunker:
    # Load the Spacy model
    
    def __init__(self):
        # BEWARE OF THE FACT THAT INACTIVE DATABASES ON PINECONE GET GARBAGE
        # COLLECTED AFTER A DAY SO WEIRD STUFF MIGHT HAPPEN!!!!!!!
        pinecone.init(api_key="b0ec4895-ab56-43b3-baf0-a404a9e28e20", environment="gcp-starter")
        openai.api_key = "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"
        if not ("data-embeddings" in pinecone.list_indexes()):
            pinecone.create_index("data-embeddings", dimension=1536, metric="euclidean")
        self.this_table = pinecone.Index("data-embeddings")

        self.nlp = spacy.load('en_core_web_sm')
        self.clusters_lens = []
        self.final_texts = []
        self.final_embeddings = []
        nltk.download('punkt')

    # Extracting Text from PDF
    def extract_text_from_pdf(self, file_path):
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = " ".join(page.extract_text() for page in pdf.pages)
        return text
    
    def process_pdf(self, file_path):
        return self.final_chunks(self.extract_text_from_pdf(file_path))

    def process(self, text):
        doc = self.nlp(text)
        sents = list(doc.sents)
        vecs = np.stack([sent.vector / sent.vector_norm for sent in sents])

        return sents, vecs

    def cluster_text(self, sents, vecs, threshold):
        clusters = [[0]]
        for i in range(1, len(sents)):
            if np.dot(vecs[i], vecs[i-1]) < threshold:
                clusters.append([])
            clusters[-1].append(i)
        
        return clusters

    def clean_text(self, text):
        # Add your text cleaning process here
        return text


    def get_embedding(self, text_to_embed):
        # Embed a line of text
        response = openai.Embedding.create(model= "text-embedding-ada-002", input=[text_to_embed])
        # Extract the AI output embedding as a list of floats
        embedding = response["data"][0]["embedding"]
        
        return embedding

    def final_chunks(self, text):
        # Process the chunk
        threshold = 0.2
        sents, vecs = self.process(text)

        # Cluster the sentences
        clusters = self.cluster_text(sents, vecs, threshold)

        for cluster in clusters:
            cluster_txt = self.clean_text(' '.join([sents[i].text for i in cluster]))
            cluster_len = len(cluster_txt)
            
            # Check if the cluster is too short
            if cluster_len < 60:
                continue
            
            # Check if the cluster is too long
            elif cluster_len > 512:
                threshold = 0.5
                sents_div, vecs_div = self.process(cluster_txt)
                reclusters = self.cluster_text(sents_div, vecs_div, threshold)
                
                for subcluster in reclusters:
                    div_txt = self.clean_text(' '.join([sents_div[i].text for i in subcluster]))
                    div_len = len(div_txt)
                    
                    if div_len < 60 or div_len > 512:
                        continue
                    
                    self.clusters_lens.append(div_len)
                    self.final_texts.append(div_txt)
                    
            else:
                # ascii_text = cluster_txt.encode('ascii', 'ignore').decode('ascii')
                # # Replace various forms of newlines and adjacent spaces
                # cleaned_txt = ascii_text.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
                # # Further strip any leading/trailing whitespace that could have been left over
                # cleaned_txt = cleaned_txt.strip()
                # split_text = cleaned_txt.split("\n")
                # clean_text = "".join(split_text)
                
                self.clusters_lens.append(cluster_len)
                self.final_texts = [x.replace('\n', '').encode('ascii', 'ignore').decode('ascii') for x in (self.final_texts + [cluster_txt])]
                self.final_embeddings.append(self.get_embedding(self.final_texts[-1]))

                if len(self.final_texts) > 120:
                    ##self.final_texts = [x.replace('\n', '') for x in self.final_texts]
                    #print(self.final_texts)
                    #print(list(zip(self.final_texts, self.final_embeddings)))
                    self.this_table.upsert(list(zip(self.final_texts, self.final_embeddings)))
                    self.final_texts = []
                    self.final_embeddings = []
                
        return self.final_texts

def main(file_path):
    doc_chunker = DocChunker()
    results = doc_chunker.process_pdf(file_path)
    print(results[20])
    with open('output.json', 'w') as f:  # Write the results to a file
        json.dump(results, f)

if __name__ == "__main__":
    main(sys.argv[1])