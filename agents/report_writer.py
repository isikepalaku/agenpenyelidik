from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage

def create_report_writer_agent(openai_config: dict) -> Agent:
    return Agent(
        name="Agen Penyusun Laporan",
        model=OpenAIChat(id="gpt-4o-mini", **openai_config),
        description="Asisten analisis hukum untuk menyusun laporan komprehensif.",
        instructions=[
            "Susun laporan analisis sesuai format berikut:",
            "",
            "## 1. Pendahuluan",
            "- Resume perkara",
            "- Tempus dan locus delicti",
            "",
            "## 2. Analisis Formil",
            "- Klasifikasi alat bukti",
            "- Analisis barang bukti",
            "",
            "## 3. Analisis Materiil",
            "- Analisis tindak pidana",
            "- Pertanggungjawaban pidana",
            "",
            "## 4. Dasar Hukum",
            "- Ketentuan yang dilanggar",
            "- Peraturan terkait",
            "",
            "## 5. Putusan-Putusan Terkait",
            "{decisions}",
            "**Pola Pemidanaan yang Ditemukan**",
            "- Hukuman Penjara: {hukuman_penjara}",
            "- Hukuman Denda: {hukuman_denda}",
            "**Pasal yang Disangkakan**",
            "- {pasal_disangkakan}",
            "**Nomor Putusan Pengadilan yang Relevan**",
            "- {nomor_putusan}",
            "- Tanggal Putusan: {tanggal_putusan}",
            "**Dokumen Pendukung**",
            "- Google Drive: {link_gdrive}",
            "",
            "## 6. Kesimpulan dan Rekomendasi",
            "- Kesimpulan analisis keseluruhan",
            "- Rekomendasi penanganan",
            "- Strategi hukum yang disarankan"
        ],
        storage=SqlAgentStorage(table_name="report_agent", db_file="tmp/agents.db"),
        markdown=True,
    )
