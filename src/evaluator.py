import numpy as np
from langchain_openai import OpenAIEmbeddings

class Evaluator:
    def __init__(self):
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
        self.stagnation_threshold = 0.95  # High similarity means stagnation

    def calculate_embedding(self, text: str) -> np.ndarray:
        embedding = self.embeddings_model.embed_query(text)
        return np.array(embedding)

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def is_stagnating(self, current_msg: str, previous_msgs: list[str]) -> bool:
        """
        Calculates perplexity delta / embedding similarity to detect redundancy.
        Returns True if the current message is too similar to previous messages.
        """
        if not previous_msgs:
            return False
            
        current_emb = self.calculate_embedding(current_msg)
        
        for msg in previous_msgs[-2:]: # Compare with last 2 turns
            prev_emb = self.calculate_embedding(msg)
            sim = self.cosine_similarity(current_emb, prev_emb)
            if sim > self.stagnation_threshold:
                return True # Semantic Stagnation detected!
                
        return False
