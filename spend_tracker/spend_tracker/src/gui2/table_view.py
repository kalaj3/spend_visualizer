from typing import Callable, Dict, List

import customtkinter as ctk

from spend_tracker.src.util.classes import CC_Transaction


class OutlierDialog(ctk.CTkToplevel):
    """Dialog to display outlier transactions"""

    def __init__(self, parent, category: str, outliers: List[CC_Transaction]):
        super().__init__(parent)

        # Configure dialog
        self.title(f"Outliers - {category}")
        self.geometry("600x400")
        self.resizable(True, True)

        # Add components
        self._setup_ui(category, outliers)

    def _setup_ui(self, category: str, outliers: List[CC_Transaction]):
        """Setup the dialog UI"""
        # Title
        ctk.CTkLabel(
            self,
            text=f"Outlier Transactions for {category}",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=(10, 5))

        # Description
        ctk.CTkLabel(
            self, text="These transactions were filtered out as outliers."
        ).pack(pady=(0, 10))

        # Create table headers
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollable frame for transactions
        scrollable_frame = ctk.CTkScrollableFrame(table_frame)
        scrollable_frame.pack(fill="both", expand=True)

        # Create grid for table
        scrollable_frame.columnconfigure(0, weight=2)  # Date
        scrollable_frame.columnconfigure(1, weight=5)  # Description
        scrollable_frame.columnconfigure(2, weight=1)  # Amount

        # Headers
        ctk.CTkLabel(
            scrollable_frame, text="Date", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(
            scrollable_frame, text="Description", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(
            scrollable_frame, text="Amount", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, sticky="e", padx=5, pady=2)

        # Separator
        separator = ctk.CTkFrame(scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # Add data rows
        sorted_outliers = sorted(outliers, key=lambda tx: tx.amount, reverse=True)

        for i, tx in enumerate(sorted_outliers):
            row = i + 2  # +2 for header and separator

            # Date
            ctk.CTkLabel(scrollable_frame, text=tx.date.strftime("%Y-%m-%d")).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )

            # Description
            ctk.CTkLabel(scrollable_frame, text=tx.description).grid(
                row=row, column=1, sticky="w", padx=5, pady=2
            )

            # Amount
            ctk.CTkLabel(scrollable_frame, text=f"${tx.amount:.2f}").grid(
                row=row, column=2, sticky="e", padx=5, pady=2
            )

        # Close button
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=10)


class TableView(ctk.CTkFrame):
    """Table view for category spending data"""

    def __init__(self, master):
        super().__init__(master)

        self.categories_data = {}
        self._setup_ui()

    def _setup_ui(self):
        """Setup the table UI"""
        # Table container
        self.table_container = ctk.CTkScrollableFrame(self)
        self.table_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure grid columns
        self.table_container.columnconfigure(0, weight=3)  # Category
        self.table_container.columnconfigure(1, weight=2)  # Monthly Average
        self.table_container.columnconfigure(2, weight=1)  # Actions

        # Table headers
        self._create_headers()

    def _create_headers(self):
        """Create table headers"""
        # Category header
        ctk.CTkLabel(
            self.table_container, text="Category", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=5)

        # Monthly Average header
        ctk.CTkLabel(
            self.table_container,
            text="Monthly Average",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Actions header
        ctk.CTkLabel(
            self.table_container, text="Actions", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, sticky="w", padx=5, pady=5)

        # Separator
        separator = ctk.CTkFrame(self.table_container, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

    def update_table(
        self,
        categories_data: Dict[str, Dict],
        show_outliers_callback: Callable,
        show_transactions_callback: Callable,
    ):
        """Update the table with new data"""
        self.categories_data = categories_data

        # Clear existing table rows (preserve headers)
        for widget in self.table_container.winfo_children():
            grid_info = widget.grid_info()
            if grid_info and int(grid_info["row"]) >= 2:
                widget.destroy()

        # Handle empty data case
        if not categories_data:
            ctk.CTkLabel(self.table_container, text="No data to display.").grid(
                row=2, column=0, columnspan=3, pady=20
            )
            return

        # Add data rows
        sorted_categories = sorted(
            categories_data.items(), key=lambda x: x[1]["average"], reverse=True
        )

        # Add data rows
        for i, (category, data) in enumerate(sorted_categories):
            row = i + 2  # +2 for header and separator

            # Category name
            ctk.CTkLabel(self.table_container, text=category).grid(
                row=row, column=0, sticky="w", padx=5, pady=5
            )

            # Monthly average with transaction count
            tx_count = len(data["transactions"])
            avg_text = f"${data['average']:.2f} ({tx_count} transactions)"
            ctk.CTkLabel(self.table_container, text=avg_text).grid(
                row=row, column=1, sticky="w", padx=5, pady=5
            )

            # Actions frame for buttons
            actions_frame = ctk.CTkFrame(self.table_container)
            actions_frame.grid(row=row, column=2, padx=5, pady=2)

            # Button to view regular transactions
            transactions_button = ctk.CTkButton(
                actions_frame,
                text="Transactions",
                width=95,
                command=lambda cat=category: show_transactions_callback(cat),
            )
            transactions_button.pack(side="left", padx=2, pady=2)

            # Button to view outlier transactions
            has_outliers = len(data["outliers"]) > 0
            outlier_button = ctk.CTkButton(
                actions_frame,
                text="Outliers",
                width=80,
                state="normal" if has_outliers else "disabled",
                command=lambda cat=category: show_outliers_callback(cat),
            )
            outlier_button.pack(side="right", padx=2, pady=2)

        # Add total row
        total_row = len(sorted_categories) + 2

        # Separator before total
        separator = ctk.CTkFrame(self.table_container, height=1, fg_color="gray")
        separator.grid(
            row=total_row, column=0, columnspan=3, sticky="ew", padx=5, pady=5
        )

        # Calculate total monthly average
        total_avg = sum(data["average"] for _, data in sorted_categories)

        # Total label
        ctk.CTkLabel(
            self.table_container, text="MONTHLY TOTAL", font=ctk.CTkFont(weight="bold")
        ).grid(row=total_row + 1, column=0, sticky="w", padx=5, pady=5)

        # Total monthly amount
        ctk.CTkLabel(
            self.table_container,
            text=f"${total_avg:.2f}",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=total_row + 1, column=1, sticky="w", padx=5, pady=5)

        # Add yearly projection
        yearly_projection = total_avg * 12

        ctk.CTkLabel(
            self.table_container,
            text="YEARLY PROJECTION",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=total_row + 2, column=0, sticky="w", padx=5, pady=5)

        # Yearly amount
        ctk.CTkLabel(
            self.table_container,
            text=f"${yearly_projection:.2f}",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=total_row + 2, column=1, sticky="w", padx=5, pady=5)


class TransactionsDialog(ctk.CTkToplevel):
    """Dialog to display category transactions"""

    def __init__(
        self,
        parent,
        category: str,
        transactions: List[CC_Transaction],
        is_outliers: bool = False,
    ):
        super().__init__(parent)

        # Configure dialog
        self.title(f"{'Outliers' if is_outliers else 'Transactions'} - {category}")
        self.geometry("700x500")
        self.resizable(True, True)

        # Add components
        self._setup_ui(category, transactions, is_outliers)

    def _setup_ui(
        self, category: str, transactions: List[CC_Transaction], is_outliers: bool
    ):
        """Setup the dialog UI"""
        # Title
        title_text = (
            f"{'Outlier' if is_outliers else 'Regular'} Transactions for {category}"
        )
        ctk.CTkLabel(
            self, text=title_text, font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Description
        description = (
            "These transactions were filtered out as outliers."
            if is_outliers
            else "These are the regular transactions included in the average calculation."
        )
        ctk.CTkLabel(self, text=description).pack(pady=(0, 10))

        # Create table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollable frame for transactions
        scrollable_frame = ctk.CTkScrollableFrame(table_frame)
        scrollable_frame.pack(fill="both", expand=True)

        # Create grid for table
        scrollable_frame.columnconfigure(0, weight=2)  # Date
        scrollable_frame.columnconfigure(1, weight=5)  # Description
        scrollable_frame.columnconfigure(2, weight=1)  # Amount

        # Headers
        ctk.CTkLabel(
            scrollable_frame, text="Date", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(
            scrollable_frame, text="Description", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(
            scrollable_frame, text="Amount", font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=2, sticky="e", padx=5, pady=2)

        # Separator
        separator = ctk.CTkFrame(scrollable_frame, height=1, fg_color="gray")
        separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)

        # Sort transactions by amount (descending for outliers, ascending for regular)
        sort_reverse = is_outliers
        sorted_transactions = sorted(
            transactions, key=lambda tx: tx.amount, reverse=sort_reverse
        )

        # Add data rows
        for i, tx in enumerate(sorted_transactions):
            row = i + 2  # +2 for header and separator

            # Date
            ctk.CTkLabel(scrollable_frame, text=tx.date.strftime("%Y-%m-%d")).grid(
                row=row, column=0, sticky="w", padx=5, pady=2
            )

            # Description
            ctk.CTkLabel(scrollable_frame, text=tx.description).grid(
                row=row, column=1, sticky="w", padx=5, pady=2
            )

            # Amount
            ctk.CTkLabel(scrollable_frame, text=f"${tx.amount:.2f}").grid(
                row=row, column=2, sticky="e", padx=5, pady=2
            )

        # Summary section
        summary_frame = ctk.CTkFrame(self)
        summary_frame.pack(fill="x", padx=10, pady=5)

        # Transaction count
        ctk.CTkLabel(
            summary_frame, text=f"Total transactions: {len(transactions)}"
        ).pack(side="left", padx=10)

        # Total amount
        total_amount = sum(tx.amount for tx in transactions)
        ctk.CTkLabel(summary_frame, text=f"Total amount: ${total_amount:.2f}").pack(
            side="left", padx=10
        )

        # Close button
        ctk.CTkButton(self, text="Close", command=self.destroy).pack(pady=10)
