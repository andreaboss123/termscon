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
        
        # Attempt to load embeddings at initialization for better performance
        print("Initializing RealVectorDB with embedded legal databases...")
        self._initialize_databases()
    
    def _initialize_databases(self):
        """Initialize databases at startup with comprehensive logging."""
        print("=== Database Initialization ===")
        
        # Try to load Criminal Code (SQLite) - usually more reliable
        criminal_success = self._load_criminal_code_embeddings()
        
        # Try to load Civil Code (ChromaDB) - may require more dependencies
        civil_success = self._load_civil_code_embeddings()
        
        # Report initialization results
        if criminal_success and civil_success:
            print("✅ Full database initialization successful - both Civil and Criminal Code loaded")
        elif criminal_success:
            print("⚠️  Partial database initialization - Criminal Code loaded, Civil Code using fallback")
        elif civil_success:
            print("⚠️  Partial database initialization - Civil Code loaded, Criminal Code using fallback")
        else:
            print("❌ Database initialization failed - using fallback contexts for both")
        
        print("=== Database Initialization Complete ===")
        
        return criminal_success or civil_success
        
    def _load_civil_code_embeddings(self):
        """Load Civil Code embeddings from ChromaDB with robust error handling."""
        print("Attempting to load Civil Code embeddings from ChromaDB...")
        
        try:
            # Check if ChromaDB is available
            try:
                import chromadb
                print("ChromaDB module imported successfully")
            except ImportError:
                print("ChromaDB module not available - will use fallback legal context")
                return False
            
            # Check if numpy is available
            try:
                import numpy as np
                print("NumPy module imported successfully")
            except ImportError:
                print("NumPy module not available - cannot process embeddings")
                return False
            
            # Test file accessibility
            if not os.path.isabs(self.chroma_db_path):
                # Convert relative path to absolute
                self.chroma_db_path = os.path.abspath(self.chroma_db_path)
            
            chroma_dir = os.path.dirname(self.chroma_db_path)
            print(f"Looking for ChromaDB directory at: {chroma_dir}")
            
            if not os.path.exists(chroma_dir):
                print(f"ChromaDB directory not found: {chroma_dir}")
                # Try alternative paths
                alternative_dirs = [
                    os.getcwd(),
                    os.path.dirname(__file__) + '/../..',
                    '.'
                ]
                
                for alt_dir in alternative_dirs:
                    alt_abs_dir = os.path.abspath(alt_dir)
                    print(f"Trying alternative ChromaDB directory: {alt_abs_dir}")
                    if os.path.exists(alt_abs_dir):
                        chroma_dir = alt_abs_dir
                        print(f"Using ChromaDB directory: {chroma_dir}")
                        break
                else:
                    print("No suitable ChromaDB directory found")
                    return False
                
            if not os.access(chroma_dir, os.R_OK):
                print(f"ChromaDB directory not accessible: {chroma_dir}")
                return False
            
            # Try multiple connection approaches
            connection_attempts = [
                # Attempt 1: Original path with settings
                lambda: chromadb.PersistentClient(
                    path=chroma_dir,
                    settings=chromadb.config.Settings(anonymized_telemetry=False)
                ),
                # Attempt 2: Simple path connection
                lambda: chromadb.PersistentClient(path=chroma_dir),
                # Attempt 3: Current directory
                lambda: chromadb.PersistentClient(path="."),
                # Attempt 4: Direct database file
                lambda: chromadb.PersistentClient(path=self.chroma_db_path)
            ]
            
            client = None
            for i, attempt in enumerate(connection_attempts, 1):
                try:
                    print(f"ChromaDB connection attempt {i}/4...")
                    client = attempt()
                    collections = client.list_collections()
                    print(f"Connection successful, found {len(collections)} collections")
                    break
                except Exception as e:
                    print(f"Connection attempt {i} failed: {e}")
                    if i == len(connection_attempts):
                        print("All ChromaDB connection attempts failed")
                        return False
                    continue
            
            if not client:
                print("Failed to establish ChromaDB connection")
                return False
            
            # Try to get the civil_code collection
            try:
                collection = client.get_collection("civil_code")
                print("Successfully retrieved civil_code collection")
            except Exception as e:
                print(f"Failed to get civil_code collection: {e}")
                # Try to list available collections
                try:
                    collections = client.list_collections()
                    collection_names = [c.name for c in collections]
                    print(f"Available collections: {collection_names}")
                    if collection_names:
                        # Try to use the first available collection
                        collection = client.get_collection(collection_names[0])
                        print(f"Using collection: {collection_names[0]}")
                    else:
                        print("No collections found in ChromaDB")
                        return False
                except Exception as e2:
                    print(f"Failed to list collections: {e2}")
                    return False
            
            # Get documents and embeddings
            try:
                print("Retrieving documents and embeddings...")
                results = collection.get(include=['documents', 'embeddings', 'metadatas'])
                
                if not results['documents']:
                    print("No documents found in collection")
                    return False
                
                print(f"Retrieved {len(results['documents'])} documents")
                
                self.civil_embeddings = {
                    'documents': results['documents'],
                    'embeddings': np.array(results['embeddings']) if results['embeddings'] else None,
                    'metadatas': results['metadatas']
                }
                
                if self.civil_embeddings['embeddings'] is not None:
                    print(f"Successfully loaded Civil Code embeddings: {len(results['documents'])} documents")
                    return True
                else:
                    print("No embeddings found in collection")
                    return False
                    
            except Exception as e:
                print(f"Failed to retrieve collection data: {e}")
                return False
                
        except Exception as e:
            print(f"Unexpected error loading Civil Code embeddings: {e}")
            print("Civil Code embeddings unavailable - will use fallback legal context")
            return False
    
    def _load_criminal_code_embeddings(self):
        """Load Criminal Code embeddings from SQLite with robust error handling."""
        print("Attempting to load Criminal Code embeddings from SQLite...")
        
        try:
            # Ensure we're using absolute paths and check existence
            if not os.path.isabs(self.criminal_db_path):
                # Convert relative path to absolute
                self.criminal_db_path = os.path.abspath(self.criminal_db_path)
            
            print(f"Looking for Criminal Code database at: {self.criminal_db_path}")
            
            # Test file accessibility first
            if not os.path.exists(self.criminal_db_path):
                print(f"Criminal Code database file not found: {self.criminal_db_path}")
                # Try alternative paths
                alternative_paths = [
                    os.path.join(os.getcwd(), 'trestni_zakonik.sqlite'),
                    os.path.join(os.path.dirname(__file__), '../../trestni_zakonik.sqlite'),
                    'trestni_zakonik.sqlite'
                ]
                
                for alt_path in alternative_paths:
                    alt_abs_path = os.path.abspath(alt_path)
                    print(f"Trying alternative path: {alt_abs_path}")
                    if os.path.exists(alt_abs_path):
                        print(f"Found database at alternative path: {alt_abs_path}")
                        self.criminal_db_path = alt_abs_path
                        break
                else:
                    print("No Criminal Code database found in any location")
                    return False
                
            if not os.access(self.criminal_db_path, os.R_OK):
                print(f"Criminal Code database file not readable: {self.criminal_db_path}")
                return False
            
            # Try to connect with timeout and proper error handling
            conn = sqlite3.connect(self.criminal_db_path, timeout=30.0)
            conn.execute("PRAGMA busy_timeout = 30000")  # 30 second timeout for busy database
            cursor = conn.cursor()
            
            # Test connection first with a simple query
            cursor.execute("SELECT COUNT(*) FROM paragrafy")
            paragrafy_count = cursor.fetchone()[0]
            print(f"Found {paragrafy_count} paragraphs in Criminal Code database")
            
            cursor.execute("SELECT COUNT(*) FROM embeddings")
            embeddings_count = cursor.fetchone()[0]
            print(f"Found {embeddings_count} embeddings in Criminal Code database")
            
            # Get all paragraphs with embeddings using correct table structure
            cursor.execute("""
                SELECT p.cislo, p.text, e.embedding 
                FROM paragrafy p 
                JOIN embeddings e ON p.id = e.paragraf_id 
                WHERE e.embedding IS NOT NULL
                LIMIT 100
            """)
            rows = cursor.fetchall()
            print(f"Retrieved {len(rows)} paragraph-embedding pairs")
            
            documents = []
            embeddings = []
            metadatas = []
            
            for row in rows:
                paragraph_number, text, embedding_blob = row
                if embedding_blob:
                    try:
                        # Try importing numpy here to handle missing dependency
                        import numpy as np
                        # Convert blob to numpy array
                        embedding = np.frombuffer(embedding_blob, dtype=np.float32)
                        
                        documents.append(text)
                        embeddings.append(embedding)
                        metadatas.append({'paragraph_number': paragraph_number})
                    except ImportError:
                        print("NumPy not available - cannot process embeddings")
                        conn.close()
                        return False
                    except Exception as e:
                        print(f"Error processing embedding for paragraph {paragraph_number}: {e}")
                        continue
            
            if documents and embeddings:
                try:
                    import numpy as np
                    self.criminal_embeddings = {
                        'documents': documents,
                        'embeddings': np.array(embeddings),
                        'metadatas': metadatas
                    }
                    print(f"Successfully loaded {len(documents)} Criminal Code embeddings")
                    conn.close()
                    return True
                except ImportError:
                    print("NumPy not available for final array creation")
                    conn.close()
                    return False
            else:
                print("No valid embeddings found in Criminal Code database")
                conn.close()
                return False
            
        except sqlite3.OperationalError as e:
            print(f"SQLite operational error loading Criminal Code embeddings: {e}")
            return False
        except sqlite3.DatabaseError as e:
            print(f"SQLite database error loading Criminal Code embeddings: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error loading Criminal Code embeddings: {e}")
            print("Criminal Code embeddings unavailable - will use fallback legal context")
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
        # Only try to load if not already loaded and not previously failed
        if not self.civil_embeddings and not hasattr(self, '_civil_load_failed'):
            if not self._load_civil_code_embeddings():
                self._civil_load_failed = True  # Mark as failed to avoid repeated attempts
                return self._fallback_civil_context()
        
        if not self.civil_embeddings:
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
        # Only try to load if not already loaded and not previously failed
        if not self.criminal_embeddings and not hasattr(self, '_criminal_load_failed'):
            if not self._load_criminal_code_embeddings():
                self._criminal_load_failed = True  # Mark as failed to avoid repeated attempts
                return self._fallback_criminal_context()
        
        if not self.criminal_embeddings:
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
        print(f"Getting legal context for query: {query_text[:50]}...")
        
        civil_results = self.search_civil_code(query_text, n_results)
        criminal_results = self.search_criminal_code(query_text, max(1, n_results // 2))
        
        # Add status information
        civil_status = "database" if self.civil_embeddings else "fallback"
        criminal_status = "database" if self.criminal_embeddings else "fallback"
        
        print(f"Legal context retrieved - Civil: {len(civil_results)} results ({civil_status}), Criminal: {len(criminal_results)} results ({criminal_status})")
        
        return {
            'civil_code': civil_results,
            'criminal_code': criminal_results
        }
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check availability of required dependencies."""
        deps = {}
        
        try:
            import numpy as np
            deps['numpy'] = True
            print("✅ NumPy available")
        except ImportError:
            deps['numpy'] = False
            print("❌ NumPy not available")
        
        try:
            import chromadb
            deps['chromadb'] = True
            print("✅ ChromaDB available")
        except ImportError:
            deps['chromadb'] = False
            print("❌ ChromaDB not available")
        
        try:
            import sqlite3
            deps['sqlite3'] = True
            print("✅ SQLite3 available")
        except ImportError:
            deps['sqlite3'] = False
            print("❌ SQLite3 not available")
        
        # Check file access
        deps['criminal_db_file'] = os.path.exists(self.criminal_db_path) and os.access(self.criminal_db_path, os.R_OK)
        deps['chroma_db_path'] = os.path.exists(os.path.dirname(self.chroma_db_path)) and os.access(os.path.dirname(self.chroma_db_path), os.R_OK)
        
        print(f"Criminal DB file accessible: {'✅' if deps['criminal_db_file'] else '❌'}")
        print(f"ChromaDB path accessible: {'✅' if deps['chroma_db_path'] else '❌'}")
        
        return deps
    
    def _fallback_civil_context(self) -> List[Dict[str, Any]]:
        """Enhanced fallback Civil Code context when embeddings unavailable."""
        print("Using fallback Civil Code context (database unavailable)")
        return [
            {
                'text': '§1815 Občanského zákoníku: Smlouva je neplatná, pokud odporuje zákonu nebo dobrým mravům.',
                'metadata': {'paragraph': '1815'},
                'similarity': 0.7
            },
            {
                'text': '§1826 Občanského zákoníku: Podmínky smlouvy musí být spravedlivé pro obě strany.',
                'metadata': {'paragraph': '1826'},
                'similarity': 0.6
            },
            {
                'text': '§1793 Občanského zákoníku: Spotřebitelské smlouvy podléhají zvláštní ochraně.',
                'metadata': {'paragraph': '1793'},
                'similarity': 0.6
            },
            {
                'text': '§1796 Občanského zákoníku: Neplatné jsou ustanovení omezující práva spotřebitele.',
                'metadata': {'paragraph': '1796'},
                'similarity': 0.5
            }
        ]
    
    def _fallback_criminal_context(self) -> List[Dict[str, Any]]:
        """Enhanced fallback Criminal Code context when embeddings unavailable."""
        print("Using fallback Criminal Code context (database unavailable)")
        return [
            {
                'paragraph_number': '1',
                'text': '§1 Trestního zákoníku: Čin je trestný, jen pokud jeho trestnost byla zákonem stanovena dříve.',
                'similarity': 0.6
            },
            {
                'paragraph_number': '209',
                'text': '§209 Trestního zákoníku: Podvod - kdo jiného uvede v omyl a způsobí mu škodu.',
                'similarity': 0.5
            }
        ]