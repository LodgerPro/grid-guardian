"""
Financial Impact Analysis and ROI Calculations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Финансовый анализ", page_icon="💰", layout="wide")

st.title("💰 Анализ финансового эффекта")
st.markdown("Анализ экономии затрат и ROI от предиктивного обслуживания")
st.markdown("---")


@st.cache_data
def calculate_financial_metrics():
    """Calculate financial impact metrics"""
    # Cost parameters
    unplanned_outage_cost = 500000  # per incident
    planned_maintenance_cost = 50000  # per maintenance
    equipment_replacement_cost = 2000000  # per unit

    # Baseline (reactive maintenance)
    baseline_failures = 12  # per year
    baseline_maintenance = 24  # per year

    # With predictive maintenance
    predicted_failures = 2  # per year
    predicted_maintenance = 30  # per year (more frequent but planned)

    return {
        'unplanned_outage_cost': unplanned_outage_cost,
        'planned_maintenance_cost': planned_maintenance_cost,
        'equipment_replacement_cost': equipment_replacement_cost,
        'baseline_failures': baseline_failures,
        'baseline_maintenance': baseline_maintenance,
        'predicted_failures': predicted_failures,
        'predicted_maintenance': predicted_maintenance
    }


# Sidebar
with st.sidebar:
    st.header("Параметры затрат")

    unplanned_cost = st.number_input(
        "Стоимость внеплановой аварии (₽)",
        value=500000,
        step=10000,
        help="Средняя стоимость внепланового отказа"
    )

    planned_cost = st.number_input(
        "Стоимость планового ТО (₽)",
        value=50000,
        step=5000,
        help="Средняя стоимость планового обслуживания"
    )

    replacement_cost = st.number_input(
        "Замена оборудования (₽)",
        value=2000000,
        step=50000,
        help="Стоимость замены основного оборудования"
    )

    st.markdown("---")

    implementation_cost = st.number_input(
        "Стоимость внедрения системы (₽)",
        value=500000,
        step=50000,
        help="Единовременные затраты на внедрение предиктивного обслуживания"
    )

    annual_operating_cost = st.number_input(
        "Годовые эксплуатационные расходы (₽)",
        value=100000,
        step=10000,
        help="Ежегодные затраты на эксплуатацию предиктивной системы"
    )


# Calculate savings
metrics = calculate_financial_metrics()

# Baseline costs
baseline_annual_cost = (
    metrics['baseline_failures'] * unplanned_cost +
    metrics['baseline_maintenance'] * planned_cost
)

# Predictive maintenance costs
predictive_annual_cost = (
    metrics['predicted_failures'] * unplanned_cost +
    metrics['predicted_maintenance'] * planned_cost +
    annual_operating_cost
)

annual_savings = baseline_annual_cost - predictive_annual_cost
roi_years = implementation_cost / annual_savings if annual_savings > 0 else float('inf')

# Key metrics
st.subheader("Ключевые финансовые показатели")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Годовая экономия",
        f"{annual_savings:,.0f} ₽",
        delta=f"{annual_savings/baseline_annual_cost*100:.1f}% снижение"
    )

with col2:
    st.metric(
        "Срок окупаемости",
        f"{roi_years:.1f} лет",
        delta="Срок достижения безубыточности"
    )

with col3:
    st.metric(
        "Выгода за 5 лет",
        f"{annual_savings * 5 - implementation_cost:,.0f} ₽",
        delta="Чистая экономия"
    )

with col4:
    failure_reduction = (1 - metrics['predicted_failures'] / metrics['baseline_failures']) * 100
    st.metric(
        "Сокращение отказов",
        f"{failure_reduction:.0f}%",
        delta=f"{metrics['baseline_failures'] - metrics['predicted_failures']} меньше в год"
    )

st.markdown("---")

# Cost comparison
st.subheader("Сравнение годовых затрат")

col1, col2 = st.columns(2)

with col1:
    cost_comparison = pd.DataFrame({
        'Scenario': ['Реактивное обслуживание', 'Предиктивное обслуживание'],
        'Внеплановые аварии': [
            metrics['baseline_failures'] * unplanned_cost,
            metrics['predicted_failures'] * unplanned_cost
        ],
        'Плановое ТО': [
            metrics['baseline_maintenance'] * planned_cost,
            metrics['predicted_maintenance'] * planned_cost
        ],
        'Эксплуатация системы': [0, annual_operating_cost]
    })

    fig = px.bar(
        cost_comparison,
        x='Scenario',
        y=['Внеплановые аварии', 'Плановое ТО', 'Эксплуатация системы'],
        title='Структура годовых затрат',
        labels={'value': 'Затраты (₽)', 'variable': 'Тип затрат', 'Scenario': 'Сценарий'},
        barmode='stack',
        color_discrete_sequence=['#f44336', '#ff9800', '#2196f3']
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    total_comparison = pd.DataFrame({
        'Scenario': ['Реактивное', 'Предиктивное'],
        'Общие затраты': [baseline_annual_cost, predictive_annual_cost]
    })

    fig = px.bar(
        total_comparison,
        x='Scenario',
        y='Общие затраты',
        title='Сравнение общих годовых затрат',
        labels={'Scenario': 'Сценарий'},
        color='Общие затраты',
        color_continuous_scale='RdYlGn_r',
        text='Общие затраты'
    )
    fig.update_traces(texttemplate='%{text:,.0f} ₽', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ROI projection
st.subheader("Прогноз ROI на 5 лет")

years = list(range(6))
cumulative_costs_reactive = [baseline_annual_cost * year for year in years]
cumulative_costs_predictive = [
    implementation_cost + (predictive_annual_cost * year) for year in years
]
cumulative_savings = [
    cumulative_costs_reactive[i] - cumulative_costs_predictive[i]
    for i in range(len(years))
]

roi_df = pd.DataFrame({
    'Year': years,
    'Реактивное обслуживание': cumulative_costs_reactive,
    'Предиктивное обслуживание': cumulative_costs_predictive,
    'Накопленная экономия': cumulative_savings
})

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=roi_df['Year'],
    y=roi_df['Реактивное обслуживание'],
    mode='lines+markers',
    name='Реактивное (базовое)',
    line=dict(color='#f44336', width=3)
))

fig.add_trace(go.Scatter(
    x=roi_df['Year'],
    y=roi_df['Предиктивное обслуживание'],
    mode='lines+markers',
    name='Предиктивное',
    line=dict(color='#4caf50', width=3)
))

fig.update_layout(
    title='Сравнение накопленных затрат',
    xaxis_title='Год',
    yaxis_title='Накопленные затраты (₽)',
    hovermode='x unified',
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Savings table
st.markdown("### Погодовая разбивка")

savings_table = pd.DataFrame({
    'Год': years[1:],
    'Реактивные затраты': [baseline_annual_cost] * 5,
    'Предиктивные затраты': [predictive_annual_cost] * 5,
    'Годовая экономия': [annual_savings] * 5,
    'Накопленная экономия': cumulative_savings[1:]
})

st.dataframe(
    savings_table.style.format({
        'Реактивные затраты': '{:,.0f} ₽',
        'Предиктивные затраты': '{:,.0f} ₽',
        'Годовая экономия': '{:,.0f} ₽',
        'Накопленная экономия': '{:,.0f} ₽'
    }).background_gradient(subset=['Годовая экономия', 'Накопленная экономия'], cmap='Greens'),
    use_container_width=True
)

st.markdown("---")

# Failure cost breakdown
st.subheader("Структура затрат по типам отказов")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### До внедрения предиктивного обслуживания")

    before_costs = pd.DataFrame({
        'Type': ['Повреждение оборудования', 'Потери производства', 'Аварийные работы', 'Простои'],
        'Cost': [unplanned_cost * 0.3, unplanned_cost * 0.4,
                unplanned_cost * 0.2, unplanned_cost * 0.1]
    })

    fig = px.pie(before_costs, values='Cost', names='Type',
                title=f'Стоимость аварии: {unplanned_cost:,.0f} ₽',
                color_discrete_sequence=px.colors.sequential.Reds)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### После внедрения предиктивного обслуживания")

    after_costs = pd.DataFrame({
        'Type': ['Плановые запчасти', 'Штатные работы', 'Инспекция', 'Документация'],
        'Cost': [planned_cost * 0.5, planned_cost * 0.3,
                planned_cost * 0.15, planned_cost * 0.05]
    })

    fig = px.pie(after_costs, values='Cost', names='Type',
                title=f'Стоимость ТО: {planned_cost:,.0f} ₽',
                color_discrete_sequence=px.colors.sequential.Greens)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Additional benefits
st.subheader("Дополнительные преимущества")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 🎯 Улучшение надёжности
    - **99.5%** доступность сети
    - **83%** сокращение внеплановых аварий
    - **50%** ускорение реагирования
    - Увеличенный срок службы оборудования
    """)

with col2:
    st.markdown("""
    ### 📊 Операционная эффективность
    - Лучшее распределение ресурсов
    - Оптимизация графика ТО
    - Снижение аварийных переработок
    - Улучшенное управление складом
    """)

with col3:
    st.markdown("""
    ### 🌍 Экологический эффект
    - Сокращение потерь энергии
    - Снижение углеродного следа
    - Меньше отказов оборудования
    - Устойчивые операции
    """)

st.markdown("---")

# Risk mitigation value
st.subheader("Ценность снижения рисков")

st.info("""
**Помимо прямой экономии затрат:**

Система предиктивного обслуживания обеспечивает дополнительную ценность:

- **Соблюдение нормативов**: Избежание штрафов и санкций (50-500 тыс. ₽ за инцидент)
- **Защита репутации**: Поддержание удовлетворённости клиентов и избежание негативной огласки
- **Повышение безопасности**: Сокращение несчастных случаев и затрат на ответственность
- **Преимущества в страховании**: Потенциальное снижение страховых премий благодаря улучшению управления рисками
- **Стратегическое планирование**: Более точное прогнозирование капитальных затрат и бюджетирование
""")

# Export functionality
st.markdown("---")

if st.button("📊 Сгенерировать финансовый отчёт", use_container_width=True):
    report_data = {
        'Показатель': [
            'Годовая экономия',
            'Срок окупаемости (лет)',
            'Чистая выгода за 5 лет',
            'Сокращение отказов (%)',
            'Базовые годовые затраты',
            'Предиктивные годовые затраты'
        ],
        'Значение': [
            f"{annual_savings:,.0f} ₽",
            f"{roi_years:.1f}",
            f"{annual_savings * 5 - implementation_cost:,.0f} ₽",
            f"{failure_reduction:.0f}%",
            f"{baseline_annual_cost:,.0f} ₽",
            f"{predictive_annual_cost:,.0f} ₽"
        ]
    }

    report_df = pd.DataFrame(report_data)
    st.success("✅ Отчёт успешно сгенерирован!")
    st.dataframe(report_df, use_container_width=True)
