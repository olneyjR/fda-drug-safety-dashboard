"""
FDA API Direct Connection
Lightweight extraction without Airflow orchestration
"""

import requests
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)


class FDAAPIClient:
    """Simplified FDA API client for Streamlit app"""
    
    BASE_URL = 'https://api.fda.gov/drug/event.json'
    RATE_LIMIT_REQUESTS = 240  # per minute
    RATE_LIMIT_PERIOD = 60  # seconds
    
    def __init__(self):
        self.session = requests.Session()
        self.request_times = []
    
    def _rate_limit(self):
        """Implement rate limiting"""
        now = time.time()
        self.request_times = [t for t in self.request_times if now - t < self.RATE_LIMIT_PERIOD]
        
        if len(self.request_times) >= self.RATE_LIMIT_REQUESTS:
            sleep_time = self.RATE_LIMIT_PERIOD - (now - self.request_times[0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def fetch_adverse_events(self, limit: int = 5000) -> pd.DataFrame:
        """
        Fetch adverse events from FDA API
        
        Args:
            limit: Number of records to fetch (default 5000 for good sample)
        
        Returns:
            DataFrame with flattened adverse events
        """
        all_records = []
        skip = 0
        batch_size = 100  # FDA API max per request
        
        while len(all_records) < limit:
            self._rate_limit()
            
            params = {
                'limit': min(batch_size, limit - len(all_records)),
                'skip': skip
            }
            
            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                results = data.get('results', [])
                
                if not results:
                    break
                
                all_records.extend(results)
                logger.info(f"Fetched {len(results)} records (total: {len(all_records)})")
                
                skip += len(results)
                
                # Check if we've reached the end
                meta = data.get('meta', {})
                total_results = meta.get('results', {}).get('total', 0)
                if skip >= total_results:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                break
        
        # Flatten the nested structure
        df = self._flatten_events(all_records)
        logger.info(f"Extraction complete: {len(df)} total records")
        
        return df
    
    def _flatten_events(self, records: List[Dict]) -> pd.DataFrame:
        """
        Flatten nested JSON structure from FDA API
        """
        flattened_records = []
        
        for record in records:
            base_record = {
                'safetyreportid': record.get('safetyreportid'),
                'receivedate': record.get('receivedate'),
                'receiptdate': record.get('receiptdate'),
                'serious': record.get('serious'),
                'seriousnessdeath': record.get('seriousnessdeath'),
                'seriousnesslifethreatening': record.get('seriousnesslifethreatening'),
                'seriousnesshospitalization': record.get('seriousnesshospitalization'),
            }
            
            # Extract patient info
            patient = record.get('patient', {})
            base_record['patient_age'] = patient.get('patientonsetage')
            base_record['patient_age_unit'] = patient.get('patientonsetageunit')
            base_record['patient_sex'] = patient.get('patientsex')
            base_record['patient_weight'] = patient.get('patientweight')
            
            # Extract drugs (can have multiple drugs per event)
            drugs = patient.get('drug', [])
            for drug_idx, drug in enumerate(drugs):
                drug_record = base_record.copy()
                drug_record['drug_sequence'] = drug_idx + 1
                drug_record['drug_name'] = drug.get('medicinalproduct')
                drug_record['drug_indication'] = drug.get('drugindication')
                drug_record['drug_characterization'] = drug.get('drugcharacterization')
                
                # Extract reactions for this drug
                reactions = patient.get('reaction', [])
                if reactions:
                    drug_record['reactions'] = '|'.join([
                        r.get('reactionmeddrapt', '') for r in reactions
                    ])
                else:
                    drug_record['reactions'] = None
                
                flattened_records.append(drug_record)
        
        return pd.DataFrame(flattened_records)
    
    def transform_to_analytics(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Transform raw FDA data to analytics-ready format
        Mimics Silver + Gold layer transformations
        
        Returns:
            Dictionary with transformed DataFrames
        """
        # Silver layer: Clean and standardize
        df_clean = df.copy()
        
        # Age normalization (fix the FDA code bug)
        age_unit_map = {
            '800': 'Decade',
            '801': 'Year',
            '802': 'Month', 
            '803': 'Week',
            '804': 'Day',
            '805': 'Hour'
        }
        
        df_clean['patient_age_unit_name'] = df_clean['patient_age_unit'].astype(str).map(age_unit_map)
        
        # Convert all ages to years
        def normalize_age(row):
            if pd.isna(row['patient_age']) or pd.isna(row['patient_age_unit_name']):
                return None
            
            age = float(row['patient_age'])
            unit = row['patient_age_unit_name']
            
            if unit == 'Decade':
                return age * 10.0
            elif unit == 'Year':
                return age
            elif unit == 'Month':
                return age / 12.0
            elif unit == 'Week':
                return age / 52.0
            elif unit == 'Day':
                return age / 365.0
            elif unit == 'Hour':
                return age / 8760.0
            return None
        
        df_clean['patient_age_years'] = df_clean.apply(normalize_age, axis=1)
        
        # Sex standardization
        sex_map = {'1': 'Male', '2': 'Female'}
        df_clean['patient_sex_name'] = df_clean['patient_sex'].astype(str).map(sex_map).fillna('Unknown')
        
        # Boolean flags
        df_clean['is_serious'] = df_clean['serious'].fillna(0).astype(int)
        df_clean['is_death'] = df_clean['seriousnessdeath'].fillna(0).astype(int)
        df_clean['is_life_threatening'] = df_clean['seriousnesslifethreatening'].fillna(0).astype(int)
        df_clean['is_hospitalization'] = df_clean['seriousnesshospitalization'].fillna(0).astype(int)
 
       # Gold layer: Build drug risk profile mart
        # Step 1: Deduplicate - keep one row per (drug, report) combination
        df_deduped = df_clean.drop_duplicates(subset=['drug_name', 'safetyreportid'], keep='first')

        # Step 2: Aggregate directly to drug level
        drug_profile = df_deduped.groupby('drug_name').agg({  # ← THIS LINE
            'safetyreportid': 'count',
            'is_serious': 'sum',
            'is_death': 'sum',
            'is_life_threatening': 'sum',
            'is_hospitalization': 'sum',
            'patient_age_years': 'mean',
            'drug_indication': lambda x: '|'.join([str(i) for i in x.dropna().unique()[:5]])
        }).reset_index()
        
        drug_profile.columns = [
            'drug_name',
            'total_adverse_events',
            'serious_events',
            'death_reports',
            'life_threatening_events',
            'hospitalization_events',
            'avg_patient_age',
            'common_indications'
        ]
        
        # Calculate rates
        drug_profile['serious_event_rate'] = (
            drug_profile['serious_events'] / drug_profile['total_adverse_events'] * 100
        ).fillna(0)
        
        drug_profile['fatality_rate'] = (
            drug_profile['death_reports'] / drug_profile['total_adverse_events'] * 100
        ).fillna(0)
        
        # Risk classification
        def classify_risk(row):
            if row['total_adverse_events'] < 5:
                return 'Minimal Data'
            elif row['fatality_rate'] > 15:
                return 'High Risk'
            elif row['fatality_rate'] > 5:
                return 'Moderate Risk'
            else:
                return 'Low Risk'
        
        drug_profile['risk_classification'] = drug_profile.apply(classify_risk, axis=1)
        
        # Severity score (0-5)
        drug_profile['avg_severity_score'] = (
            (drug_profile['serious_event_rate'] / 20) +
            (drug_profile['fatality_rate'] / 20) +
            (drug_profile['life_threatening_events'] / drug_profile['total_adverse_events'] * 5)
        ).clip(0, 5)
        
        return {
            'events': df_clean,
            'drug_risk_profile': drug_profile
        }