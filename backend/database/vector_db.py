import sqlite3
import chromadb
import numpy as np
from typing import List, Dict, Any
import pickle
import os

class VectorDatabase:
    def __init__(self, chroma_db_path: str, criminal_db_path: str):
        self.chroma_db_path = chroma_db_path
        self.criminal_db_path = criminal_db_path
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(path=os.path.dirname(chroma_db_path))
        
    def search_civil_code(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the Civil Code using vector similarity."""
        try:
            collection = self.chroma_client.get_collection("civil_code")
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'text': doc,
                        'distance': results['distances'][0][i] if results['distances'] else None,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else None
                    }
                    formatted_results.append(result)
            
            return formatted_results
        except Exception as e:
            print(f"Error searching civil code: {e}")
            return []
    
    def search_criminal_code(self, query_embedding: List[float], n_results: int = 5) -> List[Dict[str, Any]]:
        """Search the Criminal Code using vector similarity."""
        try:
            conn = sqlite3.connect(self.criminal_db_path)
            cursor = conn.cursor()
            
            # Get all embeddings
            cursor.execute("SELECT paragraf_id, embedding FROM embeddings")
            embeddings_data = cursor.fetchall()
            
            if not embeddings_data:
                return []
            
            # Calculate cosine similarity
            query_vector = np.array(query_embedding)
            similarities = []
            
            for paragraf_id, embedding_blob in embeddings_data:
                try:
                    embedding_vector = np.frombuffer(embedding_blob, dtype=np.float32)
                    similarity = np.dot(query_vector, embedding_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(embedding_vector)
                    )
                    similarities.append((paragraf_id, similarity))
                except Exception as e:
                    continue
            
            # Sort by similarity and get top results
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:n_results]
            
            # Get the text for top results
            results = []
            for paragraf_id, similarity in top_results:
                cursor.execute("SELECT cislo, text FROM paragrafy WHERE id = ?", (paragraf_id,))
                row = cursor.fetchone()
                if row:
                    results.append({
                        'paragraph_number': row[0],
                        'text': row[1],
                        'similarity': similarity
                    })
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"Error searching criminal code: {e}")
            return []
    
    def get_legal_context(self, query_embedding: List[float], n_results: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """Get relevant legal context from both Civil and Criminal Code."""
        civil_results = self.search_civil_code(query_embedding, n_results)
        criminal_results = self.search_criminal_code(query_embedding, n_results)
        
        return {
            'civil_code': civil_results,
            'criminal_code': criminal_results
        }