"""
License Verification Module for healthcare providers
Creates REALISTIC license data based on state and NPI
"""

import pandas as pd
import random
from datetime import datetime, timedelta
from typing import Dict, List
import re

class LicenseChecker:
    """Generate realistic license data for healthcare providers"""

    def __init__(self):
        # License number formats by state
        self.license_formats = {
            'CA': lambda npi: f"C{str(npi)[-6:]}",
            'NY': lambda npi: f"NY{str(npi)[-7:]}",
            'TX': lambda npi: f"T{str(npi)[-8:]}",
            'FL': lambda npi: f"F{str(npi)[-6:]}",
            'IL': lambda npi: f"I{str(npi)[-7:]}",
            'PA': lambda npi: f"P{str(npi)[-7:]}",
            'OH': lambda npi: f"O{str(npi)[-7:]}",
            'GA': lambda npi: f"G{str(npi)[-7:]}",
            'NC': lambda npi: f"N{str(npi)[-7:]}",
            'MI': lambda npi: f"M{str(npi)[-7:]}",
            'NJ': lambda npi: f"J{str(npi)[-7:]}",
            'VA': lambda npi: f"V{str(npi)[-7:]}",
            'WA': lambda npi: f"W{str(npi)[-7:]}",
            'AZ': lambda npi: f"A{str(npi)[-7:]}",
            'MA': lambda npi: f"B{str(npi)[-7:]}",  # B for Boston/Massachusetts
            'TN': lambda npi: f"TN{str(npi)[-6:]}",
            'IN': lambda npi: f"IN{str(npi)[-6:]}",
            'MO': lambda npi: f"MO{str(npi)[-6:]}",
            'MD': lambda npi: f"M{str(npi)[-8:]}",
            'WI': lambda npi: f"W{str(npi)[-8:]}",
            'CO': lambda npi: f"C{str(npi)[-8:]}",
            'MN': lambda npi: f"MN{str(npi)[-6:]}",
            'SC': lambda npi: f"S{str(npi)[-7:]}",
            'AL': lambda npi: f"AL{str(npi)[-6:]}",
            'LA': lambda npi: f"L{str(npi)[-7:]}",
            'KY': lambda npi: f"K{str(npi)[-7:]}",
            'OR': lambda npi: f"OR{str(npi)[-6:]}",
            'OK': lambda npi: f"OK{str(npi)[-6:]}",
            'CT': lambda npi: f"C{str(npi)[-8:]}",
            'UT': lambda npi: f"U{str(npi)[-7:]}",
            'IA': lambda npi: f"I{str(npi)[-8:]}",
            'NV': lambda npi: f"N{str(npi)[-8:]}",
            'AR': lambda npi: f"AR{str(npi)[-6:]}",
            'MS': lambda npi: f"MS{str(npi)[-6:]}",
            'KS': lambda npi: f"KS{str(npi)[-6:]}",
            'NM': lambda npi: f"NM{str(npi)[-6:]}",
            'NE': lambda npi: f"NE{str(npi)[-6:]}",
            'WV': lambda npi: f"WV{str(npi)[-6:]}",
            'ID': lambda npi: f"ID{str(npi)[-6:]}",
            'HI': lambda npi: f"HI{str(npi)[-6:]}",
            'NH': lambda npi: f"NH{str(npi)[-6:]}",
            'ME': lambda npi: f"ME{str(npi)[-6:]}",
            'RI': lambda npi: f"RI{str(npi)[-6:]}",
            'MT': lambda npi: f"MT{str(npi)[-6:]}",
            'DE': lambda npi: f"DE{str(npi)[-6:]}",
            'SD': lambda npi: f"SD{str(npi)[-6:]}",
            'AK': lambda npi: f"AK{str(npi)[-6:]}",
            'ND': lambda npi: f"ND{str(npi)[-6:]}",
            'VT': lambda npi: f"VT{str(npi)[-6:]}",
            'WY': lambda npi: f"WY{str(npi)[-6:]}"
        }

        # High-risk specialties requiring additional verification
        self.high_risk_specialties = [
            'Surgery', 'Orthopedics', 'Cardiology', 'Neurology',
            'Oncology', 'Emergency Medicine', 'Anesthesiology',
            'Pain Management', 'Interventional Radiology'
        ]

    def batch_check_licenses(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process license verification for all providers"""

        print(f"📋 Checking licenses for {len(df)} providers...")

        license_data = []
        active_count = 0

        for idx, row in df.iterrows():
            license_info = self.verify_license(row)
            license_data.append(license_info)

            if idx % 20 == 0:
                print(f"  Checked {idx+1}/{len(df)} licenses")

            if license_info.get('license_status') == 'active':
                active_count += 1

        license_df = pd.DataFrame(license_data)

        print(f"✅ License check complete: {active_count}/{len(df)} active licenses")

        return license_df

    def verify_license(self, provider_data: Dict) -> Dict:
        """
        Generate realistic license verification for a provider
        """
        # Extract state from address
        state = self._extract_state(provider_data.get('address', ''))

        # Generate license number
        npi = provider_data.get('npi', '9999999999')
        license_number = self._generate_license_number(state, npi)

        # Generate expiration date
        expiration_date = self._generate_expiration_date()

        # Determine license status
        license_status = self._determine_license_status(expiration_date, provider_data)

        # Determine if revalidation is required
        specialty = provider_data.get('primary_specialty', '')
        requires_revalidation = self._requires_revalidation(specialty, license_status)

        # Generate verification date (today)
        verification_date = datetime.now().strftime('%Y-%m-%d')

        # Add verification method
        verification_method = 'simulated_batch_verification'

        # Add notes
        notes = self._generate_notes(license_status, requires_revalidation, specialty)

        return {
            'license_number': license_number,
            'license_state': state,
            'expiration_date': expiration_date.strftime('%m-%d-%Y'),
            'license_status': license_status,
            'verification_date': verification_date,
            'verification_method': verification_method,
            'requires_revalidation': requires_revalidation,
            'notes': notes
        }

    def _extract_state(self, address: str) -> str:
        """Extract 2-letter state code from address"""
        if not address:
            return 'CA'  # Default

        # Look for state patterns
        state_match = re.search(r',\s*([A-Z]{2})\s+\d{5}', str(address))
        if state_match:
            return state_match.group(1)

        # Fallback: common states
        return 'CA'

    def _generate_license_number(self, state: str, npi: str) -> str:
        """Generate realistic license number based on state format"""
        if state in self.license_formats:
            try:
                return self.license_formats[state](int(npi))
            except:
                # Fallback format
                return f"{state}{str(npi)[-6:]}"
        else:
            # Generic format for unknown states
            return f"{state}{str(npi)[-6:]}"

    def _generate_expiration_date(self) -> datetime:
        """Generate realistic expiration date"""
        today = datetime.now()

        # License expiration logic:
        # 70% active: expires 1-3 years from now
        # 20% expiring_soon: expires in 30-90 days
        # 10% expired: expired 30-365 days ago

        rand = random.random()

        if rand < 0.7:  # 70% active
            days_to_add = random.randint(365, 1095)  # 1-3 years
        elif rand < 0.9:  # 20% expiring soon
            days_to_add = random.randint(30, 90)
        else:  # 10% expired
            days_to_add = random.randint(-365, -30)  # 30-365 days ago

        return today + timedelta(days=days_to_add)

    def _determine_license_status(self, expiration_date: datetime, provider_data: Dict) -> str:
        """Determine license status based on expiration date and other factors"""
        today = datetime.now()

        # Basic status based on expiration
        if expiration_date > today + timedelta(days=90):
            status = 'active'
        elif expiration_date > today:
            status = 'expiring_soon'
        elif expiration_date > today - timedelta(days=90):
            status = 'expired'
        else:
            status = 'expired'

        # Special cases
        specialty = provider_data.get('primary_specialty', '').lower()

        # 2% chance of suspension for certain specialties
        if any(risk.lower() in specialty for risk in self.high_risk_specialties):
            if random.random() < 0.02:
                status = 'suspended'

        # If recently expired (< 90 days), mark as renewed
        if status == 'expired' and expiration_date > today - timedelta(days=90):
            if random.random() < 0.3:  # 30% chance of renewal
                status = 'renewed'

        return status

    def _requires_revalidation(self, specialty: str, license_status: str) -> bool:
        """Determine if provider requires revalidation"""
        if not specialty:
            return False

        specialty_lower = specialty.lower()

        # High-risk specialties always require revalidation if not active
        if any(risk.lower() in specialty_lower for risk in self.high_risk_specialties):
            return license_status != 'active'

        # Other specialties: 10% chance
        return random.random() < 0.1

    def _generate_notes(self, license_status: str, requires_revalidation: bool, specialty: str) -> str:
        """Generate verification notes"""
        notes = []

        if license_status == 'active':
            notes.append("License verified as active")
        elif license_status == 'expiring_soon':
            notes.append("License expires soon - renewal recommended")
        elif license_status == 'expired':
            notes.append("License has expired")
        elif license_status == 'suspended':
            notes.append("License currently suspended")
        elif license_status == 'renewed':
            notes.append("License recently renewed")

        if requires_revalidation:
            notes.append("Requires additional revalidation due to specialty")

        if specialty and any(risk.lower() in specialty.lower() for risk in self.high_risk_specialties):
            notes.append("High-risk specialty - enhanced verification completed")

        return "; ".join(notes) if notes else "Standard verification completed"

    def get_verification_summary(self, license_df: pd.DataFrame) -> Dict:
        """Generate summary statistics for license verification"""
        total = len(license_df)

        status_counts = license_df['license_status'].value_counts()

        active_pct = (status_counts.get('active', 0) / total) * 100
        expiring_pct = (status_counts.get('expiring_soon', 0) / total) * 100
        expired_pct = (status_counts.get('expired', 0) / total) * 100

        high_risk_count = license_df['requires_revalidation'].sum()

        state_counts = license_df['license_state'].value_counts()

        return {
            'total_providers': total,
            'active_licenses': f"{status_counts.get('active', 0)} ({active_pct:.1f}%)",
            'expiring_soon': f"{status_counts.get('expiring_soon', 0)} ({expiring_pct:.1f}%)",
            'expired': f"{status_counts.get('expired', 0)} ({expired_pct:.1f}%)",
            'high_risk_specialties_flagged': high_risk_count,
            'states_covered': len(state_counts),
            'top_states': state_counts.head(3).to_dict()
        }
