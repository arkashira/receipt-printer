import pytest
from pdf_converter import PDFConverter, PrinterModel

def test_convert_epson_tm_t20ii():
    printer_model = PrinterModel("Epson TM-T20II", "")
    converter = PDFConverter(printer_model)
    pdf_bytes = b"PDF Bytes"
    command_stream = converter.convert(pdf_bytes)
    assert command_stream == b"Command Stream: PDF Text, PDF Image 1, PDF Image 2, PDF Layout (Epson TM-T20II)"

def test_convert_star_tsp100():
    printer_model = PrinterModel("Star TSP100", "")
    converter = PDFConverter(printer_model)
    pdf_bytes = b"PDF Bytes"
    command_stream = converter.convert(pdf_bytes)
    assert command_stream == b"Command Stream: PDF Text, PDF Image 1, PDF Image 2, PDF Layout (Star TSP100)"

def test_convert_bixolon_slp_s30():
    printer_model = PrinterModel("Bixolon SLP-S30", "")
    converter = PDFConverter(printer_model)
    pdf_bytes = b"PDF Bytes"
    command_stream = converter.convert(pdf_bytes)
    assert command_stream == b"Command Stream: PDF Text, PDF Image 1, PDF Image 2, PDF Layout (Bixolon SLP-S30)"

def test_convert_empty_pdf_bytes():
    printer_model = PrinterModel("Epson TM-T20II", "")
    converter = PDFConverter(printer_model)
    pdf_bytes = b""
    command_stream = converter.convert(pdf_bytes)
    assert command_stream == b"Command Stream: PDF Text, PDF Image 1, PDF Image 2, PDF Layout (Epson TM-T20II)"

def test_convert_none_pdf_bytes():
    printer_model = PrinterModel("Epson TM-T20II", "")
    converter = PDFConverter(printer_model)
    pdf_bytes = None
    with pytest.raises(TypeError):
        converter.convert(pdf_bytes)
