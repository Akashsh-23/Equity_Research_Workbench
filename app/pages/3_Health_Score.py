import streamlit as st
import sys
sys.path.append(".")
import plotly.graph_objects as go

from core.fetcher      import get_financials
from core.ratios       import calculate_all_ratios
from core.health_score import calculate_health_score

st.set_page_config(page_title="Health Score", page_icon="🏥", layout="wide")
st.title("🏥 Financial Health Score")

if "ticker" not in st.session_state:
    st.warning("Please search for a company on the Search page first.")
    st.stop()

ticker = st.session_state["ticker"]
st.subheader(st.session_state["info"]["name"])

with st.spinner("Calculating health score..."):
    try:
        # Use cached ratios if available, else recalculate
        if "ratios" in st.session_state:
            ratios = st.session_state["ratios"]
        else:
            financials = get_financials(ticker)
            ratios = calculate_all_ratios(
                financials["income_statement"],
                financials["balance_sheet"],
                financials["cash_flow"]
            )

        score = calculate_health_score(ratios)
        overall = score["overall_score"]
        grade   = score["grade"]
        cats    = score["category_scores"]

        # Color based on score
        if   overall >= 80: color = "#16a34a"
        elif overall >= 65: color = "#2563eb"
        elif overall >= 50: color = "#d97706"
        elif overall >= 35: color = "#ea580c"
        else:               color = "#dc2626"

        # Big score display
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div style='text-align:center; padding:2rem; border-radius:16px;
                        border: 2px solid {color}'>
                <div style='font-size:4rem; font-weight:700;
                            color:{color}'>{overall}</div>
                <div style='font-size:1rem; color:gray'>out of 100</div>
                <div style='font-size:1.2rem; font-weight:600;
                            margin-top:0.5rem'>{grade}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            # Radar / bar chart of categories
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(cats.keys()),
                y=list(cats.values()),
                marker_color=[
                    "#16a34a" if v >= 70
                    else "#d97706" if v >= 40
                    else "#dc2626"
                    for v in cats.values()
                ],
                text=[f"{v}/100" for v in cats.values()],
                textposition="outside"
            ))
            fig.update_layout(
                yaxis=dict(range=[0, 110]),
                yaxis_title="Score",
                height=320,
                margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

        st.divider()

        # Methodology — this is what impresses interviewers
        st.subheader("How the score is calculated")
        st.markdown("""
        | Category | Weight | What it measures |
        |---|---|---|
        | Profitability | 30% | ROE, ROCE, Net Margin |
        | Liquidity | 20% | Current Ratio, Quick Ratio |
        | Leverage | 20% | Debt/Equity, Interest Coverage |
        | Growth | 15% | Revenue growth YoY |
        | Cash Flow | 15% | Free Cash Flow |

        Thresholds are based on general Indian market benchmarks.
        **Limitation:** scores are sector-agnostic — capital-heavy industries
        like Oil & Gas will naturally score lower on profitability.
        """)

    except Exception as e:
        st.error("Could not calculate health score.")
        st.caption(f"Error: {e}")