from datetime import datetime
from typing import Dict, List, Set, Tuple

import numpy as np

from spend_tracker.src.util.classes import CC_Transaction, GraphableData


class TableDataManager:
    """Manages data processing for tabular spending view"""

    def __init__(self, graphable_data: GraphableData):
        self.graphable_data = graphable_data
        self.outlier_threshold = 100  # Default percentage (no filtering)
        self.visible_categories = self._get_all_categories()

    def _get_all_categories(self) -> Set[str]:
        """Extract all unique categories from the data"""
        categories = set()

        for period in self.graphable_data.months:
            categories.update(period.categories.keys())

        return categories

    def _get_total_months_count(self) -> int:
        """Get the total number of months in the dataset"""
        if not self.graphable_data.months:
            return 1  # Avoid division by zero

        # Count unique months in the data
        unique_months = set()
        for month_period in self.graphable_data.months:
            month_key = month_period.start_date.strftime("%Y-%m")
            unique_months.add(month_key)

        return len(unique_months)

    def get_category_monthly_averages(self) -> Dict[str, Dict]:
        """
        Calculate monthly averages for each category with outlier filtering
        Returns a dictionary with category stats including:
        - average: monthly average spending
        - transactions: filtered transactions
        - outliers: transactions removed as outliers
        """
        result = {}
        total_months = self._get_total_months_count()

        # Process only visible categories
        for category in self.visible_categories:
            all_transactions = []

            # Collect all transactions for this category
            for month in self.graphable_data.months:
                if category in month.categories:
                    cat_data = month.categories[category]
                    all_transactions.extend(cat_data.transactions)

            # Skip if no transactions
            if not all_transactions:
                continue

            # Calculate mean spending per transaction (for outlier detection)
            amounts = [tx.amount for tx in all_transactions]
            mean_amount = np.mean(amounts)

            # Apply outlier threshold
            if self.outlier_threshold < 100:
                threshold_value = mean_amount * (1 + (self.outlier_threshold / 100))
                filtered_transactions = [
                    tx for tx in all_transactions if tx.amount <= threshold_value
                ]
                outliers = [
                    tx for tx in all_transactions if tx.amount > threshold_value
                ]
            else:
                filtered_transactions = all_transactions
                outliers = []

            # Calculate monthly average by dividing by total months in dataset
            filtered_total = sum(tx.amount for tx in filtered_transactions)
            monthly_avg = filtered_total / total_months

            # Store results
            result[category] = {
                "average": monthly_avg,
                "transactions": filtered_transactions,
                "outliers": outliers,
                "total": filtered_total,
            }

        return result

    def calculate_total_monthly_spend(self) -> float:
        """Calculate the total monthly spending across all visible categories"""
        category_data = self.get_category_monthly_averages()
        return sum(data["average"] for data in category_data.values())
