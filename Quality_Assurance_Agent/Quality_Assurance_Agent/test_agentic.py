import requests
import json
import pandas as pd
import ast
from agentic_ai import QualityAssuranceAgent

def load_test_cases():
    df = pd.read_csv('providers_200.csv')
    test_cases = []
    for idx, row in df.iterrows():
        provider_data = {}
        for col in df.columns:
            try:
                provider_data[col] = ast.literal_eval(row[col]) if pd.notna(row[col]) else {}
            except:
                provider_data[col] = row[col] if pd.notna(row[col]) else {}
        
        name = provider_data.get('original', {}).get('name', f"Provider {idx}")
        test_cases.append({"name": name, "data": provider_data})
    return test_cases

def test_agentic_ai():
    """Test the agentic AI system"""
    
    qa_agent = QualityAssuranceAgent()
    test_cases = load_test_cases()
    
    print(f"Processing {len(test_cases)} providers...")
    
    results = []
    for test in test_cases:
        result = qa_agent.process_provider(test['data'])
        results.append({
            "name": test['name'],
            "action": result['action'],
            "confidence_score": result['confidence_score'],
            "risk_score": result['risk_score'],
            "impact_score": result['impact_score'],
            "red_flags": "; ".join(result['red_flags']),
            "name_confidence": result['element_confidence']['name']['score'],
            "phone_confidence": result['element_confidence']['phone']['score'],
            "address_confidence": result['element_confidence']['address']['score'],
            "specialty_confidence": result['element_confidence']['specialty']['score'],
            "state_confidence": result['element_confidence']['state']['score'],
            "npi_confidence": result['element_confidence']['npi']['score'],
            "license_confidence": result['element_confidence']['license']['score']
        })
    
    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv('qa_results.csv', index=False)
    
    # Save metrics to JSON
    with open('qa_metrics.json', 'w') as f:
        json.dump(qa_agent.get_metrics(), f, indent=2)
    
    print(f"✓ Processed {len(test_cases)} providers")
    print("✓ Results saved to: qa_results.csv")
    print("✓ Metrics saved to: qa_metrics.json")

if __name__ == "__main__":
    test_agentic_ai()
    print("\nDone!")
