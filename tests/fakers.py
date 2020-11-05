import bz2
import os
import pickle

from faker.providers import BaseProvider

with bz2.open(os.path.join(os.path.dirname(__file__), "substances.bz2"), "rb") as f:
    SUBSTANCES = pickle.load(f)


class SubstanceFaker(BaseProvider):
    substances = SUBSTANCES

    def sid(self):
        return f"DTXSID{self.random_int(2000000, 3000000)}"

    def casrn(self):
        return self.random_element(self.substances)
