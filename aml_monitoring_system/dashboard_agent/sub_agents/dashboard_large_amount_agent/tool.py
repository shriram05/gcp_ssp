from typing import Optional, List, Dict
from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv()

def detect_large_amount_transactions(threshold: float = 1000.00) -> List[Dict]:
    """
    Detects transactions with amounts larger than the specified threshold
    and includes customer details like name and email.

    Args:
        threshold (float): The amount threshold to consider as suspicious. Default is 1000.00.

    Returns:
        List[Dict]: A list of dictionaries containing customer details and count of large amount transactions.
    """
    client = bigquery.Client()
    query = """
            WITH large_transactions AS (
                SELECT customer_id, COUNT(*) AS large_transaction_count
                FROM (
                    SELECT customer_id_sender AS customer_id
                    FROM `amlproject-458804.aml_data.transactions`
                    WHERE amount > @threshold

                    UNION ALL

                    SELECT customer_id_receiver AS customer_id
                    FROM `amlproject-458804.aml_data.transactions`
                    WHERE amount > @threshold
                ) AS all_customers
                GROUP BY customer_id
                ORDER BY large_transaction_count DESC
            )
            
            SELECT 
                lt.customer_id,
                c.customer_name,
                c.email,
                lt.large_transaction_count
            FROM large_transactions lt
            JOIN (
                SELECT DISTINCT customer_id, customer_name, email
                FROM `amlproject-458804.aml_data.customers`
            ) c ON lt.customer_id = c.customer_id
            ORDER BY lt.large_transaction_count DESC;
        """
    
    job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("threshold", "FLOAT", threshold),
            ]
        )

    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    suspicious_transactions = []
    for row in results:
        suspicious_transactions.append({
            'customer_id': row.customer_id,
            'customer_name': row.customer_name,
            'email': row.email,
            'large_transaction_count': row.large_transaction_count
        })
    print("-----------------------largeamounttransactionsdetails---------------------------")
    print(suspicious_transactions)
    return suspicious_transactions