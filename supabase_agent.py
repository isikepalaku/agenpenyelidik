import os
import typer
from typing import Optional
from rich.prompt import Prompt
from supabase import create_client, Client
from phi.agent import Agent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SUPABASE_URL = os.getenv("VITE_SUPABASE_URL")
SUPABASE_KEY = os.getenv("VITE_SUPABASE_ANON_KEY")
OPENAI_API_KEY = os.getenv("VITE_OPENAI_API_KEY")

if not SUPABASE_URL:
    raise ValueError("VITE_SUPABASE_URL environment variable is required. Please check your .env file")
if not SUPABASE_KEY:
    raise ValueError("VITE_SUPABASE_ANON_KEY environment variable is required. Please check your .env file")
if not OPENAI_API_KEY:
    raise ValueError("VITE_OPENAI_API_KEY environment variable is required. Please check your .env file")

# Initialize OpenAI
import openai
openai.api_key = OPENAI_API_KEY

print("Environment variables loaded successfully")

class SupabaseSearch:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def search(self, query: str, top_k: int = 2) -> list[dict]:
        """Search documents using Supabase vector search"""
        try:
            # Perform vector search
            result = self.supabase.rpc('match_documents', {
                'query_embedding': self.get_embedding(query),
                'match_threshold': 0.6,
                'match_count': top_k
            }).execute()
            
            if not result.data:
                # Try with lower threshold if no results
                result = self.supabase.rpc('match_documents', {
                    'query_embedding': self.get_embedding(query),
                    'match_threshold': 0.4,
                    'match_count': top_k
                }).execute()
            
            return self.process_results(result.data)
        
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []

    def get_embedding(self, query: str) -> list[float]:
        """Generate embedding using OpenAIEmbedder
        
        Uses OpenAI's text embedding models to convert text into vector representations.
        Default model is 'text-embedding-3-small' with 1536 dimensions.
        
        Parameters:
            query (str): The text to embed
            
        Returns:
            list[float]: The embedding vector
            
        Example:
            embedder = OpenAIEmbedder(model="text-embedding-3-small", dimensions=1536)
            embedding = embedder.get_embedding("Sample text")
            
        Note:
            Requires OpenAI API key. Get your key from https://platform.openai.com/api-keys
        """
        from phi.embedder.openai import OpenAIEmbedder
        
        processed_query = query.strip().lower().replace('\s+', ' ').replace('[^\w\s]', '')
        embedder = OpenAIEmbedder(model="text-embedding-3-small", dimensions=1536)
        return embedder.get_embedding(processed_query)

    def process_results(self, documents: list[dict]) -> list[dict]:
        """Process and format search results"""
        results = []
        for doc in documents:
            metadata = doc.get('metadata', {})
            results.append({
                'nomor_putusan': metadata.get('nomor_putusan'),
                'tanggal_putusan': metadata.get('tanggal_putusan'),
                'pasal_disangkakan': metadata.get('pasal_disangkakan'),
                'hukuman_penjara': metadata.get('hukuman_penjara'),
                'hukuman_denda': metadata.get('hukuman_denda'),
                'link_gdrive': metadata.get('link_gdrive'),
                'similarity': round(doc['similarity'] * 100)
            })
        return results

def supabase_agent(user: str = "user"):
    """Main agent function"""
    run_id: Optional[str] = None
    
    # Initialize search
    search = SupabaseSearch()
    
    # Create agent
    agent = Agent(
        run_id=run_id,
        user_id=user,
        show_tool_calls=True,
        debug_mode=True,
    )

    if run_id is None:
        run_id = agent.run_id
        print(f"Started Run: {run_id}\n")
    else:
        print(f"Continuing Run: {run_id}\n")

    while True:
        message = Prompt.ask(f"[bold] :sunglasses: {user} [/bold]")
        if message in ("exit", "bye"):
            break
        
        # Perform search and display results
        results = search.search(message)
        for result in results:
            print(f"\nNomor Putusan: {result['nomor_putusan']}")
            print(f"Tanggal Putusan: {result['tanggal_putusan']}")
            print(f"Pasal Disangkakan: {result['pasal_disangkakan']}")
            print(f"Hukuman Penjara: {result['hukuman_penjara']}")
            print(f"Hukuman Denda: {result['hukuman_denda']}")
            print(f"Google Drive Link: {result['link_gdrive']}")
            print(f"Relevance: {result['similarity']}%\n")

if __name__ == "__main__":
    typer.run(supabase_agent)
