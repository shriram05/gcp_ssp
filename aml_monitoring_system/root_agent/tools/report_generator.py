from google.cloud import bigquery
import datetime
import json
from typing import Dict, List, Any, Optional
import os
import sys

# Add path to access the tools
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# Import detector tools
from root_agent.tools.large_amount_detector import detect_large_amount_transactions
from root_agent.tools.frequent_transaction_detector import detect_frequent_small_transactions
from root_agent.tools.multiple_location_detector import detect_multiple_location_transactions

def generate_sar_report(customer_id: str, suspicious_activities: Optional[List[Dict[str, Any]]] = None) -> Dict:
    """
    Generates a Suspicious Activity Report (SAR) for a customer.
    
    Args:
        customer_id (str): The ID of the customer.
        suspicious_activities (List[Dict], optional): List of pre-detected suspicious activities.
            If None, they will be detected using the detector tools.
    
    Returns:
        dict: A dictionary containing the SAR report data.
    """
    print("------------generate sar report--------------")
    
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Get customer information
    customer_info = get_customer_info(client, customer_id)
    if not customer_info:
        return {"error": f"Customer with ID {customer_id} not found."}
    
    # Get suspicious activities - either use provided activities or detect them
    formatted_activities = {}
    if suspicious_activities:
        print(suspicious_activities)
        formatted_activities = format_suspicious_activities(customer_id, suspicious_activities)
    # else:
    #     formatted_activities = get_suspicious_activities(customer_id)
    
    # Generate the report
    report = {
        "report_id": f"SAR-{customer_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        "report_date": datetime.datetime.now().isoformat(),
        "customer_information": customer_info,
        "risk_assessment": {
            "risk_score": customer_info["risk_score"],
            "assessment_date": datetime.datetime.now().isoformat()
        },
        "suspicious_activities": formatted_activities,
        "summary": generate_summary(customer_info, formatted_activities)
    }
    
    # Store the report in BigQuery
    try:
        store_report(client, report)
    except Exception as e:
        print(f"Warning: Could not store report - {e}")
    
    return report

def format_suspicious_activities(customer_id: str, activities: List[Dict[str, Any]]) -> Dict:
    """
    Formats a list of suspicious activities into the expected structure.
    
    Args:
        customer_id (str): The ID of the customer.
        activities (List[Dict]): List of suspicious activities.
    
    Returns:
        Dict: Formatted suspicious activities.
    """
    large_amount_activities = []
    frequent_small_activities = []
    multiple_location_activities = []
    
    for activity in activities:
        risk_type = activity.get("risk_type", "")
        
        if risk_type == "large_amount":
            # Determine direction (sent or received)
            direction = "sent" if activity.get("customer_id_send") == customer_id else "received"
            
            large_amount_activities.append({
                "type": "large_amount",
                "account_no": activity.get("account_no", ""),
                "location": activity.get("location", ""),
                "date": activity.get("transaction_date", ""),
                "transaction_type": activity.get("transaction_type", ""),
                "amount": activity.get("amount", 0),
                "direction": direction
            })
        elif risk_type == "frequent_small_transactions":
            frequent_small_activities.append({
                "type": "frequent_small_transactions",
                "account_no": activity.get("account_no", ""),
                "transaction_count": activity.get("transaction_count", 0),
                "total_amount": activity.get("total_amount", 0),
                "time_window": activity.get("time_window", "")
            })
        elif risk_type == "multiple_locations":
            multiple_location_activities.append({
                "type": "multiple_locations",
                "location_count": activity.get("location_count", 0),
                "locations": activity.get("locations", ""),
                "time_window": activity.get("time_window", "")
            })
    
    return {
        "large_amount_transactions": large_amount_activities,
        "frequent_small_transactions": frequent_small_activities,
        "multiple_location_transactions": multiple_location_activities
    }

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
            "risk_score": int(row.risk_score) if row.risk_score is not None else 0
        }
    
    return None

# def get_suspicious_activities(customer_id: str) -> Dict:
#     """
#     Uses detector tools to retrieve suspicious activities for a customer.
    
#     Args:
#         customer_id (str): The ID of the customer.
    
#     Returns:
#         dict: Dictionary of suspicious activities.
#     """
#     # Use detector tools to get suspicious activities
#     large_transactions = detect_large_amount_transactions(customer_id)
#     frequent_transactions = detect_frequent_small_transactions(customer_id)
#     multiple_locations = detect_multiple_location_transactions(customer_id)
    
#     print("-----------------------largeamounttransactionsdetails---------------------------")
#     print(large_transactions)
#     print("-------------------------frequenttransactiondetails-------------------------------")
#     print(frequent_transactions)
#     print("-------------------------multiplelocationdetails-------------------------------")
#     print(multiple_locations)
    
#     # Format large amount transactions to include direction
#     large_amount_activities = []
#     for activity in large_transactions:
#         # Determine direction (sent or received)
#         direction = "sent" if activity.get("customer_id_send") == customer_id else "received"
        
#         large_amount_activities.append({
#             "type": "large_amount",
#             "account_no": activity.get("account_no", ""),
#             "location": activity.get("location", ""),
#             "date": activity.get("transaction_date", ""),
#             "transaction_type": activity.get("transaction_type", ""),
#             "amount": activity.get("amount", 0),
#             "direction": direction
#         })
    
#     # Format frequent small transactions
#     frequent_small_activities = []
#     for activity in frequent_transactions:
#         frequent_small_activities.append({
#             "type": "frequent_small_transactions",
#             "account_no": activity.get("account_no", ""),
#             "transaction_count": activity.get("transaction_count", 0),
#             "total_amount": activity.get("total_amount", 0),
#             "time_window": activity.get("time_window", "")
#         })
    
#     # Format multiple location transactions
#     multiple_location_activities = []
#     for activity in multiple_locations:
#         multiple_location_activities.append({
#             "type": "multiple_locations",
#             "location_count": activity.get("location_count", 0),
#             "locations": activity.get("locations", ""),
#             "time_window": activity.get("time_window", "")
#         })
    
#     # Combine all suspicious activities
#     return {
#         "large_amount_transactions": large_amount_activities,
#         "frequent_small_transactions": frequent_small_activities,
#         "multiple_location_transactions": multiple_location_activities
#     }

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
    
    # Detailed information about large amount transactions
    if large_amount_count > 0:
        summary += f"Found {large_amount_count} large amount transactions: "
        transaction_details = []
        
        for activity in suspicious_activities["large_amount_transactions"]:
            # Determine if this was a sent or received transaction
            direction = activity.get("direction", "sent")  # Default to "sent" if not specified
            transaction_date = activity.get("date", "").split("T")[0] if "T" in activity.get("date", "") else activity.get("date", "")
            
            if direction == "sent":
                detail = f"${activity.get('amount', 0):.2f} sent on {transaction_date} from {activity.get('location', 'Unknown')}"
            else:
                detail = f"${activity.get('amount', 0):.2f} received on {transaction_date} from {activity.get('location', 'Unknown')}"
            
            transaction_details.append(detail)
        
        summary += ", ".join(transaction_details) + ". "
    
    # Detailed information about frequent small transactions
    if frequent_small_count > 0:
        summary += f"Found {frequent_small_count} instances of frequent small transactions: "
        transaction_details = []
        
        for activity in suspicious_activities["frequent_small_transactions"]:
            detail = f"{activity.get('transaction_count', 0)} transactions totaling ${activity.get('total_amount', 0):.2f} during {activity.get('time_window', 'Unknown')}"
            transaction_details.append(detail)
        
        summary += ", ".join(transaction_details) + ". "
    
    # Detailed information about multiple location transactions
    if multiple_location_count > 0:
        summary += f"Found {multiple_location_count} instances of transactions from multiple locations: "
        transaction_details = []
        
        for activity in suspicious_activities["multiple_location_transactions"]:
            detail = f"{activity.get('location_count', 0)} different locations ({activity.get('locations', 'Unknown')}) during {activity.get('time_window', 'Unknown')}"
            transaction_details.append(detail)
        
        summary += ", ".join(transaction_details) + ". "
    
    # Overall conclusion
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