from typing import Callable, Dict, List, Set

import customtkinter as ctk
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CategoryPanel(ctk.CTkFrame):
    """Panel for category selection and visualization"""

    def __init__(
        self,
        master,
        categories: List[str],
        category_colors: Dict[str, tuple],
        on_category_toggle: Callable,
    ):
        super().__init__(master, corner_radius=10)

        self.categories = categories
        self.category_colors = category_colors
        self.on_category_toggle = on_category_toggle
        self.category_buttons = {}
        self.selected_categories = set(categories)  # All selected by default

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the panel UI"""
        # Panel title
        ctk.CTkLabel(
            self, text="Categories", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Buttons frame with scrollable view
        container = ctk.CTkFrame(self)
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # Scrollable frame for categories
        scrollable_frame = ctk.CTkScrollableFrame(container)
        scrollable_frame.pack(fill="both", expand=True)

        # Create toggle buttons for each category
        for category in self.categories:
            color = self.category_colors.get(category, (0, 0, 0))

            # Convert matplotlib RGBA to hex
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
            )

            button = ctk.CTkButton(
                scrollable_frame,
                text=category,
                fg_color=hex_color,
                text_color="white" if sum(color[:3]) < 1.5 else "black",
                command=lambda cat=category: self._toggle_category(cat),
            )
            button.pack(fill="x", padx=5, pady=2)
            self.category_buttons[category] = button

        # Select/Deselect all buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkButton(button_frame, text="Select All", command=self.select_all).pack(
            side="left", fill="x", expand=True, padx=2
        )

        ctk.CTkButton(
            button_frame, text="Deselect All", command=self.deselect_all
        ).pack(side="right", fill="x", expand=True, padx=2)

    def _toggle_category(self, category: str):
        """Toggle visibility of a category"""
        button = self.category_buttons[category]

        if category in self.selected_categories:
            self.selected_categories.remove(category)
            button.configure(fg_color="gray")
        else:
            self.selected_categories.add(category)
            color = self.category_colors.get(category, (0, 0, 0))
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
            )
            button.configure(fg_color=hex_color)

        # Notify parent about the change
        self.on_category_toggle(self.selected_categories)

    def select_all(self):
        """Select all categories"""
        for category in self.categories:
            if category not in self.selected_categories:
                self._toggle_category(category)

    def deselect_all(self):
        """Deselect all categories"""
        for category in list(self.selected_categories):
            self._toggle_category(category)
