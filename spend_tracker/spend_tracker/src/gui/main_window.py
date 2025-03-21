from typing import List, Set

import customtkinter as ctk

from spend_tracker.src.util.classes import GraphableData
from spend_tracker.src.gui.category_panel import CategoryPanel
from spend_tracker.src.gui.control_panel import ControlsPanel, StatsPanel
from spend_tracker.src.gui.plot_manager import PlotManager


class SpendingVisualizer(ctk.CTk):
    """Main window for the spending visualization application"""

    def __init__(self, graphable_data: GraphableData):
        super().__init__()

        # Initialize app appearance
        ctk.set_appearance_mode("system")  # Use system theme
        ctk.set_default_color_theme("blue")

        self.title("Spending Visualizer")
        self.geometry("1400x900")
        self.minsize(900, 600)

        # Store data and initialize components
        self.graphable_data = graphable_data
        self._setup_ui()

    def _setup_ui(self):
        """Setup the main UI layout"""
        # Create main grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        self.grid_rowconfigure(0, weight=1)

        # Left panel for controls and categories
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_panel.grid_rowconfigure(0, weight=2)
        left_panel.grid_rowconfigure(1, weight=5)
        left_panel.grid_rowconfigure(2, weight=3)
        left_panel.grid_columnconfigure(0, weight=1)

        # Right panel for plots
        plot_panel = ctk.CTkFrame(self)
        plot_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Initialize the plot manager
        self.plot_manager = PlotManager(plot_panel, self.graphable_data)
        self.plot_manager.canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # Controls panel
        self.controls = ControlsPanel(
            left_panel,
            on_view_change=self._handle_view_change,
            on_total_toggle=self._handle_total_toggle,
            on_outlier_change=self._handle_outlier_change,
            on_overlay_toggle=self._handle_overlay_toggle,
            on_year_change=self._handle_year_change,
            on_month_change=self._handle_month_change,
            years=self.plot_manager.years,
        )
        self.controls.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Category panel
        self.category_panel = CategoryPanel(
            left_panel,
            categories=self.plot_manager.all_categories,
            category_colors=self.plot_manager.category_colors,
            on_category_toggle=self._handle_category_toggle,
        )
        self.category_panel.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Stats panel
        self.stats_panel = StatsPanel(left_panel)
        self.stats_panel.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        # Initial plot and stats update
        self._update_display()

    def _handle_view_change(self, view_mode: str):
        """Handle change between month/week view"""
        self.plot_manager.view_mode = view_mode
        self._update_display()

    def _handle_total_toggle(self, show_total: bool):
        """Handle toggling total spending view"""
        self.plot_manager.show_total = show_total
        self._update_display()

    def _handle_outlier_change(self, threshold: int):
        """Handle outlier threshold change"""
        self.plot_manager.outlier_threshold = threshold
        self._update_display()

    def _handle_overlay_toggle(self, overlay: bool):
        """Handle overlay toggle"""
        self.plot_manager.overlay_plots = overlay
        self._update_display()

    def _handle_year_change(self, year: int):
        """Handle year selection change"""
        self.plot_manager.current_year_filter = year
        self._update_display()

    def _handle_month_change(self, month: int):
        """Handle month selection change"""
        self.plot_manager.current_month_filter = month
        self._update_display()

    def _handle_category_toggle(self, selected_categories: Set[str]):
        """Handle category visibility toggle"""
        self.plot_manager.visible_categories = selected_categories
        self._update_display()

    def _update_display(self):
        """Update plot and statistics display"""
        self.plot_manager.update_plot()
        averages = self.plot_manager.calculate_averages()
        self.stats_panel.update_stats(averages)


def run_visualizer(graphable_data: GraphableData):
    """Run the spending visualizer application"""
    app = SpendingVisualizer(graphable_data)
    app.mainloop()
