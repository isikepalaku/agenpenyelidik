from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage

def create_classification_agent(openai_config: dict) -> Agent:
    return Agent(
        name="Agen Klasifikasi Kasus",
        model=OpenAIChat(id="gpt-4o-mini", **openai_config),
        description="Asisten analisis untuk mengklasifikasikan elemen-elemen kasus.",
        instructions=[
            "Identifikasi dan klasifikasikan elemen kasus sesuai kategori berikut:",
            "",
            "## 1. Saksi-saksi",
            "- Saksi mata",
            "- Saksi ahli",
            "- Saksi lainnya",
            "",
            "## 2. Benda-benda Terkait",
            "- Objek tindak pidana",
            "- Alat yang digunakan",
            "- Dokumen terkait",
            "",
            "## 3. Petunjuk",
            "- Bukti elektronik",
            "- Dokumen pendukung",
            "- Rekaman/foto",
            "",
            "## 4. Barang Bukti Lainnya",
            "- Bukti tambahan",
            "- Bukti pendukung",
            "",
            "## 5. Relevansi dengan Kasus",
            "- Tingkat relevansi setiap elemen",
            "- Hubungan antar elemen"
        ],
        storage=SqlAgentStorage(table_name="classification_agent", db_file="tmp/agents.db"),
        markdown=True,
    )