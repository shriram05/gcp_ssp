from google.cloud import bigquery
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

def detect_multiple_location_transactions(
    min_txn_count: int = 3,
    location_threshold: int = 2,  # Minimum different locations to be considered
    time_window_hours: int = 48
) -> List[Dict]:
    """
    Detects windows of transactions where there are at least `min_txn_count` transactions 
    in non-overlapping time windows of `time_window_hours`.
    Returns customer details including name and email along with transaction data.
    """
    client = bigquery.Client()
    query = """
        WITH base_data AS (
          SELECT
            transaction_id,
            customer_id_sender AS customer_id,
            sender_location AS location,
            TIMESTAMP(time) AS event_time
          FROM `amlproject-458804.aml_data.transactions`

          UNION ALL

          SELECT
            transaction_id,
            customer_id_receiver AS customer_id,
            recipient_location AS location,
            TIMESTAMP(time) AS event_time
          FROM `amlproject-458804.aml_data.transactions`
        ),
        ordered_txns AS (
          SELECT
            customer_id,
            transaction_id,
            location,
            event_time,
            LAG(event_time) OVER (PARTITION BY customer_id ORDER BY event_time) AS prev_event_time
          FROM base_data
        ),
        window_markers AS (
          SELECT
            customer_id,
            transaction_id,
            location,
            event_time,
            CASE 
              WHEN prev_event_time IS NULL OR 
                   TIMESTAMP_DIFF(event_time, prev_event_time, HOUR) > @time_window_hours
              THEN 1 
              ELSE 0 
            END AS is_new_window
          FROM ordered_txns
        ),
        window_ids AS (
          SELECT
            customer_id,
            transaction_id,
            location,
            event_time,
            SUM(is_new_window) OVER (PARTITION BY customer_id ORDER BY event_time) AS window_id
          FROM window_markers
        ),
        window_details AS (
          SELECT
            customer_id,
            window_id,
            STRING_AGG(transaction_id, ', ' ORDER BY event_time) AS transaction_ids,
            STRING_AGG(DISTINCT location, ', ') AS locations,
            MIN(event_time) AS start_time,
            MAX(event_time) AS end_time,
            COUNT(*) AS txn_count,
            COUNT(DISTINCT location) AS location_count
          FROM window_ids
          GROUP BY customer_id, window_id
        ),
        suspicious_windows AS (
          SELECT
            customer_id,
            transaction_ids,
            locations,
            start_time,
            end_time,
            location_count
          FROM window_details
          WHERE txn_count >= @min_txn_count AND location_count >= @location_threshold
        )
        
        SELECT
          sw.customer_id,
          c.customer_name,
          c.email,
          sw.transaction_ids,
          sw.locations,
          sw.start_time,
          sw.end_time,
          sw.location_count
        FROM suspicious_windows sw
        JOIN (
          SELECT DISTINCT customer_id, customer_name, email
          FROM `amlproject-458804.aml_data.customers`
        ) c ON sw.customer_id = c.customer_id
        ORDER BY sw.customer_id, sw.start_time
        """
    job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("min_txn_count", "INT64", min_txn_count),
                bigquery.ScalarQueryParameter("location_threshold", "INT64", location_threshold),
                bigquery.ScalarQueryParameter("time_window_hours", "INT64", time_window_hours),
            ]
        )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    suspicious_patterns = []
    for row in results:
        suspicious_patterns.append({
            "customer_id": row.customer_id,
            "customer_name": row.customer_name,
            "email": row.email,
            "location_count": row.location_count,
            "start_time": row.start_time.isoformat() if row.start_time else None,
            "end_time": row.end_time.isoformat() if row.end_time else None,
        })
    print("-----------------------multiplelocationdetails---------------------------")
    print(suspicious_patterns)
    return suspicious_patterns