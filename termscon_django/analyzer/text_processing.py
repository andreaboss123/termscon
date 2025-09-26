import re
from typing import List
from sentence_transformers import SentenceTransformer

class TextProcessor:
    def __init__(self):
        # Initialize the same embedding model that was likely used for the legal texts
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def segment_terms_conditions(self, text: str) -> List[str]:
        """Segment T&C text into individual clauses."""
        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Split by common clause separators
        # Look for numbered sections, bullet points, or paragraph breaks
        patterns = [
            r'\n\s*\d+\.\s*',  # 1. 2. 3. etc.
            r'\n\s*\(\d+\)\s*',  # (1) (2) (3) etc.
            r'\n\s*[a-z]\)\s*',  # a) b) c) etc.
            r'\n\s*[A-Z]\.\s*',  # A. B. C. etc.
            r'\n\s*-\s*',  # bullet points
            r'\n\s*•\s*',  # bullet points
            r'\n\n+'  # double line breaks
        ]
        
        # Try to split by patterns
        clauses = []
        remaining_text = text
        
        for pattern in patterns:
            if re.search(pattern, remaining_text):
                splits = re.split(pattern, remaining_text)
                # Keep the splits that are substantial (more than 50 characters)
                substantial_splits = [s.strip() for s in splits if len(s.strip()) > 50]
                if len(substantial_splits) > 1:
                    clauses = substantial_splits
                    break
        
        # If no good splits found, try sentence-based splitting for long text
        if not clauses and len(text) > 500:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            # Group sentences into clauses (3-5 sentences each)
            clause_size = max(3, len(sentences) // 10)  # Aim for around 10 clauses
            clauses = []
            current_clause = []
            
            for sentence in sentences:
                current_clause.append(sentence)
                if len(current_clause) >= clause_size:
                    clauses.append(' '.join(current_clause))
                    current_clause = []
            
            # Add remaining sentences as final clause
            if current_clause:
                clauses.append(' '.join(current_clause))
        
        # If still no good clauses, return the whole text as one clause
        if not clauses:
            clauses = [text]
        
        # Clean up clauses and filter out very short ones
        final_clauses = []
        for clause in clauses:
            clause = clause.strip()
            if len(clause) > 30:  # Minimum clause length
                final_clauses.append(clause)
        
        return final_clauses if final_clauses else [text]
    
    def get_text_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using the same model as the legal codes."""
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []