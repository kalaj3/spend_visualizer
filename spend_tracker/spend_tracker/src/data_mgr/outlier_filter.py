from spend_tracker.src.util.classes import (
    CC_Transaction,  # Import the CC_Transaction class
)


def filter_outliers(transactions: list[CC_Transaction], threshold_percentage: float):
    """
    Filters out transactions that are considered outliers based on a percentage
    threshold compared to the overall average. Adds an `outlier` field to each
    transaction to indicate whether it is an outlier.

    Args:
        transactions (list): List of CC_Transaction objects.
        threshold_percentage (float): Percentage threshold to identify outliers (e.g., 50 for 50%).

    Returns:
        tuple: A tuple containing two lists:
            - filtered_transactions: List of non-outlier transactions.
            - outlier_transactions: List of outlier transactions.
    """
    if not transactions:
        return [], []

    # Calculate the average amount
    amounts = [transaction.amount for transaction in transactions]
    average = sum(amounts) / len(amounts)

    # Calculate the threshold for outliers
    threshold = average * (1 + threshold_percentage / 100)

    # Separate outliers and non-outliers
    filtered_transactions = []
    outlier_transactions = []

    for transaction in transactions:
        if transaction.amount > threshold:
            transaction.outlier = True  # Mark as outlier
            outlier_transactions.append(transaction)
        else:
            transaction.outlier = False  # Mark as non-outlier
            filtered_transactions.append(transaction)

    return filtered_transactions, outlier_transactions
