# import os
# from google.cloud import bigquery

# def verify_schema():
#     """Verify the schema of BigQuery tables."""
#     # Set Google Cloud credentials
#     credentials_path = os.path.abspath("amlproject-458804-dfd6239cd782.json")
#     os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
#     print(f"Credentials set to: {credentials_path}")
    
#     # Initialize BigQuery client
#     client = bigquery.Client()
    
#     # Verify customers table schema
#     print("\nCustomers table schema:")
#     table_ref = client.dataset("aml_data").table("customers")
#     try:
#         table = client.get_table(table_ref)
#         for field in table.schema:
#             print(f"- {field.name} ({field.field_type})")
        
#         # Get a sample row
#         query = "SELECT * FROM `amlproject-458804.aml_data.customers` LIMIT 1"
#         query_job = client.query(query)
#         results = query_job.result()
#         for row in results:
#             print("\nSample customer row:")
#             for key, value in row.items():
#                 print(f"- {key}: {value}")
#     except Exception as e:
#         print(f"Error getting customers table schema: {e}")
    
#     # Verify transactions table schema
#     print("\nTransactions table schema:")
#     table_ref = client.dataset("aml_data").table("transactions")
#     try:
#         table = client.get_table(table_ref)
#         for field in table.schema:
#             print(f"- {field.name} ({field.field_type})")
        
#         # Get a sample row
#         query = "SELECT * FROM `amlproject-458804.aml_data.transactions` LIMIT 1"
#         query_job = client.query(query)
#         results = query_job.result()
#         for row in results:
#             print("\nSample transaction row:")
#             for key, value in row.items():
#                 print(f"- {key}: {value}")
#     except Exception as e:
#         print(f"Error getting transactions table schema: {e}")

# if __name__ == "__main__":
#     verify_schema()