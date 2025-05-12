from google.cloud import bigquery
from typing import Dict, List, Optional, Any, Union

def get_top_risk_customers(limit: int = 10, min_score: Optional[int] = None, 
                          customer_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves the top risk-prone customers from BigQuery.
    
    Args:
        limit (int, optional): The number of customers to retrieve. Default is 10.
        min_score (int, optional): Minimum risk score to filter by. Default is None.
        customer_type (str, optional): Type of customer to filter by. Default is None.
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing customer information and risk scores.
    """
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Build the WHERE clause based on optional filters
    where_clauses = []
    if min_score is not None:
        where_clauses.append(f"risk_score >= {min_score}")
    if customer_type is not None:
        where_clauses.append(f"customer_type = '{customer_type}'")
    
    where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    # Construct the query - simplified to only include essential information
    query = f"""
        WITH ranked_customers AS (
    SELECT 
        customer_id,
        customer_name,
        risk_score,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY risk_score DESC) AS rn
    FROM 
        `amlproject-458804.aml_data.customers`
    {where_clause}
)
SELECT 
    customer_id,
    customer_name,
    risk_score
FROM 
    ranked_customers
WHERE rn = 1
ORDER BY risk_score DESC
LIMIT {limit}

    """
    
    # Execute the query
    query_job = client.query(query)
    results = query_job.result()
    
    # Format the results as a list of dictionaries with only essential information
    customers = []
    for row in results:
        customers.append({
            'customer_id': row.customer_id,
            'customer_name': row.customer_name,
            'risk_score': row.risk_score
        })
    
    return customers
