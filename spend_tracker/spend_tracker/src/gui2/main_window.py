from typing import Set

import customtkinter as ctk

from spend_tracker.src.gui2.data_manager import TableDataManager
from spend_tracker.src.gui2.filter_panel import FilterPanel
from spend_tracker.src.gui2.table_view import (
    OutlierDialog,
    TableView,
    TransactionsDialog,
)
from spend_tracker.src.util.classes import CC_Transaction, GraphableData


class SpendingTableView(ctk.CTk):
    """Main window for the spending table view application"""

    def __init__(self, graphable_data: GraphableData):
        super().__init__()

        # Initialize app appearance
        ctk.set_appearance_mode("system")  # Use system theme
        ctk.set_default_color_theme("blue")

        self.title("Spending Table View")
        self.geometry("1000x800")
        self.minsize(800, 600)

        # Store data and initialize components
        self.graphable_data = graphable_data
        self.data_manager = TableDataManager(graphable_data)

        # Track open dialogs
        self.open_dialogs = []

        # Setup UI
        self._setup_ui()

        # Initial update
        self._update_table()

    def _setup_ui(self):
        """Setup the main UI layout"""
        # Create main grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        # Left panel for filters
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Right panel for table
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Initialize filter panel
        self.filter_panel = FilterPanel(
            left_panel,
            categories=self.data_manager._get_all_categories(),
            on_category_toggle=self._handle_category_toggle,
            on_outlier_change=self._handle_outlier_change,
        )
        self.filter_panel.pack(fill="both", expand=True, padx=5, pady=5)

        # Add summary frame in left panel
        self.summary_frame = ctk.CTkFrame(left_panel)
        self.summary_frame.pack(fill="x", padx=5, pady=5)

        # Add summary label
        ctk.CTkLabel(
            self.summary_frame,
            text="Monthly Spending Summary",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=(10, 5))

        # Create labels for monthly/yearly totals
        self.monthly_total_label = ctk.CTkLabel(
            self.summary_frame, text="Monthly Total: $0.00"
        )
        self.monthly_total_label.pack(anchor="w", padx=10, pady=2)

        self.yearly_total_label = ctk.CTkLabel(
            self.summary_frame, text="Yearly Projection: $0.00"
        )
        self.yearly_total_label.pack(anchor="w", padx=10, pady=2)

        # Table header
        ctk.CTkLabel(
            right_panel,
            text="Monthly Average Spending by Category",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(10, 5))

        # Description text
        ctk.CTkLabel(
            right_panel, text="Values shown are monthly averages with outliers removed."
        ).pack(pady=(0, 10))

        # Initialize table view
        self.table_view = TableView(right_panel)
        self.table_view.pack(fill="both", expand=True, padx=5, pady=5)

    def _handle_category_toggle(self, selected_categories: Set[str]):
        """Handle category selection changes"""
        self.data_manager.visible_categories = selected_categories
        self._update_table()

    def _handle_outlier_change(self, threshold: int):
        """Handle outlier threshold changes"""
        self.data_manager.outlier_threshold = threshold
        self._update_table()

    def _update_table(self):
        """Update the table with current data and settings"""
        # Calculate current data with outlier filtering
        categories_data = self.data_manager.get_category_monthly_averages()

        # Update the table
        self.table_view.update_table(
            categories_data, self._show_outliers_dialog, self._show_transactions_dialog
        )

        # Calculate monthly total
        monthly_total = sum(data["average"] for data in categories_data.values())
        yearly_total = monthly_total * 12

        # Update summary labels
        self.monthly_total_label.configure(text=f"Monthly Total: ${monthly_total:.2f}")
        self.yearly_total_label.configure(
            text=f"Yearly Projection: ${yearly_total:.2f}"
        )

    def _show_outliers_dialog(self, category: str):
        """Show dialog with outlier transactions for a category"""
        # Calculate current data to get outliers
        categories_data = self.data_manager.get_category_monthly_averages()
        total_months = self.data_manager._get_total_months_count()

        if category in categories_data:
            outliers = categories_data[category]["outliers"]

            if outliers:
                # Create and show dialog
                from spend_tracker.src.gui2.table_view import TransactionsDialog

                dialog = TransactionsDialog(
                    self,
                    category,
                    outliers,
                    is_outliers=True,
                    total_months=total_months,
                )
                dialog.grab_set()  # Make dialog modal
                self.open_dialogs.append(dialog)

                # Clean up closed dialogs
                self.open_dialogs = [d for d in self.open_dialogs if d.winfo_exists()]

    def _show_transactions_dialog(self, category: str):
        """Show dialog with regular transactions for a category"""
        # Calculate current data to get transactions
        categories_data = self.data_manager.get_category_monthly_averages()
        total_months = self.data_manager._get_total_months_count()

        if category in categories_data:
            transactions = categories_data[category]["transactions"]

            if transactions:
                # Create and show dialog
                from spend_tracker.src.gui2.table_view import TransactionsDialog

                dialog = TransactionsDialog(
                    self,
                    category,
                    transactions,
                    is_outliers=False,
                    total_months=total_months,
                )
                dialog.grab_set()  # Make dialog modal
                self.open_dialogs.append(dialog)

                # Clean up closed dialogs
                self.open_dialogs = [d for d in self.open_dialogs if d.winfo_exists()]


def run_table_view(graphable_data: GraphableData):
    """Run the spending table view application"""
    app = SpendingTableView(graphable_data)
    app.mainloop()
