import re
from typing import List

class SimpleTextProcessor:
    def __init__(self):
        pass
    
    def segment_terms_conditions(self, text: str) -> List[str]:
        """Segment T&C text into individual clauses."""
        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        clauses = []
        
        # Try specific patterns first for numbered lists
        specific_patterns = [
            r'(?<=\.)\s*(?=\d+\.)',  # Split numbered items like "1. Text 2. Text"
            r'(?<=\.)\s*(?=\(\d+\))',  # Split numbered items like "(1) Text (2) Text"
        ]
        
        for pattern in specific_patterns:
            if re.search(pattern, text):
                splits = re.split(pattern, text)
                substantial_splits = [s.strip() for s in splits if len(s.strip()) > 20]
                if len(substantial_splits) > 1:
                    clauses = substantial_splits
                    break
        
        # If no good splits found, try general patterns
        if not clauses:
            patterns = [
                r'(?=\n\s*\d+\.)',  # Lookahead for 1. 2. 3. etc.
                r'(?=\n\s*\(\d+\))',  # Lookahead for (1) (2) (3) etc.
                r'(?=\n\s*[a-z]\))',  # Lookahead for a) b) c) etc.
                r'(?=\n\s*[A-Z]\.)',  # Lookahead for A. B. C. etc.
                r'\n\s*-\s*',  # bullet points
                r'\n\s*•\s*',  # bullet points
                r'\n\n+'  # double line breaks
            ]
            
            for pattern in patterns:
                if re.search(pattern, text):
                    splits = re.split(pattern, text)
                    substantial_splits = [s.strip() for s in splits if len(s.strip()) > 20]
                    if len(substantial_splits) > 1:
                        clauses = substantial_splits
                        break
        
        # If no good splits found, try sentence-based splitting for long text
        if not clauses and len(text) > 500:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            clause_size = max(3, len(sentences) // 10)
            clauses = []
            current_clause = []
            
            for sentence in sentences:
                current_clause.append(sentence)
                if len(current_clause) >= clause_size:
                    clauses.append(' '.join(current_clause))
                    current_clause = []
            
            if current_clause:
                clauses.append(' '.join(current_clause))
        
        # If still no clauses, return whole text
        if not clauses:
            clauses = [text]
        
        final_clauses = []
        for clause in clauses:
            clause = clause.strip()
            if len(clause) > 30:
                final_clauses.append(clause)
        
        return final_clauses if final_clauses else [text]
    
    def get_text_embedding_mock(self, text: str) -> List[float]:
        """Mock embedding function - returns dummy embedding."""
        # Simple hash-based mock embedding
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to 1536 float values between -1 and 1
        embedding = []
        for i in range(0, min(len(hash_hex), 32), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0 * 2 - 1
            embedding.extend([val] * 48)  # Expand to reach 1536
        
        # Pad or truncate to exactly 1536
        while len(embedding) < 1536:
            embedding.append(0.0)
        
        return embedding[:1536]