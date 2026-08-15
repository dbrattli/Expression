# %% [markdown]
"""
# Model domain alternatives with tagged unions

Use a tagged union when a value is exactly one of several well-defined cases. It makes
the cases explicit and works naturally with Python structural pattern matching.
"""
# %%
from typing import Literal

from expression import case, tag, tagged_union

@tagged_union
class Payment:
    tag: Literal["card", "cash"] = tag()
    card: str = case()
    cash: None = case()

    @staticmethod
    def Card(last_four: str) -> "Payment":
        return Payment(card=last_four)

    @staticmethod
    def Cash() -> "Payment":
        return Payment(cash=None)

def describe(payment: Payment) -> str:
    match payment:
        case Payment(tag="card", card=last_four):
            return f"Card ending in {last_four}"
        case Payment(tag="cash"):
            return "Cash"

assert describe(Payment.Card("1234")) == "Card ending in 1234"

# %% [markdown]
"""
Use a dataclass when one record shape is sufficient. Use a tagged union when different
cases carry different data or require different handling. Keep each case small and make
constructors descriptive. See [Tagged unions](reference_union) for serialization and
advanced API details.
"""
