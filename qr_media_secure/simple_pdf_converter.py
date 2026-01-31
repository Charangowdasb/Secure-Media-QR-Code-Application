"""
Simple PDF Converter - Academic Report
Converts markdown to HTML, then provides options for PDF conversion
"""

import markdown
import os
import webbrowser

def create_styled_html(md_file, html_file):
    """Convert markdown to professionally styled HTML"""
    
    print(f"Converting {md_file} to {html_file}...")
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_content, 
        extensions=['tables', 'fenced_code', 'nl2br']
    )
    
    # Professional academic styling
    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Media QR Code Application - Academic Report</title>
    <style>
        @page {{
            size: A4;
            margin: 2.5cm;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 0;
            }}
            .no-print {{
                display: none;
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000000;
            max-width: 21cm;
            margin: 0 auto;
            padding: 2.5cm;
            background-color: #ffffff;
        }}
        
        h1 {{
            font-size: 20pt;
            font-weight: bold;
            text-align: center;
            margin: 30pt 0 20pt 0;
            color: #000000;
            text-transform: uppercase;
            page-break-after: avoid;
        }}
        
        h2 {{
            font-size: 16pt;
            font-weight: bold;
            margin-top: 24pt;
            margin-bottom: 12pt;
            color: #000000;
            page-break-after: avoid;
            border-bottom: 2px solid #000000;
            padding-bottom: 4pt;
        }}
        
        h3 {{
            font-size: 13pt;
            font-weight: bold;
            margin-top: 18pt;
            margin-bottom: 10pt;
            color: #000000;
            page-break-after: avoid;
        }}
        
        h4 {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 14pt;
            margin-bottom: 8pt;
            color: #000000;
            font-style: italic;
        }}
        
        p {{
            text-align: justify;
            margin-bottom: 10pt;
            orphans: 3;
            widows: 3;
        }}
        
        ul, ol {{
            margin-left: 30pt;
            margin-bottom: 12pt;
        }}
        
        li {{
            margin-bottom: 6pt;
            text-align: justify;
        }}
        
        strong {{
            font-weight: bold;
            color: #000000;
        }}
        
        em {{
            font-style: italic;
        }}
        
        code {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 11pt;
            background-color: #f5f5f5;
            padding: 2pt 4pt;
            border-radius: 3px;
        }}
        
        pre {{
            font-family: 'Courier New', Courier, monospace;
            font-size: 10pt;
            background-color: #f5f5f5;
            padding: 10pt;
            border-left: 3pt solid #cccccc;
            overflow-x: auto;
            margin: 12pt 0;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15pt 0;
            page-break-inside: avoid;
        }}
        
        th {{
            background-color: #e0e0e0;
            font-weight: bold;
            text-align: left;
            padding: 8pt;
            border: 1px solid #000000;
        }}
        
        td {{
            padding: 8pt;
            border: 1px solid #000000;
            text-align: left;
        }}
        
        hr {{
            border: none;
            border-top: 1px solid #cccccc;
            margin: 20pt 0;
        }}
        
        .subtitle {{
            text-align: center;
            font-size: 14pt;
            font-style: italic;
            margin-bottom: 30pt;
            color: #333333;
        }}
        
        .section-number {{
            font-weight: bold;
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 24px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14pt;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
        }}
        
        .print-button:hover {{
            background-color: #45a049;
        }}
        
        .instructions {{
            position: fixed;
            top: 70px;
            right: 20px;
            padding: 15px;
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            max-width: 300px;
            font-size: 11pt;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 999;
        }}
    </style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">🖨️ Save as PDF</button>
    
    <div class="instructions no-print">
        <strong>📄 How to Save as PDF:</strong><br>
        1. Click the "Save as PDF" button<br>
        2. In print dialog, select "Save as PDF"<br>
        3. Choose destination and click Save
    </div>
    
    {html_body}
</body>
</html>
"""
    
    # Write HTML file
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(styled_html)
    
    print(f"✅ HTML file created successfully: {html_file}")
    return html_file

def main():
    md_file = "ACADEMIC_REPORT.md"
    html_file = "ACADEMIC_REPORT.html"
    
    if not os.path.exists(md_file):
        print(f"❌ Error: {md_file} not found!")
        return
    
    # Create HTML
    html_path = create_styled_html(md_file, html_file)
    
    print(f"\n{'='*60}")
    print("📄 CONVERSION COMPLETE!")
    print(f"{'='*60}")
    print(f"\n✅ File created: {os.path.abspath(html_file)}")
    print(f"\n📋 To convert to PDF:")
    print("   1. The HTML file will open in your browser")
    print("   2. Press Ctrl+P (or click the 'Save as PDF' button)")
    print("   3. Select 'Save as PDF' as the destination")
    print("   4. Click 'Save' and choose location")
    print(f"\n{'='*60}\n")
    
    # Open in browser
    print("Opening in browser...")
    webbrowser.open(os.path.abspath(html_file))
    
    print("\n✅ Done! Your academic report is ready for PDF conversion.")

if __name__ == "__main__":
    # Install markdown if needed
    try:
        import markdown
    except ImportError:
        print("Installing markdown package...")
        import subprocess
        import sys
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown
    
    main()
