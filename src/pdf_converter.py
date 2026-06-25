import re
from dataclasses import dataclass
from typing import List

@dataclass
class ReceiptText:
    text: str
    line_breaks: List[int]

def extract_text_from_pdf(pdf_content: str) -> ReceiptText:
    lines = pdf_content.split('\n')
    text = ''
    line_breaks = []
    for i, line in enumerate(lines):
        if line.strip():
            text += line.strip() + '\n'
            line_breaks.append(i)
    return ReceiptText(text.strip(), line_breaks)

def preserve_line_breaks_and_formatting(text: str, line_breaks: List[int]) -> str:
    formatted_text = ''
    for i, line in enumerate(text.split('\n')):
        if i in line_breaks:
            formatted_text += line + '\n'
        else:
            formatted_text += line + ' '
    return formatted_text.strip()

def handle_high_dpi_resolution(pdf_content: str) -> str:
    lines = pdf_content.split('\n')
    for i, line in enumerate(lines):
        if 'font-size: 12pt' in line:
            lines[i] = line.replace('font-size: 12pt', 'font-size: 6pt')
    return '\n'.join(lines)

def convert_pdf_to_receipt_text(pdf_content: str) -> str:
    pdf_content = handle_high_dpi_resolution(pdf_content)
    receipt_text = extract_text_from_pdf(pdf_content)
    formatted_text = preserve_line_breaks_and_formatting(receipt_text.text, receipt_text.line_breaks)
    return formatted_text
