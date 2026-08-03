import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from scipy.stats import norm


st.set_page_config(
    page_title="SARB Macro Stress Tester",
    page_icon="🇿🇦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🇿🇦 SARB Prime Rate & Macro-Sensitive Portfolio Stress Tester")
st.markdown(
    "Quantifying multi-asset portfolio P&L impacts across **SARB Repo/Prime rate shifts**, "
    "**USD/ZAR exchange rate shocks**, and **sovereign yield movements**."
)


@st.cache_data(ttl=300)
def fetch_live_market_data():
    tickers = {
        'FSR.JO': 'FirstRand Ltd',
        'SHP.JO': 'Shoprite Holdings',
        'AGL.JO': 'Anglo American plc',
        'GRT.JO': 'Growthpoint Properties',
        'ZAR=X':  'USD/ZAR FX Rate'
    }
    try:
        data = yf.download(list(tickers.keys()), period='5d')['Close']
        latest = data.iloc[-1]
        prices = {
            'FSR.JO': float(latest['FSR.JO']) / 100.0,
            'SHP.JO': float(latest['SHP.JO']) / 100.0,
            'AGL.JO': float(latest['AGL.JO']) / 100.0,
            'GRT.JO': float(latest['GRT.JO']) / 100.0,
            'USDZAR': float(latest['ZAR=X'])
        }
        return prices, True
    except Exception:
        return {'FSR.JO': 65.0, 'SHP.JO': 270.0, 'AGL.JO': 480.0, 'GRT.JO': 12.5, 'USDZAR': 18.50}, False

live_prices, is_live = fetch_live_market_data()

if is_live:
    st.success(f"🟢 **Live Market Data Connected** | USD/ZAR: R {live_prices['USDZAR']:.2f}", icon="✅")
else:
    st.warning("⚠️ Market data offline. Using cached baseline prices.", icon="⚠️")

st.markdown("---")


st.sidebar.header("🕹️ Macro Scenario Controls")

repo_bps = st.sidebar.slider(
    "SARB Repo Rate Shift (Basis Points)",
    min_value=-300, max_value=400, value=100, step=25,
    help="+100 bps = +1.00% Interest Rate Hike"
)

fx_pct_shift = st.sidebar.slider(
    "USD/ZAR Exchange Rate Move (%)",
    min_value=-20.0, max_value=20.0, value=5.0, step=1.0,
    help="+10% = Rand Depreciation (USD/ZAR increases)"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Baseline Reference Rates")
st.sidebar.text("Current Repo Rate: 7.00%")
st.sidebar.text(f"Stressed Repo Rate: {7.00 + (repo_bps/100.0):.2f}%")
st.sidebar.text(f"Stressed Prime Rate: {10.50 + (repo_bps/100.0):.2f}%")
st.sidebar.text(f"Stressed USD/ZAR: R {live_prices['USDZAR'] * (1 + fx_pct_shift/100.0):.2f}")


def build_portfolio():
    portfolio = [
        {'Asset_ID': 'R2030 Bond', 'Asset_Class': 'Fixed Income', 'Sector': 'Sovereign Debt', 'Market_Value_ZAR': 2_500_000, 'Coupon_Rate': 0.0800, 'Maturity_Years': 3.75, 'Yield_To_Maturity': 0.1020, 'Rate_Beta': None, 'FX_Beta': None, 'Ann_Vol': 0.065},
        {'Asset_ID': 'R2035 Bond', 'Asset_Class': 'Fixed Income', 'Sector': 'Sovereign Debt', 'Market_Value_ZAR': 1_500_000, 'Coupon_Rate': 0.0885, 'Maturity_Years': 8.75, 'Yield_To_Maturity': 0.1150, 'Rate_Beta': None, 'FX_Beta': None, 'Ann_Vol': 0.095},
        {'Asset_ID': 'FirstRand (FSR)', 'Asset_Class': 'Equity', 'Sector': 'Financials', 'Market_Value_ZAR': 1_200_000, 'Coupon_Rate': None, 'Maturity_Years': None, 'Yield_To_Maturity': None, 'Rate_Beta': -2.5, 'FX_Beta': 0.20, 'Ann_Vol': 0.220},
        {'Asset_ID': 'Growthpoint (GRT)', 'Asset_Class': 'Equity', 'Sector': 'Property/REIT', 'Market_Value_ZAR': 800_000, 'Coupon_Rate': None, 'Maturity_Years': None, 'Yield_To_Maturity': None, 'Rate_Beta': -4.0, 'FX_Beta': -0.10, 'Ann_Vol': 0.250},
        {'Asset_ID': 'Anglo American (AGL)', 'Asset_Class': 'Equity', 'Sector': 'Resources', 'Market_Value_ZAR': 1_500_000, 'Coupon_Rate': None, 'Maturity_Years': None, 'Yield_To_Maturity': None, 'Rate_Beta': -0.8, 'FX_Beta': 0.85, 'Ann_Vol': 0.280},
        {'Asset_ID': 'Shoprite (SHP)', 'Asset_Class': 'Equity', 'Sector': 'Consumer Retail', 'Market_Value_ZAR': 1_000_000, 'Coupon_Rate': None, 'Maturity_Years': None, 'Yield_To_Maturity': None, 'Rate_Beta': -1.2, 'FX_Beta': 0.10, 'Ann_Vol': 0.180},
        {'Asset_ID': 'Prime Floating Debt', 'Asset_Class': 'Credit', 'Sector': 'Corporate Credit', 'Market_Value_ZAR': 1_000_000, 'Coupon_Rate': None, 'Maturity_Years': None, 'Yield_To_Maturity': None, 'Rate_Beta': None, 'FX_Beta': None, 'Ann_Vol': 0.030},
        {'Asset_ID': 'Call Cash Account', 'Asset_Class': 'Cash', 'Sector': 'Money Market', 'Market_Value_ZAR': 500_000, 'Coupon_Rate': None, 'Maturity_Years': None, 'Yield_To_Maturity': None, 'Rate_Beta': None, 'FX_Beta': None, 'Ann_Vol': 0.010}
    ]
    
    df = pd.DataFrame(portfolio)
    mod_durs, convexities = [], []
    for _, row in df.iterrows():
        if row['Asset_Class'] == 'Fixed Income':
            freq = 2
            periods = int(row['Maturity_Years'] * freq)
            rate_per = row['Yield_To_Maturity'] / freq
            coupon_per = (row['Coupon_Rate'] / freq) * 100
            times = np.arange(1, periods + 1)
            cfs = np.full(periods, coupon_per)
            cfs[-1] += 100
            pv = cfs / ((1 + rate_per) ** times)
            price = np.sum(pv)
            mac_dur = np.sum(times * pv) / price / freq
            mod_dur = mac_dur / (1 + rate_per)
            conv = np.sum(times * (times + 1) * pv) / (price * ((1 + rate_per) ** 2)) / (freq ** 2)
            mod_durs.append(mod_dur)
            convexities.append(conv)
        else:
            mod_durs.append(0.0)
            convexities.append(0.0)
            
    df['Mod_Duration'] = mod_durs
    df['Convexity'] = convexities
    return df

df_portfolio = build_portfolio()

def run_simulation(df, bps, fx_pct):
    delta_y = bps / 10000.0
    fx_shift = fx_pct / 100.0
    pnls = []
    
    for _, row in df.iterrows():
        ac = row['Asset_Class']
        val = row['Market_Value_ZAR']
        if ac == 'Fixed Income':
            pct_change = (-row['Mod_Duration'] * delta_y) + (0.5 * row['Convexity'] * (delta_y ** 2))
            pnl = val * pct_change
        elif ac == 'Equity':
            rate_impact = (row['Rate_Beta'] * (bps / 100.0)) / 100.0
            fx_impact = row['FX_Beta'] * fx_shift
            pnl = val * (rate_impact + fx_impact)
        elif ac == 'Credit':
            pnl = (val * delta_y) * 0.90
        elif ac == 'Cash':
            pnl = val * delta_y
        else:
            pnl = 0.0
        pnls.append(pnl)
        
    res = df.copy()
    res['PnL_ZAR'] = pnls
    res['Stressed_Value'] = res['Market_Value_ZAR'] + res['PnL_ZAR']
    res['Return_Pct'] = (res['PnL_ZAR'] / res['Market_Value_ZAR']) * 100
    return res

results = run_simulation(df_portfolio, repo_bps, fx_pct_shift)


total_value = results['Market_Value_ZAR'].sum()
weights = results['Market_Value_ZAR'] / total_value
port_vol_annual = np.sum(weights * results['Ann_Vol'])
port_vol_10d = port_vol_annual * np.sqrt(10 / 252.0)
z_score = norm.ppf(0.95)

var_95 = total_value * z_score * port_vol_10d
es_95 = total_value * port_vol_10d * (norm.pdf(z_score) / (1 - 0.95))

total_pnl = results['PnL_ZAR'].sum()
stressed_total = total_value + total_pnl
total_pct = (total_pnl / total_value) * 100


m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Portfolio Value", f"R {total_value:,.2f}")
m2.metric("Stressed Value", f"R {stressed_total:,.2f}")
m3.metric("Total P&L Impact", f"R {total_pnl:,.2f}", delta=f"{total_pct:+.2f}%")
m4.metric("10-Day 95% VaR", f"R {var_95:,.2f}")
m5.metric("10-Day Expected Shortfall", f"R {es_95:,.2f}")

st.markdown("---")


tab1, tab2, tab3 = st.tabs(["📊 P&L & Sector Breakdown", "📈 Sensitivity Surfaces", "📄 Asset Breakdown Table"])

with tab1:
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("P&L Impact by Asset Class")
        fig_asset = px.bar(
            results.groupby('Asset_Class')['PnL_ZAR'].sum().reset_index(),
            x='Asset_Class', y='PnL_ZAR',
            color='PnL_ZAR',
            color_continuous_scale=px.colors.diverging.RdYlGn,
            text_auto='.2s'
        )
        fig_asset.update_layout(showlegend=False, template="plotly_white")
        st.plotly_chart(fig_asset, use_container_width=True)

    with col_right:
        st.subheader("Sector P&L Contribution")
        fig_sector = px.bar(
            results.groupby('Sector')['PnL_ZAR'].sum().reset_index(),
            x='Sector', y='PnL_ZAR',
            color='PnL_ZAR',
            color_continuous_scale=px.colors.diverging.RdYlGn,
            text_auto='.2s'
        )
        fig_sector.update_layout(showlegend=False, template="plotly_white")
        st.plotly_chart(fig_sector, use_container_width=True)

with tab2:
    st.subheader("Multi-Factor Sensitivity Curve: Repo Rate vs. USD/ZAR Shock")
    bps_range = np.linspace(-200, 300, 11)
    fx_range = np.linspace(-15, 15, 11)
    matrix = np.zeros((len(fx_range), len(bps_range)))
    
    for i, fx in enumerate(fx_range):
        for j, bps in enumerate(bps_range):
            res_ij = run_simulation(df_portfolio, bps, fx)
            matrix[i, j] = res_ij['PnL_ZAR'].sum()
            
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=matrix,
        x=[f"{b:+.0f} bps" for b in bps_range],
        y=[f"{f:+.1f}% FX" for f in fx_range],
        colorscale='RdYlGn',
        colorbar=dict(title="P&L (ZAR)")
    ))
    fig_heatmap.update_layout(
        xaxis_title="SARB Rate Shift (bps)",
        yaxis_title="USD/ZAR Currency Shift (%)",
        template="plotly_white",
        height=500
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

with tab3:
    st.subheader("Asset-Level Stress Simulation Details")
    formatted_df = results[[
        'Asset_ID', 'Asset_Class', 'Sector', 'Market_Value_ZAR', 
        'Mod_Duration', 'Rate_Beta', 'FX_Beta', 'PnL_ZAR', 'Stressed_Value', 'Return_Pct'
    ]].copy()
    
    st.dataframe(
        formatted_df.style.format({
            'Market_Value_ZAR': 'R {:,.2f}',
            'Mod_Duration': '{:.2f}',
            'Rate_Beta': '{:.2f}',
            'FX_Beta': '{:.2f}',
            'PnL_ZAR': 'R {:,.2f}',
            'Stressed_Value': 'R {:,.2f}',
            'Return_Pct': '{:+.2f}%'
        }),
        use_container_width=True
    )
