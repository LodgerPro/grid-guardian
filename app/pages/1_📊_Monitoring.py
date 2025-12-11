"""
Real-time Equipment Monitoring Dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Мониторинг оборудования", page_icon="📊", layout="wide")

st.title("📊 Мониторинг оборудования в реальном времени")
st.markdown("Отслеживание показаний датчиков и состояния оборудования")
st.markdown("---")


@st.cache_data(ttl=60)
def load_monitoring_data():
    """Load real-time monitoring data"""
    try:
        # Try to load from processed features
        df = pd.read_csv('data/processed/features.csv')
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Rename columns to standard names if needed
        column_mapping = {
            'temperature_top': 'temperature',
            'vibration_x': 'vibration',
            'current_phase_a': 'current',
            'voltage_phase_a': 'voltage',
        }

        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        # Add missing columns with synthetic data if needed
        if 'power_factor' not in df.columns:
            df['power_factor'] = np.random.normal(0.95, 0.03, len(df))
        if 'oil_level' not in df.columns:
            df['oil_level'] = np.random.normal(85, 10, len(df))

        # Take only recent data for performance
        df = df.tail(10000)

        return df
    except:
        # Generate sample real-time data
        np.random.seed(int(datetime.now().timestamp()))
        n_samples = 500
        equipment_list = ['SUB001_EQ01', 'SUB001_EQ02', 'SUB002_EQ01', 'SUB002_EQ02', 'SUB003_EQ01']

        df = pd.DataFrame({
            'timestamp': pd.date_range(end=datetime.now(), periods=n_samples, freq='5min'),
            'equipment_id': np.random.choice(equipment_list, n_samples),
            'temperature': np.random.normal(70, 15, n_samples),
            'vibration': np.random.normal(3, 1, n_samples),
            'current': np.random.normal(100, 20, n_samples),
            'voltage': np.random.normal(230, 5, n_samples),
            'power_factor': np.random.normal(0.95, 0.03, n_samples),
            'oil_level': np.random.normal(85, 10, n_samples),
            'humidity': np.random.normal(45, 15, n_samples),
        })

    return df


# Sidebar filters
with st.sidebar:
    st.header("Фильтры")

    df = load_monitoring_data()

    equipment_list = df['equipment_id'].unique().tolist() if 'equipment_id' in df.columns else []
    selected_equipment = st.multiselect(
        "Выберите оборудование",
        options=equipment_list,
        default=equipment_list[:3] if len(equipment_list) >= 3 else equipment_list
    )

    time_range = st.select_slider(
        "Временной диапазон",
        options=['1 час', '6 часов', '12 часов', '24 часа', '7 дней'],
        value='12 часов'
    )

    st.markdown("---")
    auto_refresh = st.checkbox("Автообновление (60с)", value=False)

    if auto_refresh:
        st.rerun()


# Filter data
if selected_equipment:
    df = df[df['equipment_id'].isin(selected_equipment)]

# Time range filter
time_mapping = {
    '1 час': 1,
    '6 часов': 6,
    '12 часов': 12,
    '24 часа': 24,
    '7 дней': 168
}
hours = time_mapping.get(time_range, 12)
cutoff_time = datetime.now() - timedelta(hours=hours)
df = df[df['timestamp'] >= cutoff_time]

# Current status metrics
st.subheader("Текущее состояние")
col1, col2, col3, col4 = st.columns(4)

with col1:
    current_temp = df['temperature'].iloc[-1] if len(df) > 0 else 0
    st.metric(
        "Температура",
        f"{current_temp:.1f}°C",
        delta=f"{current_temp - 65:.1f}°C",
        delta_color="inverse"
    )

with col2:
    current_vibration = df['vibration'].iloc[-1] if len(df) > 0 else 0
    st.metric(
        "Вибрация",
        f"{current_vibration:.2f} мм/с",
        delta=f"{current_vibration - 2.5:.2f}",
        delta_color="inverse"
    )

with col3:
    current_voltage = df['voltage'].iloc[-1] if len(df) > 0 else 0
    st.metric(
        "Напряжение",
        f"{current_voltage:.1f} кВ",
        delta=f"{current_voltage - 230:.1f}"
    )

with col4:
    current_pf = df['power_factor'].iloc[-1] if len(df) > 0 else 0
    st.metric(
        "Коэф. мощности",
        f"{current_pf:.3f}",
        delta=f"{current_pf - 0.95:.3f}"
    )

st.markdown("---")

# Multi-sensor time series
st.subheader("Тренды датчиков")

tab1, tab2, tab3 = st.tabs(["Температура и вибрация", "Электрические параметры", "Прочие датчики"])

with tab1:
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Динамика температуры", "Динамика вибрации"),
        vertical_spacing=0.12
    )

    for equipment in selected_equipment:
        eq_data = df[df['equipment_id'] == equipment]
        fig.add_trace(
            go.Scatter(x=eq_data['timestamp'], y=eq_data['temperature'],
                      mode='lines', name=f'{equipment} Темп'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=eq_data['timestamp'], y=eq_data['vibration'],
                      mode='lines', name=f'{equipment} Вибр'),
            row=2, col=1
        )

    fig.update_xaxes(title_text="Время", row=2, col=1)
    fig.update_yaxes(title_text="Температура (°C)", row=1, col=1)
    fig.update_yaxes(title_text="Вибрация (мм/с)", row=2, col=1)
    fig.update_layout(height=600, showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Напряжение", "Ток"),
        vertical_spacing=0.12
    )

    for equipment in selected_equipment:
        eq_data = df[df['equipment_id'] == equipment]
        fig.add_trace(
            go.Scatter(x=eq_data['timestamp'], y=eq_data['voltage'],
                      mode='lines', name=f'{equipment} Напр'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=eq_data['timestamp'], y=eq_data['current'],
                      mode='lines', name=f'{equipment} Ток'),
            row=2, col=1
        )

    fig.update_xaxes(title_text="Время", row=2, col=1)
    fig.update_yaxes(title_text="Напряжение (кВ)", row=1, col=1)
    fig.update_yaxes(title_text="Ток (А)", row=2, col=1)
    fig.update_layout(height=600, showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Уровень масла", "Влажность"),
        vertical_spacing=0.12
    )

    for equipment in selected_equipment:
        eq_data = df[df['equipment_id'] == equipment]
        fig.add_trace(
            go.Scatter(x=eq_data['timestamp'], y=eq_data['oil_level'],
                      mode='lines', name=f'{equipment} Масло'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=eq_data['timestamp'], y=eq_data['humidity'],
                      mode='lines', name=f'{equipment} Влажн'),
            row=2, col=1
        )

    fig.update_xaxes(title_text="Время", row=2, col=1)
    fig.update_yaxes(title_text="Уровень масла (%)", row=1, col=1)
    fig.update_yaxes(title_text="Влажность (%)", row=2, col=1)
    fig.update_layout(height=600, showlegend=True)

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Sensor distribution
st.subheader("Распределение показателей датчиков")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df, x='temperature', nbins=30,
                      title='Распределение температуры',
                      labels={'temperature': 'Температура (°C)'})
    fig.add_vline(x=85, line_dash="dash", line_color="red",
                 annotation_text="Порог")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df, x='vibration', nbins=30,
                      title='Распределение вибрации',
                      labels={'vibration': 'Вибрация (мм/с)'})
    fig.add_vline(x=5, line_dash="dash", line_color="red",
                 annotation_text="Порог")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Equipment comparison
st.subheader("Сравнение оборудования")

comparison_metric = st.selectbox(
    "Выберите параметр для сравнения",
    ['temperature', 'vibration', 'current', 'voltage', 'power_factor', 'oil_level']
)

equipment_avg = df.groupby('equipment_id')[comparison_metric].mean().reset_index()
equipment_avg.columns = ['Оборудование', 'Среднее значение']

metric_names = {
    'temperature': 'температура',
    'vibration': 'вибрация',
    'current': 'ток',
    'voltage': 'напряжение',
    'power_factor': 'коэффициент мощности',
    'oil_level': 'уровень масла'
}

fig = px.bar(equipment_avg, x='Оборудование', y='Среднее значение',
            title=f'Средн. {metric_names.get(comparison_metric, comparison_metric)} по оборудованию',
            color='Среднее значение', color_continuous_scale='RdYlGn_r')
st.plotly_chart(fig, use_container_width=True)

# Raw data table
with st.expander("📋 Просмотр исходных данных"):
    st.dataframe(df.sort_values('timestamp', ascending=False).head(100),
                use_container_width=True)
