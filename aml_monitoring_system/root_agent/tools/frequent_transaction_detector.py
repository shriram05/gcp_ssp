from google.cloud import bigquery
from datetime import datetime, timedelta
from typing import List, Dict

def detect_frequent_small_transactions(
    customer_id: str = "",
    amount_threshold: float = 1000.00,
    count_threshold: int = 5,
    time_window_hours: int = 24
) -> List[Dict]:
    """
    Detects frequent small transactions within a specified time window.
    
    Args:
        customer_id (str, optional): The ID of the customer to check. If None, checks all customers.
        amount_threshold (float, optional): The maximum amount to consider as a small transaction.
        count_threshold (int, optional): The minimum number of transactions to be considered suspicious.
        time_window_hours (int, optional): The time window in hours to check for frequency.
    
    Returns:
        list: A list of dictionaries containing information about suspicious transaction patterns.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Construct the query based on whether a specific customer_id is provided
    if customer_id:
        query = """
            WITH SmallTransactions AS (
                SELECT 
                    customer_id_sender,
                    sender_id_account_no,
                    time,
                    amount
                FROM 
                    `amlproject-458804.aml_data.transactions`
                WHERE 
                    customer_id_sender = @customer_id
                    AND amount <= @amount_threshold
            ),
            FrequentTransactions AS (
                SELECT 
                    customer_id_sender,
                    sender_id_account_no,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount,
                    MIN(time) as first_transaction,
                    MAX(time) as last_transaction
                FROM 
                    SmallTransactions
                GROUP BY 
                    customer_id_sender, sender_id_account_no
                HAVING 
                    COUNT(*) >= @count_threshold
                    AND TIMESTAMP_DIFF(MAX(time), MIN(time), HOUR) <= @time_window_hours
            )
            SELECT * FROM FrequentTransactions
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
                bigquery.ScalarQueryParameter("amount_threshold", "FLOAT", amount_threshold),
                bigquery.ScalarQueryParameter("count_threshold", "INT64", count_threshold),
                bigquery.ScalarQueryParameter("time_window_hours", "INT64", time_window_hours),
            ]
        )
    else:
        query = """
            WITH SmallTransactions AS (
                SELECT 
                    customer_id_sender,
                    sender_id_account_no,
                    time,
                    amount
                FROM 
                    `amlproject-458804.aml_data.transactions`
                WHERE 
                    amount <= @amount_threshold
            ),
            FrequentTransactions AS (
                SELECT 
                    customer_id_sender,
                    sender_id_account_no,
                    COUNT(*) as transaction_count,
                    SUM(amount) as total_amount,
                    MIN(time) as first_transaction,
                    MAX(time) as last_transaction
                FROM 
                    SmallTransactions
                GROUP BY 
                    customer_id_sender, sender_id_account_no
                HAVING 
                    COUNT(*) >= @count_threshold
                    AND TIMESTAMP_DIFF(MAX(time), MIN(time), HOUR) <= @time_window_hours
            )
            SELECT * FROM FrequentTransactions
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("amount_threshold", "FLOAT", amount_threshold),
                bigquery.ScalarQueryParameter("count_threshold", "INT64", count_threshold),
                bigquery.ScalarQueryParameter("time_window_hours", "INT64", time_window_hours),
            ]
        )
    
    # Execute the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    # Format the results
    suspicious_patterns = []
    for row in results:
        suspicious_patterns.append({
            'customer_id': row.customer_id_sender,
            'account_no': row.sender_id_account_no,
            'transaction_count': row.transaction_count,
            'total_amount': row.total_amount,
            'time_window': f"{row.first_transaction} to {row.last_transaction}",
            'risk_type': 'frequent_small_transactions'
        })
    
    return suspicious_patterns