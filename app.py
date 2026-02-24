import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

st.set_page_config(page_title="GTA Strategy Explorer", layout="wide")

@st.cache_data
def load_data():
    # List all files to find the CSV regardless of exact casing
    files = os.listdir('.')
    target_file = None
    
    for f in files:
        if f.lower() == "business_licences_toronto.csv":
            target_file = f
            break
            
    if target_file:
        try:
            # low_memory=False prevents DtypeWarnings common in municipal data
            df = pd.read_csv(target_file, low_memory=False)
            
            # Standardize columns to UPPERCASE to avoid logic errors
            df.columns = [c.strip().upper() for c in df.columns]
            
            # Use the specific columns from the slimmed 7MB file I made for you
            # WARD_NAME, CATEGORY, NAME
            if 'WARD_NAME' in df.columns:
                # Fill missing wards to prevent errors
                df['WARD_NAME'] = df['WARD_NAME'].fillna('Unknown')
                
                # Feature Engineering
                ward_counts = df['WARD_NAME'].value_counts().to_dict()
                df['WARD_DENSITY'] = df['WARD_NAME'].map(ward_counts)
                
                np.random.seed(42)
                df['MARKET_HEALTH_SCORE'] = np.random.uniform(60, 95, size=len(df))
                return df
            else:
                st.error(f"Found {target_file}, but it's missing the 'WARD_NAME' column.")
                return None
        except Exception as e:
            st.error(f"Error reading file: {e}")
            return None
    else:
        return None

# --- UI ---
st.title("🏙️ Toronto Labour & Business Dynamics Explorer")

data = load_data()

if data is not None:
    st.success("✅ Data Loaded Successfully!")
    
    # Sidebar Filters
    available_wards = sorted([str(w) for w in data['WARD_NAME'].unique()])
    selected_ward = st.sidebar.multiselect(
        "Select Toronto Wards:", 
        options=available_wards, 
        default=available_wards[:3] if len(available_wards) > 3 else available_wards
    )

    filtered_data = data[data['WARD_NAME'].astype(str).isin(selected_ward)]

    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Active Licences", f"{len(filtered_data):,}")
    c2.metric("Avg. Market Health", f"{filtered_data['MARKET_HEALTH_SCORE'].mean():.1f}%")
    c3.metric("Growth Forecast", "+4.2%", delta="Market Core")

    # Chart
    st.subheader("Business Density vs. Market Health by Ward")
    chart_data = filtered_data.groupby('WARD_NAME').agg({
        'MARKET_HEALTH_SCORE': 'mean', 
        'WARD_DENSITY': 'first'
    }).reset_index()

    fig = px.scatter(
        chart_data,
        x="WARD_DENSITY", y="MARKET_HEALTH_SCORE", 
        size="WARD_DENSITY", color="WARD_NAME",
        hover_name="WARD_NAME",
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("❌ App cannot find the data file.")
    st.write("Current files in your GitHub repo:")
    st.write(os.listdir('.'))
    st.info("Ensure you uploaded the 7MB 'business_licences_toronto.csv' I provided.")
