"""
Enhanced RAG (Retrieval-Augmented Generation) System
Uses LangChain + Gemini API + ChromaDB for intelligent question answering
"""

import os
from typing import List, Optional
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import PyPDF2
from config import settings

# Replacement for LangChain's text splitter to avoid dependency issues
class RecursiveCharacterTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200, length_function=len, separators=None):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function
        self.separators = separators or ["\n\n", "\n", " ", ""]

    def split_text(self, text):
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            
            # Try to break at a space to maintain word integrity
            if end < text_len:
                 # Look back for a space in the last 20% of the chunk
                 lookback = int(self.chunk_size * 0.2)
                 last_space = text.rfind(' ', max(start, end - lookback), end)
                 if last_space != -1:
                     end = last_space
            
            chunk = text[start:end]
            if chunk:
                chunks.append(chunk)
            else:
                break # Avoid empty chunks loop
                
            # Move forward with overlap
            # If we didn't advance (e.g. huge word), simply force advance to avoid loop
            if end == start:
                start += 1
            else:
                next_start = end - self.chunk_overlap
                start = max(start + 1, next_start) # Ensure we always move forward
                
        return chunks


class RAGSystem:
    """
    RAG System for intelligent chatbot responses
    
    Workflow:
    1. Document Upload: Teacher uploads PDF/TXT
    2. Chunking: Split into 512-token chunks with overlap
    3. Embedding: Generate vector embeddings
    4. Storage: Store in ChromaDB collection
    5. Query: Student asks question
    6. Retrieval: Find top-k relevant chunks
    7. Generation: Gemini generates answer with context
    """
    
    def __init__(self):
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=512,
            chunk_overlap=50,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    
    def load_document(self, file_path: str) -> str:
        """
        Load document content from PDF or TXT file
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content
        """
        if file_path.endswith('.pdf'):
            return self._load_pdf(file_path)
        elif file_path.endswith('.txt'):
            return self._load_txt(file_path)
        else:
            raise ValueError("Unsupported file type. Only PDF and TXT are supported.")
    
    
    def _load_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    
    def _load_txt(self, file_path: str) -> str:
        """Load text from TXT file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    
    def chunk_document(self, text: str) -> List[str]:
        """
        Split document into chunks
        
        Args:
            text: Full document text
            
        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        return chunks
    
    
    def embed_chunks(self, chunks: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of embedding vectors
        """
        embeddings = self.embedding_model.encode(chunks, show_progress_bar=False)
        return embeddings.tolist()
    
    
    def store_in_chromadb(
        self,
        collection_name: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Optional[List[dict]] = None
    ):
        """
        Store chunks and embeddings in ChromaDB
        
        Args:
            collection_name: Name of the ChromaDB collection
            chunks: Text chunks
            embeddings: Embedding vectors
            metadata: Optional metadata for each chunk
        """
        # Get or create collection
        try:
            collection = self.chroma_client.get_collection(collection_name)
        except:
            collection = self.chroma_client.create_collection(collection_name)
        
        # Generate IDs for chunks
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Add documents to collection
        # Ensure metadata is valid
        metadatas = metadata or [{"source": "unknown"} for _ in chunks]
        
        collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        return len(chunks)
    
    
    def process_and_store_document(
        self,
        file_path: str,
        collection_name: str
    ) -> int:
        """
        Complete pipeline: Load → Chunk → Embed → Store
        
        Args:
            file_path: Path to document file
            collection_name: ChromaDB collection name
            
        Returns:
            Number of chunks stored
        """
        # Load document
        text = self.load_document(file_path)
        
        # Chunk document
        chunks = self.chunk_document(text)
        
        # Generate embeddings
        embeddings = self.embed_chunks(chunks)
        
        # Store in ChromaDB
        chunk_count = self.store_in_chromadb(collection_name, chunks, embeddings)
        
        return chunk_count
    
    
    def retrieve_relevant_chunks(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[dict]:
        """
        Retrieve most relevant chunks for a query
        
        Args:
            collection_name: ChromaDB collection to search
            query: User's question
            top_k: Number of chunks to retrieve
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            collection = self.chroma_client.get_collection(collection_name)
        except:
            return []
        
        # Embed the query
        query_embedding = self.embedding_model.encode([query])[0].tolist()
        
        # Query the collection
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        chunks = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i] if results['distances'] else None
                chunks.append({
                    "content": doc,
                    "id": results['ids'][0][i] if results['ids'] else None,
                    "distance": distance,
                    "relevance_score": 1 - distance if distance is not None else 0  # Convert distance to similarity
                })
        
        return chunks
    
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[dict],
        system_prompt: Optional[str] = None,
        llm_provider: str = "gemini",
        llm_model: str = None
    ) -> str:
        """
        Generate answer using LLM with retrieved context
        
        Args:
            question: Student's question
            context_chunks: Retrieved relevant chunks
            system_prompt: Optional custom system prompt
            llm_provider: 'gemini' or 'mistral'
            llm_model: Specific model name
            
        Returns:
            Generated answer
        """
        
        # Check if we have any relevant context
        # Filter out chunks with low relevance (distance > 1.2 means less similar)
        RELEVANCE_THRESHOLD = 1.2  # Lower distance = more relevant
        relevant_chunks = [chunk for chunk in context_chunks if chunk.get("distance", 2) < RELEVANCE_THRESHOLD]
        
        # If no relevant chunks found, decline to answer
        if not relevant_chunks:
            return """I'm sorry, but I can only answer questions related to the course materials that have been uploaded.

**Your question doesn't seem to match any content in the current course documents.**

Please try:
- Asking a question related to the topics covered in this course
- Rephrasing your question using terms from the course materials
- Checking if the correct course is selected

If you believe this topic should be covered, please contact your teacher to upload relevant materials."""
        
        # Build context from relevant chunks only
        context = "\n\n".join([chunk["content"] for chunk in relevant_chunks])
        
        # Strict RAG-only prompt - NEVER use general knowledge
        default_prompt = """You are a helpful AI tutor. Answer the student's question based STRICTLY on the provided course materials.

**CRITICAL RULES:**
- Use ONLY information from the provided context below
- NEVER use your general knowledge or training data
- If the answer is not clearly stated in the context, say "This information is not covered in the course materials"
- Do not make assumptions or inferences beyond what's explicitly in the context
- Be clear, concise, and educational
- Use examples from the course materials when helpful

**FORMATTING RULES:**
- Use proper markdown formatting (headers with ##, bold with **, lists with -)
- For mathematical expressions, use LaTeX with proper delimiters:
  - Inline math: wrap with single dollar signs like $\\frac{a}{b}$ or $\\sqrt{2}$ or $\\pi$
  - Block math: wrap with double dollar signs like $$\\frac{a^2 + b^2}{c}$$
- Always use these delimiters for fractions, square roots, Greek letters, and equations"""

        prompt = system_prompt or default_prompt
        
        # Build the full prompt
        full_prompt = f"""{prompt}

**Context from course materials:**
{context}

**Student's question:**
{question}

**Answer (based ONLY on the above context):**"""
        
        try:
            # Use the multi-LLM provider system
            from ai_services.llm_providers import get_llm_provider
            
            provider = get_llm_provider(llm_provider, llm_model)
            response = provider.generate(full_prompt)
            
            return response
        except Exception as e:
            return f"❌ Error generating response: {str(e)}"
    
    
    def query(
        self,
        collection_name: str,
        question: str,
        system_prompt: Optional[str] = None,
        top_k: int = 5,
        llm_provider: str = "gemini",
        llm_model: str = None
    ) -> dict:
        """
        Complete RAG query: Retrieve → Generate
        
        Args:
            collection_name: ChromaDB collection to query
            question: Student's question
            system_prompt: Optional custom system prompt
            top_k: Number of chunks to retrieve
            llm_provider: 'gemini' or 'mistral'
            llm_model: Specific model name
            
        Returns:
            Dict with answer and metadata
        """
        # Retrieve relevant chunks
        chunks = self.retrieve_relevant_chunks(collection_name, question, top_k)
        
        # Generate answer using specified LLM (will handle empty/irrelevant chunks internally)
        answer = self.generate_answer(question, chunks, system_prompt, llm_provider, llm_model)
        
        # Check if any chunks were actually relevant (distance < threshold)
        RELEVANCE_THRESHOLD = 1.2
        relevant_chunks = [c for c in chunks if c.get("distance", 2) < RELEVANCE_THRESHOLD]
        
        return {
            "answer": answer,
            "sources": [chunk["content"][:100] + "..." for chunk in relevant_chunks[:3]],
            "context_used": len(relevant_chunks) > 0,
            "chunks_retrieved": len(relevant_chunks),
            "llm_provider": llm_provider,
            "llm_model": llm_model
        }


# Singleton instance
_rag_instance = None

def get_rag_system() -> RAGSystem:
    """Get or create RAG system singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance
