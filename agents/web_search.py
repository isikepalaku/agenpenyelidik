from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.googlesearch import GoogleSearch

def create_web_search_agent(openai_config: dict) -> Agent:
    return Agent(
        name="Agen Penelusuran Hukum",
        model=OpenAIChat(id="gpt-4o-mini", **openai_config),
        tools=[GoogleSearch()],
        description="Asisten penelusuran tinjauan yuridis dan peraturan terkait.",
        instructions=[
            "Cari sumber hukum dengan prioritas:",
            "1. Peraturan Perundang-undangan dari sumber resmi (JDIH, dll)",
            "2. Jurnal hukum terakreditasi",
            "3. Artikel tinjauan yuridis terkait",
            "",
            "Format hasil:",
            "## Peraturan Perundang-undangan",
            "[Daftar peraturan yang relevan]",
            "",
            "## Tinjauan Yuridis",
            "[Daftar artikel dan analisis relevan]"
        ],
        storage=SqlAgentStorage(table_name="web_search_agent", db_file="tmp/agents.db"),
        markdown=True,
    )