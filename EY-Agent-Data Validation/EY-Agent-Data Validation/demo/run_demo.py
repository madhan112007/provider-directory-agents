import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Now imports work
from data_validation_agent.agent import DataValidationAgent
from data_validation_agent.types import FieldTag

# Load sample data
here = os.path.dirname(__file__)
sample_path = os.path.join(here, "sample_providers.json")
with open(sample_path) as f:
    providers = json.load(f)
agent = DataValidationAgent()

print("=== Data Validation Agent Demo ===\n")

results = []
for provider in providers:
    result = agent.validate_contact_info(provider)
    results.append(result)
    
    print(f"\n✅ {result['provider_id']}: {result['provider_confidence']:.1%} confidence")
    for field, data in result['fields'].items():
        tag_emoji = {"confirmed": "✅", "updated": "🔄", "suspect": "⚠️", "missing": "❌"}
        print(f"  {tag_emoji[data['tag']]} {field}: {data['confidence']:.1%}")

# Save results
import os

here = os.path.dirname(__file__)
out_dir = os.path.join(here, "..", "outputs")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "sample_results.json")

with open(out_path, "w") as f:
    json.dump(results, f, indent=2)

print(f"\n💾 Results saved to {out_path}")
print(f"📊 Summary: {len([r for r in results if r['provider_confidence'] >= 0.85])}/{len(results)} AUTO_APPROVED")
