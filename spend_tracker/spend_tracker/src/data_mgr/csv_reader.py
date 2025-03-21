import csv
from datetime import datetime

from spend_tracker.src.util.classes import CC_Transaction


def read_csv(file_path: str) -> list[CC_Transaction]:
    """
    Reads a CSV file and parses it into a list of CC_Transaction objects.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list[CC_Transaction]: List of parsed transactions.
    """
    transactions: list[CC_Transaction] = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    transaction = CC_Transaction(
                        date=datetime.strptime(row["Date"], "%Y-%m-%d"),
                        description=row["Description"],
                        category=row["Category"],
                        amount=float(row["Amount"]),
                        source=row["Source"],
                    )
                    transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid row: {row}. Error: {e}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")

    return transactions


def prepare_data(transactions: list[CC_Transaction]) -> dict[str, list[CC_Transaction]]:
    """
    Prepares the data for future use cases by organizing it into a dictionary
    grouped by category.

    Args:
        transactions (list[CC_Transaction]): List of transactions.

    Returns:
        dict: Dictionary where keys are categories and values are lists of transactions.
    """
    data_by_category: dict[str, list[CC_Transaction]] = {}
    for transaction in transactions:
        if transaction.category not in data_by_category:
            data_by_category[transaction.category] = []
        data_by_category[transaction.category].append(transaction)

    return data_by_category
