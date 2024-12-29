from rich.prompt import Prompt
from agents.report_writer import LegalReportWriter

def main():
    # Initialize the Legal Report Writer (which manages all other agents)
    report_writer = LegalReportWriter()

    # Get case information from user
    print("\n=== Sistem Analisis Kasus Hukum ===\n")
    
    case_info = Prompt.ask(
        "[bold]Masukkan informasi kasus[/bold]\n"
        "Sertakan detail-detail berikut:\n"
        "- Ringkasan kasus\n"
        "- Barang bukti\n"
        "- Informasi tersangka\n"
        "- Keterangan saksi\n"
        "✨ "
    )

    session_id = f"analisis-kasus-{case_info[:30].lower().replace(' ', '-')}"

    print("\nMenghasilkan laporan analisis hukum komprehensif...")
    print("Mohon tunggu sebentar sementara analisis sedang dilakukan...\n")

    # Generate the report
    report = report_writer.generate_report(case_info, session_id)

    print("\n=== Laporan Analisis Hukum ===\n")
    print(report)

if __name__ == "__main__":
    main()