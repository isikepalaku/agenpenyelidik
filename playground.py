import os
from pathlib import Path
from dotenv import load_dotenv
from phi.playground import Playground, serve_playground_app
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from supabase import create_client, Client

# Import agent creators
from agents.case_classification import create_classification_agent
from agents.criminal_analysis import create_criminal_analysis_agent
from agents.web_search import create_web_search_agent
from agents.report_writer import create_report_writer_agent
from agents.court_decision import PutusanAgent

# Create directory for database
Path("tmp").mkdir(exist_ok=True)

# Load environment variables
load_dotenv()

# Initialize OpenAI settings
openai_config = {"api_key": os.getenv("VITE_OPENAI_API_KEY")}

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("VITE_SUPABASE_URL"),
    os.getenv("VITE_SUPABASE_ANON_KEY")
)

# Create agents
case_classification_agent = create_classification_agent(openai_config)
criminal_analysis_agent = create_criminal_analysis_agent(openai_config)
web_search_agent = create_web_search_agent(openai_config)
putusan_agent = PutusanAgent(
    name="Agen Pencarian Putusan",
    model=OpenAIChat(id="gpt-4o-mini", **openai_config),
    description="Asisten pencarian putusan pengadilan yang relevan.",
    instructions=[
        "Tampilkan metadata putusan pengadilan yang relevan dengan kasus ini.",
        "Pastikan setiap putusan memiliki:",
        "- Nomor putusan yang valid",
        "- Tanggal putusan yang valid",
        "- Pasal yang disangkakan",
        "- Hukuman yang dijatuhkan",
        "- Link dokumen yang valid",
        "Jika ada data yang tidak lengkap atau tidak valid, jangan tampilkan putusan tersebut.",
        "Urutkan hasil berdasarkan relevansi dengan kasus.",
        "Batasi hasil maksimal 3 putusan yang paling relevan.",
        "Jika tidak menemukan putusan yang relevan, beri tahu pengguna dan jelaskan alasannya."
    ],
    storage=SqlAgentStorage(table_name="putusan_agent", db_file="tmp/agents.db"),
    markdown=True,
    supabase=supabase
)
report_agent = create_report_writer_agent(openai_config)

# Create the playground
app = Playground(
    agents=[
        case_classification_agent,  # 1. Case Classification
        criminal_analysis_agent,    # 2. Criminal Analysis
        web_search_agent,          # 3. Legal Research
        putusan_agent,             # 4. Court Decisions
        report_agent               # 5. Final Report
    ]
).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)
