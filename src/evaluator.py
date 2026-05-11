import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Evaluator:
    def __init__(self):
        # Replaced heavy PyTorch embeddings with lightweight TF-IDF to prevent 512MB Render RAM OOM
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.stagnation_threshold = 0.85  # Adjusted threshold for TF-IDF

    def is_stagnating(self, current_msg: str, previous_msgs: list[str]) -> bool:
        """
        Calculates TF-IDF cosine similarity to detect redundancy.
        Returns True if the current message is too similar to previous messages.
        """
        if not previous_msgs:
            return False
            
        corpus = [current_msg] + previous_msgs[-2:]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            
            # tfidf_matrix[0] is current_msg, [1:] are the previous msgs
            current_vec = tfidf_matrix[0:1]
            prev_vecs = tfidf_matrix[1:]
            
            similarities = cosine_similarity(current_vec, prev_vecs)[0]
            
            if any(sim > self.stagnation_threshold for sim in similarities):
                return True # Semantic Stagnation detected!
                
        except ValueError:
            # Vocabulary empty (e.g. all stop words)
            pass
            
        return False
