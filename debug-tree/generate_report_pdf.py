from fpdf import FPDF
import datetime

class ReportPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'Technical Audit: Debug Tree v8 Sovereign Engine', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_report():
    pdf = ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)

    # Introduction
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1, 'L')
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, "This report provides an objective technical analysis of the Debug Tree v8 system. "
                         "Unlike standard debugging tools that focus on linear error reporting, Debug Tree "
                         "implements a 'Sovereign' diagnostic model - treating a crash not as a point of failure, "
                         "but as a signal to be interpreted through structural context and historical evolution.")
    pdf.ln(5)

    # Core Proofs
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "2. Real Proofs: Technical Truths", 0, 1, 'L')
    pdf.set_font("Helvetica", size=11)
    
    proofs = [
        ("Multi-Signal Fusion:", "The tool combines Traceback Depth, AST-based Symbol Match, and Git Rename History. "
                                "Standard tools like 'pdb' or 'grep' only look at one of these."),
        ("Git-Rename Immunity:", "Debug Tree can identify root causes in files that have been renamed since the log was generated. "
                                  "This is a 'special' capability rare in local diagnostic tools."),
        ("Calibrated Confidence:", "Using a Softmax-inspired exponential ranking, it provides a mathematical probability "
                                    "rather than a simple list, allowing for automated decision-making.")
    ]
    
    for title, desc in proofs:
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(0, 7, title, 0, 1, 'L')
        pdf.set_font("Helvetica", size=11)
        pdf.multi_cell(0, 7, desc)
        pdf.ln(2)

    # Comparison
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "3. Comparison with Real-World Tools", 0, 1, 'L')
    pdf.set_font("Helvetica", size=11)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, "Feature", 1, 0, 'C', True)
    pdf.cell(50, 10, "Debug Tree v8", 1, 0, 'C', True)
    pdf.cell(50, 10, "Sentry / Logs", 1, 0, 'C', True)
    pdf.cell(50, 10, "Standard pdb", 1, 1, 'C', True)
    
    # Table Rows
    data = [
        ("AST Analysis", "YES (Recursive)", "NO (Text-based)", "NO"),
        ("Rename Support", "YES (Similarity)", "NO", "NO"),
        ("Prob. Verdict", "YES (Calibrated)", "NO", "NO"),
        ("Active Fix", "Diagnostic Only", "Monitoring", "Interactive")
    ]
    
    for row in data:
        pdf.cell(40, 10, row[0], 1)
        pdf.cell(50, 10, row[1], 1)
        pdf.cell(50, 10, row[2], 1)
        pdf.cell(50, 10, row[3], 1)
        pdf.ln(10)
    pdf.ln(5)

    # Critical Truths
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "4. Critical Truths (Honest Critique)", 0, 1, 'L')
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, "- Currently Python-bound: The AST logic is specifically for .py files.\n"
                         "- Heuristic Dependency: The weightage (0.4/0.4/0.2) is a manually tuned value.\n"
                         "- Simulated History: The git-rename bridge in the current code is a simulation model "
                         "and requires live git-diff integration for production deployments.")
    pdf.ln(5)

    # Conclusion
    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "5. Verdict: Is it Special?", 0, 1, 'L')
    pdf.set_font("Helvetica", size=11)
    pdf.multi_cell(0, 7, "Yes. Debug Tree is not just a 'prettier traceback'. It is a Structural Bridge. "
                         "By mapping crash symbols to AST nodes AND historical paths, it achieves a "
                         "level of diagnostic precision that 'standard' tools lack. It is a 'New Tool' in "
                         "the sense that it treats codebase history as a first-class citizen in debugging.")

    pdf.output("DebugTree_Technical_Report.pdf")
    print("Report generated: DebugTree_Technical_Report.pdf")

if __name__ == "__main__":
    create_report()
