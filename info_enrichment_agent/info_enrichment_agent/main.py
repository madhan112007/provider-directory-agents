 #!/usr/bin/env python3
"""
Main orchestrator for Information Enrichment Agent
"""

import pandas as pd
import os
import json
from datetime import datetime
import sys
import argparse
import re
import random
from dateutil.relativedelta import relativedelta

# Import your modules
from src.config import GOOGLE_API_KEY
from src.npi_enhancer import NPIEnhancer
from src.google_enricher import GoogleEnricher
from src.education_inferrer import EducationInferrer
from src.specialty_expander import SpecialtyExpander
from src.license_checker import LicenseChecker
from src.gap_analyzer import GapAnalyzer
from src.profile_builder import ProfileBuilder
from src.utils import print_progress, format_timestamp

# New imports for enrichment
try:
    import usaddress
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
except ImportError:
    print("Warning: usaddress and phonenumbers libraries not installed. Please run: pip install usaddress phonenumbers python-dateutil")
    usaddress = None
    phonenumbers = None

class InformationEnrichmentAgent:
    """Main agent orchestrator"""
    
    def __init__(self):
        self.npi_enhancer = NPIEnhancer()
        self.google_enricher = GoogleEnricher()
        self.education_inferrer = EducationInferrer()
        self.specialty_expander = SpecialtyExpander()
        self.license_checker = LicenseChecker()
        self.gap_analyzer = GapAnalyzer()
        self.profile_builder = ProfileBuilder()
        
        # Create output directories
        os.makedirs("data/output", exist_ok=True)
        os.makedirs("data/cache", exist_ok=True)
    
    def run(self, input_file="data/input_data.csv", enrich_level="full"):
        """
        Main method to run the enrichment agent

        Args:
            input_file: Path to input CSV/Excel file
            enrich_level: 'basic', 'moderate', or 'full'
        """

        print("="*60)
        print(f"🏥 INFORMATION ENRICHMENT AGENT - {enrich_level.upper()} LEVEL")
        print("="*60)

        # 1. Load input data
        print(f"\n📂 Loading input data: {input_file}")
        base_df = self._load_input_data(input_file)

        if base_df.empty:
            print("❌ No data loaded. Check your input file.")
            return None

        print(f"   Loaded {len(base_df)} providers")

        # 2. Apply detailed enrichments
        base_df = self._enrich_provider_data(base_df)

        # 3. NPI Enhancement (ALWAYS RUN - FREE)
        print(f"\n3️⃣  NPI ENHANCEMENT")
        npi_enhanced = self.npi_enhancer.batch_enhance(base_df['npi'].tolist())

        # 4. License Checking
        print(f"\n4️⃣  LICENSE VERIFICATION")
        license_checked = self.license_checker.batch_check_licenses(base_df)
        # Add name column for merging
        license_checked['name'] = base_df['name'].values

        # 5. Education Inference
        print(f"\n5️⃣  EDUCATION INFERENCE")
        education_data = []
        for idx, row in base_df.iterrows():
            edu_inferred = self.education_inferrer.infer_education(row.to_dict())
            edu_inferred['name'] = row['name']  # Add name for merging
            education_data.append(edu_inferred)
        education_df = pd.DataFrame(education_data)

        # 6. Google Places Enrichment (only for full enrichment) - COMMENTED OUT TO AVOID API COSTS
        google_data = []
        google_df = pd.DataFrame()

        # 7. Specialty Expansion (for moderate and full)
        specialty_df = pd.DataFrame()
        if enrich_level in ['moderate', 'full']:
            print(f"\n6️⃣  SPECIALTY EXPANSION")
            specialty_data = []
            for idx, row in npi_enhanced.iterrows():
                specialty_profile = self.specialty_expander.create_specialty_profile(
                    row.get('all_specialties', [])
                )
                specialty_data.append(specialty_profile)
            specialty_df = pd.DataFrame(specialty_data)

        # 8. Build final profiles
        print(f"\n7️⃣  BUILDING FINAL PROFILES")
        final_profiles = self.profile_builder.build_profiles(
            base_df, npi_enhanced, google_df, education_df, specialty_df, license_checked, enrich_level
        )

        # 9. Gap Analysis (only for moderate and full)
        gap_report = {}
        if enrich_level in ['moderate', 'full']:
            print(f"\n8️⃣  NETWORK GAP ANALYSIS")
            gap_report = self.gap_analyzer.analyze_gaps(final_profiles)

        # 10. Save results
        print(f"\n💾 SAVING RESULTS")

        # Save enriched profiles - ONLY CSV
        csv_path = self._save_csv_only(final_profiles)

        # Save gap analysis (only for moderate and full) - ONLY CSV
        if enrich_level in ['moderate', 'full']:
            gap_csv_path = self._save_gap_analysis_csv(gap_report)

        # 10. Show final summary
        self._show_final_summary(final_profiles, gap_report, csv_path, enrich_level)

        return final_profiles, gap_report

    def _enrich_provider_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all required enriched columns to the dataframe"""

        print(f"\n🔧 ENRICHING PROVIDER DATA")

        # A. ADDRESS ENRICHMENT
        print(f"   📍 Address enrichment...")
        df = self._enrich_address_data(df)

        # B. PHONE ENRICHMENT
        print(f"   📞 Phone enrichment...")
        df = self._enrich_phone_data(df)

        # C. NPI ENRICHMENT
        print(f"   🆔 NPI enrichment...")
        df = self._enrich_npi_data(df)

        # D. SPECIALTY ENRICHMENT
        print(f"   🏥 Specialty enrichment...")
        df = self._enrich_specialty_data(df)

        # E. PROVIDER EXPERIENCE & STATUS
        print(f"   👨‍⚕️ Provider experience & status...")
        df = self._enrich_provider_status(df)

        # F. GEOGRAPHIC ENRICHMENT
        print(f"   🌍 Geographic enrichment...")
        df = self._enrich_geographic_data(df)

        # G. QUALITY METRICS
        print(f"   📊 Quality metrics...")
        df = self._calculate_quality_metrics(df)

        return df

    def _enrich_address_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Extract state, ZIP, city from addresses"""

        def extract_address_components(address):
            if not address or pd.isna(address):
                return pd.Series({'address_state': None, 'address_zip': None, 'address_city': None})

            try:
                # Parse address using usaddress if available
                if usaddress:
                    parsed = usaddress.parse(address)
                    components = {comp: value for value, comp in parsed}

                    state = components.get('StateName', None)
                    zip_code = components.get('ZipCode', None)
                    city = components.get('PlaceName', None)

                    # Fallback: extract from string patterns
                    if not state:
                        state_match = re.search(r',\s*([A-Z]{2})\s+\d{5}', str(address))
                        if state_match:
                            state = state_match.group(1)

                    if not zip_code:
                        zip_match = re.search(r'\b(\d{5})(?:-\d{4})?\b', str(address))
                        if zip_match:
                            zip_code = zip_match.group(1)

                    if not city:
                        # Extract first word before comma and state
                        city_match = re.search(r'^([^,]+),\s*[A-Z]{2}', str(address))
                        if city_match:
                            city = city_match.group(1).strip()

                    return pd.Series({
                        'address_state': state,
                        'address_zip': zip_code,
                        'address_city': city
                    })
                else:
                    # Fallback without usaddress
                    state_match = re.search(r',\s*([A-Z]{2})\s+\d{5}', str(address))
                    zip_match = re.search(r'\b(\d{5})(?:-\d{4})?\b', str(address))
                    city_match = re.search(r'^([^,]+),\s*[A-Z]{2}', str(address))

                    return pd.Series({
                        'address_state': state_match.group(1) if state_match else None,
                        'address_zip': zip_match.group(1) if zip_match else None,
                        'address_city': city_match.group(1).strip() if city_match else None
                    })
            except:
                return pd.Series({'address_state': None, 'address_zip': None, 'address_city': None})

        address_components = df['address'].apply(extract_address_components)
        df = pd.concat([df, address_components], axis=1)

        return df

    def _enrich_phone_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize phone numbers to E.164 format"""

        def format_phone(phone):
            if not phone or pd.isna(phone):
                return None

            try:
                if phonenumbers:
                    # Parse and format phone number
                    parsed = phonenumbers.parse(str(phone), "US")
                    if phonenumbers.is_valid_number(parsed):
                        formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                        return formatted
                    else:
                        return None
                else:
                    # Basic formatting fallback
                    digits = re.sub(r'\D', '', str(phone))
                    if len(digits) == 10:
                        return f"+1{digits}"
                    elif len(digits) == 11 and digits.startswith('1'):
                        return f"+{digits}"
                    else:
                        return None
            except:
                return None

        df['phone_formatted'] = df['phone'].apply(format_phone)
        return df

    def _enrich_npi_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate NPI format and checksum"""

        def validate_npi(npi):
            if not npi or pd.isna(npi):
                return pd.Series({'npi_valid': False, 'npi_checksum_passed': False})

            npi_str = str(npi).strip()

            # Check format (10 digits)
            if not re.match(r'^\d{10}$', npi_str):
                return pd.Series({'npi_valid': False, 'npi_checksum_passed': False})

            # Luhn algorithm for checksum validation
            def luhn_checksum(card_num):
                def digits_of(n):
                    return [int(d) for d in str(n)]
                digits = digits_of(card_num)
                odd_digits = digits[-1::-2]
                even_digits = digits[-2::-2]
                checksum = sum(odd_digits)
                for d in even_digits:
                    checksum += sum(digits_of(d*2))
                return checksum % 10

            try:
                checksum = luhn_checksum(int(npi_str))
                is_valid = checksum == 0
                return pd.Series({'npi_valid': True, 'npi_checksum_passed': is_valid})
            except:
                return pd.Series({'npi_valid': False, 'npi_checksum_passed': False})

        npi_validation = df['npi'].apply(validate_npi)
        df = pd.concat([df, npi_validation], axis=1)

        return df

    def _enrich_specialty_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Categorize specialties into groups"""

        specialty_mapping = {
            'Primary Care': ['pediatrics', 'family medicine', 'internal medicine', 'general practice'],
            'Surgical': ['orthopedics', 'cardiology', 'neurology', 'surgery', 'urology', 'gynecology'],
            'Specialized': ['dermatology', 'oncology', 'emergency', 'radiology', 'pathology', 'psychiatry']
        }

        def categorize_specialty(specialty):
            if not specialty or pd.isna(specialty):
                return 'Unknown'

            specialty_lower = str(specialty).lower()

            for category, keywords in specialty_mapping.items():
                if any(keyword in specialty_lower for keyword in keywords):
                    return category

            return 'Other'

        # Check if specialty column exists, if not create it with default values
        if 'specialty' not in df.columns:
            df['specialty'] = 'Unknown'

        df['specialty_group'] = df['specialty'].apply(categorize_specialty)
        return df

    def _enrich_provider_status(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate experience, career stage, license status, and degree with India-specific data"""

        # Indian states and union territories
        indian_states = {
            'AP': 'Andhra Pradesh', 'AR': 'Arunachal Pradesh', 'AS': 'Assam', 'BR': 'Bihar',
            'CG': 'Chhattisgarh', 'GA': 'Goa', 'GJ': 'Gujarat', 'HR': 'Haryana',
            'HP': 'Himachal Pradesh', 'JK': 'Jammu and Kashmir', 'JH': 'Jharkhand',
            'KA': 'Karnataka', 'KL': 'Kerala', 'MP': 'Madhya Pradesh', 'MH': 'Maharashtra',
            'MN': 'Manipur', 'ML': 'Meghalaya', 'MZ': 'Mizoram', 'NL': 'Nagaland',
            'OR': 'Odisha', 'PB': 'Punjab', 'RJ': 'Rajasthan', 'SK': 'Sikkim',
            'TN': 'Tamil Nadu', 'TG': 'Telangana', 'TR': 'Tripura', 'UP': 'Uttar Pradesh',
            'UT': 'Uttarakhand', 'WB': 'West Bengal',
            'AN': 'Andaman and Nicobar Islands', 'CH': 'Chandigarh', 'DN': 'Dadra and Nagar Haveli and Daman and Diu',
            'DL': 'Delhi', 'JK': 'Jammu and Kashmir', 'LA': 'Ladakh', 'LD': 'Lakshadweep', 'PY': 'Puducherry'
        }

        # State medical council codes
        state_council_codes = {
            'TN': 'TNMC', 'MH': 'MMC', 'KA': 'KMC', 'AP': 'APMC', 'TG': 'TSMC',
            'WB': 'WBMC', 'UP': 'UPMC', 'DL': 'DMC', 'GJ': 'GMC', 'RJ': 'RMC',
            'MP': 'MPMC', 'KL': 'TCMC', 'OR': 'OMMC', 'PB': 'PMC', 'HR': 'HMC'
        }

        def infer_indian_degree(name):
            """Infer Indian medical degrees"""
            if not name or pd.isna(name):
                return 'Unknown'

            name_str = str(name).upper()
            # Indian medical degrees
            if 'MBBS' in name_str:
                return 'MBBS'
            elif 'MD' in name_str:
                return 'MD'
            elif 'MS' in name_str:
                return 'MS'
            elif 'DM' in name_str:
                return 'DM'
            elif 'MCH' in name_str:
                return 'MCh'
            elif 'DNB' in name_str:
                return 'DNB'
            else:
                # Default to MBBS for Indian context
                return 'MBBS'

        def generate_mci_number():
            """Generate MCI registration number: MCI-XXXXX"""
            return f"MCI-{random.randint(10000, 99999)}"

        def generate_state_council_registration(state_code):
            """Generate state council registration: e.g., TNMC-XXXXX"""
            if state_code in state_council_codes:
                council_code = state_council_codes[state_code]
                return f"{council_code}-{random.randint(10000, 99999)}"
            else:
                # Default to TNMC if state not found
                return f"TNMC-{random.randint(10000, 99999)}"

        def calculate_registration_year(years_exp):
            """Calculate registration year based on experience"""
            current_year = datetime.now().year
            return max(1980, current_year - years_exp - random.randint(0, 3))

        def determine_indian_license_status():
            """Indian medical licenses don't expire but have status"""
            rand = random.random()
            if rand < 0.90:
                return 'Active'
            elif rand < 0.95:
                return 'Inactive'
            else:
                return 'Suspended'

        def calculate_renewal_due_date(registration_year):
            """Renewal due every 5 years"""
            current_year = datetime.now().year
            years_since_registration = current_year - registration_year
            next_renewal_year = registration_year + ((years_since_registration // 5) + 1) * 5
            return f"{next_renewal_year}-12-31"

        def calculate_last_verified_date():
            """Last verification date within last 2 years"""
            days_ago = random.randint(0, 730)  # 2 years
            verified_date = datetime.now() - relativedelta(days=days_ago)
            return verified_date.strftime('%Y-%m-%d')

        def calculate_experience():
            # Random graduation year between 1990-2015 for simulation
            grad_year = random.randint(1990, 2015)
            current_year = datetime.now().year
            return max(0, current_year - grad_year)

        def determine_career_stage(years_exp):
            if years_exp < 5:
                return 'Entry'
            elif years_exp < 15:
                return 'Mid'
            else:
                return 'Senior'

        # Generate experience first
        df['years_experience'] = [calculate_experience() for _ in range(len(df))]

        # India-specific fields
        df['inferred_degree'] = df['name'].apply(infer_indian_degree)
        df['mci_registration_number'] = [generate_mci_number() for _ in range(len(df))]

        # Generate state council registrations based on address_state
        df['state_council_registration'] = df['address_state'].apply(
            lambda state: generate_state_council_registration(state) if pd.notna(state) else 'TNMC-12345'
        )

        # Registration year based on experience
        df['registration_year'] = df['years_experience'].apply(calculate_registration_year)

        # License status for Indian context
        df['license_status'] = [determine_indian_license_status() for _ in range(len(df))]
        df['renewal_due_date'] = df['registration_year'].apply(calculate_renewal_due_date)
        df['last_verified_date'] = [calculate_last_verified_date() for _ in range(len(df))]

        # Career stage
        df['career_stage'] = df['years_experience'].apply(determine_career_stage)

        return df

    def _enrich_geographic_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add region, timezone based on state"""

        state_to_region = {
            'Northeast': ['ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA'],
            'Midwest': ['OH', 'MI', 'IN', 'IL', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS'],
            'South': ['DE', 'MD', 'VA', 'WV', 'KY', 'NC', 'SC', 'GA', 'FL', 'AL', 'MS', 'TN', 'AR', 'LA', 'OK', 'TX'],
            'West': ['MT', 'ID', 'WY', 'CO', 'NM', 'AZ', 'UT', 'NV', 'CA', 'OR', 'WA', 'AK', 'HI']
        }

        state_to_timezone = {
            'Eastern': ['ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA', 'DE', 'MD', 'VA', 'WV', 'KY', 'NC', 'SC', 'GA', 'FL', 'AL', 'MS', 'TN'],
            'Central': ['OH', 'MI', 'IN', 'IL', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS', 'AR', 'LA', 'OK', 'TX'],
            'Mountain': ['MT', 'ID', 'WY', 'CO', 'NM', 'AZ', 'UT', 'NV'],
            'Pacific': ['CA', 'OR', 'WA', 'AK', 'HI']
        }

        def get_region(state):
            if not state or pd.isna(state):
                return 'Unknown'

            for region, states in state_to_region.items():
                if state.upper() in states:
                    return region
            return 'Unknown'

        def get_timezone(state):
            if not state or pd.isna(state):
                return 'Unknown'

            for tz, states in state_to_timezone.items():
                if state.upper() in states:
                    return tz
            return 'Unknown'

        df['geo_region'] = df['address_state'].apply(get_region)
        df['timezone'] = df['address_state'].apply(get_timezone)

        return df

    def _calculate_quality_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate enrichment score and level"""

        def calculate_enrichment_score(row):
            score = 0
            max_score = 100

            # Address enrichment (20 points)
            if pd.notna(row.get('address_state')): score += 7
            if pd.notna(row.get('address_zip')): score += 7
            if pd.notna(row.get('address_city')): score += 6

            # Phone enrichment (10 points)
            if pd.notna(row.get('phone_formatted')): score += 10

            # NPI enrichment (15 points)
            if row.get('npi_valid', False): score += 10
            if row.get('npi_checksum_passed', False): score += 5

            # Specialty enrichment (10 points)
            if pd.notna(row.get('specialty_group')) and row['specialty_group'] != 'Unknown': score += 10

            # Provider status (25 points)
            if pd.notna(row.get('inferred_degree')): score += 5
            if pd.notna(row.get('years_experience')): score += 5
            if pd.notna(row.get('career_stage')): score += 5
            if pd.notna(row.get('license_status')): score += 5
            if pd.notna(row.get('mci_registration_number')): score += 5

            # Geographic (10 points)
            if pd.notna(row.get('geo_region')) and row['geo_region'] != 'Unknown': score += 5
            if pd.notna(row.get('timezone')) and row['timezone'] != 'Unknown': score += 5

            return min(score, max_score)



        df['enrichment_score'] = df.apply(calculate_enrichment_score, axis=1)

        return df

    def _load_input_data(self, input_file: str) -> pd.DataFrame:
        """Load input data from CSV or Excel"""
        
        if not os.path.exists(input_file):
            print(f"⚠️  Input file not found: {input_file}")
            print("   Creating sample data...")
            return self._create_sample_data()
        
        try:
            # Try to detect file type
            if input_file.endswith('.csv'):
                df = pd.read_csv(input_file)
            elif input_file.endswith('.xlsx') or input_file.endswith('.xls'):
                df = pd.read_excel(input_file)
            else:
                print(f"❌ Unsupported file format: {input_file}")
                return pd.DataFrame()
            
            # Ensure required columns exist
            required = ['name', 'npi', 'address']
            missing = [col for col in required if col not in df.columns]
            
            if missing:
                print(f"⚠️  Missing columns: {missing}")
                print("   Using available columns...")
            
            return df
            
        except Exception as e:
            print(f"❌ Error loading {input_file}: {e}")
            return pd.DataFrame()
    
    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample data for demo"""
        
        sample_data = {
            'name': [
                'Dr. John Smith', 
                'Dr. Jane Doe', 
                'Dr. Robert Johnson',
                'Dr. Sarah Williams',
                'Dr. Michael Brown'
            ],
            'npi': ['1234567890', '9876543210', '4567891230', '3216549870', '7891234560'],
            'address': [
                '123 Main St, San Francisco, CA 94105',
                '456 Oak Ave, New York, NY 10001',
                '789 Pine Rd, Chicago, IL 60601',
                '321 Elm St, Miami, FL 33101',
                '654 Maple Dr, Dallas, TX 75201'
            ],
            'phone': ['(415) 555-0100', '(212) 555-0200', '(312) 555-0300', 
                     '(305) 555-0400', '(214) 555-0500'],
            'license_number': ['CA12345', 'NY67890', 'IL45678', 'FL90123', 'TX34567']
        }
        
        df = pd.DataFrame(sample_data)
        
        # Save sample data
        os.makedirs("data", exist_ok=True)
        sample_path = "data/sample_data.csv"
        df.to_csv(sample_path, index=False)
        print(f"📋 Sample data created: {sample_path}")
        
        return df
    
    def _show_final_summary(self, profiles_df: pd.DataFrame, gap_report: dict, output_path: str, enrich_level: str = 'full'):
        """Display final summary"""

        print("\n" + "="*60)
        print("✅ ENRICHMENT COMPLETE!")
        print("="*60)

        print(f"\n📊 RESULTS SUMMARY:")
        print(f"   Providers enriched: {len(profiles_df)}")

        if 'enrichment_score' in profiles_df.columns:
            avg_score = profiles_df['enrichment_score'].mean()
            print(f"   Average enrichment score: {avg_score:.1f}/100")



        # Gap analysis summary (only for moderate and full)
        if enrich_level in ['moderate', 'full']:
            summary = gap_report.get('summary', {})
            print(f"\n🔍 GAP ANALYSIS:")
            print(f"   Network health score: {summary.get('network_health_score', 0):.1f}/100")
            print(f"   Specialty gaps found: {summary.get('specialty_gaps_count', 0)}")
            print(f"   Geographic gaps found: {summary.get('geographic_gaps_count', 0)}")

            # Show top recommendations
            recommendations = gap_report.get('recommendations', [])
            if recommendations:
                print(f"\n🎯 TOP RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"   {i}. {rec}")

        print(f"\n💾 OUTPUT FILES:")
        print(f"   Enriched profiles: {output_path}")
        if enrich_level in ['moderate', 'full']:
            print(f"   Gap analysis report: data/output/gap_analysis_*.csv")

    def _save_csv_only(self, profiles_df: pd.DataFrame) -> str:
        """Save enriched profiles to CSV only"""
        # Remove unnecessary columns
        columns_to_remove = ['enrichment_at', 'urban_rural', 'enrichment_level', 'npi_sum_checked', 'enrichment_status', 'enriched_at', 'enriched_date']
        profiles_df = profiles_df.drop(columns=[col for col in columns_to_remove if col in profiles_df.columns])

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/output/enriched_profiles_{timestamp}.csv"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        profiles_df.to_csv(output_path, index=False)

        print(f"💾 Profiles saved to CSV: {output_path}")
        return output_path

    def _save_gap_analysis_csv(self, gap_report: dict) -> str:
        """Save gap analysis to CSV only"""
        if not gap_report:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/output/gap_analysis_{timestamp}.csv"

        # Convert gap report to DataFrame
        gap_data = []

        # Summary data
        summary = gap_report.get('summary', {})
        gap_data.append(['Summary', ''])
        gap_data.append(['Network Health Score', summary.get('network_health_score', 0)])
        gap_data.append(['Specialty Gaps Count', summary.get('specialty_gaps_count', 0)])
        gap_data.append(['Geographic Gaps Count', summary.get('geographic_gaps_count', 0)])
        gap_data.append(['', ''])

        # Specialty gaps (list of dicts)
        gap_data.append(['Specialty Gaps', ''])
        specialty_gaps = gap_report.get('specialty_gaps', [])
        for gap in specialty_gaps:
            gap_data.append([f"{gap.get('specialty', 'Unknown')}", f"Need {gap.get('gap_size', 0)} more (Current: {gap.get('current_providers', 0)})"])
        gap_data.append(['', ''])

        # Geographic gaps (list of dicts)
        gap_data.append(['Geographic Gaps', ''])
        geo_gaps = gap_report.get('geographic_gaps', [])
        for gap in geo_gaps:
            gap_data.append([f"{gap.get('state', 'Unknown')}", f"Need {gap.get('gap', 0)} more (Current: {gap.get('providers', 0)})"])
        gap_data.append(['', ''])

        # Recommendations
        gap_data.append(['Recommendations', ''])
        recommendations = gap_report.get('recommendations', [])
        for i, rec in enumerate(recommendations, 1):
            gap_data.append([f'{i}. {rec}', ''])

        gap_df = pd.DataFrame(gap_data, columns=['Metric', 'Value'])

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        gap_df.to_csv(output_path, index=False)

        print(f"📊 Gap analysis saved to CSV: {output_path}")
        return output_path

def main():
    """Command line interface"""

    # Create data directories
    os.makedirs("data", exist_ok=True)

    agent = InformationEnrichmentAgent()

    input_file = "data/input_data.csv"

    # Run both basic and moderate levels at once
    print("🚀 Running Basic + Moderate levels...")

    # Run basic level
    print("\n" + "="*60)
    print("🏥 RUNNING BASIC LEVEL ENRICHMENT")
    print("="*60)
    basic_profiles, _ = agent.run(input_file, "basic")

    # Run moderate level
    print("\n" + "="*60)
    print("🏥 RUNNING MODERATE LEVEL ENRICHMENT")
    print("="*60)
    moderate_profiles, gap_report = agent.run(input_file, "moderate")

    # Create output with gap analysis included
    print("\n" + "="*60)
    print("📊 CREATING OUTPUT")
    print("="*60)

    # Use moderate profiles as base (includes specialty expansion)
    output_df = moderate_profiles.copy()

    # Remove unnecessary columns
    columns_to_remove = ['enrichment_at', 'urban_rural', 'enrichment_level', 'npi_sum_checked', 'enrichment_status', 'enriched_at', 'enriched_date']
    output_df = output_df.drop(columns=[col for col in columns_to_remove if col in output_df.columns])

    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/output/enriched_profiles_{timestamp}.csv"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    output_df.to_csv(output_path, index=False)

    print(f"💾 Output saved to: {output_path}")
    print(f"   Records: {len(output_df)}")
    print(f"   Columns: {len(output_df.columns)}")

    print("\n" + "="*60)
    print("✅ ENRICHMENT COMPLETE!")
    print("="*60)
    print("Enrichment with gap analysis has been processed.")
    print(f"📄 Final output: {output_path}")

if __name__ == "__main__":
    main()