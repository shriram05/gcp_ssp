from google.cloud import bigquery
import datetime
import json

def generate_sar_report(customer_id):
    """
    Generates a Suspicious Activity Report (SAR) for a customer.
    
    Args:
        customer_id (str): The ID of the customer.
    
    Returns:
        dict: A dictionary containing the SAR report data.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Get customer information
    customer_info = get_customer_info(client, customer_id)
    if not customer_info:
        return {"error": f"Customer with ID {customer_id} not found."}
    
    # Get suspicious activities
    suspicious_activities = get_suspicious_activities(client, customer_id)
    
    # Generate the report
    report = {
        "report_id": f"SAR-{customer_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "report_date": datetime.datetime.now().isoformat(),
        "customer_information": customer_info,
        "risk_assessment": {
            "risk_score": customer_info["risk_score"],
            "assessment_date": datetime.datetime.now().isoformat()
        },
        "suspicious_activities": suspicious_activities,
        "summary": generate_summary(customer_info, suspicious_activities)
    }
    
    # Store the report in BigQuery (if needed, create a sar_reports table first)
    try:
        store_report(client, report)
    except Exception as e:
        print(f"Warning: Could not store report - {e}")
    
    return report

def get_customer_info(client, customer_id):
    """
    Retrieves customer information from BigQuery.
    
    Args:
        client (bigquery.Client): The BigQuery client.
        customer_id (str): The ID of the customer.
    
    Returns:
        dict: Customer information.
    """
    query = """
        SELECT 
            customer_id,
            account_no,
            location_of_account,
            customer_name,
            phone,
            email,
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
    
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()
    
    for row in results:
        return {
            "customer_id": row.customer_id,
            "account_no": row.account_no,
            "location": row.location_of_account,
            "name": row.customer_name,
            "phone": row.phone,
            "email": row.email,
            "risk_score": float(row.risk_score) if row.risk_score is not None else 0.0
        }
    
    return None

def get_suspicious_activities(client, customer_id):
    """
    Retrieves suspicious activities for a customer from BigQuery.
    
    Args:
        client (bigquery.Client): The BigQuery client.
        customer_id (str): The ID of the customer.
    
    Returns:
        dict: Dictionary of suspicious activities.
    """
    # Query for large amount transactions
    large_amount_query = """
        SELECT 
            customer_id,
            account_no,
            location_of_account,
            transaction_date,
            transaction_type,
            amount
        FROM 
            `amlproject-458804.aml_data.transactions`
        WHERE 
            customer_id = @customer_id
            AND amount > 5000.00
    """
    large_amount_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
        ]
    )
    
    large_amount_job = client.query(large_amount_query, job_config=large_amount_config)
    large_amount_results = large_amount_job.result()
    
    large_amount_activities = []
    for row in large_amount_results:
        large_amount_activities.append({
            "type": "large_amount",
            "account_no": row.account_no,
            "location": row.location_of_account,
            "date": row.transaction_date.isoformat() if hasattr(row.transaction_date, 'isoformat') else str(row.transaction_date),
            "transaction_type": row.transaction_type,
            "amount": row.amount
        })
    
    # Query for frequent small transactions
    frequent_small_query = """
        WITH SmallTransactions AS (
            SELECT 
                customer_id,
                account_no,
                transaction_date,
                amount
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE 
                customer_id = @customer_id
                AND amount <= 1000.00
        ),
        FrequentTransactions AS (
            SELECT 
                customer_id,
                account_no,
                COUNT(*) as transaction_count,
                SUM(amount) as total_amount,
                MIN(transaction_date) as first_transaction,
                MAX(transaction_date) as last_transaction
            FROM 
                SmallTransactions
            GROUP BY 
                customer_id, account_no
            HAVING 
                COUNT(*) >= 5
                AND TIMESTAMP_DIFF(MAX(transaction_date), MIN(transaction_date), HOUR) <= 24
        )
        SELECT * FROM FrequentTransactions
    """
    frequent_small_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
        ]
    )
    
    frequent_small_job = client.query(frequent_small_query, job_config=frequent_small_config)
    frequent_small_results = frequent_small_job.result()
    
    frequent_small_activities = []
    for row in frequent_small_results:
        frequent_small_activities.append({
            "type": "frequent_small_transactions",
            "account_no": row.account_no,
            "transaction_count": row.transaction_count,
            "total_amount": row.total_amount,
            "time_window": f"{row.first_transaction.isoformat() if hasattr(row.first_transaction, 'isoformat') else str(row.first_transaction)} to {row.last_transaction.isoformat() if hasattr(row.last_transaction, 'isoformat') else str(row.last_transaction)}"
        })
    
    # Query for multiple location transactions
    multiple_location_query = """
        WITH CustomerTransactions AS (
            SELECT 
                customer_id,
                transaction_date,
                location_of_account
            FROM 
                `amlproject-458804.aml_data.transactions`
            WHERE 
                customer_id = @customer_id
        ),
        LocationGroups AS (
            SELECT 
                customer_id,
                COUNT(DISTINCT location_of_account) as location_count,
                MIN(transaction_date) as first_transaction,
                MAX(transaction_date) as last_transaction,
                STRING_AGG(DISTINCT location_of_account, ', ') as locations
            FROM 
                CustomerTransactions
            GROUP BY 
                customer_id
            HAVING 
                COUNT(DISTINCT location_of_account) >= 2
                AND TIMESTAMP_DIFF(MAX(transaction_date), MIN(transaction_date), HOUR) <= 48
        )
        SELECT * FROM LocationGroups
    """
    multiple_location_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
        ]
    )
    
    multiple_location_job = client.query(multiple_location_query, job_config=multiple_location_config)
    multiple_location_results = multiple_location_job.result()
    
    multiple_location_activities = []
    for row in multiple_location_results:
        multiple_location_activities.append({
            "type": "multiple_locations",
            "location_count": row.location_count,
            "locations": row.locations,
            "time_window": f"{row.first_transaction.isoformat() if hasattr(row.first_transaction, 'isoformat') else str(row.first_transaction)} to {row.last_transaction.isoformat() if hasattr(row.last_transaction, 'isoformat') else str(row.last_transaction)}"
        })
    
    # Combine all suspicious activities
    return {
        "large_amount_transactions": large_amount_activities,
        "frequent_small_transactions": frequent_small_activities,
        "multiple_location_transactions": multiple_location_activities
    }

def generate_summary(customer_info, suspicious_activities):
    """
    Generates a summary of the suspicious activities.
    
    Args:
        customer_info (dict): Customer information.
        suspicious_activities (dict): Suspicious activities.
    
    Returns:
        str: Summary of suspicious activities.
    """
    large_amount_count = len(suspicious_activities["large_amount_transactions"])
    frequent_small_count = len(suspicious_activities["frequent_small_transactions"])
    multiple_location_count = len(suspicious_activities["multiple_location_transactions"])
    
    summary = f"Customer {customer_info['name']} (ID: {customer_info['customer_id']}) "
    summary += f"has a risk score of {customer_info['risk_score']}. "
    
    if large_amount_count > 0:
        summary += f"Found {large_amount_count} large amount transactions. "
    
    if frequent_small_count > 0:
        summary += f"Found {frequent_small_count} instances of frequent small transactions. "
    
    if multiple_location_count > 0:
        summary += f"Found {multiple_location_count} instances of transactions from multiple locations. "
    
    if large_amount_count == 0 and frequent_small_count == 0 and multiple_location_count == 0:
        summary += "No suspicious activities were detected."
    else:
        summary += "This activity is suspicious and requires investigation."
    
    return summary

def store_report(client, report):
    """
    Stores the SAR report in BigQuery.
    
    Args:
        client (bigquery.Client): The BigQuery client.
        report (dict): The SAR report.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    # First check if the sar_reports table exists, if not create it
    try:
        # Try to create the sar_reports table if it doesn't exist
        query = """
            CREATE TABLE IF NOT EXISTS `amlproject-458804.aml_data.sar_reports` (
                report_id STRING,
                customer_id STRING,
                report_date TIMESTAMP,
                report_content STRING
            )
        """
        query_job = client.query(query)
        query_job.result()
    except Exception as e:
        print(f"Error creating sar_reports table: {e}")
        return False
    
    # Convert the report to JSON
    report_json = json.dumps(report)
    
    # Construct the query
    query = """
        INSERT INTO `amlproject-458804.aml_data.sar_reports`
        (report_id, customer_id, report_date, report_content)
        VALUES (@report_id, @customer_id, @report_date, @report_content)
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("report_id", "STRING", report['report_id']),
            bigquery.ScalarQueryParameter("customer_id", "STRING", report['customer_information']['customer_id']),
            bigquery.ScalarQueryParameter("report_date", "TIMESTAMP", report['report_date']),
            bigquery.ScalarQueryParameter("report_content", "STRING", report_json),
        ]
    )
    
    # Execute the query
    try:
        query_job = client.query(query, job_config=job_config)
        query_job.result()
        return True
    except Exception as e:
        print(f"Error storing report: {e}")
        return False