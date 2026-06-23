import json
from receipt_printer import Receipt, ReceiptPrinter

def test_generate_receipt():
    receipt = Receipt(1, "John Doe", ["Item 1", "Item 2"], 10.99)
    expected_output = {
        "id": 1,
        "customer_name": "John Doe",
        "items": ["Item 1", "Item 2"],
        "total": 10.99
    }
    assert ReceiptPrinter().generate_receipt(receipt) == expected_output

def test_print_receipt(capsys):
    receipt = Receipt(1, "John Doe", ["Item 1", "Item 2"], 10.99)
    ReceiptPrinter().print_receipt(receipt)
    captured = capsys.readouterr()
    assert captured.out.strip() == json.dumps({
        "id": 1,
        "customer_name": "John Doe",
        "items": ["Item 1", "Item 2"],
        "total": 10.99
    }, indent=4)

def test_store_receipt():
    receipt = Receipt(1, "John Doe", ["Item 1", "Item 2"], 10.99)
    printer = ReceiptPrinter()
    printer.store_receipt(receipt)
    assert printer.get_receipt(1) == receipt

def test_get_receipt():
    receipt = Receipt(1, "John Doe", ["Item 1", "Item 2"], 10.99)
    printer = ReceiptPrinter()
    printer.store_receipt(receipt)
    assert printer.get_receipt(1) == receipt

def test_print_stored_receipt(capsys):
    receipt = Receipt(1, "John Doe", ["Item 1", "Item 2"], 10.99)
    printer = ReceiptPrinter()
    printer.store_receipt(receipt)
    printer.print_stored_receipt(1)
    captured = capsys.readouterr()
    assert captured.out.strip() == json.dumps({
        "id": 1,
        "customer_name": "John Doe",
        "items": ["Item 1", "Item 2"],
        "total": 10.99
    }, indent=4)

def test_print_stored_receipt_not_found():
    printer = ReceiptPrinter()
    try:
        printer.print_stored_receipt(1)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert str(e) == "Receipt not found"
