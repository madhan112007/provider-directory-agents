"""
Analyze geographic and specialty coverage gaps
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import json
import os

class GapAnalyzer:
    """Analyze network coverage gaps"""
    
    def analyze_gaps(self, providers_df: pd.DataFrame) -> Dict:
        """Analyze all types of gaps"""
        
        print("\n🔍 Analyzing network coverage gaps...")
        
        gaps = {
            'summary': {},
            'geographic_gaps': [],
            'specialty_gaps': [],
            'experience_gaps': [],
            'recommendations': []
        }
        
        if len(providers_df) == 0:
            return gaps
        
        # 1. Specialty gap analysis
        gaps['specialty_gaps'] = self._analyze_specialty_gaps(providers_df)
        
        # 2. Geographic gap analysis (simplified - based on state distribution)
        gaps['geographic_gaps'] = self._analyze_geographic_gaps(providers_df)
        
        # 3. Experience gap analysis
        gaps['experience_gaps'] = self._analyze_experience_gaps(providers_df)
        
        # 4. Generate recommendations
        gaps['recommendations'] = self._generate_recommendations(gaps)
        
        # 5. Create summary
        gaps['summary'] = self._create_gap_summary(gaps, len(providers_df))
        
        print(f"✅ Gap analysis complete:")
        print(f"   Found {len(gaps['specialty_gaps'])} specialty gaps")
        print(f"   Found {len(gaps['geographic_gaps'])} geographic gaps")
        
        return gaps
    
    def _analyze_specialty_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Identify specialty coverage gaps"""
        
        # Count providers by specialty
        if 'primary_specialty' in df.columns:
            specialty_counts = df['primary_specialty'].value_counts()
        else:
            # Fallback: use provider_type
            specialty_counts = df['provider_type'].value_counts()
        
        # Define minimum providers per specialty
        min_providers = {
            'Internal Medicine': 5,
            'Family Medicine': 5,
            'Pediatrics': 3,
            'Cardiology': 2,
            'Orthopedics': 2,
            'Dermatology': 2,
            'Psychiatry': 3,
            'Neurology': 2,
            'General Practice': 3,
            'Surgery': 2
        }
        
        gaps = []
        for specialty, required in min_providers.items():
            current = specialty_counts.get(specialty, 0)
            
            if current < required:
                gaps.append({
                    'specialty': specialty,
                    'current_providers': int(current),
                    'required_providers': required,
                    'gap_size': required - current,
                    'priority': 'HIGH' if current == 0 else 'MEDIUM',
                    'impact': 'High member impact' if specialty in ['Internal Medicine', 'Pediatrics'] else 'Moderate'
                })
        
        # Sort by gap size (largest first)
        gaps.sort(key=lambda x: x['gap_size'], reverse=True)
        
        return gaps
    
    def _analyze_geographic_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Identify geographic coverage gaps (simplified)"""
        
        # Extract states from addresses
        def extract_state(address):
            if pd.isna(address):
                return 'Unknown'
            address_str = str(address).upper()
            states = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA',
                     'HI','ID','IL','IN','IA','KS','KY','LA','ME','MD',
                     'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ',
                     'NM','NY','NC','ND','OH','OK','OR','PA','RI','SC',
                     'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
            for state in states:
                if f' {state} ' in f' {address_str} ':
                    return state
            return 'Unknown'
        
        if 'address' in df.columns:
            df['state'] = df['address'].apply(extract_state)
            state_counts = df['state'].value_counts()
        else:
            state_counts = pd.Series({'Unknown': len(df)})
        
        # Identify states with few providers
        gaps = []
        for state, count in state_counts.items():
            if state != 'Unknown' and count < 3:  # Less than 3 providers
                gaps.append({
                    'state': state,
                    'providers': int(count),
                    'recommended': 5,
                    'gap': 5 - count if count < 5 else 0,
                    'priority': 'HIGH' if count == 0 else 'MEDIUM' if count == 1 else 'LOW'
                })
        
        return gaps
    
    def _analyze_experience_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """Analyze experience distribution gaps"""
        
        if 'years_experience' not in df.columns:
            return []
        
        experience_data = df['years_experience'].dropna()
        
        if len(experience_data) == 0:
            return []
        
        # Categorize providers
        categories = {
            'Senior (20+ years)': (experience_data >= 20).sum(),
            'Experienced (10-19 years)': ((experience_data >= 10) & (experience_data < 20)).sum(),
            'Mid-Career (5-9 years)': ((experience_data >= 5) & (experience_data < 10)).sum(),
            'Early Career (1-4 years)': ((experience_data >= 1) & (experience_data < 5)).sum(),
            'New (0-1 years)': (experience_data < 1).sum()
        }
        
        gaps = []
        total = len(experience_data)
        
        for category, count in categories.items():
            percentage = (count / total) * 100
            
            # Identify imbalances
            if 'Senior' in category and percentage > 40:
                gaps.append({
                    'type': 'Experience Concentration',
                    'issue': 'Too many senior providers near retirement',
                    'percentage': round(percentage, 1),
                    'recommended': '<30%',
                    'risk': 'HIGH' if percentage > 50 else 'MEDIUM'
                })
            elif 'New' in category and percentage > 30:
                gaps.append({
                    'type': 'Experience Concentration',
                    'issue': 'Too many new/inexperienced providers',
                    'percentage': round(percentage, 1),
                    'recommended': '<20%',
                    'risk': 'MEDIUM'
                })
        
        # Retirement risk
        senior_count = categories['Senior (20+ years)']
        if senior_count > total * 0.3:
            gaps.append({
                'type': 'Retirement Risk',
                'issue': f'{senior_count} senior providers may retire soon',
                'recommendation': 'Develop succession planning',
                'priority': 'HIGH'
            })
        
        return gaps
    
    def _generate_recommendations(self, gaps: Dict) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Specialty recommendations
        for gap in gaps.get('specialty_gaps', []):
            if gap['gap_size'] > 0:
                rec = f"Recruit {gap['gap_size']} {gap['specialty']} provider(s)"
                if gap['priority'] == 'HIGH':
                    rec += " - URGENT"
                recommendations.append(rec)
        
        # Geographic recommendations
        for gap in gaps.get('geographic_gaps', []):
            if gap['gap'] > 0:
                rec = f"Add providers in {gap['state']} (currently {gap['providers']})"
                recommendations.append(rec)
        
        # Experience recommendations
        for gap in gaps.get('experience_gaps', []):
            recommendations.append(f"{gap['issue']}: {gap.get('recommendation', 'Review staffing')}")
        
        # General recommendations
        if len(recommendations) == 0:
            recommendations.append("Network coverage appears adequate. Maintain current levels.")
        else:
            recommendations.append("Consider these priorities for network improvement.")
        
        return recommendations[:10]  # Limit to top 10
    
    def _create_gap_summary(self, gaps: Dict, total_providers: int) -> Dict:
        """Create summary of gap analysis"""
        
        return {
            'total_providers_analyzed': total_providers,
            'specialty_gaps_count': len(gaps.get('specialty_gaps', [])),
            'geographic_gaps_count': len(gaps.get('geographic_gaps', [])),
            'experience_gaps_count': len(gaps.get('experience_gaps', [])),
            'total_recommendations': len(gaps.get('recommendations', [])),
            'network_health_score': self._calculate_health_score(gaps, total_providers),
            'analysis_timestamp': pd.Timestamp.now().isoformat()
        }
    
    def _calculate_health_score(self, gaps: Dict, total_providers: int) -> float:
        """Calculate network health score (0-100)"""
        if total_providers == 0:
            return 0.0
        
        # Deduct points for gaps
        score = 100.0
        
        # Deduct for specialty gaps
        specialty_gaps = gaps.get('specialty_gaps', [])
        for gap in specialty_gaps:
            if gap['priority'] == 'HIGH':
                score -= 5 * gap['gap_size']
            else:
                score -= 2 * gap['gap_size']
        
        # Deduct for geographic gaps
        geo_gaps = gaps.get('geographic_gaps', [])
        for gap in geo_gaps:
            if gap['priority'] == 'HIGH':
                score -= 10
            elif gap['priority'] == 'MEDIUM':
                score -= 5
        
        return max(0.0, min(100.0, score))
    
    def save_gap_report(self, gaps: Dict, output_path: str = None):
        """Save gap analysis to JSON report"""
        
        if output_path is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/gap_analysis_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(gaps, f, indent=2)
        
        print(f"📊 Gap report saved to: {output_path}")
        
        # Also create a simple text summary
        txt_path = output_path.replace('.json', '.txt')
        self._create_text_summary(gaps, txt_path)
        
        return output_path
    
    def _create_text_summary(self, gaps: Dict, txt_path: str):
        """Create human-readable summary"""
        
        with open(txt_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("NETWORK GAP ANALYSIS REPORT\n")
            f.write("="*60 + "\n\n")
            
            summary = gaps.get('summary', {})
            f.write(f"Total Providers Analyzed: {summary.get('total_providers_analyzed', 0)}\n")
            f.write(f"Network Health Score: {summary.get('network_health_score', 0):.1f}/100\n\n")
            
            f.write("SPECIALTY GAPS:\n")
            f.write("-"*40 + "\n")
            for gap in gaps.get('specialty_gaps', []):
                f.write(f"{gap['specialty']}: {gap['current_providers']}/{gap['required_providers']} "
                       f"(Need {gap['gap_size']} more) [{gap['priority']}]\n")
            
            f.write("\nGEOGRAPHIC GAPS:\n")
            f.write("-"*40 + "\n")
            for gap in gaps.get('geographic_gaps', []):
                f.write(f"{gap['state']}: {gap['providers']} providers "
                       f"(Recommend {gap['recommended']}) [{gap['priority']}]\n")
            
            f.write("\nTOP RECOMMENDATIONS:\n")
            f.write("-"*40 + "\n")
            for i, rec in enumerate(gaps.get('recommendations', [])[:5], 1):
                f.write(f"{i}. {rec}\n")
            
            f.write("\n" + "="*60 + "\n")