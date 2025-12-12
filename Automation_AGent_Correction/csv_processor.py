"""
CSV Processor for Automative Correction Agent
Processes provider data from CSV files and applies corrections.
"""

import csv
from typing import List, Dict
from automative_correction_agent import AutomativeCorrectionAgent
from email_generator import EmailGenerator, create_email_pipeline
import json


class CSVProcessor:
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.agent = AutomativeCorrectionAgent(confidence_threshold=0.9)
        self.email_gen = EmailGenerator()
        self.process_and_notify = create_email_pipeline(self.agent, self.email_gen)
    
    def read_csv(self) -> List[Dict]:
        """Read provider data from CSV file"""
        providers = []
        with open(self.csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                providers.append(row)
        return providers
    
    def process_csv(self, dry_run: bool = True) -> Dict:
        """Process all providers from CSV file"""
        providers = self.read_csv()
        
        print(f"\n📊 Processing {len(providers)} providers from CSV...")
        print("="*70)
        
        results = []
        corrected_count = 0
        email_sent_count = 0
        manual_review_count = 0
        
        for i, provider in enumerate(providers, 1):
            print(f"\n[{i}/{len(providers)}] Processing {provider['name']} ({provider['provider_id']})")
            
            # Process provider
            result = self.process_and_notify(provider, dry_run=dry_run)
            
            if result['corrections']:
                corrected_count += 1
                print(f"  ✓ {len(result['corrections'])} corrections applied")
                for correction in result['corrections']:
                    print(f"    • {correction['field']}: {correction['before']} → {correction['after']}")
            else:
                print(f"  ✓ No corrections needed")
            
            if result['email_status']:
                email_sent_count += 1
                print(f"  📧 Email: {result['email_status']['status']}")
            
            if result['needs_manual_review']:
                manual_review_count += 1
                print(f"  ⚠️  Flagged for manual review")
            
            results.append(result)
        
        print("\n" + "="*70)
        print("✅ CSV PROCESSING COMPLETE")
        print("="*70)
        print(f"\nSummary:")
        print(f"  Total Providers: {len(providers)}")
        print(f"  Corrected: {corrected_count}")
        print(f"  Emails Sent: {email_sent_count}")
        print(f"  Manual Review: {manual_review_count}")
        
        print(f"\n📊 Correction Statistics:")
        stats = self.agent.get_statistics()
        print(json.dumps(stats, indent=2))
        
        print(f"\n📧 Email Statistics:")
        email_stats = self.email_gen.get_email_statistics()
        print(json.dumps(email_stats, indent=2))
        
        return {
            'total_providers': len(providers),
            'corrected_count': corrected_count,
            'email_sent_count': email_sent_count,
            'manual_review_count': manual_review_count,
            'results': results,
            'correction_stats': stats,
            'email_stats': email_stats
        }
    
    def export_corrected_csv(self, output_file: str):
        """Export corrected provider data to new CSV file"""
        providers = self.read_csv()
        results = self.agent.batch_process(providers)
        
        # Write corrected data
        with open(output_file, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['provider_id', 'name', 'email', 'phone', 'address', 'specialty', 
                         'correction_count', 'corrected_fields', 'validation_status']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in results:
                provider = result['provider_data']
                corrected_fields = [c['field'] for c in result['corrections']]
                
                writer.writerow({
                    'provider_id': provider['provider_id'],
                    'name': provider['name'],
                    'email': provider['email'],
                    'phone': provider['phone'],
                    'address': provider['address'],
                    'specialty': provider['specialty'],
                    'correction_count': len(result['corrections']),
                    'corrected_fields': ', '.join(corrected_fields) if corrected_fields else 'none',
                    'validation_status': 'manual_review' if result['needs_manual_review'] else 'auto_corrected'
                })
        
        print(f"\n✅ Corrected data exported to: {output_file}")
    
    def generate_correction_report(self, output_file: str):
        """Generate detailed correction report"""
        providers = self.read_csv()
        results = self.agent.batch_process(providers)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("AUTOMATIVE CORRECTION AGENT - CORRECTION REPORT\n")
            file.write("="*70 + "\n\n")
            
            for result in results:
                provider = result['provider_data']
                file.write(f"Provider: {provider['name']} ({provider['provider_id']})\n")
                file.write(f"Email: {provider['email']}\n")
                
                if result['corrections']:
                    file.write(f"\nCorrections Applied ({len(result['corrections'])}):\n")
                    for correction in result['corrections']:
                        file.write(f"  • {correction['field'].upper()}\n")
                        file.write(f"    Before: {correction['before']}\n")
                        file.write(f"    After:  {correction['after']}\n")
                        file.write(f"    Confidence: {correction['confidence']:.0%}\n")
                        file.write(f"    Source: {correction['source']}\n")
                        file.write(f"    Timestamp: {correction['timestamp']}\n")
                else:
                    file.write("\nNo corrections needed - data already accurate\n")
                
                if result['needs_manual_review']:
                    file.write("\n⚠️  FLAGGED FOR MANUAL REVIEW\n")
                
                file.write("\n" + "-"*70 + "\n\n")
            
            # Summary statistics
            file.write("\nSUMMARY STATISTICS\n")
            file.write("="*70 + "\n")
            stats = self.agent.get_statistics()
            file.write(json.dumps(stats, indent=2))
        
        print(f"\n✅ Correction report generated: {output_file}")


def main():
    """Main execution function"""
    import os
    
    # Get CSV file path
    csv_file = 'sample_data.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: CSV file not found: {csv_file}")
        print(f"Please ensure {csv_file} exists in the current directory.")
        return
    
    print("\n" + "="*70)
    print("🚀 AUTOMATIVE CORRECTION AGENT - CSV PROCESSOR")
    print("="*70)
    
    processor = CSVProcessor(csv_file)
    
    # Process CSV
    results = processor.process_csv(dry_run=True)
    
    # Export corrected data
    processor.export_corrected_csv('corrected_providers.csv')
    
    # Generate report
    processor.generate_correction_report('correction_report.txt')
    
    print("\n" + "="*70)
    print("✅ ALL PROCESSING COMPLETE!")
    print("="*70)
    print("\nGenerated Files:")
    print("  • corrected_providers.csv - Corrected provider data")
    print("  • correction_report.txt - Detailed correction report")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
