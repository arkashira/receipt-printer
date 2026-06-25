import pytest
import sys
sys.path.insert(0, '../src')
from pdf_converter import convert_pdf_to_receipt_text, ReceiptText, handle_high_dpi_resolution

def test_extract_text_from_pdf():
    pdf_content = "Hello\nWorld"
    receipt_text = ReceiptText("Hello\nWorld", [0, 1])
    assert convert_pdf_to_receipt_text(pdf_content) == "Hello\nWorld"

def test_preserve_line_breaks_and_formatting():
    text = "Hello\nWorld"
    line_breaks = [0, 1]
    formatted_text = "Hello\nWorld"
    assert convert_pdf_to_receipt_text("Hello\nWorld") == formatted_text

def test_handle_high_dpi_resolution():
    pdf_content = "Hello\nWorld\nfont-size: 12pt"
    expected_content = "Hello\nWorld\nfont-size: 6pt"
    assert handle_high_dpi_resolution(pdf_content) == expected_content

def test_convert_pdf_to_receipt_text():
    pdf_content = "Hello\nWorld"
    expected_text = "Hello\nWorld"
    assert convert_pdf_to_receipt_text(pdf_content) == expected_text

def test_convert_pdf_to_receipt_text_empty():
    pdf_content = ""
    expected_text = ""
    assert convert_pdf_to_receipt_text(pdf_content) == expected_text

def test_convert_pdf_to_receipt_text_multiple_lines():
    pdf_content = "Hello\nWorld\nThis is a test"
    expected_text = "Hello\nWorld\nThis is a test"
    assert convert_pdf_to_receipt_text(pdf_content) == expected_text
