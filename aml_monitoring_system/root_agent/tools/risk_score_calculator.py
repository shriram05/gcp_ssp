from google.cloud import bigquery

def get_current_risk_score(customer_id):
    """
    Retrieves the current risk score for a customer from BigQuery.
    
    Args:
        customer_id (str): The ID of the customer.
    
    Returns:
        float: The current risk score of the customer. Returns 0 if not found.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Construct the query
    query = """
        SELECT risk_score
        FROM `amlproject-458804.aml_data.customers`
        WHERE customer_id = @customer_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
        ]
    )
    
    # Execute the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    # Get the risk score
    for row in results:
        return float(row.risk_score) if row.risk_score is not None else 0.0
    
    # Return 0 if no risk score is found
    return 0.0

def calculate_risk_score(suspicious_activities):
    """
    Calculates a risk score based on suspicious activities.
    
    Args:
        suspicious_activities (list): A list of dictionaries containing information about suspicious activities.
    
    Returns:
        dict: A dictionary containing customer_id and calculated risk score.
    """
    if not suspicious_activities:
        return {'customer_id': None, 'risk_score': 0}
    
    # Get the customer_id from the first activity
    customer_id = suspicious_activities[0]['customer_id']
    
    # Get the current risk score
    current_risk_score = get_current_risk_score(customer_id)
    
    # Define weights for different types of suspicious activities
    risk_weights = {
        'large_amount': 15.0,
        'frequent_small_transactions': 10.0,
        'multiple_locations': 20.0
    }
    
    # Calculate the new risk increment
    risk_increment = 0.0
    for activity in suspicious_activities:
        risk_type = activity.get('risk_type')
        if risk_type in risk_weights:
            risk_increment += risk_weights[risk_type]
    
    # Calculate the total risk score
    total_risk_score = current_risk_score + risk_increment
    
    # Update the risk score in BigQuery
    update_risk_score(customer_id, total_risk_score)
    
    return {
        'customer_id': customer_id,
        'previous_risk_score': current_risk_score,
        'risk_increment': risk_increment,
        'total_risk_score': total_risk_score
    }

def update_risk_score(customer_id, risk_score):
    """
    Updates the risk score for a customer in BigQuery.
    
    Args:
        customer_id (str): The ID of the customer.
        risk_score (float): The new risk score.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Convert the risk score to an integer to match the column type
    risk_score_int = int(risk_score)
    
    # Update the risk score record
    query = """
        UPDATE `amlproject-458804.aml_data.customers`
        SET risk_score = @risk_score
        WHERE customer_id = @customer_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
            bigquery.ScalarQueryParameter("risk_score", "INT64", risk_score_int),  # Changed to INT64
        ]
    )
    
    # Execute the query
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return True
    except Exception as e:
        print(f"Error updating risk score: {e}")
        return False  # Return False to indicate the update failed

def check_risk_threshold(customer_id, threshold=50.0):
    """
    Checks if a customer's risk score exceeds the specified threshold.
    
    Args:
        customer_id (str): The ID of the customer.
        threshold (float, optional): The risk threshold to trigger an alert. Default is 50.0.
    
    Returns:
        dict: A dictionary containing risk status and customer information.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Construct the query to get customer information and risk score
    query = """
        SELECT 
            customer_id,
            customer_name,
            email,
            phone,
            risk_score
        FROM 
            `amlproject-458804.aml_data.customers`
        WHERE 
            customer_id = @customer_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
        ]
    )
    
    # Execute the query
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    # Format the results
    for row in results:
        risk_score = float(row.risk_score) if row.risk_score is not None else 0.0
        return {
            'threshold_exceeded': risk_score >= threshold,
            'customer_id': row.customer_id,
            'customer_name': row.customer_name,
            'email': row.email,
            'phone': row.phone,
            'risk_score': risk_score
        }
    
    # Return False if customer not found
    return {'threshold_exceeded': False, 'customer_id': customer_id}