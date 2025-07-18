"""
Type definitions for the clinic AI system.
This file contains only type definitions and data classes, no executable code.
"""

from dataclasses import dataclass
from supabase import Client
from openai import AsyncOpenAI

@dataclass
class ClinicAIDeps:
    """Dependencies for the Clinic AI system"""
    supabase: Client
    openai_client: AsyncOpenAI