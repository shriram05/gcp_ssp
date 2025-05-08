from google.cloud import bigquery

def detect_large_amount_transactions(customer_id=None, threshold=5000.00):
    """
    Detects transactions with amounts larger than the specified threshold.
    
    Args:
        customer_id (str, optional): The ID of the customer to check. If None, checks all customers.
        threshold (float, optional): The amount threshold to consider as suspicious. Default is 5000.00.
    
    Returns:
        list: A list of dictionaries containing information about suspicious transactions.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Construct the query based on whether a specific customer_id is provided
    if customer_id:
        query = """
            SELECT 
                customer_id_sender,
                sender_id_account_no,
                sender_location,
                time,
                payment_type,
                amount
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE 
                customer_id_sender = @customer_id
                AND amount > @threshold
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
                bigquery.ScalarQueryParameter("threshold", "FLOAT", threshold),
            ]
        )
    else:
        query = """
            SELECT 
                customer_id_sender,
                sender_id_account_no,
                sender_location,
                time,
                payment_type,
                amount
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE 
                amount > @threshold
        """
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("threshold", "FLOAT", threshold),
            ]
        )
    
    # Execute the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    # Format the results
    suspicious_transactions = []
    for row in results:
        suspicious_transactions.append({
            'customer_id': row.customer_id_sender,
            'account_no': row.sender_id_account_no,
            'location': row.sender_location,
            'transaction_date': row.time,
            'transaction_type': row.payment_type,
            'amount': row.amount,
            'risk_type': 'large_amount'
        })
    
    return suspicious_transactions