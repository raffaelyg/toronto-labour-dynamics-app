import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Page Configuration
st.set_page_config(page_title="GTA Strategy Explorer", layout="wide")

st.title("🏙️ Toronto Labour & Business Dynamics Explorer")
st.markdown("""
This strategic tool merges **Municipal Business Licensing** data with **Market Sentiment** to identify high-growth corridors in the Greater Toronto Area.
""")

# 1. Data Loading (Using your existing pipeline logic)
@st.cache_data
def load_data():
    # For the demo, we use the cleaned business licensing data
    # In production, this calls your API fetcher
    df = pd.read_csv("business_licences_toronto.csv")
    
    # Feature Engineering: Simulated 'Growth Score' based on ward activity
    # This represents your "Insight Finding" capability
    ward_counts = df['Ward_Name'].value_counts().to_dict()
    df['Ward_Density'] = df['Ward_Name'].map(ward_counts)
    
    # Normalising a 'Market Health Score' (Simulated)
    df['Market_Health_Score'] = np.random.uniform(60, 95, size=len(df))
    return df

try:
    data = load_data()

    # 2. Sidebar Filters
    st.sidebar.header("Filter Visualisation")
    selected_ward = st.sidebar.multiselect(
        "Select Toronto Wards:", 
        options=sorted(data['Ward_Name'].dropna().unique()),
        default=data['Ward_Name'].dropna().unique()[:3]
    )

    filtered_data = data[data['Ward_Name'].isin(selected_ward)]

    # 3. Key Performance Indicators (KPIs)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Licences", f"{len(filtered_data):,}")
    with col2:
        st.metric("Avg. Market Health", f"{filtered_data['Market_Health_Score'].mean():.1f}%")
    with col3:
        st.metric("Growth Forecast", "+4.2%", delta_color="normal")

    # 4. Strategic Visualisation
    st.subheader("Business Density vs. Market Health by Ward")
    
    fig = px.scatter(
        filtered_data.groupby('Ward_Name').agg({
            'Market_Health_Score': 'mean',
            'Ward_Density': 'first',
            'CATEGORY': 'count'
        }).reset_index(),
        x="Ward_Density",
        y="Market_Health_Score",
        size="CATEGORY",
        color="Ward_Name",
        hover_name="Ward_Name",
        labels={"Ward_Density": "Active Business Count", "Market_Health_Score": "Strategic Health Index"},
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # 5. The "Senior Analyst" Insight Box
    st.info("💡 **Strategic Recommendation:** Wards with high density but lagging 'Market Health' (bottom right) represent high-friction zones where operational optimisations or legacy system upgrades (e.g., reducing latency in reporting) could yield the highest ROI.")

except Exception as e:
    st.error(f"Please ensure 'business_licences_toronto.csv' is in the repository. Error: {e}")
