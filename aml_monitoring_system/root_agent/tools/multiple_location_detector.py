from google.cloud import bigquery
from typing import List, Dict

def detect_multiple_location_transactions(
    customer_id: str = "",
    location_threshold: int = 2,
    time_window_hours: int = 48
) -> List[Dict]:

    """
    Detects transactions from the same customer occurring in multiple different locations 
    within a specified time window.
    
    Args:
        customer_id (str, optional): The ID of the customer to check. If None, checks all customers.
        location_threshold (int, optional): The minimum number of different locations to be considered suspicious.
        time_window_hours (int, optional): The time window in hours to check for transactions.
    
    Returns:
        list: A list of dictionaries containing information about suspicious transaction patterns.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Construct the query based on whether a specific customer_id is provided
    if customer_id:
        query = """
            WITH CustomerTransactions AS (
                SELECT 
                    customer_id_sender,
                    time,
                    sender_location
                FROM 
                    `amlproject-458804.aml_data.transactions`
                WHERE 
                    customer_id_sender = @customer_id
            ),
            LocationGroups AS (
                SELECT 
                    customer_id_sender,
                    COUNT(DISTINCT sender_location) as location_count,
                    MIN(time) as first_transaction,
                    MAX(time) as last_transaction,
                    STRING_AGG(DISTINCT sender_location, ', ') as locations
                FROM 
                    CustomerTransactions
                GROUP BY 
                    customer_id_sender
                HAVING 
                    COUNT(DISTINCT sender_location) >= @location_threshold
                    AND TIMESTAMP_DIFF(MAX(time), MIN(time), HOUR) <= @time_window_hours
            )
            SELECT * FROM LocationGroups
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
                bigquery.ScalarQueryParameter("location_threshold", "INT64", location_threshold),
                bigquery.ScalarQueryParameter("time_window_hours", "INT64", time_window_hours),
            ]
        )
    else:
        query = """
            WITH CustomerTransactions AS (
                SELECT 
                    customer_id_sender,
                    time,
                    sender_location
                FROM 
                    `amlproject-458804.aml_data.transactions`
            ),
            LocationGroups AS (
                SELECT 
                    customer_id_sender,
                    COUNT(DISTINCT sender_location) as location_count,
                    MIN(time) as first_transaction,
                    MAX(time) as last_transaction,
                    STRING_AGG(DISTINCT sender_location, ', ') as locations
                FROM 
                    CustomerTransactions
                GROUP BY 
                    customer_id_sender
                HAVING 
                    COUNT(DISTINCT sender_location) >= @location_threshold
                    AND TIMESTAMP_DIFF(MAX(time), MIN(time), HOUR) <= @time_window_hours
            )
            SELECT * FROM LocationGroups
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("location_threshold", "INT64", location_threshold),
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
            'location_count': row.location_count,
            'locations': row.locations,
            'time_window': f"{row.first_transaction} to {row.last_transaction}",
            'risk_type': 'multiple_locations'
        })
    
    return suspicious_patterns