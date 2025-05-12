from google.cloud import bigquery
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

def detect_frequent_small_transactions(
    amount_threshold: float = 5000.00,
    count_threshold: int = 3,
    time_window_hours: int = 24
) -> List[Dict]:
    """
    Detects frequent small transactions within a specified time window.
    
    Args:
        amount_threshold (float, optional): The maximum amount to consider as a small transaction.
        count_threshold (int, optional): The minimum number of transactions to be considered suspicious.
        time_window_hours (int, optional): The time window in hours to check for frequency.
    
    Returns:
        list: A list of dictionaries containing information about suspicious transaction patterns.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # For all customers version of the query
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
                -- Keep track of customer for both sending and receiving
                customer_id_sender as customer_id,
                'sender' as direction
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE amount <= @amount_threshold
            
            UNION ALL
            
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
                -- Keep track of customer for both sending and receiving
                customer_id_receiver as customer_id,
                'receiver' as direction
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE amount <= @amount_threshold
        ),
        -- For each customer and transaction, look ahead to find the window end
        CustomerTransactionWindows AS (
            SELECT
                customer_id,
                time as window_start,
                TIMESTAMP_ADD(time, INTERVAL @time_window_hours HOUR) as window_end,
                transaction_id
            FROM AllTransactions
            -- Include every transaction as a potential window start
        ),
        -- Join transactions with windows to find which transactions fall into each window
        CustomerTransactionsInWindows AS (
            SELECT
                ctw.customer_id,
                ctw.transaction_id as window_start_txn_id,
                ctw.window_start,
                ctw.window_end,
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
            FROM CustomerTransactionWindows ctw
            JOIN AllTransactions t
                ON t.customer_id = ctw.customer_id
                AND t.time >= ctw.window_start 
                AND t.time <= ctw.window_end
            GROUP BY ctw.customer_id, ctw.transaction_id, ctw.window_start, ctw.window_end
            HAVING COUNT(t.transaction_id) >= @count_threshold
        ),
        -- Find non-overlapping windows by ordering by count and taking the first
        -- occurrence for any transaction that appears in multiple windows
        CustomerRankedWindows AS (
            SELECT
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY customer_id, window_start_txn_id 
                    ORDER BY transaction_count DESC, total_amount DESC
                ) as rn
            FROM CustomerTransactionsInWindows
        ),
        -- Get all transaction IDs for each window and flatten into rows
        CustomerTransactionDetailsFlat AS (
            SELECT
                crw.customer_id,
                crw.window_start,
                crw.window_end,
                crw.transaction_count,
                crw.total_amount,
                crw.transactions,
                t.transaction_id,
                ROW_NUMBER() OVER (PARTITION BY crw.customer_id ORDER BY crw.window_start, t.time) as window_order
            FROM CustomerRankedWindows crw,
                UNNEST(crw.transactions) t
            WHERE crw.rn = 1
        ),
        -- Flag each transaction as first occurrence per customer
        CustomerFirstOccurrence AS (
            SELECT
                customer_id,
                window_start,
                window_end,
                transaction_count,
                total_amount,
                transactions,
                transaction_id,
                ROW_NUMBER() OVER (PARTITION BY customer_id, transaction_id ORDER BY window_order) = 1 AS is_first_occurrence
            FROM CustomerTransactionDetailsFlat
        ),
        -- Group transactions by customer and window and check if all are first occurrences
        CustomerNonOverlappingWindows AS (
            SELECT
                customer_id,
                window_start,
                window_end,
                transaction_count,
                total_amount,
                transactions,
                LOGICAL_AND(is_first_occurrence) AS all_unique_transactions
            FROM CustomerFirstOccurrence
            GROUP BY customer_id, window_start, window_end, transaction_count, total_amount, transactions
        )
        SELECT
            customer_id,
            transaction_count,
            total_amount,
            window_start as first_transaction_time,
            (SELECT MIN(time) FROM UNNEST(transactions)) as first_transaction,
            (SELECT MAX(time) FROM UNNEST(transactions)) as last_transaction,
            transactions
        FROM CustomerNonOverlappingWindows
        WHERE all_unique_transactions = TRUE
        ORDER BY customer_id, first_transaction_time
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
        pattern = {
            'customer_id': row.customer_id,
            'transaction_count': row.transaction_count,
            'total_amount': row.total_amount,
            'first_transaction_date': row.first_transaction.isoformat(),
            'last_transaction_date': row.last_transaction.isoformat(),
        }
        
        # Extract the transactions array
        
        suspicious_patterns.append(pattern)
    print("----------------------frequent------------------------")
    print(f"Found {len(suspicious_patterns)} suspicious frequent transaction patterns")
    print(suspicious_patterns)
    return suspicious_patterns
 