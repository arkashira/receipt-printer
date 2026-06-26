import enum
from dataclasses import dataclass, field
from typing import List, Set, Dict


class ReceiptPrintError(Exception):
    """Raised when a test scenario cannot be printed correctly."""
    pass


class PrinterModel(enum.Enum):
    """Supported thermal printer models."""
    GENERIC = "GenericThermal"
    EPSON_TM_T20 = "EpsonTM-T20"
    STAR_TSP100 = "StarTSP100"


@dataclass
class ReceiptLayout:
    """Defines the printable area of a receipt."""
    width: int                # characters per line
    max_lines: int            # total printable lines

    def fits_line(self, line: str) -> bool:
        """Return True if a single line fits within the layout width."""
        return len(line) <= self.width

    def fits_content(self, lines: List[str]) -> bool:
        """Return True if all lines and total count fit the layout."""
        if len(lines) > self.max_lines:
            return False
        return all(self.fits_line(l) for l in lines)


@dataclass
class TestScenario:
    """A concrete test case for a printer."""
    name: str
    model: PrinterModel
    layout: ReceiptLayout
    content: List[str] = field(default_factory=list)

    def validate(self) -> None:
        """Validate the scenario; raise ReceiptPrintError on problems."""
        if not isinstance(self.model, PrinterModel):
            raise ReceiptPrintError(f"Unsupported printer model: {self.model}")
        if not self.layout.fits_content(self.content):
            raise ReceiptPrintError(
                f"Content does not fit layout (width={self.layout.width}, "
                f"max_lines={self.layout.max_lines})"
            )


class ReceiptPrinterTester:
    """Core API that runs test scenarios against simulated printers."""

    def __init__(self, supported_models: Set[PrinterModel] = None):
        if supported_models is None:
            supported_models = {m for m in PrinterModel}
        self.supported_models = supported_models

    def run_scenario(self, scenario: TestScenario) -> Dict[str, str]:
        """
        Simulate printing the scenario.

        Returns a dict with keys:
            - scenario: scenario name
            - status: "passed" or "failed"
            - details: description of result or error
        """
        try:
            self._ensure_supported_model(scenario.model)
            scenario.validate()
            # Simulate printing by joining lines (no real I/O)
            printed_output = "\n".join(scenario.content)
            # In a real implementation we might compare to an expected output.
            return {
                "scenario": scenario.name,
                "status": "passed",
                "details": f"Printed {len(scenario.content)} lines."
            }
        except ReceiptPrintError as exc:
            return {
                "scenario": scenario.name,
                "status": "failed",
                "details": str(exc)
            }

    def _ensure_supported_model(self, model: PrinterModel) -> None:
        """Raise an error if the model is not in the supported set."""
        if model not in self.supported_models:
            raise ReceiptPrintError(f"Model {model.value} is not supported.")
