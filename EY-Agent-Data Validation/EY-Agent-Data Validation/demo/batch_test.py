import json
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_validation_agent.agent import DataValidationAgent


def generate_batch(n: int = 100):
    """Generate synthetic batch for throughput testing"""
    import random
    return [
        {
            "provider_id": f"PRV_{i:03d}",
            "name": f"Dr. Provider {i}",
            "address": f"{random.randint(100,999)} {random.choice(['Main','Oak','Pine'])} St, {random.choice(['Boston','Dallas','NYC'])}",
            "phone": f"+1-{random.randint(200,999)}-{random.randint(1000,9999)}",
            "specialty": random.choice(["Internal Medicine", "Cardiology", "Pediatrics"]),
            "npi": random.choice([None, f"1{random.randint(10**9, 10**10-1)}"])
        }
        for i in range(1, n+1)
    ]

if __name__ == "__main__":
    agent = DataValidationAgent()
    providers = generate_batch(100)
    
    start = time.time()
    results = [agent.validate_contact_info(p) for p in providers]
    end = time.time()
    
    total_time = end - start
    providers_per_min = len(providers) / (total_time / 60)
    
    print(f"🚀 BATCH TEST RESULTS")
    print(f"📈 Processed {len(providers)} providers in {total_time:.1f}s")
    print(f"⚡ Throughput: {providers_per_min:.0f} providers/min")
    print(f"✅ AUTO_APPROVED: {len([r for r in results if r['provider_confidence'] >= 0.85])}/{len(results)}")
