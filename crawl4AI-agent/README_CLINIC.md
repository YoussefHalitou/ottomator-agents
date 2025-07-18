# 🏥 Haut Labor Oldenburg - AI Consultant System

This project provides an AI-powered consultant system for Haut Labor Oldenburg, a premium aesthetic medicine clinic in Germany led by Dr. Larisa Pfahl.

## 🎯 Overview

The system uses advanced RAG (Retrieval-Augmented Generation) technology to provide detailed, accurate information about the clinic's treatments, procedures, and services based on comprehensive website content that has been crawled and indexed.

## 🚀 Features

### 🤖 AI Agent Capabilities
- **Comprehensive Treatment Information**: Details about 30+ aesthetic treatments
- **Intelligent Search**: RAG-powered search through clinic website content
- **Professional Responses**: Detailed information about procedures, costs, and aftercare
- **Multilingual Support**: Handles German and English queries
- **Real-time Information**: Based on up-to-date website content

### 🏥 Clinic Services Covered
- **Facial Treatments**: Botox, Dermal Fillers, HydraFacial, Morpheus8, Ultherapy
- **Laser Treatments**: CO2 Laser, LaseMD, Lumecca, Hair Removal
- **Body Contouring**: Sculptra, Radiesse, Lipolyse
- **Specialized Services**: Treatments for Men, Aesthetic Gynecology, Skin Analysis
- **Advanced Procedures**: Polynukleotide, Vampirlifting, Fadenlifting

### 💻 User Interfaces
1. **Streamlit Web App**: Interactive web interface with sidebar information
2. **Command Line Chat**: Terminal-based interactive chat
3. **Test Scripts**: Automated testing and demonstration

## 📋 Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- OpenAI API key
- Supabase account with vector database setup

## 🛠️ Installation

1. **Clone and setup environment**:
```bash
cd /Users/youssef/Desktop/ottomator-agents/crawl4AI-agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Environment configuration**:
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_supabase_service_key
LLM_MODEL=gpt-4o-mini
```

3. **Database setup**:
Ensure your Supabase database has the crawled clinic data in the `site_pages` table.

## 🚀 Usage

### 1. Streamlit Web Interface
```bash
# Using the launch script
python run_streamlit.py

# Or directly with streamlit
streamlit run streamlit_ui.py
```
Access at: http://localhost:8501

### 2. Interactive Chat
```bash
python clinic_chat.py
```

### 3. Test the System
```bash
python test_clinic_agent.py
```

## 🏗️ System Architecture

### Core Components

1. **`pydantic_ai_expert.py`**: Main AI agent with RAG capabilities
   - `clinic_ai_expert`: The main AI agent
   - `ClinicAIDeps`: Dependencies (Supabase, OpenAI)
   - `retrieve_relevant_clinic_information()`: RAG search function
   - `list_clinic_pages()`: Page listing function
   - `get_page_content()`: Full page content retrieval

2. **`streamlit_ui.py`**: Web interface
   - Interactive chat interface
   - Sidebar with clinic information
   - Example questions
   - Treatment categories overview

3. **`clinic_chat.py`**: Command-line interface
   - Interactive terminal chat
   - Help system with example questions

### Data Flow
1. User asks a question
2. AI agent uses RAG to search clinic website content
3. Relevant information retrieved from Supabase vector database
4. AI generates comprehensive response
5. Response displayed to user

## 🔧 Configuration

### AI Agent Settings
- **Model**: GPT-4o-mini (configurable via LLM_MODEL env var)
- **Temperature**: Optimized for factual responses
- **Max Tokens**: Configured for detailed responses
- **Retries**: 2 attempts for reliability

### Database Schema
The system expects a `site_pages` table with:
- `url`: Page URL
- `title`: Page title
- `content`: Page content
- `chunk_number`: Chunk sequence
- `embedding`: Vector embedding for search

## 🎨 Customization

### Adding New Questions
Add to `example_questions` list in `streamlit_ui.py`:
```python
example_questions = [
    "Your new question here",
    # ... existing questions
]
```

### Modifying System Prompt
Update the `system_prompt` in `pydantic_ai_expert.py` to adjust AI behavior.

### UI Customization
Modify `streamlit_ui.py` for:
- Styling changes
- Layout modifications
- Additional features

## 🧪 Testing

### Available Test Scripts
1. **`test_clinic_agent.py`**: Comprehensive testing with multiple queries
2. **`clinic_chat.py`**: Interactive testing
3. **Manual testing**: Use the Streamlit interface

### Example Test Queries
- "What treatments are available for wrinkle reduction?"
- "Tell me about Morpheus8 treatments"
- "What is the cost of Botox treatments?"
- "Can you explain the HydraFacial procedure?"
- "What treatments are specifically available for men?"

## 📞 Clinic Information

**Haut Labor Oldenburg**
- **Doctor**: Dr. Larisa Pfahl (Gynecologist)
- **Specialty**: Minimally invasive aesthetic treatments
- **Phone**: +49 (0) 157 834 488 90
- **Email**: info@haut-labor.de
- **Website**: https://haut-labor.de

## 🔍 Troubleshooting

### Common Issues
1. **Import errors**: Ensure virtual environment is activated
2. **Database connection**: Check Supabase credentials
3. **OpenAI API issues**: Verify API key and usage limits
4. **Missing data**: Ensure clinic website has been crawled

### Debug Mode
Enable debug logging by setting:
```python
import logfire
logfire.configure(send_to_logfire='if-token-present')
```

## 📚 Development

### Project Structure
```
crawl4AI-agent/
├── pydantic_ai_expert.py      # Main AI agent
├── streamlit_ui.py            # Web interface
├── clinic_chat.py             # CLI interface
├── test_clinic_agent.py       # Test script
├── run_streamlit.py           # Launch script
├── requirements.txt           # Dependencies
├── .env                       # Environment variables
└── README_CLINIC.md          # This file
```

### Key Dependencies
- `pydantic-ai`: AI agent framework
- `streamlit`: Web interface
- `supabase`: Vector database
- `openai`: LLM integration
- `python-dotenv`: Environment management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is proprietary software for Haut Labor Oldenburg clinic.

## 🙏 Acknowledgments

- Built with Pydantic AI framework
- Powered by OpenAI GPT models
- Data storage via Supabase
- Web interface with Streamlit
