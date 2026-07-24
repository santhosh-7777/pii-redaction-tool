"""
fake_mapper.py — maps real PII to fake values, same input always gives
same output across a document.
"""

from typing import Callable, Dict, Tuple
from faker import Faker


class FakeMapper:
    def __init__(self, seed: int = 42):
        self.fake = Faker()
        Faker.seed(seed)
        self._map: Dict[Tuple[str, str], str] = {}
        self._generators: Dict[str, Callable[[], str]] = {
            "PERSON": self.fake.name,
            "EMAIL": self.fake.email,
            "PHONE": lambda: "+91 " + self.fake.msisdn()[3:],
            "COMPANY": lambda: self.fake.company() + " Limited",
            "ADDRESS": self.fake.address,
            "SSN": self.fake.ssn,
            "CREDIT_CARD": self.fake.credit_card_number,
            "DATE_OF_BIRTH": lambda: self.fake.date_of_birth(18, 80).strftime("%Y-%m-%d"),
            "IP_ADDRESS": self.fake.ipv4,
            "DIN": lambda: str(self.fake.random_number(digits=8, fix_len=True)),
        }

    def get(self, original: str, label: str) -> str:
        key = (label, original.strip().lower())
        if key in self._map:
            return self._map[key]
        gen = self._generators.get(label, lambda: f"[REDACTED:{label}]")
        val = gen()
        self._map[key] = val
        return val