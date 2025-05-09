# import os
# import sys
# import json
# from google.cloud import bigquery
# import argparse

# def run_improved_test(customer_id=None):
#     """Set up credentials and run a local test with improved output and customer ID handling."""
#     # Set Google Cloud credentials
#     credentials_path = os.path.abspath("amlproject-458804-dfd6239cd782.json")
#     os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
#     print(f"Credentials set to: {credentials_path}")
    
#     # Verify BigQuery connection
#     print("\nVerifying BigQuery connection...")
#     try:
#         client = bigquery.Client()
#         # Run a simple query to verify connection
#         query = "SELECT 1"
#         query_job = client.query(query)
#         results = query_job.result()
#         for row in results:
#             print(f"Connection successful: {row}")
#     except Exception as e:
#         print(f"Error connecting to BigQuery: {e}")
#         sys.exit(1)
    
#     # Check for tables
#     print("\nChecking BigQuery tables...")
#     try:
#         # Check customers table
#         query = "SELECT COUNT(*) AS count FROM `amlproject-458804.aml_data.customers`"
#         query_job = client.query(query)
#         results = query_job.result()
#         for row in results:
#             print(f"Customers table: {row.count} records")
        
#         # Check transactions table
#         query = "SELECT COUNT(*) AS count FROM `amlproject-458804.aml_data.transactions`"
#         query_job = client.query(query)
#         results = query_job.result()
#         for row in results:
#             print(f"Transactions table: {row.count} records")
        
#     except Exception as e:
#         print(f"Error checking tables: {e}")
#         sys.exit(1)
    
#     # If customer_id is provided, make sure it uses uppercase
#     if customer_id:
#         customer_id = customer_id.upper()  # Convert to uppercase
    
#     # Validate customer ID exists if provided
#     if customer_id:
#         try:
#             query = f"""
#                 SELECT customer_id, customer_name 
#                 FROM `amlproject-458804.aml_data.customers` 
#                 WHERE customer_id = @customer_id
#             """
#             job_config = bigquery.QueryJobConfig(
#                 query_parameters=[
#                     bigquery.ScalarQueryParameter("customer_id", "STRING", customer_id),
#                 ]
#             )
#             query_job = client.query(query, job_config=job_config)
#             results = list(query_job.result())
            
#             if not results:
#                 print(f"\nWARNING: Customer ID '{customer_id}' not found in database!")
#                 print("Available customer IDs:")
                
#                 # Show available customer IDs
#                 query = """
#                     SELECT customer_id, customer_name  
#                     FROM `amlproject-458804.aml_data.customers`
#                     LIMIT 10
#                 """
#                 query_job = client.query(query)
#                 results = query_job.result()
#                 for row in results:
#                     print(f"- {row.customer_id}: {row.customer_name}")
                
#                 # Ask for a valid customer ID
#                 valid_id = input("\nEnter a valid customer ID from the list above: ")
#                 if valid_id:
#                     customer_id = valid_id.upper()
#                 else:
#                     # Get a valid sample customer ID
#                     query = "SELECT customer_id FROM `amlproject-458804.aml_data.customers` LIMIT 1"
#                     query_job = client.query(query)
#                     results = query_job.result()
#                     for row in results:
#                         customer_id = row.customer_id
#                         break
#             else:
#                 print(f"\nFound customer: {results[0].customer_name} (ID: {results[0].customer_id})")
#         except Exception as e:
#             print(f"Error validating customer ID: {e}")
#             # Get a valid sample customer ID
#             query = "SELECT customer_id FROM `amlproject-458804.aml_data.customers` LIMIT 1"
#             query_job = client.query(query)
#             results = query_job.result()
#             for row in results:
#                 customer_id = row.customer_id
#                 break
#     else:
#         # No customer ID provided, get a sample one
#         query = "SELECT customer_id, customer_name FROM `amlproject-458804.aml_data.customers` LIMIT 1"
#         query_job = client.query(query)
#         results = query_job.result()
#         for row in results:
#             customer_id = row.customer_id
#             print(f"\nUsing sample customer: {row.customer_name} (ID: {row.customer_id})")
#             break
    
#     print("\n" + "="*50)
#     print(f"TESTING COMPONENTS WITH CUSTOMER ID: {customer_id}")
#     print("="*50)
    
#     # Test large amount detector
#     print("\n1. TESTING LARGE AMOUNT DETECTOR")
#     print("-"*30)
#     try:
#         from root_agent.tools.large_amount_detector import detect_large_amount_transactions
        
#         # Test with specific customer
#         customer_results = detect_large_amount_transactions(customer_id=customer_id, threshold=1000.00)
#         print(f"Large transactions for customer {customer_id}: {len(customer_results)}")
#         if customer_results:
#             print("\nSample customer transaction:")
#             for key, value in customer_results[0].items():
#                 print(f"  - {key}: {value}")
#         else:
#             print(f"No large transactions found for customer {customer_id}")
        
#         # Test overall (limit results to avoid overwhelming output)
#         all_results = detect_large_amount_transactions(threshold=3000.00)
#         print(f"\nTotal large transactions (over $3000) in system: {len(all_results)}")
        
#     except Exception as e:
#         print(f"Error testing large amount detector: {e}")
    
#     # Test frequent transaction detector
#     print("\n2. TESTING FREQUENT SMALL TRANSACTIONS DETECTOR")
#     print("-"*30)
#     try:
#         from root_agent.tools.frequent_transaction_detector import detect_frequent_small_transactions
        
#         # Test with specific customer
#         customer_results = detect_frequent_small_transactions(
#             customer_id=customer_id, 
#             amount_threshold=1000.00,
#             count_threshold=2,  # Lower for testing
#             time_window_hours=720  # 30 days to catch more patterns
#         )
#         print(f"Frequent small transaction patterns for customer {customer_id}: {len(customer_results)}")
#         if customer_results:
#             print("\nSample pattern:")
#             for key, value in customer_results[0].items():
#                 print(f"  - {key}: {value}")
#         else:
#             print(f"No frequent small transaction patterns found for customer {customer_id}")
        
#         # Test overall
#         all_results = detect_frequent_small_transactions(
#             amount_threshold=1000.00,
#             count_threshold=2,
#             time_window_hours=720
#         )
#         print(f"\nTotal frequent small transaction patterns in system: {len(all_results)}")
        
#     except Exception as e:
#         print(f"Error testing frequent transaction detector: {e}")
    
#     # Test multiple location detector
#     print("\n3. TESTING MULTIPLE LOCATION DETECTOR")
#     print("-"*30)
#     try:
#         from root_agent.tools.multiple_location_detector import detect_multiple_location_transactions
        
#         # Test with specific customer
#         customer_results = detect_multiple_location_transactions(
#             customer_id=customer_id,
#             location_threshold=2,
#             time_window_hours=720  # 30 days to catch more patterns
#         )
#         print(f"Multiple location patterns for customer {customer_id}: {len(customer_results)}")
#         if customer_results:
#             print("\nSample pattern:")
#             for key, value in customer_results[0].items():
#                 print(f"  - {key}: {value}")
#         else:
#             print(f"No multiple location patterns found for customer {customer_id}")
        
#         # Test overall
#         all_results = detect_multiple_location_transactions(location_threshold=2, time_window_hours=720)
#         print(f"\nTotal multiple location patterns in system: {len(all_results)}")
#         if all_results and len(all_results) > 0:
#             print("\nSample system-wide pattern:")
#             for key, value in all_results[0].items():
#                 print(f"  - {key}: {value}")
        
#     except Exception as e:
#         print(f"Error testing multiple location detector: {e}")
    
#     # Test risk score calculator
#     print("\n4. TESTING RISK SCORE CALCULATOR")
#     print("-"*30)
#     try:
#         from root_agent.tools.risk_score_calculator import get_current_risk_score, check_risk_threshold
        
#         risk_score = get_current_risk_score(customer_id)
#         print(f"Current risk score for customer {customer_id}: {risk_score}")
        
#         threshold_check = check_risk_threshold(customer_id)
#         print("\nThreshold check result:")
#         for key, value in threshold_check.items():
#             print(f"  - {key}: {value}")
        
#     except Exception as e:
#         print(f"Error testing risk score calculator: {e}")
    
#     print("\n" + "="*50)
#     print("COMPONENT TESTING COMPLETED")
#     print("="*50)
#     print("\nYou can run the full system test with: python testing.py")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Test AML monitoring system components")
#     parser.add_argument("--customer_id", help="Specify a customer ID to test with")
    
#     args = parser.parse_args()
    
#     run_improved_test(args.customer_id)