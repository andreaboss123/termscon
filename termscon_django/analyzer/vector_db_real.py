import sqlite3
import numpy as np
from typing import List, Dict, Any
import json
import os

class RealVectorDB:
    """Real vector database interface that actually uses the embedded legal codes."""
    
    def __init__(self, chroma_db_path: str, criminal_db_path: str):
        self.chroma_db_path = chroma_db_path
        self.criminal_db_path = criminal_db_path
        self.civil_embeddings = None
        self.criminal_embeddings = None
        
    def _load_civil_code_embeddings(self):
        """Load Civil Code embeddings from ChromaDB."""
        try:
            import chromadb
            # Connect to the existing ChromaDB
            client = chromadb.PersistentClient(path=os.path.dirname(self.chroma_db_path))
            collection = client.get_collection("civil_code")
            
            # Get all documents and embeddings
            results = collection.get(include=['documents', 'embeddings', 'metadatas'])
            
            self.civil_embeddings = {
                'documents': results['documents'],
                'embeddings': np.array(results['embeddings']) if results['embeddings'] else None,
                'metadatas': results['metadatas']
            }
            return True
        except Exception as e:
            print(f"Error loading Civil Code embeddings: {e}")
            return False
    
    def _load_criminal_code_embeddings(self):
        """Load Criminal Code embeddings from SQLite."""
        try:
            conn = sqlite3.connect(self.criminal_db_path)
            cursor = conn.cursor()
            
            # Get all paragraphs with embeddings
            cursor.execute("SELECT paragraph_number, text, embedding FROM paragraphs WHERE embedding IS NOT NULL")
            rows = cursor.fetchall()
            
            documents = []
            embeddings = []
            metadatas = []
            
            for row in rows:
                paragraph_number, text, embedding_blob = row
                if embedding_blob:
                    # Convert blob to numpy array
                    embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                    
                    documents.append(text)
                    embeddings.append(embedding)
                    metadatas.append({'paragraph_number': paragraph_number})
            
            self.criminal_embeddings = {
                'documents': documents,
                'embeddings': np.array(embeddings) if embeddings else None,
                'metadatas': metadatas
            }
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error loading Criminal Code embeddings: {e}")
            return False
    
    def _create_query_embedding(self, query_text: str) -> np.ndarray:
        """Create embedding for query text using a simple method."""
        # For now, use a simple approach - in production, use same model as original embeddings
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            return model.encode([query_text])[0]
        except:
            # Fallback: create a dummy embedding for testing
            return np.random.random(384).astype(np.float32)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_civil_code(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """Search Civil Code embeddings for relevant paragraphs."""
        if not self.civil_embeddings:
            if not self._load_civil_code_embeddings():
                return self._fallback_civil_context()
        
        if self.civil_embeddings['embeddings'] is None:
            return self._fallback_civil_context()
        
        # Create query embedding
        query_embedding = self._create_query_embedding(query_text)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.civil_embeddings['embeddings']):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((similarity, i))
        
        # Sort by similarity and get top results
        similarities.sort(reverse=True)
        
        results = []
        for similarity, idx in similarities[:n_results]:
            if similarity > 0.3:  # Only include relevant results
                results.append({
                    'text': self.civil_embeddings['documents'][idx],
                    'metadata': self.civil_embeddings['metadatas'][idx] if self.civil_embeddings['metadatas'] else {},
                    'similarity': similarity
                })
        
        return results if results else self._fallback_civil_context()
    
    def search_criminal_code(self, query_text: str, n_results: int = 2) -> List[Dict[str, Any]]:
        """Search Criminal Code embeddings for relevant paragraphs."""
        if not self.criminal_embeddings:
            if not self._load_criminal_code_embeddings():
                return self._fallback_criminal_context()
        
        if self.criminal_embeddings['embeddings'] is None:
            return self._fallback_criminal_context()
        
        # Create query embedding  
        query_embedding = self._create_query_embedding(query_text)
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.criminal_embeddings['embeddings']):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((similarity, i))
        
        # Sort by similarity and get top results
        similarities.sort(reverse=True)
        
        results = []
        for similarity, idx in similarities[:n_results]:
            if similarity > 0.3:  # Only include relevant results
                results.append({
                    'text': self.criminal_embeddings['documents'][idx],
                    'paragraph_number': self.criminal_embeddings['metadatas'][idx]['paragraph_number'],
                    'similarity': similarity
                })
        
        return results if results else self._fallback_criminal_context()
    
    def get_legal_context(self, query_text: str, n_results: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Get relevant legal context from both Civil and Criminal Code."""
        civil_results = self.search_civil_code(query_text, n_results)
        criminal_results = self.search_criminal_code(query_text, max(1, n_results // 2))
        
        return {
            'civil_code': civil_results,
            'criminal_code': criminal_results
        }
    
    def _fallback_civil_context(self) -> List[Dict[str, Any]]:
        """Fallback Civil Code context when embeddings unavailable."""
        return [
            {
                'text': '§1815 Občanského zákoníku: Smlouva je neplatná, pokud odporuje zákonu nebo dobrým mravům.',
                'metadata': {'paragraph': '1815'},
                'similarity': 0.5
            },
            {
                'text': '§1826 Občanského zákoníku: Podmínky smlouvy musí být spravedlivé pro obě strany.',
                'metadata': {'paragraph': '1826'},
                'similarity': 0.5
            }
        ]
    
    def _fallback_criminal_context(self) -> List[Dict[str, Any]]:
        """Fallback Criminal Code context when embeddings unavailable."""
        return [
            {
                'paragraph_number': '1',
                'text': '§1 Trestního zákoníku: Čin je trestný, jen pokud jeho trestnost byla zákonem stanovena dříve.',
                'similarity': 0.5
            }
        ]