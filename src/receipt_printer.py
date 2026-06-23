import json
from dataclasses import dataclass
from typing import List

@dataclass
class Receipt:
    id: int
    customer_name: str
    items: List[str]
    total: float

class ReceiptPrinter:
    def __init__(self):
        self.receipts = {}

    def generate_receipt(self, receipt: Receipt):
        return {
            "id": receipt.id,
            "customer_name": receipt.customer_name,
            "items": receipt.items,
            "total": receipt.total
        }

    def print_receipt(self, receipt: Receipt):
        print(json.dumps(self.generate_receipt(receipt), indent=4))

    def store_receipt(self, receipt: Receipt):
        self.receipts[receipt.id] = receipt

    def get_receipt(self, receipt_id: int):
        return self.receipts.get(receipt_id)

    def print_stored_receipt(self, receipt_id: int):
        receipt = self.get_receipt(receipt_id)
        if receipt:
            self.print_receipt(receipt)
        else:
            raise ValueError("Receipt not found")
