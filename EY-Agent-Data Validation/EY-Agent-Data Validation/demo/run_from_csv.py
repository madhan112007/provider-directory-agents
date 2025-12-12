import sys
import os
import csv
import ast
import time

# Allow importing the agent package from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_validation_agent.agent import DataValidationAgent

def main():
    here = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(here, ".."))
    csv_path = os.path.join(root, "providers_200.csv")
    out_dir = os.path.join(root, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "providers_200_validated.csv")

    print(f"Loading providers from: {csv_path}")

    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # If you’re unsure about the column name, uncomment next line:
        # print("CSV columns:", reader.fieldnames)
        for row in reader:
            rows.append(row)

    agent = DataValidationAgent()
    results = []

    start = time.time()

    for idx, row in enumerate(rows, start=1):
        # adjust this key if your header is different
        original_str = row["original"]
        original = ast.literal_eval(original_str)

        provider = {
            "provider_id": f"PRV_{idx:03d}",
            "name": original.get("name"),
            "address": original.get("address"),
            "phone": original.get("phone"),
            "specialty": original.get("specialty"),
            "npi": original.get("npi"),
            "email": original.get("email"),
        }

        res = agent.validate_contact_info(provider)
        fields = res["fields"]

        results.append({
            "provider_id": provider["provider_id"],
            "name": fields["name"]["value"],
            "name_conf": fields["name"]["confidence"],
            "name_tag": fields["name"]["tag"],
            "address": fields["address"]["value"],
            "address_conf": fields["address"]["confidence"],
            "address_tag": fields["address"]["tag"],
            "phone": fields["phone"]["value"],
            "phone_conf": fields["phone"]["confidence"],
            "phone_tag": fields["phone"]["tag"],
            "specialty": fields["specialty"]["value"],
            "specialty_conf": fields["specialty"]["confidence"],
            "specialty_tag": fields["specialty"]["tag"],
            "npi": fields["npi"]["value"],
            "npi_conf": fields["npi"]["confidence"],
            "npi_tag": fields["npi"]["tag"],
            "provider_confidence": res["provider_confidence"],
        })

    end = time.time()
    total_time = end - start
    n = len(results)
    throughput_per_min = n / (total_time / 60) if total_time > 0 else 0

    # Count “AUTO_APPROVED” as provider_confidence >= 0.85 (you can tweak threshold)
    auto_approved = sum(1 for r in results if r["provider_confidence"] >= 0.85)

    # Write CSV
    fieldnames = list(results[0].keys()) if results else []
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print("\n🚀 BATCH TEST RESULTS")
    print(f"📈 Processed {n} providers in {total_time:.1f}s")
    print(f"⚡ Throughput: {throughput_per_min:.0f} providers/min")
    print(f"✅ AUTO_APPROVED: {auto_approved}/{n}")
    print(f"💾 CSV saved to: {out_path}")

if __name__ == "__main__":
    main()
