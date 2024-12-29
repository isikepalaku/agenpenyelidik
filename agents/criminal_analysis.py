from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage

def create_criminal_analysis_agent(openai_config: dict) -> Agent:
    return Agent(
        name="Agen Analisis Pidana",
        model=OpenAIChat(id="gpt-4o-mini", **openai_config),
        description="Asisten analisis untuk mengidentifikasi perbuatan pidana dan modus operandi.",
        instructions=[
            "Analisis fakta kasus untuk mengidentifikasi:",
            "",
            "## 1. Perbuatan Pidana",
            "- Jenis tindak pidana",
            "- Unsur-unsur pidana",
            "- Tempus dan locus delicti",
            "",
            "## 2. Modus Operandi",
            "- Cara pelaksanaan",
            "- Alat/sarana yang digunakan",
            "- Tahapan perbuatan",
            "",
            "## 3. Unsur Pemberatan",
            "- Faktor-faktor pemberat",
            "- Akibat perbuatan",
            "",
            "## 4. Pihak Terlibat",
            "- Pelaku utama",
            "- Pelaku pembantu",
            "- Peran masing-masing"
        ],
        storage=SqlAgentStorage(table_name="criminal_analysis_agent", db_file="tmp/agents.db"),
        markdown=True,
    )