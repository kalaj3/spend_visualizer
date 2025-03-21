from typing import Callable, Dict, List

import customtkinter as ctk


class ControlsPanel(ctk.CTkFrame):
    """Panel for visualization controls"""

    def __init__(
        self,
        master,
        on_view_change: Callable,
        on_total_toggle: Callable,
        on_outlier_change: Callable,
        on_overlay_toggle: Callable,
        on_year_change: Callable,
        on_month_change: Callable,
        years: List[int],
    ):
        super().__init__(master, corner_radius=10)

        self.on_view_change = on_view_change
        self.on_total_toggle = on_total_toggle
        self.on_outlier_change = on_outlier_change
        self.on_overlay_toggle = on_overlay_toggle
        self.on_year_change = on_year_change
        self.on_month_change = on_month_change
        self.years = years

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the panel UI"""
        # Panel title
        ctk.CTkLabel(
            self, text="Controls", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Time period frame
        period_frame = ctk.CTkFrame(self)
        period_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(period_frame, text="Time Period:").pack(side="left", padx=5)

        self.view_var = ctk.StringVar(value="month")
        month_radio = ctk.CTkRadioButton(
            period_frame,
            text="Monthly",
            variable=self.view_var,
            value="month",
            command=self._handle_view_change,
        )
        month_radio.pack(side="left", padx=10)

        week_radio = ctk.CTkRadioButton(
            period_frame,
            text="Weekly",
            variable=self.view_var,
            value="week",
            command=self._handle_view_change,
        )
        week_radio.pack(side="left", padx=10)

        # Overlay option
        overlay_frame = ctk.CTkFrame(self)
        overlay_frame.pack(fill="x", padx=10, pady=5)

        self.overlay_var = ctk.BooleanVar(value=False)
        overlay_checkbox = ctk.CTkCheckBox(
            overlay_frame,
            text="Overlay Week/Month",
            variable=self.overlay_var,
            command=self._handle_overlay_toggle,
        )
        overlay_checkbox.pack(side="left", padx=5)

        # Total spending toggle
        total_frame = ctk.CTkFrame(self)
        total_frame.pack(fill="x", padx=10, pady=5)

        self.total_var = ctk.BooleanVar(value=False)
        total_checkbox = ctk.CTkCheckBox(
            total_frame,
            text="Show Total Spending",
            variable=self.total_var,
            command=self._handle_total_toggle,
        )
        total_checkbox.pack(side="left", padx=5)

        # Outlier filtering
        outlier_frame = ctk.CTkFrame(self)
        outlier_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(outlier_frame, text="Outlier Threshold (%):").pack(
            side="left", padx=5
        )

        self.outlier_var = ctk.StringVar(value="100")
        outlier_entry = ctk.CTkEntry(
            outlier_frame, width=50, textvariable=self.outlier_var
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

        # Time navigation controls
        time_frame = ctk.CTkFrame(self)
        time_frame.pack(fill="x", padx=10, pady=5)

        # Year selection
        year_frame = ctk.CTkFrame(time_frame)
        year_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(year_frame, text="Year:").pack(side="left", padx=5)

        year_options = ["All Years"] + [str(year) for year in self.years]
        self.year_var = ctk.StringVar(value="All Years")
        year_dropdown = ctk.CTkOptionMenu(
            year_frame,
            values=year_options,
            variable=self.year_var,
            command=self._handle_year_change,
        )
        year_dropdown.pack(side="left", padx=5, fill="x", expand=True)

        # Month selection
        month_frame = ctk.CTkFrame(time_frame)
        month_frame.pack(fill="x", pady=2)

        ctk.CTkLabel(month_frame, text="Month:").pack(side="left", padx=5)

        month_names = [
            "All Months",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        self.month_var = ctk.StringVar(value="All Months")
        month_dropdown = ctk.CTkOptionMenu(
            month_frame,
            values=month_names,
            variable=self.month_var,
            command=self._handle_month_change,
        )
        month_dropdown.pack(side="left", padx=5, fill="x", expand=True)

    def _handle_view_change(self):
        """Handle view mode change"""
        self.on_view_change(self.view_var.get())

    def _handle_total_toggle(self):
        """Handle total spending toggle"""
        self.on_total_toggle(self.total_var.get())

    def _handle_outlier_change(self):
        """Handle outlier threshold change"""
        try:
            value = int(self.outlier_var.get())
            if 1 <= value <= 100:
                self.on_outlier_change(value)
            else:
                # Reset to 100 if out of range
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

    def _handle_overlay_toggle(self):
        """Handle overlay toggle"""
        self.on_overlay_toggle(self.overlay_var.get())

    def _handle_year_change(self, value):
        """Handle year selection change"""
        year = None if value == "All Years" else int(value)
        self.on_year_change(year)

    def _handle_month_change(self, value):
        """Handle month selection change"""
        month_names = [
            "All Months",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        month = None if value == "All Months" else month_names.index(value)
        self.on_month_change(month)


class StatsPanel(ctk.CTkFrame):
    """Panel for displaying statistics"""

    def __init__(self, master):
        super().__init__(master, corner_radius=10)

        # Setup UI
        self._setup_ui()

    def _setup_ui(self):
        """Setup the panel UI"""
        # Panel title
        ctk.CTkLabel(
            self, text="Statistics", font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(10, 5))

        # Stats content
        self.stats_frame = ctk.CTkScrollableFrame(self)
        self.stats_frame.pack(fill="both", expand=True, padx=5, pady=5)

    def update_stats(self, averages: Dict[str, float]):
        """Update the statistics display with new averages"""
        # Clear existing content
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Add header
        ctk.CTkLabel(
            self.stats_frame,
            text="Category Average Spending",
            font=ctk.CTkFont(weight="bold"),
        ).pack(anchor="w", pady=(0, 5))

        # Add averages
        if not averages:
            ctk.CTkLabel(self.stats_frame, text="No data available").pack(anchor="w")
        else:
            for category, avg in sorted(
                averages.items(), key=lambda x: x[1], reverse=True
            ):
                ctk.CTkLabel(self.stats_frame, text=f"{category}: ${avg:.2f}").pack(
                    anchor="w"
                )
