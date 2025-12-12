"""
Build final enriched provider profiles
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import json
import os
from datetime import datetime

class ProfileBuilder:
    """Build comprehensive provider profiles from all sources"""
    
    def build_profiles(self, base_df: pd.DataFrame,
                      npi_data: pd.DataFrame,
                      google_data: pd.DataFrame,
                      education_data: pd.DataFrame,
                      specialty_data: pd.DataFrame,
                      license_data: pd.DataFrame,
                      enrich_level: str = 'full') -> pd.DataFrame:
        """Combine all data sources into final profiles"""
        
        print("\n🏗️ Building enriched provider profiles...")
        
        # Start with base data
        profiles = base_df.copy()
        
        # Add NPI enhancement data
        if not npi_data.empty:
            profiles = self._merge_data(profiles, npi_data, 'npi', ['years_experience', 'career_stage', 'primary_specialty'])

        # Add Google data
        if not google_data.empty:
            profiles = self._merge_data(profiles, google_data, 'name', ['telehealth_available', 'business_hours', 'google_rating'])

        # Add education data
        if not education_data.empty:
            profiles = self._merge_data(profiles, education_data, 'name', ['inferred_degree', 'inferred_medical_school', 'graduation_year'])

        # Add specialty data
        if not specialty_data.empty:
            profiles = self._merge_data(profiles, specialty_data, 'primary_specialty', ['subspecialties', 'common_procedures'])

        # Add license data
        if not license_data.empty:
            profiles = self._merge_data(profiles, license_data, 'name', ['license_status', 'expiration_date'])

        # Ensure all required enriched columns are present (they should be added in main.py)
        required_enriched_cols = [
            'address_state', 'address_zip', 'phone_formatted',
            'npi_valid', 'npi_checksum_passed', 'specialty_group',
            'inferred_degree', 'years_experience', 'career_stage', 'license_status',
            'geo_region', 'timezone'
        ]

        for col in required_enriched_cols:
            if col not in profiles.columns:
                profiles[col] = None

        print(f"✅ Built {len(profiles)} enriched profiles")

        return profiles
    
    def _merge_data(self, base_df: pd.DataFrame, new_df: pd.DataFrame,
                   merge_key: str, columns_to_add: List[str]) -> pd.DataFrame:
        """Merge new data into base dataframe"""

        # Ensure merge key is string type
        if merge_key in base_df.columns:
            base_df = base_df.copy()
            base_df[merge_key] = base_df[merge_key].astype(str)
        if merge_key in new_df.columns:
            new_df = new_df.copy()
            new_df[merge_key] = new_df[merge_key].astype(str)

        # Filter columns_to_add to only those that exist in new_df
        existing_columns_to_add = [col for col in columns_to_add if col in new_df.columns]

        if not existing_columns_to_add:
            return base_df

        # Create a mapping for renaming conflicting columns
        rename_dict = {}
        for col in existing_columns_to_add:
            if col in base_df.columns:
                rename_dict[col] = f'{col}_new'

        # Merge
        if rename_dict:
            # Rename conflicting columns in new_df
            new_df_renamed = new_df.rename(columns=rename_dict)
            merged = pd.merge(base_df, new_df_renamed[[merge_key] + [rename_dict.get(col, col) for col in existing_columns_to_add]], on=merge_key, how='left')

            # Fill missing values
            for col in existing_columns_to_add:
                if rename_dict.get(col) in merged.columns:
                    merged[col] = merged[col].fillna(merged[rename_dict[col]])
                    merged = merged.drop(columns=[rename_dict[col]])
        else:
            merged = pd.merge(base_df, new_df[[merge_key] + existing_columns_to_add], on=merge_key, how='left')

        return merged
    
    def _calculate_enrichment_scores(self, df: pd.DataFrame, enrich_level: str = 'full') -> pd.DataFrame:
        """Calculate enrichment scores for each provider based on enrichment level"""

        scores = []

        for _, row in df.iterrows():
            score = 0
            max_score = 0

            # 1. Basic info (always included)
            max_score += 25
            basic_fields = ['name', 'address', 'phone']
            basic_count = sum(1 for field in basic_fields if pd.notna(row.get(field, '')) and str(row[field]).strip())
            score += (basic_count / len(basic_fields)) * 25

            # 2. Professional info (always included)
            max_score += 25
            prof_fields = ['years_experience', 'primary_specialty', 'license_status']
            prof_count = sum(1 for field in prof_fields if pd.notna(row.get(field, '')) and str(row[field]).strip())
            score += (prof_count / len(prof_fields)) * 25

            # 3. Education info (for moderate and full)
            if enrich_level in ['moderate', 'full']:
                max_score += 25
                edu_fields = ['inferred_degree', 'inferred_medical_school']
                edu_count = sum(1 for field in edu_fields if pd.notna(row.get(field, '')) and str(row[field]).strip())
                score += (edu_count / len(edu_fields)) * 25

            # 4. Practice info (only for full, and only if columns exist)
            if enrich_level == 'full':
                practice_fields = ['telehealth_available', 'business_hours', 'google_rating']
                existing_practice_fields = [f for f in practice_fields if f in df.columns]
                if existing_practice_fields:
                    max_score += 25
                    practice_count = sum(1 for field in existing_practice_fields if pd.notna(row.get(field, '')) and str(row[field]).strip())
                    score += (practice_count / len(existing_practice_fields)) * 25

            # Calculate final score (0-100)
            if max_score > 0:
                final_score = (score / max_score) * 100
            else:
                final_score = 0

            scores.append(round(final_score, 1))

        df['enrichment_score'] = scores
        return df
    
    def save_profiles(self, profiles_df: pd.DataFrame, output_path: str = None):
        """Save enriched profiles to CSV and Excel"""
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"data/output/enriched_profiles_{timestamp}"
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save to CSV
        csv_path = f"{output_path}.csv"
        profiles_df.to_csv(csv_path, index=False)
        print(f"💾 Profiles saved to CSV: {csv_path}")
        
        # Save to Excel (better formatting)
        excel_path = f"{output_path}.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            profiles_df.to_excel(writer, sheet_name='Enriched Profiles', index=False)
            
            # Add summary sheet
            summary = self._create_summary_sheet(profiles_df)
            summary.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"💾 Profiles saved to Excel: {excel_path}")
        
        # Create a simplified version for quick review
        simple_cols = ['name', 'primary_specialty', 'years_experience',
                      'telehealth_available', 'enrichment_score']
        simple_cols = [col for col in simple_cols if col in profiles_df.columns]

        simple_df = profiles_df[simple_cols].copy()
        simple_path = f"{output_path}_simple.csv"
        simple_df.to_csv(simple_path, index=False)
        print(f"📋 Simple view saved to: {simple_path}")
        
        return csv_path, excel_path
    
    def _create_summary_sheet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create summary statistics sheet"""
        
        summary_data = []
        
        # Basic counts
        summary_data.append(['Total Providers', len(df)])
        summary_data.append(['With Experience Data', df['years_experience'].notna().sum() if 'years_experience' in df.columns else 0])
        summary_data.append(['With Specialty Data', df['primary_specialty'].notna().sum() if 'primary_specialty' in df.columns else 0])
        summary_data.append(['With Telehealth Info', df['telehealth_available'].notna().sum() if 'telehealth_available' in df.columns else 0])
        
        # Averages
        if 'years_experience' in df.columns:
            avg_exp = df['years_experience'].mean()
            summary_data.append(['Average Experience (years)', round(avg_exp, 1)])
        
        if 'enrichment_score' in df.columns:
            avg_score = df['enrichment_score'].mean()
            summary_data.append(['Average Enrichment Score', round(avg_score, 1)])
        
        # Enrichment level distribution
        if 'enrichment_level' in df.columns:
            level_counts = df['enrichment_level'].value_counts()
            for level, count in level_counts.items():
                percentage = (count / len(df)) * 100
                summary_data.append([f'{level} Enrichment', f'{count} ({percentage:.1f}%)'])
        
        # Telehealth availability
        if 'telehealth_available' in df.columns:
            telehealth_count = (df['telehealth_available'] == True).sum()
            telehealth_pct = (telehealth_count / len(df)) * 100
            summary_data.append(['Telehealth Available', f'{telehealth_count} ({telehealth_pct:.1f}%)'])
        
        summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
        return summary_df