from typing import List, Dict, Optional, Union
import asyncio
import time
from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.embedder.openai import OpenAIEmbedder

class PutusanAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.supabase = kwargs.get('supabase')
        self.embedder = OpenAIEmbedder(
            model="text-embedding-3-small",
            dimensions=1536,
            api_key=kwargs.get('openai_config', {}).get('api_key')
        )
        self.current_query: Optional[str] = None
        self.court_decisions: List[Dict[str, Union[str, float]]] = []
        self.formatted_decisions: List[str] = []

    async def search_decisions(self, query: str, top_k: int = 5) -> List[Dict[str, Union[str, float]]]:
        try:
            if not query.strip():
                return []

            start_time = time.time()
            
            # Generate embedding asynchronously
            query_embedding = await self.embedder.get_embedding_async(query)
            embedding_time = time.time() - start_time
            
            # First try with higher threshold
            search_start = time.time()
            result = await asyncio.wait_for(
                self.supabase.rpc(
                    'match_documents',
                    {
                        'query_embedding': query_embedding,
                        'match_count': top_k,
                        'match_threshold': 0.6
                    }
                ).execute(),
                timeout=10.0
            )
            
            # If no results, try with lower threshold
            if not result.data:
                result = await asyncio.wait_for(
                    self.supabase.rpc(
                        'match_documents',
                        {
                            'query_embedding': query_embedding,
                            'match_count': top_k,
                            'match_threshold': 0.4
                        }
                    ).execute(),
                    timeout=10.0
                )
            
            search_time = time.time() - search_start
            
            # Process and format results
            processed_results = []
            for doc in result.data:
                # Find best matching segment
                search_terms = [term for term in query.lower().split() if len(term) > 2]
                content = doc.get('content', '').lower()
                best_match = ''
                best_score = 0
                
                window_size = 300
                for i in range(0, len(content) - window_size, 50):
                    window = content[i:i + window_size]
                    score = sum(window.count(term) for term in search_terms)
                    if score > best_score:
                        best_score = score
                        best_match = doc.get('content', '')[i:i + window_size]
                
                # Highlight matching terms
                if best_match:
                    for term in search_terms:
                        best_match = best_match.replace(
                            term,
                            f'**{term}**'
                        )
                
                processed_results.append({
                    'id': doc.get('id'),
                    'title': doc.get('title'),
                    'content': doc.get('content'),
                    'category': doc.get('category'),
                    'date_added': doc.get('date_added'),
                    'tags': doc.get('tags'),
                    'file_path': doc.get('file_path'),
                    'file_url': doc.get('file_url'),
                    'link_gdrive': doc.get('link_gdrive'),
                    'metadata': {
                        **doc.get('metadata', {}),
                        'file_url': doc.get('file_url'),
                        'link_gdrive': doc.get('link_gdrive')
                    },
                    'relevance_score': round(doc.get('similarity', 0) * 100),
                    'matched_segment': best_match + '...' if best_match else ''
                })
            
            # Sort by relevance and limit results
            self.court_decisions = sorted(
                processed_results,
                key=lambda x: x['relevance_score'],
                reverse=True
            )[:top_k]
            
            format_start = time.time()
            self.format_results(self.court_decisions)
            format_time = time.time() - format_start
            
            # Log performance metrics
            total_time = time.time() - start_time
            print(f"Search performance: "
                  f"Embedding: {embedding_time:.2f}s, "
                  f"Search: {search_time:.2f}s, "
                  f"Format: {format_time:.2f}s, "
                  f"Total: {total_time:.2f}s")
            
            return self.court_decisions

        except asyncio.TimeoutError:
            print("Search operation timed out after 10 seconds")
            return []
        except Exception as e:
            print(f"Error in decision search: {e}")
            return []

    def format_results(self, results: List[Dict]) -> None:
        template = """**Metadata Putusan Pengadilan**
* **Nomor Putusan:** {nomor_putusan}
* **Tanggal Putusan:** {tanggal_putusan}
* **Pasal Disangkakan:** {pasal_disangkakan}
* **Hukuman Penjara:** {hukuman_penjara}
* **Hukuman Denda:** {hukuman_denda}
* **Google Drive Link:** {link_gdrive}"""
        
        self.formatted_decisions = [
            template.format(
                nomor_putusan=doc.get('metadata', {}).get('nomor_putusan', 'N/A'),
                tanggal_putusan=doc.get('metadata', {}).get('tanggal_putusan', 'N/A'),
                pasal_disangkakan=doc.get('metadata', {}).get('pasal_disangkakan', 'N/A'),
                hukuman_penjara=doc.get('metadata', {}).get('hukuman_penjara', 'N/A'),
                hukuman_denda=doc.get('metadata', {}).get('hukuman_denda', 'N/A'),
                link_gdrive=doc.get('metadata', {}).get('link_gdrive', 'N/A')
            )
            for doc in results
        ]

    def get_formatted_decisions(self) -> str:
        return "\n\n".join(self.formatted_decisions) if self.formatted_decisions else ""
