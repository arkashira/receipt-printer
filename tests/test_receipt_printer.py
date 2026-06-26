import pytest
from receipt_printer import (
    PrinterModel,
    ReceiptLayout,
    TestScenario,
    ReceiptPrinterTester,
    ReceiptPrintError,
)


@pytest.fixture
def tester():
    # Use only two models to demonstrate unsupported model handling
    return ReceiptPrinterTester(supported_models={PrinterModel.GENERIC, PrinterModel.EPSON_TM_T20})


def test_simple_text_happy_path(tester):
    layout = ReceiptLayout(width=32, max_lines=10)
    scenario = TestScenario(
        name="simple_text",
        model=PrinterModel.GENERIC,
        layout=layout,
        content=[
            "Thank you for shopping!",
            "Item A   $5.00",
            "Item B   $3.50",
            "Total    $8.50",
        ],
    )
    result = tester.run_scenario(scenario)
    assert result["status"] == "passed"
    assert "Printed 4 lines" in result["details"]
    assert result["scenario"] == "simple_text"


def test_long_receipt_exceeds_max_lines(tester):
    layout = ReceiptLayout(width=30, max_lines=5)
    # 6 lines > max_lines
    scenario = TestScenario(
        name="long_receipt",
        model=PrinterModel.EPSON_TM_T20,
        layout=layout,
        content=[
            "Line 1",
            "Line 2",
            "Line 3",
            "Line 4",
            "Line 5",
            "Line 6",
        ],
    )
    result = tester.run_scenario(scenario)
    assert result["status"] == "failed"
    assert "Content does not fit layout" in result["details"]
    assert result["scenario"] == "long_receipt"


def test_line_width_overflow(tester):
    layout = ReceiptLayout(width=10, max_lines=3)
    scenario = TestScenario(
        name="width_overflow",
        model=PrinterModel.GENERIC,
        layout=layout,
        content=[
            "Short",
            "This line is definitely too long",
            "OK",
        ],
    )
    result = tester.run_scenario(scenario)
    assert result["status"] == "failed"
    assert "Content does not fit layout" in result["details"]
    assert result["scenario"] == "width_overflow"


def test_unsupported_printer_model(tester):
    layout = ReceiptLayout(width=20, max_lines=5)
    scenario = TestScenario(
        name="unsupported_model",
        model=PrinterModel.STAR_TSP100,  # Not in tester's supported set
        layout=layout,
        content=["Hello"],
    )
    result = tester.run_scenario(scenario)
    assert result["status"] == "failed"
    assert "is not supported" in result["details"]
    assert result["scenario"] == "unsupported_model"
