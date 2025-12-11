"""
Geographic Equipment Map Visualization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from folium import plugins
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title="Карта оборудования", page_icon="🗺️", layout="wide")

st.title("🗺️ Карта расположения оборудования")
st.markdown("Географическая визуализация сетевого оборудования и статуса рисков")
st.markdown("---")


@st.cache_data(ttl=300)
def load_location_data():
    """Load equipment location data from parquet file"""
    try:
        # Try to load from parquet first
        df = pd.read_parquet('data/raw/equipment_locations.parquet')
        print(f"[Maps] Loaded {len(df)} equipment locations from parquet")
    except Exception as e:
        print(f"[Maps] Error loading parquet: {e}")
        try:
            # Fallback to CSV
            df = pd.read_csv('data/raw/equipment_locations.csv')
            print(f"[Maps] Loaded {len(df)} equipment locations from CSV")
        except Exception as e2:
            print(f"[Maps] Error loading CSV: {e2}, using sample data")
            # Sample location data (Russian substations - fallback)
            df = pd.DataFrame({
                'equipment_id': ['SUB001_EQ01', 'SUB002_EQ01', 'SUB003_EQ01', 'SUB004_EQ01',
                               'SUB005_EQ01', 'SUB006_EQ01', 'SUB007_EQ01', 'SUB008_EQ01'],
                'substation_id': ['SUB001', 'SUB002', 'SUB003', 'SUB004',
                                 'SUB005', 'SUB006', 'SUB007', 'SUB008'],
                'substation_name': ['ПС Подольская', 'ПС Тульская', 'ПС Южная', 'ПС Ростовская',
                                   'ПС Казанская', 'ПС Нижегородская', 'ПС Сибирская', 'ПС Красноярская'],
                'latitude': [55.424, 54.193, 45.035, 47.222, 55.796, 56.326, 55.030, 56.010],
                'longitude': [37.547, 37.618, 38.975, 39.720, 49.108, 44.006, 82.920, 92.852],
                'equipment_type': ['Power Transformer'] * 8,
                'capacity_mw': [100, 100, 150, 150, 200, 100, 100, 200],
                'installation_year': [1995, 2000, 2005, 2008, 2010, 2012, 2015, 2018],
                'region': ['Московская область', 'Тульская область', 'Краснодарский край', 'Ростовская область',
                          'Республика Татарстан', 'Нижегородская область', 'Новосибирская область', 'Красноярский край']
            })

    # Load risk data from features.csv if available
    try:
        features_df = pd.read_csv('data/processed/features.csv')
        if 'equipment_id' in features_df.columns and 'risk_level' in features_df.columns:
            # Get latest risk level for each equipment
            risk_data = features_df.groupby('equipment_id').agg({
                'risk_level': 'last',
                'failure_probability': 'last',
                'temperature_top': 'last'
            }).reset_index()
            risk_data.columns = ['equipment_id', 'risk_level', 'failure_probability', 'temperature']

            # Merge with location data
            df = df.merge(risk_data, on='equipment_id', how='left')
            print(f"[Maps] Merged risk data for {len(df)} equipment")
    except Exception as e:
        print(f"[Maps] Could not load risk data: {e}, using synthetic")
        # Add synthetic risk scores
        np.random.seed(42)
        df['failure_probability'] = np.random.beta(2, 20, len(df))
        df['temperature'] = np.random.normal(70, 15, len(df))
        df['risk_level'] = pd.cut(df['failure_probability'],
                                   bins=[0, 0.3, 0.7, 1.0],
                                   labels=[0, 1, 2]).astype(int)

    # Map risk level to status
    if 'risk_level' in df.columns:
        df['status'] = df['risk_level'].map({0: 'Норма', 1: 'Внимание', 2: 'Критично'})
    else:
        df['status'] = df['failure_probability'].apply(
            lambda x: 'Критично' if x > 0.7 else 'Внимание' if x > 0.3 else 'Норма'
        )

    return df


# Load data
df = load_location_data()

# Sidebar filters
with st.sidebar:
    st.header("Фильтры карты")

    equipment_types = st.multiselect(
        "Типы оборудования",
        options=df['equipment_type'].unique(),
        default=df['equipment_type'].unique()
    )

    status_filter = st.multiselect(
        "Статус",
        options=['Норма', 'Внимание', 'Критично'],
        default=['Норма', 'Внимание', 'Критично']
    )

    show_heatmap = st.checkbox("Показать тепловую карту рисков", value=False)
    show_clusters = st.checkbox("Показать кластеры", value=True)

    st.markdown("---")
    st.markdown("### Легенда карты")
    st.markdown("""
    - 🟢 **Норма**: Риск < 30%
    - 🟡 **Внимание**: Риск 30-70%
    - 🔴 **Критично**: Риск > 70%
    """)


# Filter data
filtered_df = df[
    (df['equipment_type'].isin(equipment_types)) &
    (df['status'].isin(status_filter))
]

# Summary metrics
st.subheader("Обзор расположения")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Всего оборудования", len(filtered_df))

with col2:
    critical_count = len(filtered_df[filtered_df['status'] == 'Критично'])
    st.metric("Критическое оборудование", critical_count, delta=f"{critical_count} ед.")

with col3:
    avg_capacity = filtered_df['capacity_mw'].mean()
    st.metric("Ср. мощность", f"{avg_capacity:.0f} МВт")

with col4:
    total_capacity = filtered_df['capacity_mw'].sum()
    st.metric("Общая мощность", f"{total_capacity:.0f} МВт")

st.markdown("---")

# Create map
st.subheader("Интерактивная карта оборудования")

# Calculate map center and zoom based on data spread
center_lat = filtered_df['latitude'].mean()
center_lon = filtered_df['longitude'].mean()

# Calculate appropriate zoom level based on lat/lon range
lat_range = filtered_df['latitude'].max() - filtered_df['latitude'].min()
lon_range = filtered_df['longitude'].max() - filtered_df['longitude'].min()

# Determine zoom level: larger range = smaller zoom (zoomed out more)
if lat_range > 15 or lon_range > 30:
    zoom_level = 3  # Country-level view for Russia
elif lat_range > 5 or lon_range > 10:
    zoom_level = 6  # Regional view
elif lat_range > 1 or lon_range > 2:
    zoom_level = 9  # City-level view
else:
    zoom_level = 12  # Neighborhood view

# Create base map
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=zoom_level,
    tiles='OpenStreetMap'
)

# Color mapping
color_map = {
    'Норма': 'green',
    'Внимание': 'orange',
    'Критично': 'red'
}

icon_map = {
    'Transformer': 'bolt',
    'Generator': 'cog',
    'Transmission Line': 'line-chart',
    'Substation': 'building'
}

# Add markers
if show_clusters:
    marker_cluster = plugins.MarkerCluster().add_to(m)
    parent = marker_cluster
else:
    parent = m

for idx, row in filtered_df.iterrows():
    # Create popup content
    popup_html = f"""
    <div style="font-family: Arial; width: 200px;">
        <h4 style="margin-bottom: 10px;">{row['equipment_id']}</h4>
        <b>Тип:</b> {row['equipment_type']}<br>
        <b>Статус:</b> <span style="color: {color_map[row['status']]};">
            {row['status']}
        </span><br>
        <b>Оценка риска:</b> {row['failure_probability']:.1%}<br>
        <b>Температура:</b> {row['temperature']:.1f}°C<br>
        <b>Мощность:</b> {row['capacity_mw']} МВт<br>
        <b>Установлено:</b> {row['installation_year']}
    </div>
    """

    # Add marker
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['equipment_id']} - {row['status']}",
        icon=folium.Icon(
            color=color_map[row['status']],
            icon=icon_map.get(row['equipment_type'], 'info-sign'),
            prefix='fa'
        )
    ).add_to(parent)

# Add heatmap layer
if show_heatmap:
    heat_data = [[row['latitude'], row['longitude'], row['failure_probability']]
                for idx, row in filtered_df.iterrows()]

    plugins.HeatMap(
        heat_data,
        min_opacity=0.2,
        radius=25,
        blur=35,
        gradient={0.0: 'green', 0.5: 'yellow', 1.0: 'red'}
    ).add_to(m)

# Display map
folium_static(m, width=1200, height=600)

st.markdown("---")

# Equipment details table
st.subheader("Детали оборудования")

display_df = filtered_df[[
    'equipment_id', 'equipment_type', 'status', 'failure_probability',
    'temperature', 'capacity_mw', 'installation_year'
]].copy()

display_df.columns = ['ID оборудования', 'Тип', 'Статус', 'Оценка риска',
                     'Температура (°C)', 'Мощность (МВт)', 'Год']

st.dataframe(
    display_df.style
    .background_gradient(subset=['Оценка риска'], cmap='RdYlGn_r')
    .format({'Оценка риска': '{:.1%}', 'Температура (°C)': '{:.1f}'}),
    use_container_width=True
)

st.markdown("---")

# Geographic analysis
st.subheader("Географический анализ")

col1, col2 = st.columns(2)

with col1:
    # Equipment distribution by type
    type_counts = filtered_df['equipment_type'].value_counts()

    fig = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        title='Распределение оборудования по типам',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Risk distribution by location
    fig = px.scatter(
        filtered_df,
        x='longitude',
        y='latitude',
        size='capacity_mw',
        color='failure_probability',
        hover_data=['equipment_id', 'equipment_type'],
        title='Распределение рисков по географическому положению',
        color_continuous_scale='RdYlGn_r',
        labels={'failure_probability': 'Оценка риска', 'longitude': 'Долгота', 'latitude': 'Широта'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Capacity analysis
st.markdown("---")
st.subheader("Анализ мощности")

capacity_by_type = filtered_df.groupby('equipment_type')['capacity_mw'].sum().reset_index()
capacity_by_type.columns = ['Тип оборудования', 'Общая мощность (МВт)']

fig = px.bar(
    capacity_by_type,
    x='Тип оборудования',
    y='Общая мощность (МВт)',
    title='Общая мощность по типам оборудования',
    color='Общая мощность (МВт)',
    color_continuous_scale='Blues'
)
st.plotly_chart(fig, use_container_width=True)

# Age analysis
st.markdown("---")
st.subheader("Анализ возраста оборудования")

current_year = 2025
filtered_df['age'] = current_year - filtered_df['installation_year']

fig = px.scatter(
    filtered_df,
    x='age',
    y='failure_probability',
    size='capacity_mw',
    color='equipment_type',
    hover_data=['equipment_id'],
    title='Возраст оборудования в сравнении с оценкой риска',
    labels={'age': 'Возраст оборудования (лет)', 'failure_probability': 'Оценка риска', 'equipment_type': 'Тип оборудования'},
    trendline='lowess'
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.info("""
💡 **Совет**: Нажмите на маркеры карты для просмотра подробной информации об оборудовании.
Используйте фильтры в боковой панели для фокусировки на конкретных типах оборудования или уровнях риска.
""")
