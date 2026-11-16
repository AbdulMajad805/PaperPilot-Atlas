
from app.tools.pdf_reader import extract_pdf_text
from app.workflow.graph import paperpilot_workflow

import json

from app.models.paper_analysis import PaperAnalysis, PaperReview
from app.services.report_generator import (
    generate_markdown_report,
    save_markdown_report,
)
from app.services.pdf_generator import generate_pdf_report



PDF_PATH = r"D:\PaperPilot-AI\data\uploads\ReAct.pdf"


def main():
    print("\n" + "=" * 60)
    print("PAPERPILOT AI - RESEARCH PAPER ANALYSIS")
    print("=" * 60)

    paper_text = extract_pdf_text(PDF_PATH)[:12000]

    print(f"\nExtracted paper characters: {len(paper_text):,}")

    initial_state = {
        "paper_text": paper_text,
        "analysis": "",
        "review": "",
    }

    result = paperpilot_workflow.invoke(initial_state)

    print("\n" + "=" * 60)
    print("PAPER ANALYST OUTPUT")
    print("=" * 60)
    print(result["analysis"])

    print("\n" + "=" * 60)
    print("PAPER REVIEWER OUTPUT")
    print("=" * 60)
    print(result["review"])

    print("\n" + "=" * 60)
    print("PAPERPILOT AI - COMPLETE")
    print("=" * 60)


# Parse validated workflow outputs
    analysis = PaperAnalysis.model_validate_json(result["analysis"])
    review = PaperReview.model_validate_json(result["review"])

    # Generate Markdown report
    report = generate_markdown_report(
        analysis=analysis,
        review=review,
    )

    # Save report
    report_path = save_markdown_report(
        report=report,
        output_path=r"D:\PaperPilot-AI\outputs\ReAct_Analysis_Report.md",
    )


    pdf_path = generate_pdf_report(
        markdown_path=r"D:\PaperPilot-AI\outputs\ReAct_Analysis_Report.md",
        pdf_path=r"D:\PaperPilot-AI\outputs\ReAct_Analysis_Report.pdf",
    )

    print(f"PDF generated successfully: {pdf_path}")

    print("\n" + "=" * 60)
    print("PAPERPILOT AI - REPORT GENERATED")
    print("=" * 60)
    print(f"Report saved successfully: {report_path}")
    print(f"Report characters: {len(report):,}")


if __name__ == "__main__":
    main()
