from __future__ import annotations
from typing import Literal, TypedDict
import asyncio
import os

import streamlit as st
import json
import logfire

# Configure Streamlit page
st.set_page_config(
    page_title="Haut Labor Oldenburg - AI Consultant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)
from supabase import Client
from openai import AsyncOpenAI

# Import all the message part classes
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    UserPromptPart,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    RetryPromptPart,
    ModelMessagesTypeAdapter
)
from pydantic_ai_expert import clinic_ai_expert, ClinicAIDeps
from ai_manager import process_clinic_query

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
supabase: Client = Client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Configure logfire to suppress warnings (optional)
logfire.configure(send_to_logfire='never')

class ChatMessage(TypedDict):
    """Format of messages sent to the browser/API."""

    role: Literal['user', 'model']
    timestamp: str
    content: str


def display_message_part(part):
    """
    Display a single part of a message in the Streamlit UI.
    Customize how you display system prompts, user prompts,
    tool calls, tool returns, etc.
    """
    # system-prompt
    if part.part_kind == 'system-prompt':
        with st.chat_message("system"):
            st.markdown(f"**System**: {part.content}")
    # user-prompt
    elif part.part_kind == 'user-prompt':
        with st.chat_message("user"):
            st.markdown(part.content)
    # text
    elif part.part_kind == 'text':
        with st.chat_message("assistant"):
            st.markdown(part.content)          


async def run_agent_with_streaming(user_input: str):
    """
    Run the AI Manager to process the user input with intelligent RAG + web search.
    Shows a nice loading experience while processing.
    """
    # Prepare dependencies
    deps = ClinicAIDeps(
        supabase=supabase,
        openai_client=openai_client
    )

    # Show loading indicator
    message_placeholder = st.empty()
    
    # Show different loading messages to indicate what's happening
    loading_messages = [
        "🔍 Searching clinic knowledge base...",
        "🧠 Analyzing your question...", 
        "🌐 Checking for current information...",
        "📝 Preparing comprehensive answer..."
    ]
    
    import time
    
    # Show loading progression
    for i, loading_msg in enumerate(loading_messages):
        message_placeholder.markdown(loading_msg)
        await asyncio.sleep(0.5)  # Brief pause between loading messages
    
    try:
        # Use the AI Manager to process the query
        result = await process_clinic_query(
            user_input,
            deps,
            message_history=st.session_state.messages[:-1]  # pass entire conversation so far
        )
        
        # Get the response text
        if hasattr(result, 'data'):
            response_text = result.data
        else:
            # Handle different response formats
            if hasattr(result, 'parts') and result.parts:
                response_text = ""
                for part in result.parts:
                    if hasattr(part, 'content'):
                        response_text += part.content
            else:
                response_text = str(result)
        
        # Display the final response
        message_placeholder.markdown(response_text)
        
        # Add the response to session state
        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=response_text)])
        )
        
    except Exception as e:
        error_message = f"❌ I encountered an error while processing your question: {str(e)}\n\nPlease try again or contact the clinic directly at +49 (0) 157 834 488 90 or info@haut-labor.de."
        message_placeholder.markdown(error_message)
        
        # Add error response to session state
        st.session_state.messages.append(
            ModelResponse(parts=[TextPart(content=error_message)])
        )


async def main():
    st.title("🏥 Haut Labor Oldenburg - AI Consultant")
    st.write("Ask me anything about aesthetic treatments, procedures, and services at Haut Labor Oldenburg clinic in Germany.")
    
    # Sidebar with clinic information
    with st.sidebar:
        st.header("📍 Clinic Information")
        st.write("**Haut Labor Oldenburg**")
        st.write("Dr. Larisa Pfahl - Gynecologist")
        st.write("Specialized in minimally invasive aesthetic treatments")
        
        st.divider()
        
        st.header("📞 Contact")
        st.write("**Phone:** +49 (0) 157 834 488 90")
        st.write("**Email:** info@haut-labor.de")
        
        st.divider()
        
        st.header("💡 Example Questions")
        example_questions = [
            "What treatments are available for wrinkle reduction?",
            "Tell me about Morpheus8 treatments",
            "What is the cost of Botox treatments?",
            "Can you explain the HydraFacial procedure?",
            "What treatments are specifically available for men?",
            "Tell me about Dr. Larisa Pfahl",
            "How do I book an appointment?",
            "What are the laser hair removal options?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{hash(question)}"):
                st.session_state.example_question = question
                st.rerun()
                
        st.divider()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    # Initialize chat history in session state if not present
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Show welcome message if no messages yet
    if len(st.session_state.messages) == 0:
        st.info("👋 Welcome to Haut Labor Oldenburg! I'm here to help you learn about our aesthetic treatments and services. Feel free to ask me anything or click on the example questions in the sidebar.")
        
        # Display treatment categories
        st.subheader("🎆 Our Treatment Categories")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**💆 Facial Treatments**")
            st.write("• Botox/Faltenrelaxan")
            st.write("• Dermal Fillers")
            st.write("• HydraFacial")
            st.write("• Morpheus8")
            st.write("• Ultherapy")
            
        with col2:
            st.write("**✨ Laser Treatments**")
            st.write("• CO2 Laser")
            st.write("• LaseMD")
            st.write("• Lumecca")
            st.write("• Hair Removal")
            
        with col3:
            st.write("**👨 Specialized Services**")
            st.write("• Treatments for Men")
            st.write("• Body Contouring")
            st.write("• Aesthetic Gynecology")
            st.write("• Skin Analysis")

    # Display all messages from the conversation so far
    # Each message is either a ModelRequest or ModelResponse.
    # We iterate over their parts to decide how to display them.
    for msg in st.session_state.messages:
        if isinstance(msg, ModelRequest) or isinstance(msg, ModelResponse):
            for part in msg.parts:
                display_message_part(part)

    # Check if an example question was clicked
    if "example_question" in st.session_state:
        user_input = st.session_state.example_question
        del st.session_state.example_question
    else:
        # Chat input for the user
        user_input = st.chat_input("What questions do you have about our aesthetic treatments?")

    if user_input:
        # We append a new request to the conversation explicitly
        st.session_state.messages.append(
            ModelRequest(parts=[UserPromptPart(content=user_input)])
        )
        
        # Display user prompt in the UI
        with st.chat_message("user"):
            st.markdown(user_input)

        # Display the assistant's partial response while streaming
        with st.chat_message("assistant"):
            # Actually run the agent now, streaming the text
            await run_agent_with_streaming(user_input)


if __name__ == "__main__":
    asyncio.run(main())
