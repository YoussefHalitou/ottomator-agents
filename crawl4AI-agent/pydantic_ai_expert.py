from __future__ import annotations as _annotations

from dataclasses import dataclass
from dotenv import load_dotenv
import logfire
import asyncio
import httpx
import os

from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIModel
from openai import AsyncOpenAI
from supabase import Client
from typing import List

load_dotenv()

llm = os.getenv('LLM_MODEL', 'gpt-4o-mini')
model = OpenAIModel(llm)

logfire.configure(send_to_logfire='if-token-present')

@dataclass
class ClinicAIDeps:
    supabase: Client
    openai_client: AsyncOpenAI

system_prompt = """
You are an expert consultant for Haut Labor Oldenburg, a premium aesthetic medicine clinic in Germany led by Dr. Larisa Pfahl.

Your role is to provide detailed information about the clinic's treatments, procedures, and services based on the comprehensive website content that has been crawled and indexed.

You have access to information about:
- Dr. Larisa Pfahl (Gynecologist specialized in minimally invasive aesthetic treatments)
- Over 30 different aesthetic treatments including:
  * Botox/Faltenrelaxan treatments
  * Dermal fillers (Hyaluron-Filler)
  * Laser treatments (CO2 Laser, LaseMD, Lumecca)
  * Radiofrequency treatments (Morpheus8, Ultherapy)
  * Body contouring (Sculptra, Radiesse, Lipolyse)
  * Skin treatments (HydraFacial, Skinbooster, Vampirlifting)
  * Hair removal and PRP therapy
  * Specialized treatments for men
  * Aesthetic gynecology

When users ask questions, always use the RAG tool first to find relevant information from the clinic's website content.
Provide detailed, accurate information about treatments, procedures, expected results, and aftercare.
Maintain a professional, knowledgeable tone while being helpful and informative.

If you cannot find specific information in the crawled content, be honest about it and suggest contacting the clinic directly at +49 (0) 157 834 488 90 or info@haut-labor.de.

Don't ask the user before taking an action, just search for the information they need.
"""

clinic_ai_expert = Agent(
    model,
    system_prompt=system_prompt,
    deps_type=ClinicAIDeps,
    retries=2
)

async def get_embedding(text: str, openai_client: AsyncOpenAI) -> List[float]:
    """Get embedding vector from OpenAI."""
    try:
        response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return [0] * 1536  # Return zero vector on error

@clinic_ai_expert.tool
async def retrieve_relevant_clinic_information(ctx: RunContext[ClinicAIDeps], user_query: str) -> str:
    """
    Retrieve relevant information about Haut Labor Oldenburg clinic based on the query with RAG.
    
    Args:
        ctx: The context including the Supabase client and OpenAI client
        user_query: The user's question or query about treatments, procedures, or clinic services
        
    Returns:
        A formatted string containing the top 5 most relevant clinic information chunks
    """
    try:
        # Get the embedding for the query
        query_embedding = await get_embedding(user_query, ctx.deps.openai_client)
        
        # Query Supabase for relevant documents from the German clinic
        result = ctx.deps.supabase.rpc(
            'match_site_pages',
            {
                'query_embedding': query_embedding,
                'match_count': 5,
                'filter': {}
            }
        ).execute()
        
        # Filter for haut-labor.de URLs
        if result.data:
            filtered_data = [doc for doc in result.data if 'haut-labor.de' in doc.get('url', '')]
            if not filtered_data:
                # If no filtered data, try direct query
                result = ctx.deps.supabase.from_('site_pages').select('*').like('url', '%haut-labor.de%').limit(5).execute()
                filtered_data = result.data if result.data else []
        else:
            filtered_data = []
            
        if not filtered_data:
            return "No relevant clinic information found. Please contact the clinic directly at +49 (0) 157 834 488 90 or info@haut-labor.de."
            
        # Format the results
        formatted_chunks = []
        for doc in filtered_data:
            chunk_text = f"""
# {doc['title']}
**URL:** {doc['url']}

{doc['content']}
"""
            formatted_chunks.append(chunk_text)
            
        # Join all chunks with a separator
        return "\n\n---\n\n".join(formatted_chunks)
        
    except Exception as e:
        print(f"Error retrieving clinic information: {e}")
        return f"Error retrieving clinic information: {str(e)}"

@clinic_ai_expert.tool
async def list_clinic_pages(ctx: RunContext[ClinicAIDeps]) -> List[str]:
    """
    Retrieve a list of all available Haut Labor Oldenburg clinic pages.
    
    Returns:
        List[str]: List of unique URLs for all clinic pages
    """
    try:
        # Query Supabase for unique URLs from haut-labor.de
        result = ctx.deps.supabase.from_('site_pages') \
            .select('url') \
            .like('url', '%haut-labor.de%') \
            .execute()
        
        if not result.data:
            return []
            
        # Extract unique URLs
        urls = sorted(set(doc['url'] for doc in result.data))
        return urls
        
    except Exception as e:
        print(f"Error retrieving clinic pages: {e}")
        return []

@clinic_ai_expert.tool
async def get_page_content(ctx: RunContext[ClinicAIDeps], url: str) -> str:
    """
    Retrieve the full content of a specific clinic page by combining all its chunks.
    
    Args:
        ctx: The context including the Supabase client
        url: The URL of the clinic page to retrieve
        
    Returns:
        str: The complete page content with all chunks combined in order
    """
    try:
        # Query Supabase for all chunks of this URL, ordered by chunk_number
        result = ctx.deps.supabase.from_('site_pages') \
            .select('title, content, chunk_number') \
            .eq('url', url) \
            .order('chunk_number') \
            .execute()
        
        if not result.data:
            return f"No content found for URL: {url}"
            
        # Format the page with its title and all chunks
        page_title = result.data[0]['title']
        formatted_content = [f"# {page_title}\n"]
        
        # Add each chunk's content
        for chunk in result.data:
            formatted_content.append(chunk['content'])
            
        # Join everything together
        return "\n\n".join(formatted_content)
        
    except Exception as e:
        print(f"Error retrieving page content: {e}")
        return f"Error retrieving page content: {str(e)}"
