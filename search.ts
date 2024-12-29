import type { SearchResult } from '../types';
import { supabase } from './supabase';

async function getEmbedding(query: string): Promise<number[]> {
  const processedQuery = query.trim().toLowerCase().replace(/\s+/g, ' ').replace(/[^\w\s]/g, '');
  
  const response = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${import.meta.env.VITE_OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      input: processedQuery,
      model: "text-embedding-3-small",
      dimensions: 1536,
      encoding_format: "float"
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`Failed to generate embedding: ${error.error?.message || 'Unknown error'}`);
  }

  const result = await response.json();
  return result.data[0].embedding;
}

export const searchLawDocuments = async (query: string): Promise<SearchResult[]> => {
  try {
    if (!query.trim()) return [];

    const embedding = await getEmbedding(query);
    let { data: documents, error } = await supabase.rpc('match_documents', {
      query_embedding: embedding,
      match_threshold: 0.6,
      match_count: 10
    });

    if (error) throw error;

    if (!documents?.length) {
      const { data: fallbackDocuments, error: fallbackError } = await supabase.rpc('match_documents', {
        query_embedding: embedding,
        match_threshold: 0.4,
        match_count: 5
      });

      if (fallbackError) throw fallbackError;
      documents = fallbackDocuments || [];
    }

    const results: SearchResult[] = documents.map((doc: any) => {
      const fileUrl = doc.file_url?.startsWith('http') 
        ? doc.file_url 
        : doc.file_url 
          ? `${import.meta.env.VITE_SUPABASE_URL}/storage/v1/object/public/${doc.file_url}`
          : null;

      let matchedSegment = '';
      const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 2);
      const content = doc.content.toLowerCase();
      let bestMatchIndex = -1;
      let bestMatchScore = 0;

      const windowSize = 300;
      for (let i = 0; i < content.length - windowSize; i += 50) {
        const window = content.substring(i, i + windowSize);
        const matchScore = searchTerms.reduce((score, term) => {
          const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const regex = new RegExp(escapedTerm, 'g');
          const matches = window.match(regex);
          return score + (matches ? matches.length : 0);
        }, 0);

        if (matchScore > bestMatchScore) {
          bestMatchScore = matchScore;
          bestMatchIndex = i;
        }
      }

      matchedSegment = bestMatchIndex !== -1 
        ? doc.content.substring(bestMatchIndex, bestMatchIndex + windowSize)
        : doc.content.substring(0, windowSize);

      const highlightedSegment = searchTerms.reduce((text, term) => {
        const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(`(${escapedTerm})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
      }, matchedSegment);

      return {
        document: {
          id: doc.id,
          title: doc.title,
          content: doc.content,
          category: doc.category,
          dateAdded: doc.date_added,
          tags: doc.tags,
          file_path: doc.file_path,
          file_url: fileUrl,
          link_gdrive: doc.link_gdrive,
          metadata: {
            ...doc.metadata,
            file_url: fileUrl,
            link_gdrive: doc.link_gdrive
          }
        },
        relevanceScore: Math.round(doc.similarity * 100),
        matchedSegments: [highlightedSegment + '...']
      };
    });

    return results
      .sort((a, b) => b.relevanceScore - a.relevanceScore)
      .slice(0, 5);
  } catch (error) {
    console.error('Error searching documents:', error);
    throw error;
  }
};
