"""
Configuration file for Information Enrichment Agent
"""

# GOOGLE PLACES API KEY (Optional - only needed for full enrichment)
# Get from: https://console.cloud.google.com/
# Leave as empty string if not using Google API
GOOGLE_API_KEY = "AIzaSyDT1-YOloB8uKhuBN9HATZsf8VEBYCuxVs"

# NPI Registry API (FREE - no key needed)
NPI_API_URL = "https://npiregistry.cms.hhs.gov/api/"
NPI_RATE_LIMIT = 10  # requests per second

# State License Board URLs (FREE)
STATE_APIS = {
    'FL': 'https://mqa-internet.doh.state.fl.us/MQASearchServices/HealthCareProviders',
    'TX': 'https://www.tmb.state.tx.us/api/search',
    'CA': 'https://www.mbc.ca.gov/Breeze/LicenseVerification.aspx',
    'NY': 'https://www.nysed.gov/verification-search',
    'IL': 'https://www.idfpr.com/LicenseLookUp/',
    'MA': 'https://profiles.mass.gov/search/physician'
}

# File paths
INPUT_CSV = "data/input_data.csv"
OUTPUT_FOLDER = "data/output/"
CACHE_FOLDER = "data/cache/"

# Enrichment settings
ENRICHMENT_LEVELS = {
    'basic': ['npi_enhancement', 'experience_calculation', 'specialty_expansion'],
    'moderate': ['npi_enhancement', 'license_check', 'specialty_expansion', 'education_inference'],
    'full': ['npi_enhancement', 'license_check', 'google_places', 'education_inference', 'specialty_expansion']
}

# Cache settings
ENABLE_CACHE = True
CACHE_EXPIRY_DAYS = 7

# Processing settings
BATCH_SIZE = 50
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "data/enrichment_log.txt"