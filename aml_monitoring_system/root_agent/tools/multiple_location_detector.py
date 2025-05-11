from google.cloud import bigquery
from typing import List, Dict

def detect_multiple_location_transactions(
    customer_id: str = "",
    min_txn_count: int = 3,
    location_threshold: int = 2,  # Minimum different locations to be considered
    time_window_hours: int = 48
) -> List[Dict]:
    """
    Detects windows of transactions for a specific customer (or all customers) where there are at least
    `min_txn_count` transactions in non-overlapping time windows of `time_window_hours`.
    Returns only the columns: customer_id, transaction_ids, locations, start_time, end_time.
    """
    client = bigquery.Client()
    temp=customer_id
    if customer_id:
        query = """
        WITH base_data AS (
          SELECT
            transaction_id,
            customer_id_sender AS customer_id,
            sender_location AS location,
            TIMESTAMP(time) AS event_time
          FROM `amlproject-458804.aml_data.transactions`
          WHERE customer_id_sender = @customer_id

          UNION ALL

          SELECT
            transaction_id,
            customer_id_receiver AS customer_id,
            recipient_location AS location,
            TIMESTAMP(time) AS event_time
          FROM `amlproject-458804.aml_data.transactions`
          WHERE customer_id_receiver = @customer_id
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
        )
        SELECT
          customer_id,
          transaction_ids,
          locations,
          start_time,
          end_time
        FROM window_details
        WHERE txn_count >= @min_txn_count AND location_count >= @location_threshold
        ORDER BY start_time
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
                bigquery.ScalarQueryParameter("min_txn_count", "INT64", min_txn_count),
                bigquery.ScalarQueryParameter("location_threshold", "INT64", location_threshold),
                bigquery.ScalarQueryParameter("time_window_hours", "INT64", time_window_hours),
            ]
        )
    else:
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
        )
        SELECT
          customer_id,
          transaction_ids,
          locations,
          start_time,
          end_time
        FROM window_details
        WHERE txn_count >= @min_txn_count AND location_count >= @location_threshold
        ORDER BY customer_id, start_time
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
            "original_id":temp,
            "customer_id": row.customer_id,
            "transaction_ids": row.transaction_ids,
            "locations": row.locations,
            'risk_type': 'multiple_locations',
            "start_time": row.start_time.isoformat() if row.start_time else None,
            "end_time": row.end_time.isoformat() if row.end_time else None,
        })
    print("-----------------------multiplelocationdetails---------------------------")
    print(suspicious_patterns)
    return suspicious_patterns
