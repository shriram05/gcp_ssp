from typing import Optional, List, Dict
from google.cloud import bigquery
from dotenv import load_dotenv
load_dotenv()

def detect_large_amount_transactions(customer_id: str) -> List[Dict]:
    """
    Detects transactions with amounts larger than the specified threshold.

    Args:
        customer_id (str, optional): The ID of the customer to check. If None, checks all customers.
        threshold (float): The amount threshold to consider as suspicious. Default is 1000.00.

    Returns:
        List[Dict]: A list of dictionaries containing information about suspicious transactions.
    """
    client = bigquery.Client()
    original_id=customer_id
    if customer_id:
        query = """
            SELECT 
                customer_id_sender,
                transaction_id,
                customer_id_receiver,
                sender_id_account_no,
                recipient_id_account_no,
                sender_location,
                recipient_location,
                time,
                payment_type,
                amount
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE 
                (customer_id_sender = @customer_id OR customer_id_receiver = @customer_id)
                AND amount > 1000
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id)
            ]
        )
    else:
        query = """
            SELECT 
                customer_id_sender, 
                customer_id_receiver,
                sender_id_account_no,
                sender_location,
                time,
                payment_type,
                amount
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE 
                amount > 1000
        """
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    suspicious_transactions = []
    for row in results:
        suspicious_transactions.append({
            'customer_id_send': row.customer_id_sender,
            'customer_id_dest':row.customer_id_receiver,
            'account_no_send': row.sender_id_account_no,
            'account_no_dest': row.recipient_id_account_no,
            'location_sender': row.sender_location,
            'location_receiver':row.recipient_location,
            'transaction_id':row.transaction_id,
            'transaction_date': row.time.isoformat(),
            'transaction_type': row.payment_type,
            'amount': row.amount,
            'risk_type': 'large_amount',
            'original_id':original_id
        })
    print("-----------------------largeamounttransactionsdetails---------------------------")
    print(suspicious_transactions)
    return suspicious_transactions
