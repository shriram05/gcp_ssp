from google.cloud import bigquery
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

def detect_frequent_small_transactions(
    customer_id: str = "",
    amount_threshold: float = 5000.00,
    count_threshold: int = 3,
    time_window_hours: int = 24
) -> List[Dict]:
    """
    Detects frequent small transactions within a specified time window.
    
    Args:
        customer_id (str, optional): The ID of the customer to check. If empty, checks all customers.
        amount_threshold (float, optional): The maximum amount to consider as a small transaction.
        count_threshold (int, optional): The minimum number of transactions to be considered suspicious.
        time_window_hours (int, optional): The time window in hours to check for frequency.
    
    Returns:
        list: A list of dictionaries containing information about suspicious transaction patterns.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    original_id = customer_id
    
    if customer_id:
        # Using window functions instead of correlated subqueries
        query = """
            WITH AllTransactions AS (
    SELECT 
        transaction_id,
        customer_id_sender,
        customer_id_receiver,
        sender_id_account_no,
        recipient_id_account_no,
        sender_location,
        recipient_location,
        time,
        payment_type,
        amount,
        CASE 
            WHEN customer_id_sender = @customer_id THEN 'sender'
            WHEN customer_id_receiver = @customer_id THEN 'receiver'
        END as direction
    FROM 
        `amlproject-458804.aml_data.transactions`
    WHERE 
        (customer_id_sender = @customer_id OR customer_id_receiver = @customer_id)
        AND amount <= @amount_threshold
),
-- For each transaction, look ahead to find the window end
TransactionWindows AS (
    SELECT
        time as window_start,
        TIMESTAMP_ADD(time, INTERVAL @time_window_hours HOUR) as window_end,
        transaction_id
    FROM AllTransactions
    -- Include every transaction as a potential window start
),
-- Join transactions with windows to find which transactions fall into each window
TransactionsInWindows AS (
    SELECT
        tw.transaction_id as window_start_txn_id,
        tw.window_start,
        tw.window_end,
        COUNT(t.transaction_id) as transaction_count,
        SUM(t.amount) as total_amount,
        -- Creating a JSON array of transaction details
        ARRAY_AGG(
            STRUCT(
                t.transaction_id,
                t.customer_id_sender,
                t.customer_id_receiver,
                t.sender_id_account_no,
                t.recipient_id_account_no,
                t.sender_location,
                t.recipient_location,
                t.time,
                t.payment_type,
                t.amount,
                t.direction
            ) ORDER BY t.time
        ) as transactions
    FROM TransactionWindows tw
    JOIN AllTransactions t
        ON t.time >= tw.window_start 
        AND t.time <= tw.window_end
    GROUP BY tw.transaction_id, tw.window_start, tw.window_end
    HAVING COUNT(t.transaction_id) >= @count_threshold
),
-- Find non-overlapping windows by ordering by count and taking the first
-- occurrence for any transaction that appears in multiple windows
RankedWindows AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY window_start_txn_id 
            ORDER BY transaction_count DESC, total_amount DESC
        ) as rn
    FROM TransactionsInWindows
),
-- Get all transaction IDs for each window and flatten into rows
TransactionDetailsFlat AS (
    SELECT
        rw.window_start,
        rw.window_end,
        rw.transaction_count,
        rw.total_amount,
        rw.transactions,
        t.transaction_id,
        ROW_NUMBER() OVER (ORDER BY rw.window_start, t.time) as window_order
    FROM RankedWindows rw,
        UNNEST(rw.transactions) t
    WHERE rw.rn = 1
),
-- Flag each transaction as first occurrence
FirstOccurrence AS (
    SELECT
        window_start,
        window_end,
        transaction_count,
        total_amount,
        transactions,
        transaction_id,
        ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY window_order) = 1 AS is_first_occurrence
    FROM TransactionDetailsFlat
),
-- Group transactions by window and check if all are first occurrences
NonOverlappingWindows AS (
    SELECT
        @customer_id as customer_id,
        window_start,
        window_end,
        transaction_count,
        total_amount,
        transactions,
        LOGICAL_AND(is_first_occurrence) AS all_unique_transactions
    FROM FirstOccurrence
    GROUP BY window_start, window_end, transaction_count, total_amount, transactions
)
SELECT
    customer_id,
    transaction_count,
    total_amount,
    window_start as first_transaction_time,
    (SELECT MIN(time) FROM UNNEST(transactions)) as first_transaction,
    (SELECT MAX(time) FROM UNNEST(transactions)) as last_transaction,
    transactions
FROM NonOverlappingWindows
WHERE all_unique_transactions = TRUE
ORDER BY first_transaction_time
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
        # For all customers (implementation omitted for brevity)
        # You can implement this similar to the approach above but for all customers
        pass
    
    # Execute the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    # Format the results
    suspicious_patterns = []
    for row in results:
        pattern = {
            'customer_id': row.customer_id,
            'transaction_count': row.transaction_count,
            'total_amount': row.total_amount,
            'first_transaction_date': row.first_transaction.isoformat(),
            'last_transaction_date': row.last_transaction.isoformat(),
            'time_window_hours': time_window_hours,
            'risk_type': 'frequent_small_transactions',
            'original_id': original_id,
            'transactions': []
        }
        
        # Extract the transactions array
        for transaction in row.transactions:
            pattern['transactions'].append({
                'transaction_id': transaction['transaction_id'],
                'customer_id_send': transaction['customer_id_sender'],
                'customer_id_dest': transaction['customer_id_receiver'],
                'account_no_send': transaction['sender_id_account_no'],
                'account_no_dest': transaction['recipient_id_account_no'],
                'location_sender': transaction['sender_location'],
                'location_receiver': transaction['recipient_location'],
                'transaction_date': transaction['time'].isoformat(),
                'transaction_type': transaction['payment_type'],
                'amount': transaction['amount'],
                'direction': transaction.get('direction')

            })
        
        suspicious_patterns.append(pattern)
    print("----------------------frequent------------------------")
    print(f"Found {len(suspicious_patterns)} suspicious frequent transaction patterns")
    print(suspicious_patterns)
    return suspicious_patterns

# Example usage
 