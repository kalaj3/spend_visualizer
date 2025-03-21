from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from spend_tracker.src.util.classes import CC_Transaction, GraphableData


class PlotManager:
    """Manages the matplotlib plots and data processing for visualization"""

    def __init__(self, master_frame, graphable_data: GraphableData):
        self.graphable_data = graphable_data
        self.master_frame = master_frame

        # Create figure and canvas
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=master_frame)
        self.canvas_widget = self.canvas.get_tk_widget()

        # Extract all categories from data
        self.all_categories = self._get_all_categories()

        # Initialize plot settings
        self.outlier_threshold = 100  # Default: include all transactions
        self.view_mode = "month"  # "month" or "week"
        self.show_total = False
        self.overlay_plots = False
        self.visible_categories = set(self.all_categories)

        # Time navigation
        self.years = self._get_unique_years()
        self.months = list(range(1, 13))  # 1-12 for months
        self.current_year_filter = None  # None means all years
        self.current_month_filter = None  # None means all months

        # Color mapping for consistent category colors
        self.category_colors = {}
        self._assign_category_colors()

    def _get_all_categories(self) -> List[str]:
        """Extract all unique categories from the data"""
        categories = set()

        for period in self.graphable_data.months:
            categories.update(period.categories.keys())

        return sorted(list(categories))

    def _get_unique_years(self) -> List[int]:
        """Get the unique years in the data"""
        years = set()
        for period in self.graphable_data.months:
            years.add(period.start_date.year)
        return sorted(list(years))

    def _assign_category_colors(self) -> None:
        """Assign consistent colors to categories"""
        # Generate color map using a colormap
        cmap = plt.cm.get_cmap("tab20", len(self.all_categories))

        for i, category in enumerate(self.all_categories):
            self.category_colors[category] = cmap(i)

    def update_plot(self) -> None:
        """Update the plot based on current settings"""
        self.ax.clear()

        # Get data based on current view mode
        periods = (
            self.graphable_data.months
            if self.view_mode == "month"
            else self.graphable_data.weeks
        )

        # Filter periods by year/month if specified
        filtered_periods = self._filter_periods(periods)

        if self.show_total:
            self._plot_total_spending(filtered_periods)
        else:
            self._plot_categories(filtered_periods)

        # Set labels and format
        self.ax.set_ylabel("Spending ($)")
        time_unit = "Month" if self.view_mode == "month" else "Week"
        self.ax.set_xlabel(f"{time_unit}")
        self.ax.set_title(f"Spending by {time_unit}")

        # Format x-axis dates
        if self.view_mode == "month":
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        else:
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

        self.fig.autofmt_xdate()  # Rotate date labels
        self.ax.grid(True, linestyle="--", alpha=0.7)

        if not self.show_total and len(self.visible_categories) > 0:
            self.ax.legend()

        self.canvas.draw()

    def _filter_periods(self, periods):
        """Filter periods based on year and month filters"""
        if not self.current_year_filter and not self.current_month_filter:
            return periods

        filtered = []
        for period in periods:
            include = True

            if (
                self.current_year_filter
                and period.start_date.year != self.current_year_filter
            ):
                include = False

            if (
                self.current_month_filter
                and period.start_date.month != self.current_month_filter
            ):
                include = False

            if include:
                filtered.append(period)

        return filtered

    def _plot_categories(self, periods):
        """Plot each category as a separate line"""
        # For each visible category
        for category in self.visible_categories:
            dates = []
            values = []

            # Collect data points
            for period in periods:
                if category in period.categories:
                    cat_data = period.categories[category]

                    # Apply outlier filtering if needed
                    included_transactions = self._filter_outliers(cat_data.transactions)

                    # Only include if we have transactions after filtering
                    if included_transactions:
                        period_total = sum(tx.amount for tx in included_transactions)
                        dates.append(period.start_date)
                        values.append(period_total)

            # Plot if we have data points
            if dates and values:
                self.ax.plot(
                    dates,
                    values,
                    "o-",
                    label=category,
                    color=self.category_colors.get(category),
                )

    def _plot_total_spending(self, periods):
        """Plot the total spending across all visible categories"""
        dates = []
        totals = []

        for period in periods:
            period_total = 0
            for category, cat_data in period.categories.items():
                if category in self.visible_categories:
                    # Apply outlier filtering
                    included_transactions = self._filter_outliers(cat_data.transactions)
                    period_total += sum(tx.amount for tx in included_transactions)

            if period_total > 0:
                dates.append(period.start_date)
                totals.append(period_total)

        if dates and totals:
            self.ax.plot(dates, totals, "o-", color="blue", linewidth=2, label="Total")

    def _filter_outliers(
        self, transactions: List[CC_Transaction]
    ) -> List[CC_Transaction]:
        """Filter transactions based on outlier threshold"""
        if self.outlier_threshold >= 100:
            return transactions

        # Calculate threshold values for this set of transactions
        if not transactions:
            return []

        amounts = [tx.amount for tx in transactions]
        threshold_value = np.percentile(amounts, self.outlier_threshold)

        # Return transactions below the threshold
        return [tx for tx in transactions if tx.amount <= threshold_value]

    def calculate_averages(self) -> Dict[str, float]:
        """Calculate average spending for each visible category"""
        averages = {}

        for category in self.visible_categories:
            periods = (
                self.graphable_data.months
                if self.view_mode == "month"
                else self.graphable_data.weeks
            )
            filtered_periods = self._filter_periods(periods)

            total = 0
            count = 0

            for period in filtered_periods:
                if category in period.categories:
                    cat_data = period.categories[category]
                    included_transactions = self._filter_outliers(cat_data.transactions)

                    if included_transactions:
                        period_total = sum(tx.amount for tx in included_transactions)
                        total += period_total
                        count += 1

            if count > 0:
                averages[category] = total / count
            else:
                averages[category] = 0

        return averages
