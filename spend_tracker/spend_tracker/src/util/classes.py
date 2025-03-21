from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CC_Transaction:
    date: datetime
    description: str
    category: str
    amount: float
    source: str
    outlier: bool | None = None


@dataclass
class CategoryPeriodData:
    """Data for a specific category within a time period"""

    total_spend: float = 0.0
    transactions: list[CC_Transaction] = field(default_factory=list)

    def add_transaction(self, transaction: CC_Transaction) -> None:
        """Add a transaction to this category period and update total spend"""
        self.transactions.append(transaction)
        self.total_spend += transaction.amount


@dataclass
class PeriodData:
    """Data for a specific time period across all categories"""

    start_date: datetime
    end_date: datetime
    categories: dict[str, CategoryPeriodData] = field(default_factory=dict)


@dataclass
class GraphableData:
    """Structure containing transaction data organized for graphing"""

    months: list[PeriodData] = field(default_factory=list)
    weeks: list[PeriodData] = field(default_factory=list)
