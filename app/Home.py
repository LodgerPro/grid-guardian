"""
Grid Guardian - Main Dashboard
Streamlit application for power grid predictive maintenance
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Page configuration
st.set_page_config(
    page_title="Grid Guardian - Предиктивное обслуживание",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .alert-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .alert-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_sample_data():
    """Load real data from features.csv with caching"""
    try:
        # Load real data
        df = pd.read_csv('data/processed/features.csv')

        # Parse timestamp
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Rename columns if needed for backward compatibility
        column_mapping = {
            'temperature_top': 'temperature',
            'vibration_x': 'vibration',
        }
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        # Ensure required columns exist
        if 'failure_probability' not in df.columns:
            if 'failure' in df.columns:
                df['failure_probability'] = df['failure'].astype(float)
            else:
                df['failure_probability'] = np.random.beta(2, 20, len(df))

        if 'risk_level' not in df.columns:
            # Create risk_level from failure_probability
            df['risk_level'] = pd.cut(df['failure_probability'],
                                      bins=[0, 0.3, 0.7, 1.0],
                                      labels=[0, 1, 2])
            df['risk_level'] = df['risk_level'].astype(int)

        # Take stratified sample for performance (keep risk level proportions)
        if len(df) > 50000:
            # Calculate proportional sample sizes for each risk level
            total_sample = 50000
            risk_counts = df['risk_level'].value_counts()
            sample_sizes = {}
            for level in [0, 1, 2]:
                if level in risk_counts.index:
                    proportion = risk_counts[level] / len(df)
                    sample_sizes[level] = int(total_sample * proportion)
                else:
                    sample_sizes[level] = 0

            # Sample from each risk level proportionally
            sampled_dfs = []
            for level, size in sample_sizes.items():
                if size > 0:
                    level_df = df[df['risk_level'] == level]
                    n = min(len(level_df), size)
                    sampled_dfs.append(level_df.sample(n=n, random_state=42))

            df = pd.concat(sampled_dfs, ignore_index=True).sample(frac=1, random_state=42)

        print(f"[Dashboard] Loaded {len(df):,} records from features.csv")
        return df

    except Exception as e:
        print(f"[Dashboard] Error loading data: {e}")
        # Generate minimal sample data
        np.random.seed(42)
        n_samples = 100
        df = pd.DataFrame({
            'equipment_id': np.random.choice(['SUB001_EQ01', 'SUB001_EQ02', 'SUB002_EQ01'], n_samples),
            'temperature': np.random.normal(70, 15, n_samples),
            'vibration': np.random.normal(3, 1, n_samples),
            'failure_probability': np.random.beta(2, 20, n_samples),
            'risk_level': np.random.choice([0, 1, 2], n_samples, p=[0.75, 0.20, 0.05]),
            'timestamp': pd.date_range(end=datetime.now(), periods=n_samples, freq='H')
        })
        return df


def display_header():
    """Display application header"""
    st.markdown('<h1 class="main-header">⚡ Grid Guardian</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 1.2rem; color: #666;">'
        'Система предиктивного обслуживания электросетевого оборудования на основе ИИ'
        '</p>',
        unsafe_allow_html=True
    )
    st.markdown("---")


def display_key_metrics(df):
    """Display key performance metrics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Всего оборудования",
            value=df['equipment_id'].nunique() if 'equipment_id' in df.columns else "N/A",
            delta=None
        )

    with col2:
        # Count high risk equipment using risk_level if available
        if 'risk_level' in df.columns:
            high_risk = (df['risk_level'] == 2).sum()
        elif 'failure_probability' in df.columns:
            high_risk = (df['failure_probability'] > 0.7).sum()
        else:
            high_risk = 0
        st.metric(
            label="Высокий риск",
            value=high_risk,
            delta=f"{high_risk} критичных",
            delta_color="inverse"
        )

    with col3:
        avg_temp = df['temperature'].mean() if 'temperature' in df.columns else 0
        st.metric(
            label="Средняя температура (°C)",
            value=f"{avg_temp:.1f}",
            delta=f"{avg_temp - 65:.1f}°C от нормы"
        )

    with col4:
        uptime = 98.5  # Sample uptime
        st.metric(
            label="Доступность сети",
            value=f"{uptime}%",
            delta="0.5%"
        )


def display_risk_overview(df):
    """Display risk overview"""
    st.subheader("📊 Обзор рисков")

    if 'risk_level' in df.columns:
        # Map risk levels to labels
        risk_mapping = {0: 'Низкий', 1: 'Средний', 2: 'Высокий'}
        df_risk = df.copy()
        df_risk['risk_label'] = df_risk['risk_level'].map(risk_mapping)
        risk_counts = df_risk['risk_label'].value_counts()

        # Ensure all categories are present
        for label in ['Низкий', 'Средний', 'Высокий']:
            if label not in risk_counts.index:
                risk_counts[label] = 0

        # Sort by risk level
        risk_order = ['Низкий', 'Средний', 'Высокий']
        risk_counts = risk_counts.reindex(risk_order, fill_value=0)

        col1, col2 = st.columns([2, 1])

        with col1:
            # Risk distribution chart
            fig = go.Figure(data=[
                go.Bar(
                    x=risk_counts.index,
                    y=risk_counts.values,
                    marker_color=['#4caf50', '#ff9800', '#f44336']
                )
            ])
            fig.update_layout(
                title="Распределение рисков",
                xaxis_title="Уровень риска",
                yaxis_title="Количество записей",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Сводка по рискам")
            total = len(df_risk)
            high_pct = (risk_counts.get('Высокий', 0) / total * 100) if total > 0 else 0
            medium_pct = (risk_counts.get('Средний', 0) / total * 100) if total > 0 else 0
            low_pct = (risk_counts.get('Низкий', 0) / total * 100) if total > 0 else 0

            st.markdown(f"""
            <div class="metric-card alert-high">
                <strong>Высокий риск:</strong> {risk_counts.get('Высокий', 0):,} ({high_pct:.1f}%)
            </div>
            <div class="metric-card alert-medium">
                <strong>Средний риск:</strong> {risk_counts.get('Средний', 0):,} ({medium_pct:.1f}%)
            </div>
            <div class="metric-card alert-low">
                <strong>Низкий риск:</strong> {risk_counts.get('Низкий', 0):,} ({low_pct:.1f}%)
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Данные о рисках отсутствуют. Запустите прогнозирование.")


def display_equipment_status(df):
    """Display equipment status table"""
    st.subheader("🔧 Состояние оборудования")

    if 'equipment_id' in df.columns:
        # Aggregate by equipment
        agg_dict = {
            'temperature': 'mean',
            'vibration': 'mean',
            'failure_probability': 'max'
        }

        # Add risk_level if available
        if 'risk_level' in df.columns:
            agg_dict['risk_level'] = 'max'

        equipment_summary = df.groupby('equipment_id').agg(agg_dict).reset_index()

        equipment_summary.columns = ['ID оборудования', 'Ср. температура (°C)', 'Ср. вибрация (мм/с)', 'Оценка риска'] + \
                                   (['Уровень риска'] if 'risk_level' in df.columns else [])

        # Determine status from risk_level if available, otherwise from failure_probability
        if 'Уровень риска' in equipment_summary.columns:
            # Convert to int to ensure proper mapping
            equipment_summary['Уровень риска'] = equipment_summary['Уровень риска'].fillna(0).astype(int)
            equipment_summary['Статус'] = equipment_summary['Уровень риска'].map({
                0: '🟢 Норма',
                1: '🟡 Внимание',
                2: '🔴 Критично'
            }).fillna('🟢 Норма')
            # Drop the numeric risk_level column after mapping
            equipment_summary = equipment_summary.drop(columns=['Уровень риска'])
        else:
            equipment_summary['Статус'] = equipment_summary['Оценка риска'].apply(
                lambda x: '🔴 Критично' if x > 0.7 else '🟡 Внимание' if x > 0.3 else '🟢 Норма'
            )

        st.dataframe(
            equipment_summary.style.background_gradient(subset=['Оценка риска'], cmap='RdYlGn_r'),
            use_container_width=True
        )
    else:
        st.info("Данные об оборудовании отсутствуют.")


def display_recent_alerts():
    """Display recent alerts"""
    st.subheader("🚨 Последние оповещения")

    alerts = [
        {
            'time': '2 часа назад',
            'equipment': 'TRANS_001',
            'severity': 'High',
            'message': 'Превышена температура (95°C)'
        },
        {
            'time': '5 часов назад',
            'equipment': 'GEN_001',
            'severity': 'Medium',
            'message': 'Повышенный уровень вибрации'
        },
        {
            'time': '8 часов назад',
            'equipment': 'LINE_001',
            'severity': 'Low',
            'message': 'Плановое обслуживание'
        }
    ]

    for alert in alerts:
        severity_class = f"alert-{alert['severity'].lower()}"
        st.markdown(f"""
        <div class="metric-card {severity_class}">
            <strong>{alert['time']}</strong> - {alert['equipment']}<br>
            {alert['message']}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)


def display_time_series(df):
    """Display time series chart"""
    st.subheader("📈 Тренды датчиков")

    if 'timestamp' in df.columns and 'temperature' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Temperature trend
        fig = px.line(
            df.sort_values('timestamp'),
            x='timestamp',
            y='temperature',
            color='equipment_id' if 'equipment_id' in df.columns else None,
            title='Динамика температуры'
        )
        fig.update_layout(
            height=300,
            xaxis_title="Время",
            yaxis_title="Температура (°C)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Данные временных рядов отсутствуют.")


def main():
    """Main application"""
    # Display header
    display_header()

    # Sidebar
    with st.sidebar:
        st.title("Навигация")
        st.markdown("---")
        st.markdown("""
        ### Страницы
        - 🏠 **Главная** (Текущая)
        - 📊 Мониторинг
        - 🔮 Прогнозы
        - 💰 Финансовый анализ
        - 🗺️ Карта оборудования

        ### Быстрые действия
        """)

        if st.button("🔄 Обновить данные", use_container_width=True):
            st.rerun()

        if st.button("⚙️ Запустить прогноз", use_container_width=True):
            st.info("Перейдите на страницу Прогнозы для анализа")

        st.markdown("---")
        st.markdown("""
        ### Информация о системе
        - **Статус**: В сети
        - **Обновлено**: Только что
        - **Модель**: XGBoost v1.0
        """)

    # Load data
    df = load_sample_data()

    # Display key metrics
    display_key_metrics(df)

    st.markdown("---")

    # Main content
    col1, col2 = st.columns([2, 1])

    with col1:
        display_risk_overview(df)
        st.markdown("---")
        display_time_series(df)

    with col2:
        display_recent_alerts()

    st.markdown("---")

    # Equipment status
    display_equipment_status(df)

    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">'
        'Grid Guardian © 2025 | На основе ИИ и машинного обучения'
        '</p>',
        unsafe_allow_html=True
    )


if __name__ == '__main__':
    import numpy as np
    main()
