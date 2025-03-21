import os

from spend_tracker.src.data_mgr.csv_reader import prepare_data, read_csv
from spend_tracker.src.data_mgr.outlier_filter import filter_outliers
from spend_tracker.src.data_mgr.restructure_data_for_graphing import (
    restructure_for_graphing,
)

# Convert to graphable format
test_category = "Drugs"


def test_csv_reader():
    # Automatically manage the file path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "jk_full_cc_history.csv")

    # Read transactions from CSV
    transactions = read_csv(file_path)

    # Prepare data grouped by category
    data_by_category = prepare_data(transactions)

    # Example: Access transactions for a specific category
    print(f"Full csv for {test_category}:")
    print(data_by_category.get(test_category, []))

    return data_by_category.get(test_category, [])


def test_outlier():

    # Prepare data grouped by category
    data_by_category = test_csv_reader()

    # Filter outliers with a 50% threshold
    filtered_data, outliers = filter_outliers(data_by_category, 1)

    # Print filtered data and outliers for a specific category
    print("Filtered Data (Non-Outliers):")
    print(filtered_data)

    print("\nOutliers:")

    print(outliers)


def test_graphable_data():
    # Get transactions
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "jk_full_cc_history.csv")
    transactions = read_csv(file_path)

    graphable_data = restructure_for_graphing(transactions)

    # Example: Print monthly spending by category
    print("\nMonthly spending by category:")
    for i, month in enumerate(graphable_data.months):
        print(f"\nMonth {i+1}: {month.start_date.strftime('%b %Y')}")
        for category, data in month.categories.items():
            print(
                f"  {category}: ${data.total_spend:.2f} ({len(data.transactions)} transactions)"
            )

    # Example: Print weekly spending for a specific category
    category_to_check = test_category  # Using the existing test_category from main.py
    print(f"\nWeekly spending for {category_to_check}:")
    for i, week in enumerate(graphable_data.weeks):
        if category_to_check in week.categories:
            cat_data = week.categories[category_to_check]
            print(
                f"  Week {i+1} ({week.start_date.strftime('%Y-%m-%d')} to {week.end_date.strftime('%Y-%m-%d')}): ${cat_data.total_spend:.2f}"
            )

    return graphable_data


def test_gui_past():
    """Test the GUI visualization"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "jk_full_cc_history.csv")
    transactions = read_csv(file_path)

    # Convert to graphable format
    graphable_data = restructure_for_graphing(transactions)

    # Launch GUI
    from spend_tracker.src.gui.main_window import run_visualizer

    run_visualizer(graphable_data)


def test_table_gui():
    """Test the table GUI visualization"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "data", "jk_full_cc_history.csv")
    transactions = read_csv(file_path)

    # Convert to graphable format
    graphable_data = restructure_for_graphing(transactions)

    # Launch GUI
    from spend_tracker.src.gui2.main_window import run_table_view

    run_table_view(graphable_data)
