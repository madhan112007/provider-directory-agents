import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import json
from orchestrator import ProviderOrchestrator

st.set_page_config(page_title="Provider Directory Intelligence", layout="wide", page_icon="📊")

# Custom CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {font-family: 'Inter', sans-serif;}
    .main {background: linear-gradient(135deg, #e0f2fe 0%, #dbeafe 100%); padding: 1rem 2rem;}
    
    [data-testid="stSidebar"] {display: none;}
    
    .stButton button {
        background: transparent !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s !important;
        border-bottom: 3px solid transparent !important;
    }
    
    .stButton button:hover {
        background: rgba(255,255,255,0.1) !important;
        border-bottom: 3px solid white !important;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
        transition: transform 0.2s;
    }
    .metric-card:hover {transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0,0,0,0.12);}
    
    .stMetric {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid #667eea;
    }
    .stMetric label {color: #64748b !important; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;}
    .stMetric [data-testid="stMetricValue"] {color: #1e293b !important; font-size: 2rem; font-weight: 700;}
    .stMetric [data-testid="stMetricDelta"] {font-size: 0.875rem;}
    
    .stButton>button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(14, 165, 233, 0.6);
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    }
    
    h1 {color: #991b1b !important; font-weight: 700; font-size: 2.5rem; margin-bottom: 0.5rem;}
    h2 {color: #991b1b !important; font-weight: 600; font-size: 1.75rem;}
    h3 {color: #dc2626 !important; font-weight: 600; font-size: 1.25rem;}
    
    .navbar h2 {color: white !important;}
    .navbar p {color: #fecaca !important;}
    p, div, span, label {color: #334155 !important;}
    
    .stDataFrame {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        overflow: hidden;
    }
    
    .content-box {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #334155 100%);
    }
    
    .css-1d391kg {padding: 2rem 1rem;}
    
    .stExpander {
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = ProviderOrchestrator()
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

orchestrator = st.session_state.orchestrator

# Top Navigation Bar
if st.session_state.user_role:
    # Initialize current page
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Create container for navbar
    st.markdown("""
    <style>
    .navbar {
        background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);
        padding: 1.5rem 2rem;
        margin: -1rem -2rem 2rem -2rem;
        box-shadow: 0 4px 20px rgba(220, 38, 38, 0.3);
    }
    </style>
    <div class='navbar'></div>
    """, unsafe_allow_html=True)
    
    # Logo and User Info Row
    top_col1, top_col2 = st.columns([8, 2])
    with top_col1:
        st.markdown("""
        <div style='margin-top: -5rem;'>
            <h2 style='color: white !important; margin: 0; font-size: 1.75rem; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>🏥 Provider Directory</h2>
            <p style='color: #fecaca !important; margin: 0; font-size: 0.875rem;'>Healthcare Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    with top_col2:
        st.markdown(f"""
        <div style='margin-top: -5rem; text-align: right;'>
            <p style='color: #bae6fd; margin: 0; font-size: 0.875rem;'>Logged in as</p>
            <p style='color: white; margin: 0; font-size: 1rem; font-weight: 600;'>{st.session_state.user_role}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation Menu Row
    st.markdown("<div style='margin-top: -3.5rem;'></div>", unsafe_allow_html=True)
    
    if st.session_state.user_role == "Patient":
        menu_items = ["Home", "Find a Doctor", "Book Appointment", "My Appointments"]
    else:
        menu_items = ["Home", "Dashboard", "Process Batch", "Workflow Queue", "Analytics", "Settings"]
    
    nav_cols = st.columns(len(menu_items) + 1)
    
    for idx, item in enumerate(menu_items):
        with nav_cols[idx]:
            if st.button(item, key=f"nav_{item}", use_container_width=True):
                st.session_state.current_page = item
                st.rerun()
    
    with nav_cols[-1]:
        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state.user_role = None
            st.session_state.current_page = "Home"
            st.rerun()
    
    st.markdown("<div style='margin-bottom: 2rem;'></div>", unsafe_allow_html=True)
    
    page = st.session_state.current_page
else:
    page = "Home"

# HOME PAGE
if page == "Home":
    if not st.session_state.user_role:
        st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <h1 style='font-size: 3rem; margin-bottom: 1rem;'>Welcome to Provider Directory</h1>
            <p style='color: #e2e8f0; font-size: 1.5rem;'>Your trusted healthcare network platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # Patient Card
            st.markdown("""
            <div style='background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%); padding: 3rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(14, 165, 233, 0.4); text-align: center;'>
                <img src='https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=400&h=300&fit=crop' style='width: 100%; height: 200px; object-fit: cover; border-radius: 12px; margin-bottom: 1.5rem;'/>
                <h2 style='color: white; margin-bottom: 1rem;'>I'm a Patient</h2>
                <p style='color: white; font-size: 1.125rem; margin-bottom: 2rem;'>Find doctors, view specialties, and book appointments</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Continue as Patient", key="patient_btn", use_container_width=True):
                st.session_state.user_role = "Patient"
                st.rerun()
            
            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # Admin Card
            st.markdown("""
            <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 3rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 10px 40px rgba(16, 185, 129, 0.4); text-align: center;'>
                <img src='https://images.unsplash.com/photo-1504813184591-01572f98c85f?w=400&h=300&fit=crop' style='width: 100%; height: 200px; object-fit: cover; border-radius: 12px; margin-bottom: 1.5rem;'/>
                <h2 style='color: white; margin-bottom: 1rem;'>I'm an Admin</h2>
                <p style='color: white; font-size: 1.125rem; margin-bottom: 2rem;'>Manage providers, process data, and view analytics</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Continue as Admin", key="admin_btn", use_container_width=True):
                st.session_state.user_role = "Admin"
                st.rerun()
    
    else:
        # Dashboard for logged-in users
        st.markdown(f"""
        <div style='margin-bottom: 2rem;'>
            <h1>Welcome, {st.session_state.user_role}!</h1>
            <p style='color: #e2e8f0; font-size: 1.125rem;'>Access your personalized dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.user_role == "Patient":
            # Welcome Section
            st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                <h2 style='color: #1e293b; margin-bottom: 1rem;'>Welcome to Provider Directory</h2>
                <p style='color: #64748b; font-size: 1.125rem; line-height: 1.8;'>
                    Your trusted healthcare companion for finding and connecting with qualified medical professionals. 
                    We make healthcare accessible by providing you with a comprehensive directory of verified doctors, 
                    specialists, and healthcare providers in your area.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Why Choose Us Section
            st.markdown("""
            <div style='background: white; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                <h3 style='color: #1e293b; margin-bottom: 1.5rem;'>Why Choose Our Platform?</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style='background: #f0f9ff; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <h4 style='color: #0369a1; margin-bottom: 0.5rem;'>✓ Verified Providers</h4>
                    <p style='color: #64748b; margin: 0;'>All doctors are verified and licensed healthcare professionals</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background: #f0fdf4; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <h4 style='color: #15803d; margin-bottom: 0.5rem;'>✓ Easy Booking</h4>
                    <p style='color: #64748b; margin: 0;'>Book appointments online in just a few clicks</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: #fef3c7; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <h4 style='color: #92400e; margin-bottom: 0.5rem;'>✓ Wide Network</h4>
                    <p style='color: #64748b; margin: 0;'>Access to hundreds of doctors across multiple specialties</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("""
                <div style='background: #fce7f3; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;'>
                    <h4 style='color: #9f1239; margin-bottom: 0.5rem;'>✓ Location Based</h4>
                    <p style='color: #64748b; margin: 0;'>Find doctors near you with interactive maps</p>
                </div>
                """, unsafe_allow_html=True)
            

            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div style='background: white; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                    <img src='https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=300&h=200&fit=crop' style='width: 100%; height: 150px; object-fit: cover; border-radius: 8px;'/>
                    <h3 style='color: #1e293b; margin-top: 1rem;'>Find Doctors</h3>
                    <p style='color: #64748b;'>Search our network</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div style='background: white; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                    <img src='https://images.unsplash.com/photo-1631217868264-e5b90bb7e133?w=300&h=200&fit=crop' style='width: 100%; height: 150px; object-fit: cover; border-radius: 8px;'/>
                    <h3 style='color: #1e293b; margin-top: 1rem;'>Book Appointment</h3>
                    <p style='color: #64748b;'>Schedule online</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div style='background: white; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                    <img src='https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=300&h=200&fit=crop' style='width: 100%; height: 150px; object-fit: cover; border-radius: 8px;'/>
                    <h3 style='color: #1e293b; margin-top: 1rem;'>My Appointments</h3>
                    <p style='color: #64748b;'>Manage bookings</p>
                </div>
                """, unsafe_allow_html=True)
        
        else:  # Admin
            conn = sqlite3.connect(orchestrator.db_path)
            total_providers = pd.read_sql("SELECT COUNT(*) as cnt FROM providers", conn).iloc[0]['cnt']
            manual_review = pd.read_sql("SELECT COUNT(*) as cnt FROM workflow_queue WHERE status='pending'", conn).iloc[0]['cnt']
            total_jobs = pd.read_sql("SELECT COUNT(*) as cnt FROM jobs", conn).iloc[0]['cnt']
            conn.close()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                    <img src='https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=300&h=200&fit=crop' style='width: 100%; height: 150px; object-fit: cover; border-radius: 8px;'/>
                    <h3 style='color: #1e293b; margin-top: 1rem;'>{total_providers}</h3>
                    <p style='color: #64748b;'>Total Providers</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                    <img src='https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=300&h=200&fit=crop' style='width: 100%; height: 150px; object-fit: cover; border-radius: 8px;'/>
                    <h3 style='color: #1e293b; margin-top: 1rem;'>{manual_review}</h3>
                    <p style='color: #64748b;'>Pending Reviews</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='background: white; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 20px rgba(0,0,0,0.08);'>
                    <img src='https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=300&h=200&fit=crop' style='width: 100%; height: 150px; object-fit: cover; border-radius: 8px;'/>
                    <h3 style='color: #1e293b; margin-top: 1rem;'>{total_jobs}</h3>
                    <p style='color: #64748b;'>Jobs Completed</p>
                </div>
                """, unsafe_allow_html=True)

# FIND A DOCTOR PAGE (Patient-Friendly)
elif page == "Find a Doctor":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Find a Doctor</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Search for healthcare providers in our network</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    
    # Search filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_name = st.text_input("Doctor Name", placeholder="Enter doctor's name...")
    
    with col2:
        conn = sqlite3.connect(orchestrator.db_path)
        specialties = pd.read_sql("SELECT DISTINCT specialty FROM providers ORDER BY specialty", conn)
        specialty_list = ['All'] + specialties['specialty'].tolist()
        search_specialty = st.selectbox("Specialty", specialty_list)
    
    with col3:
        states = pd.read_sql("SELECT DISTINCT state FROM providers ORDER BY state", conn)
        state_list = ['All'] + states['state'].tolist()
        search_state = st.selectbox("State", state_list)
    
    if st.button("Search", type="primary"):
        # Build query
        query = "SELECT name, specialty, phone, address, state FROM providers WHERE 1=1"
        
        if search_name:
            query += f" AND name LIKE '%{search_name}%'"
        if search_specialty != 'All':
            query += f" AND specialty = '{search_specialty}'"
        if search_state != 'All':
            query += f" AND state = '{search_state}'"
        
        query += " LIMIT 50"
        
        results = pd.read_sql(query, conn)
        
        st.markdown(f"<h3>Found {len(results)} Doctors</h3>", unsafe_allow_html=True)
        
        if not results.empty:
            # Show map with doctor locations
            state_coords = {
                'CA': [36.7783, -119.4179], 'TX': [31.9686, -99.9018], 'FL': [27.6648, -81.5158],
                'NY': [40.7128, -74.0060], 'PA': [41.2033, -77.1945], 'IL': [40.6331, -89.3985],
                'OH': [40.4173, -82.9071], 'GA': [32.1656, -82.9001], 'NC': [35.7596, -79.0193],
                'MI': [44.3148, -85.6024], 'NJ': [40.0583, -74.4057], 'VA': [37.4316, -78.6569],
                'WA': [47.7511, -120.7401], 'AZ': [34.0489, -111.0937], 'MA': [42.4072, -71.3824],
                'Unknown': [39.8283, -98.5795]
            }
            
            map_data = []
            for _, row in results.iterrows():
                state = row['state'] if row['state'] in state_coords else 'Unknown'
                coords = state_coords[state]
                map_data.append({
                    'lat': coords[0],
                    'lon': coords[1],
                    'name': row['name'],
                    'specialty': row['specialty']
                })
            
            map_df = pd.DataFrame(map_data)
            
            fig = px.scatter_mapbox(map_df, lat='lat', lon='lon',
                                   hover_name='name',
                                   hover_data={'specialty': True, 'lat': False, 'lon': False},
                                   color='specialty',
                                   zoom=4,
                                   height=400)
            
            fig.update_layout(
                mapbox_style='open-street-map',
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
            
            # Doctor cards
            for idx, row in results.iterrows():
                with st.container():
                    st.markdown("""
                    <div style='background: #f8fafc; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #667eea;'>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"<h4 style='margin: 0; color: #1e293b;'>{row['name']}</h4>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin: 0.5rem 0; color: #64748b;'><strong>Specialty:</strong> {row['specialty']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin: 0.5rem 0; color: #64748b;'><strong>Phone:</strong> {row['phone']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin: 0.5rem 0; color: #64748b;'><strong>Address:</strong> {row['address']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin: 0.5rem 0; color: #64748b;'><strong>State:</strong> {row['state']}</p>", unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("Book Appointment", key=f"book_{idx}", type="primary"):
                            if 'appointments' not in st.session_state:
                                st.session_state.appointments = []
                            st.session_state.appointments.append({
                                'doctor': row['name'],
                                'specialty': row['specialty'],
                                'phone': row['phone'],
                                'status': 'Pending'
                            })
                            st.success(f"Appointment request sent to {row['name']}!")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.warning("No doctors found matching your search criteria. Try different filters.")
    
    conn.close()
    st.markdown("</div>", unsafe_allow_html=True)

# BOOK APPOINTMENT PAGE
elif page == "Book Appointment":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Book New Appointment</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Schedule an appointment with your preferred doctor</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    
    # Step 1: Select Doctor
    st.markdown("<h3>Step 1: Select Doctor</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        conn = sqlite3.connect(orchestrator.db_path)
        specialties = pd.read_sql("SELECT DISTINCT specialty FROM providers ORDER BY specialty", conn)
        specialty_list = specialties['specialty'].tolist()
        selected_specialty = st.selectbox("Select Specialty", specialty_list)
    
    with col2:
        doctors = pd.read_sql(f"SELECT name FROM providers WHERE specialty='{selected_specialty}' LIMIT 20", conn)
        doctor_list = doctors['name'].tolist()
        selected_doctor = st.selectbox("Select Doctor", doctor_list)
    
    # Get doctor details
    doctor_info = pd.read_sql(f"SELECT * FROM providers WHERE name='{selected_doctor}' LIMIT 1", conn)
    conn.close()
    
    if not doctor_info.empty:
        st.markdown("""
        <div style='background: #f0f9ff; padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid #0ea5e9;'>
        """, unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0; color: #0c4a6e;'><strong>Doctor:</strong> {doctor_info.iloc[0]['name']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0; color: #0c4a6e;'><strong>Specialty:</strong> {doctor_info.iloc[0]['specialty']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0; color: #0c4a6e;'><strong>Phone:</strong> {doctor_info.iloc[0]['phone']}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin: 0; color: #0c4a6e;'><strong>Address:</strong> {doctor_info.iloc[0]['address']}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Step 2: Select Date & Time
    st.markdown("<h3>Step 2: Select Date & Time</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        appointment_date = st.date_input("Appointment Date", min_value=datetime.now().date())
    
    with col2:
        time_slots = ["09:00 AM", "10:00 AM", "11:00 AM", "02:00 PM", "03:00 PM", "04:00 PM"]
        appointment_time = st.selectbox("Time Slot", time_slots)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Step 3: Patient Details
    st.markdown("<h3>Step 3: Your Details</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        patient_name = st.text_input("Your Name")
        patient_phone = st.text_input("Phone Number")
    
    with col2:
        patient_email = st.text_input("Email Address")
        reason = st.text_area("Reason for Visit", height=100)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    # Book Button
    if st.button("Confirm Appointment", type="primary", use_container_width=True):
        if patient_name and patient_phone:
            if 'appointments' not in st.session_state:
                st.session_state.appointments = []
            
            st.session_state.appointments.append({
                'doctor': selected_doctor,
                'specialty': selected_specialty,
                'phone': doctor_info.iloc[0]['phone'],
                'date': str(appointment_date),
                'time': appointment_time,
                'patient_name': patient_name,
                'patient_phone': patient_phone,
                'reason': reason,
                'status': 'Confirmed'
            })
            
            st.success(f"✅ Appointment confirmed with {selected_doctor} on {appointment_date} at {appointment_time}!")
            st.balloons()
        else:
            st.error("Please fill in your name and phone number.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# MY APPOINTMENTS PAGE
elif page == "My Appointments":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>My Appointments</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>View and manage your appointments</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    
    if 'appointments' not in st.session_state or len(st.session_state.appointments) == 0:
        st.info("You have no appointments scheduled. Search for a doctor to book an appointment.")
    else:
        st.markdown(f"<h3>You have {len(st.session_state.appointments)} appointment(s)</h3>", unsafe_allow_html=True)
        
        for idx, appt in enumerate(st.session_state.appointments):
            with st.container():
                st.markdown("""
                <div style='background: #f0fdf4; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #10b981;'>
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"<h4 style='margin: 0; color: #1e293b;'>{appt['doctor']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin: 0.5rem 0; color: #64748b;'><strong>Specialty:</strong> {appt['specialty']}</p>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"<p style='margin: 0.5rem 0; color: #64748b;'><strong>Phone:</strong> {appt['phone']}</p>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin: 0.5rem 0; color: #10b981;'><strong>Status:</strong> {appt['status']}</p>", unsafe_allow_html=True)
                
                with col3:
                    if st.button("Cancel", key=f"cancel_{idx}"):
                        st.session_state.appointments.pop(idx)
                        st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# DASHBOARD PAGE (Admin)
elif page == "Dashboard":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Provider Directory Intelligence</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Real-time monitoring and analytics dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    conn = sqlite3.connect(orchestrator.db_path)
    
    total_providers = pd.read_sql("SELECT COUNT(*) as cnt FROM providers", conn).iloc[0]['cnt']
    auto_resolved = pd.read_sql("SELECT COUNT(*) as cnt FROM providers WHERE status='auto_resolve'", conn).iloc[0]['cnt']
    manual_review = pd.read_sql("SELECT COUNT(*) as cnt FROM workflow_queue WHERE status='pending'", conn).iloc[0]['cnt']
    total_jobs = pd.read_sql("SELECT COUNT(*) as cnt FROM jobs", conn).iloc[0]['cnt']
    
    with col1:
        st.metric("Total Providers", f"{total_providers:,}", delta="+12 today")
    with col2:
        st.metric("Auto-Resolved", f"{auto_resolved:,}", delta=f"{(auto_resolved/max(total_providers,1)*100):.1f}%")
    with col3:
        st.metric("Manual Review", f"{manual_review:,}", delta="-3 today", delta_color="inverse")
    with col4:
        st.metric("Total Jobs", f"{total_jobs:,}", delta="+2 today")
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Processing Pipeline</h3>", unsafe_allow_html=True)
        pipeline_data = pd.DataFrame({
            'Stage': ['Validation', 'Enrichment', 'QA', 'Correction', 'Completed'],
            'Count': [total_providers, total_providers, total_providers, auto_resolved, auto_resolved]
        })
        fig = px.funnel(pipeline_data, x='Count', y='Stage', color='Stage',
                       color_discrete_sequence=['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'])
        fig.update_layout(showlegend=False, height=350, paper_bgcolor='white', plot_bgcolor='white',
                         font=dict(family='Inter', size=12))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Resolution Rate</h3>", unsafe_allow_html=True)
        resolution_data = pd.DataFrame({
            'Status': ['Auto-Resolved', 'Manual Review'],
            'Count': [auto_resolved, manual_review]
        })
        fig = px.pie(resolution_data, values='Count', names='Status', 
                     color_discrete_sequence=['#667eea', '#f093fb'],
                     hole=0.4)
        fig.update_layout(height=350, paper_bgcolor='white',
                         font=dict(family='Inter', size=12))
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.markdown("<h3>Recent Jobs</h3>", unsafe_allow_html=True)
    jobs_df = pd.read_sql("SELECT * FROM jobs ORDER BY started_at DESC LIMIT 10", conn)
    if not jobs_df.empty:
        jobs_df['metrics'] = jobs_df['metrics'].apply(lambda x: json.loads(x) if x else {})
        st.dataframe(jobs_df[['job_id', 'batch_size', 'status', 'started_at', 'completed_at']], 
                     use_container_width=True, hide_index=True)
    else:
        st.info("No jobs processed yet. Start by processing a batch!")
    st.markdown("</div>", unsafe_allow_html=True)
    
    conn.close()

# PROCESS BATCH PAGE (Admin)
elif page == "Process Batch":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Process Provider Batch</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Upload and process provider data files</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Upload Provider Data</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} providers")
            
            # Parse the 'original' column if it exists (QA Agent format)
            if 'original' in df.columns:
                import ast
                providers_list = []
                for idx, row in df.iterrows():
                    try:
                        original_data = ast.literal_eval(row['original']) if isinstance(row['original'], str) else row['original']
                        providers_list.append(original_data)
                    except:
                        providers_list.append(row.to_dict())
                df_display = pd.DataFrame(providers_list)
            else:
                df_display = df
            
            st.dataframe(df_display.head(10), use_container_width=True)
            
            if st.button("Start Processing", type="primary"):
                job_id = f"JOB_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Use parsed data if available
                if 'original' in df.columns:
                    providers = providers_list
                else:
                    providers = df.to_dict('records')
                
                with st.spinner("Processing batch..."):
                    results = orchestrator.process_batch(providers, job_id)
                    progress_bar.progress(100)
                    status_text.success(f"✅ Completed in {results['processing_time']:.2f}s")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Auto-Resolved", results['auto_resolved'])
                with col2:
                    st.metric("Manual Review", results['manual_review'])
                with col3:
                    st.metric("Errors", results['errors'])
                
                st.json(orchestrator.generate_summary_report(job_id))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Sample Template</h3>", unsafe_allow_html=True)
        st.code("""provider_id,name,npi,phone,address,specialty,state
P001,Dr. Smith,1234567890,555-1234,123 Main St,Cardiology,CA
P002,Dr. Jones,9876543210,555-5678,456 Oak Ave,Pediatrics,NY""")
        
        st.download_button(
            "Download Template",
            data="provider_id,name,npi,phone,address,specialty,state\n",
            file_name="provider_template.csv",
            mime="text/csv"
        )
        st.markdown("</div>", unsafe_allow_html=True)

# WORKFLOW QUEUE PAGE (Admin)
elif page == "Workflow Queue":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Manual Review Queue</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Providers requiring manual verification</p>
    </div>
    """, unsafe_allow_html=True)
    
    queue = orchestrator.get_workflow_queue(100)
    
    if queue:
        st.info(f"{len(queue)} providers awaiting manual review")
        
        queue_df = pd.DataFrame(queue)
        queue_df = queue_df.sort_values('priority', ascending=False)
        
        for idx, row in queue_df.iterrows():
            with st.expander(f"{row['provider_id']} - Priority: {row['priority']}"):
                conn = sqlite3.connect(orchestrator.db_path)
                provider_data = pd.read_sql(
                    f"SELECT * FROM providers WHERE id='{row['provider_id']}'", conn
                ).iloc[0]
                conn.close()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Name:**", provider_data['name'])
                    st.write("**NPI:**", provider_data['npi'])
                    st.write("**Phone:**", provider_data['phone'])
                with col2:
                    st.write("**Address:**", provider_data['address'])
                    st.write("**Specialty:**", provider_data['specialty'])
                    st.write("**State:**", provider_data['state'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Approve", key=f"approve_{row['id']}"):
                        st.success("Approved!")
                with col2:
                    if st.button("Edit", key=f"edit_{row['id']}"):
                        st.info("Edit mode activated")
                with col3:
                    if st.button("Reject", key=f"reject_{row['id']}"):
                        st.error("Rejected")
    else:
        st.success("No providers in queue! All caught up.")

# ANALYTICS PAGE (Admin)
elif page == "Analytics":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>Advanced Analytics</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Comprehensive data insights and trends</p>
    </div>
    """, unsafe_allow_html=True)
    
    conn = sqlite3.connect(orchestrator.db_path)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Specialty Distribution</h3>", unsafe_allow_html=True)
        specialty_df = pd.read_sql("""
            SELECT specialty, COUNT(*) as count 
            FROM providers 
            GROUP BY specialty 
            ORDER BY count DESC 
            LIMIT 10
        """, conn)
        
        if not specialty_df.empty:
            # Create animated sunburst chart
            fig = px.sunburst(
                specialty_df,
                path=['specialty'],
                values='count',
                color='count',
                color_continuous_scale='RdPu',
                hover_data={'count': True}
            )
            fig.update_traces(
                textinfo='label+percent entry',
                marker=dict(line=dict(color='white', width=2))
            )
            fig.update_layout(
                height=350,
                paper_bgcolor='white',
                font=dict(family='Inter', size=11),
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Global Provider Map</h3>", unsafe_allow_html=True)
        
        # Get provider locations
        providers_map = pd.read_sql("SELECT name, address, state, specialty FROM providers LIMIT 200", conn)
        
        if not providers_map.empty:
            # Create map data with coordinates (using state centers as approximation)
            state_coords = {
                'CA': [36.7783, -119.4179], 'TX': [31.9686, -99.9018], 'FL': [27.6648, -81.5158],
                'NY': [40.7128, -74.0060], 'PA': [41.2033, -77.1945], 'IL': [40.6331, -89.3985],
                'OH': [40.4173, -82.9071], 'GA': [32.1656, -82.9001], 'NC': [35.7596, -79.0193],
                'MI': [44.3148, -85.6024], 'NJ': [40.0583, -74.4057], 'VA': [37.4316, -78.6569],
                'WA': [47.7511, -120.7401], 'AZ': [34.0489, -111.0937], 'MA': [42.4072, -71.3824],
                'TN': [35.5175, -86.5804], 'IN': [40.2672, -86.1349], 'MO': [37.9643, -91.8318],
                'MD': [39.0458, -76.6413], 'WI': [43.7844, -88.7879], 'CO': [39.5501, -105.7821],
                'MN': [46.7296, -94.6859], 'SC': [33.8361, -81.1637], 'AL': [32.3182, -86.9023],
                'LA': [30.9843, -91.9623], 'KY': [37.8393, -84.2700], 'OR': [43.8041, -120.5542],
                'OK': [35.0078, -97.0929], 'CT': [41.6032, -73.0877], 'IA': [41.8780, -93.0977],
                'MS': [32.3547, -89.3985], 'AR': [35.2010, -91.8318], 'KS': [39.0119, -98.4842],
                'UT': [39.3210, -111.0937], 'NV': [38.8026, -116.4194], 'NM': [34.5199, -105.8701],
                'WV': [38.5976, -80.4549], 'NE': [41.4925, -99.9018], 'ID': [44.0682, -114.7420],
                'HI': [19.8968, -155.5828], 'NH': [43.1939, -71.5724], 'ME': [45.2538, -69.4455],
                'RI': [41.5801, -71.4774], 'MT': [46.8797, -110.3626], 'DE': [38.9108, -75.5277],
                'SD': [43.9695, -99.9018], 'ND': [47.5515, -101.0020], 'AK': [64.2008, -149.4937],
                'VT': [44.5588, -72.5778], 'WY': [43.0760, -107.2903], 'Unknown': [39.8283, -98.5795]
            }
            
            map_data = []
            for _, row in providers_map.iterrows():
                state = row['state'] if row['state'] in state_coords else 'Unknown'
                coords = state_coords[state]
                map_data.append({
                    'lat': coords[0],
                    'lon': coords[1],
                    'name': row['name'],
                    'specialty': row['specialty'],
                    'state': row['state']
                })
            
            map_df = pd.DataFrame(map_data)
            
            # Create scatter map with satellite view
            fig = px.scatter_mapbox(map_df, lat='lat', lon='lon',
                                   hover_name='name',
                                   hover_data={'specialty': True, 'state': True, 'lat': False, 'lon': False},
                                   color='specialty',
                                   zoom=3,
                                   height=350)
            
            fig.update_layout(
                mapbox_style='open-street-map',
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor='white',
                font=dict(family='Inter', size=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Processing Time Trends</h3>", unsafe_allow_html=True)
        jobs_df = pd.read_sql("SELECT * FROM jobs ORDER BY started_at", conn)
        
        if not jobs_df.empty:
            jobs_df['metrics'] = jobs_df['metrics'].apply(lambda x: json.loads(x) if x else {})
            jobs_df['processing_time'] = jobs_df['metrics'].apply(lambda x: x.get('processing_time', 0))
            jobs_df['started_at'] = pd.to_datetime(jobs_df['started_at'])
            
            fig = px.line(jobs_df, x='started_at', y='processing_time', 
                         markers=True)
            fig.update_layout(height=350, paper_bgcolor='white', plot_bgcolor='white',
                             font=dict(family='Inter', size=12))
            fig.update_traces(line_color='#667eea', marker=dict(size=8, color='#764ba2'))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>State Rankings</h3>", unsafe_allow_html=True)
        top_states = pd.read_sql("""
            SELECT state, COUNT(*) as count 
            FROM providers 
            GROUP BY state 
            ORDER BY count DESC 
            LIMIT 10
        """, conn)
        
        if not top_states.empty:
            fig = px.bar(top_states, x='count', y='state', orientation='h',
                        color='count', color_continuous_scale='Purples')
            fig.update_layout(height=350, paper_bgcolor='white', plot_bgcolor='white',
                            font=dict(family='Inter', size=12),
                            yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    conn.close()

# SETTINGS PAGE (Admin)
elif page == "Settings":
    st.markdown("""
    <div style='margin-bottom: 2rem;'>
        <h1>System Settings</h1>
        <p style='color: #e2e8f0; font-size: 1.125rem;'>Configure system parameters and preferences</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Agent Configuration</h3>", unsafe_allow_html=True)
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.9, 0.05)
        batch_size = st.number_input("Default Batch Size", 50, 500, 200, 50)
        auto_correction = st.checkbox("Enable Auto-Correction", value=True)
        
        if st.button("Save Settings"):
            st.success("Settings saved successfully!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        st.markdown("<h3>Email Configuration</h3>", unsafe_allow_html=True)
        smtp_server = st.text_input("SMTP Server", "smtp.gmail.com")
        smtp_port = st.number_input("SMTP Port", 1, 65535, 587)
        sender_email = st.text_input("Sender Email", "noreply@provider.ai")
        
        if st.button("Test Email"):
            st.info("Test email sent!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='content-box'>", unsafe_allow_html=True)
    st.markdown("<h3>Database Management</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Backup Database"):
            st.success("Database backed up!")
    with col2:
        if st.button("Clear Cache"):
            st.success("Cache cleared!")
    with col3:
        if st.button("Export Data"):
            st.success("Data exported!")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; color: #e2e8f0; padding: 2rem; margin-top: 3rem; border-top: 1px solid rgba(255,255,255,0.1);'>
    <p style='margin: 0; font-size: 0.875rem;'>Provider Directory Intelligence System | Powered by Multi-Agent Architecture</p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #94a3b8;'>© 2024 Healthcare AI Solutions</p>
</div>
""", unsafe_allow_html=True)
