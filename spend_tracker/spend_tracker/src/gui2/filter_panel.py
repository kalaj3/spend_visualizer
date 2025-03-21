from typing import Callable, List, Set

import customtkinter as ctk


class FilterPanel(ctk.CTkFrame):
    """Panel for category selection and outlier filtering"""

    def __init__(
        self,
        master,
        categories: List[str],
        on_category_toggle: Callable[[Set[str]], None],
        on_outlier_change: Callable[[int], None],
    ):
        super().__init__(master, corner_radius=10)

        self.categories = sorted(categories)
        self.on_category_toggle = on_category_toggle
        self.on_outlier_change = on_outlier_change
        self.selected_categories = set(categories)  # All selected by default
        self.category_checkboxes = {}

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the panel UI"""
        # Panel title
        ctk.CTkLabel(
            self, text="Filters", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Outlier filtering
        outlier_frame = ctk.CTkFrame(self)
        outlier_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(outlier_frame, text="Outlier Threshold (%):").pack(
            side="left", padx=5
        )

        self.outlier_var = ctk.StringVar(value="100")
        outlier_entry = ctk.CTkEntry(
            outlier_frame, width=60, textvariable=self.outlier_var
        )
        outlier_entry.pack(side="left", padx=5)

        outlier_apply = ctk.CTkButton(
            outlier_frame, text="Apply", width=60, command=self._handle_outlier_change
        )
        outlier_apply.pack(side="left", padx=5)

        outlier_reset = ctk.CTkButton(
            outlier_frame, text="Reset", width=60, command=self._reset_outlier
        )
        outlier_reset.pack(side="left", padx=5)

        # Category selection label
        ctk.CTkLabel(self, text="Categories:", anchor="w").pack(
            fill="x", padx=15, pady=(10, 0)
        )

        # Scrollable frame for categories
        categories_container = ctk.CTkScrollableFrame(self)
        categories_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Create checkboxes for each category
        for category in self.categories:
            checkbox_var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                categories_container,
                text=category,
                variable=checkbox_var,
                command=lambda cat=category, var=checkbox_var: self._toggle_category(
                    cat, var.get()
                ),
            )
            checkbox.pack(fill="x", padx=5, pady=2, anchor="w")
            self.category_checkboxes[category] = (checkbox, checkbox_var)

        # Select/Deselect all buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(button_frame, text="Select All", command=self.select_all).pack(
            side="left", fill="x", expand=True, padx=2
        )

        ctk.CTkButton(
            button_frame, text="Deselect All", command=self.deselect_all
        ).pack(side="right", fill="x", expand=True, padx=2)

    def _toggle_category(self, category: str, is_selected: bool):
        """Toggle a category's selection state"""
        if is_selected:
            self.selected_categories.add(category)
        else:
            self.selected_categories.discard(category)

        # Notify parent
        self.on_category_toggle(self.selected_categories)

    def _handle_outlier_change(self):
        """Handle outlier threshold change"""
        try:
            value = int(self.outlier_var.get())
            if value >= 0:
                self.on_outlier_change(value)
            else:
                # Reset to 100 if invalid
                self.outlier_var.set("100")
                self.on_outlier_change(100)
        except ValueError:
            # Reset to 100 if invalid
            self.outlier_var.set("100")
            self.on_outlier_change(100)

    def _reset_outlier(self):
        """Reset outlier threshold to include all data"""
        self.outlier_var.set("100")
        self.on_outlier_change(100)

    def select_all(self):
        """Select all categories"""
        for category in self.categories:
            checkbox, var = self.category_checkboxes[category]
            var.set(True)
            if category not in self.selected_categories:
                self.selected_categories.add(category)

        self.on_category_toggle(self.selected_categories)

    def deselect_all(self):
        """Deselect all categories"""
        for category in self.categories:
            checkbox, var = self.category_checkboxes[category]
            var.set(False)

        self.selected_categories.clear()
        self.on_category_toggle(self.selected_categories)
