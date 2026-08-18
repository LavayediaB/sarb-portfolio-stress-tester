<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/e01e0b54-3549-4e06-8849-129cabceb3c8" />

[README.md](https://github.com/user-attachments/files/30681196/README.md)
# SARB Prime Rate & Macro-Sensitive Portfolio Stress Tester

An interactive, multi-factor quantitative risk engine and stress-testing application engineered for the South African financial market. Built using Python, SciPy, and Streamlit, this dashboard models portfolio P&L sensitivity across **SARB Repo/Prime rate shifts**, **USD/ZAR exchange rate volatility**, and **sovereign yield curve movements**.

**Live Interactive App:**https://sarb-portfolio-stress-tester-dgtfmd9yvhf7ryttghwzes.streamlit.app/
---
<img width="1920" height="1080" alt="2" src="https://github.com/user-attachments/assets/4d07cc61-3083-443e-96d1-db2c9eabb837" />
<img width="1920" height="1080" alt="3" src="https://github.com/user-attachments/assets/e5ae3c92-99a2-43ab-8d07-9e48bd1a15ca" />
<img width="1920" height="1080" alt="4" src="https://github.com/user-attachments/assets/45040bbe-206c-4f39-b8b9-b167688d362b" />
<img width="1920" height="1080" alt="5" src="https://github.com/user-attachments/assets/e8ed28f5-8031-403a-a6fb-a1cb2f13d0f0" />

## Key Features

- **Multi-Factor Sensitivity Engine:** Simulates joint macro shocks combining interest rate changes ($\Delta y$) and USD/ZAR currency fluctuations ($\Delta FX$).
- **Closed-Form Fixed Income Pricing:** Calculates exact Macaulay Duration, Modified Duration, and 2nd-Order Convexity adjustments for South African Government Bonds (e.g., $R2030, R2035$).
- **Multi-Factor Equity Sensitivities:** Applies sector-specific interest rate ($\beta_{\text{Rate}}$) and exchange rate ($\beta_{\text{FX}}$) sensitivities tailored to JSE listings (Financials, Resources, REITs, Consumer Retail).
- **Parametric Tail Risk Modeling:** Calculates 10-Day 95% Parametric Value at Risk (VaR) and Expected Shortfall (CVaR).
- **Live Market Data Ingestion:** Connects dynamically to Yahoo Finance (`yfinance`) for real-time JSE stock feeds (`.JO` tickers) and USD/ZAR exchange rates.
- **Interactive Visualizations:** Includes Plotly sensitivity surface heatmaps, sector P&L breakdowns, and asset stress tables.

---

## Quantitative Financial Methodology

### 1. Sovereign Bond Sensitivity (Duration & Convexity)
Fixed Income price movements under yield shocks $\Delta y$ utilize the standard second-order Taylor expansion:

$$\frac{\Delta P}{P} \approx -D_{\text{mod}} \cdot \Delta y + \frac{1}{2} C \cdot (\Delta y)^2$$

Where:
- $D_{\text{mod}} = \frac{D_{\text{Mac}}}{1 + \frac{y}{k}}$ is the Modified Duration ($k = 2$ semi-annual compounding).
- $C$ is the Convexity coefficient capturing yield curve curvature.

### 2. Multi-Factor Equity Return Sensitivity
Equity returns are modeled using joint macro-factor beta sensitivities:

$$\Delta S_i = \beta_{\text{Rate}, i} \cdot \left(\frac{\Delta \text{Repo}}{100}\right) + \beta_{\text{FX}, i} \cdot \left(\frac{\Delta \text{USD/ZAR}}{\text{USD/ZAR}_{\text{base}}}\right)$$

### 3. Parametric Portfolio Risk Metrics (VaR & Expected Shortfall)
The 10-Day Parametric Value at Risk (VaR) and Expected Shortfall (ES) at a 95% confidence level ($\alpha = 0.95$):

$$\text{VaR}_{0.95} = V_{\text{total}} \cdot z_{0.95} \cdot \sigma_{10\text{d}}$$

$$\text{ES}_{0.95} = V_{\text{total}} \cdot \sigma_{10\text{d}} \cdot \left( \frac{\phi(z_{0.95})}{1 - 0.95} \right)$$

---

##  Tech Stack

- **Language:** Python 3.10+
- **Quantitative & Statistical Libraries:** Pandas, NumPy, SciPy (Normal distribution & statistics)
- **Market Data:** YFinance API (JSE Equity & USD/ZAR feeds)
- **UI & Dashboarding:** Streamlit, Plotly Express & Graph Objects

---

## Installation & Local Execution

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/sarb-portfolio-stress-tester.git](https://github.com/YOUR_USERNAME/sarb-portfolio-stress-tester.git)
   cd sarb-portfolio-stress-tester
   ```

2. **Set Up a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Web Dashboard:**
   ```bash
   python -m streamlit run app.py
   ```
   Open your browser to `http://localhost:8501`.

---
<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/e42e2473-762e-4527-a896-92b3170f590c" />

##  License

Distributed under the MIT License. See `LICENSE` for more information.
