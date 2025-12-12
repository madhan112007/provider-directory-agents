import pandas as pd
import random
from faker import Faker

fake = Faker()

# Medical specialties
specialties = [
    'Internal Medicine', 'Family Medicine', 'Pediatrics', 'Cardiology',
    'Orthopedics', 'Dermatology', 'Psychiatry', 'Neurology',
    'Obstetrics & Gynecology', 'Ophthalmology', 'Urology', 'Oncology'
]

# US cities with medical centers
cities = [
    ('New York', 'NY'), ('Los Angeles', 'CA'), ('Chicago', 'IL'),
    ('Houston', 'TX'), ('Phoenix', 'AZ'), ('Philadelphia', 'PA'),
    ('San Antonio', 'TX'), ('San Diego', 'CA'), ('Dallas', 'TX'),
    ('San Jose', 'CA'), ('Austin', 'TX'), ('Jacksonville', 'FL'),
    ('Fort Worth', 'TX'), ('Columbus', 'OH'), ('Charlotte', 'NC'),
    ('San Francisco', 'CA'), ('Indianapolis', 'IN'), ('Seattle', 'WA'),
    ('Denver', 'CO'), ('Washington', 'DC'), ('Boston', 'MA')
]

def generate_npi():
    """Generate realistic NPI number"""
    return str(random.randint(1000000000, 1999999999))

def generate_license(state):
    """Generate state-specific license number"""
    return f"{state}{random.randint(10000, 99999)}"

def generate_provider():
    """Generate one provider record"""
    first_name = fake.first_name()
    last_name = fake.last_name()
    city, state = random.choice(cities)
    
    return {
        'name': f"Dr. {first_name} {last_name}",
        'npi': generate_npi(),
        'address': f"{random.randint(100, 9999)} {fake.street_name()}, {city}, {state} {fake.zipcode()}",
        'phone': f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        'license_number': generate_license(state),
        'specialty': random.choice(specialties),
        'email': f"{first_name.lower()}.{last_name.lower()}@medicalgroup.com",
        'hospital_affiliation': f"{city} {random.choice(['General Hospital', 'Medical Center', 'Community Hospital', 'Health System'])}"
    }

# Generate 200 providers
print("Generating 200 sample providers...")
providers = [generate_provider() for _ in range(200)]

# Create DataFrame
df = pd.DataFrame(providers)

# Save to CSV
df.to_csv('data/sample_200_providers.csv', index=False)

print(f"✅ Generated {len(df)} providers")
print("\nSample of generated data:")
print(df.head().to_string())
print(f"\n📁 Saved to: data/sample_200_providers.csv")

# Show statistics
print("\n📊 Data Statistics:")
print(f"Specialties distribution:")
print(df['specialty'].value_counts().head())
print(f"\nStates distribution:")
print(df['address'].apply(lambda x: x.split(',')[-2].strip()).value_counts().head())