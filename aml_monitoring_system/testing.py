import os
import json
from root_agent.agent import root_agent

def test_aml_agent(customer_id=None):
    """
    Tests the AML monitoring agent with a specific customer ID or a sample input.
    
    Args:
        customer_id (str, optional): The customer ID to analyze. If None, will use a default.
    """
    # Set up credentials
    credentials_path = os.path.abspath("amlproject-458804-dfd6239cd782.json")
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    print(f"Credentials set to: {credentials_path}")
    
    # Prepare the input for the agent
    if customer_id:
        test_input = f"Analyze customer {customer_id} for suspicious activities and generate a comprehensive report."
    else:
        test_input = "Analyze customer C10045 for suspicious activities and generate a comprehensive report."
    
    print(f"\nRunning AML agent with input: '{test_input}'")
    print("\n" + "="*60)
    print("STARTING FULL AGENT PIPELINE")
    print("="*60)
    
    try:
        # SequentialAgent doesn't have a run method, let's use our direct test approach
        print("\nCalling direct test with tools...")
        from root_agent.tools.large_amount_detector import detect_large_amount_transactions
        from root_agent.tools.frequent_transaction_detector import detect_frequent_small_transactions
        from root_agent.tools.multiple_location_detector import detect_multiple_location_transactions
        from root_agent.tools.risk_score_calculator import calculate_risk_score, check_risk_threshold, get_current_risk_score
        from root_agent.tools.report_generator import generate_sar_report
        
        # Get the customer ID from the input
        if not customer_id:
            customer_id = "C10045"
        
        print(f"\nStep 1: Collecting suspicious activities for {customer_id}...")
        suspicious_activities = []
        
        # Detect large amount transactions
        large_transactions = detect_large_amount_transactions(customer_id=customer_id, threshold=3000.00)
        print(f"Found {len(large_transactions)} large amount transactions")
        suspicious_activities.extend(large_transactions)
        
        # Detect frequent small transactions
        frequent_transactions = detect_frequent_small_transactions(
            customer_id=customer_id,
            amount_threshold=1000.00,
            count_threshold=2,
            time_window_hours=720
        )
        print(f"Found {len(frequent_transactions)} frequent small transaction patterns")
        suspicious_activities.extend(frequent_transactions)
        
        # Detect multiple location transactions
        multiple_locations = detect_multiple_location_transactions(
            customer_id=customer_id,
            location_threshold=2,
            time_window_hours=720
        )
        print(f"Found {len(multiple_locations)} multiple location patterns")
        suspicious_activities.extend(multiple_locations)
        
        print(f"Total suspicious activities: {len(suspicious_activities)}")
        
        # Calculate risk score
        print("\nStep 2: Calculating risk score...")
        current_score = get_current_risk_score(customer_id)
        print(f"Current risk score: {current_score}")
        
        if suspicious_activities:
            # Calculate new risk score
            risk_result = calculate_risk_score(suspicious_activities)
            print(f"Previous risk score: {risk_result['previous_risk_score']}")
            print(f"Risk increment: {risk_result['risk_increment']}")
            print(f"New total risk score: {risk_result['total_risk_score']}")
            
            # Check threshold
            threshold_check = check_risk_threshold(customer_id)
            print(f"Threshold exceeded: {threshold_check['threshold_exceeded']}")
        else:
            print("No suspicious activities found - risk score remains unchanged")
        
        # Generate report
        print("\nStep 3: Generating SAR report...")
        report = generate_sar_report(customer_id)
        
        # Format result
        result = {
            "customer_id": customer_id,
            "suspicious_activities": {
                "large_transactions": len(large_transactions),
                "frequent_transactions": len(frequent_transactions),
                "multiple_locations": len(multiple_locations),
                "total": len(suspicious_activities)
            },
            "risk_assessment": {
                "previous_score": current_score,
                "risk_increment": risk_result['risk_increment'] if suspicious_activities else 0,
                "new_score": risk_result['total_risk_score'] if suspicious_activities else current_score,
                "threshold_exceeded": threshold_check['threshold_exceeded'] if suspicious_activities else False
            },
            "report": {
                "report_id": report['report_id'],
                "report_date": report['report_date'],
                "summary": report['summary']
            }
        }
        
        # Print the result
        print("\n" + "="*60)
        print("AGENT PIPELINE COMPLETED")
        print("="*60)
        print("\nAnalysis Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\nError running agent: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "="*60)
    print("TEST COMPLETED")
    print("="*60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test AML monitoring agent")
    parser.add_argument("--customer_id", help="Specify a customer ID to analyze")
    
    args = parser.parse_args()
    
    test_aml_agent(args.customer_id)