"""
Nexus Wealth — Demo Data Seeder
Populates the Client 360 database with 5 realistic Mass Affluent profiles.
Idempotent — safe to run multiple times.
"""
import json
from db import get_connection, init_db

CLIENTS = [
    {
        "id": "CLT-001",
        "first_name": "Sarah",
        "last_name": "Chen",
        "email": "sarah.chen@email.com",
        "phone": "(212) 555-0142",
        "age": 42,
        "occupation": "VP of Engineering, Tech Startup",
        "annual_income": 385000,
        "tax_bracket": "35%",
        "risk_tolerance": "aggressive",
        "investment_horizon": "15+ years",
        "total_aum": 875000,
        "segment": "Mass Affluent",
        "life_events": json.dumps(["Stock options vesting Q3 2026", "Second child expected", "Planning home upgrade"]),
        "goals": json.dumps(["Maximize tax-advantaged growth", "College fund for 2 children", "Early retirement at 55"]),
    },
    {
        "id": "CLT-002",
        "first_name": "Michael",
        "last_name": "Rodriguez",
        "email": "m.rodriguez@email.com",
        "phone": "(415) 555-0287",
        "age": 55,
        "occupation": "Small Business Owner, Restaurant Group",
        "annual_income": 290000,
        "tax_bracket": "32%",
        "risk_tolerance": "moderate",
        "investment_horizon": "10 years",
        "total_aum": 620000,
        "segment": "Mass Affluent",
        "life_events": json.dumps(["Business expansion planned", "Daughter's wedding 2027", "Considering partial retirement"]),
        "goals": json.dumps(["Retirement income stream", "Business succession planning", "Estate planning"]),
    },
    {
        "id": "CLT-003",
        "first_name": "Priya",
        "last_name": "Patel",
        "email": "priya.patel@email.com",
        "phone": "(646) 555-0391",
        "age": 34,
        "occupation": "Attending Physician, Cardiology",
        "annual_income": 420000,
        "tax_bracket": "35%",
        "risk_tolerance": "aggressive",
        "investment_horizon": "20+ years",
        "total_aum": 450000,
        "segment": "Mass Affluent",
        "life_events": json.dumps(["Student loan payoff milestone", "Recently married", "First home purchase"]),
        "goals": json.dumps(["Aggressive wealth building", "Student loan elimination", "Build diversified portfolio"]),
    },
    {
        "id": "CLT-004",
        "first_name": "James",
        "last_name": "Whitfield",
        "email": "james.whitfield@email.com",
        "phone": "(312) 555-0518",
        "age": 62,
        "occupation": "Retired Corporate Attorney",
        "annual_income": 180000,
        "tax_bracket": "24%",
        "risk_tolerance": "conservative",
        "investment_horizon": "5-10 years",
        "total_aum": 980000,
        "segment": "Mass Affluent",
        "life_events": json.dumps(["Recent retirement", "Medicare enrollment", "Downsizing primary home"]),
        "goals": json.dumps(["Capital preservation", "Tax-efficient income", "Legacy planning for grandchildren"]),
    },
    {
        "id": "CLT-005",
        "first_name": "Aisha",
        "last_name": "Thompson",
        "email": "aisha.thompson@email.com",
        "phone": "(404) 555-0672",
        "age": 38,
        "occupation": "Director of Marketing, Fortune 500",
        "annual_income": 310000,
        "tax_bracket": "32%",
        "risk_tolerance": "moderate",
        "investment_horizon": "15 years",
        "total_aum": 540000,
        "segment": "Mass Affluent",
        "life_events": json.dumps(["RSU vesting schedule", "Divorce finalized 2025", "Relocating to new city"]),
        "goals": json.dumps(["Rebuild financial independence", "Max 401k + backdoor Roth", "Build emergency reserves"]),
    },
]

PORTFOLIOS = {
    "CLT-001": [
        {"asset_name": "Vanguard S&P 500 ETF", "asset_type": "US Equity", "ticker": "VOO", "quantity": 520, "current_price": 485.20, "cost_basis": 198000, "weight_pct": 28.8},
        {"asset_name": "Invesco QQQ Trust", "asset_type": "US Equity", "ticker": "QQQ", "quantity": 280, "current_price": 510.75, "cost_basis": 112000, "weight_pct": 16.3},
        {"asset_name": "iShares MSCI Emerging Mkts", "asset_type": "Intl Equity", "ticker": "EEM", "quantity": 1200, "current_price": 48.30, "cost_basis": 52000, "weight_pct": 6.6},
        {"asset_name": "iShares Core US Aggregate Bond", "asset_type": "Fixed Income", "ticker": "AGG", "quantity": 800, "current_price": 98.50, "cost_basis": 82000, "weight_pct": 9.0},
        {"asset_name": "Company Stock Options", "asset_type": "Single Stock", "ticker": "PRIV", "quantity": 5000, "current_price": 42.00, "cost_basis": 25000, "weight_pct": 24.0},
        {"asset_name": "Vanguard Real Estate ETF", "asset_type": "REITs", "ticker": "VNQ", "quantity": 400, "current_price": 88.60, "cost_basis": 32000, "weight_pct": 4.1},
        {"asset_name": "Cash & Money Market", "asset_type": "Cash", "ticker": "CASH", "quantity": 1, "current_price": 98500, "cost_basis": 98500, "weight_pct": 11.3},
    ],
    "CLT-002": [
        {"asset_name": "Vanguard Total Stock Market", "asset_type": "US Equity", "ticker": "VTI", "quantity": 450, "current_price": 268.40, "cost_basis": 95000, "weight_pct": 19.5},
        {"asset_name": "iShares Core US Aggregate Bond", "asset_type": "Fixed Income", "ticker": "AGG", "quantity": 1200, "current_price": 98.50, "cost_basis": 122000, "weight_pct": 19.1},
        {"asset_name": "Vanguard Dividend Appreciation", "asset_type": "US Equity", "ticker": "VIG", "quantity": 380, "current_price": 185.20, "cost_basis": 58000, "weight_pct": 11.4},
        {"asset_name": "SPDR Gold Shares", "asset_type": "Commodities", "ticker": "GLD", "quantity": 200, "current_price": 245.80, "cost_basis": 38000, "weight_pct": 7.9},
        {"asset_name": "Vanguard Short-Term Bond", "asset_type": "Fixed Income", "ticker": "BSV", "quantity": 600, "current_price": 76.90, "cost_basis": 46000, "weight_pct": 7.4},
        {"asset_name": "Schwab US REIT ETF", "asset_type": "REITs", "ticker": "SCHH", "quantity": 500, "current_price": 42.10, "cost_basis": 18500, "weight_pct": 3.4},
        {"asset_name": "Cash & Money Market", "asset_type": "Cash", "ticker": "CASH", "quantity": 1, "current_price": 195000, "cost_basis": 195000, "weight_pct": 31.5},
    ],
    "CLT-003": [
        {"asset_name": "Invesco QQQ Trust", "asset_type": "US Equity", "ticker": "QQQ", "quantity": 200, "current_price": 510.75, "cost_basis": 85000, "weight_pct": 22.7},
        {"asset_name": "ARK Innovation ETF", "asset_type": "US Equity", "ticker": "ARKK", "quantity": 600, "current_price": 62.40, "cost_basis": 48000, "weight_pct": 8.3},
        {"asset_name": "Vanguard S&P 500 ETF", "asset_type": "US Equity", "ticker": "VOO", "quantity": 180, "current_price": 485.20, "cost_basis": 72000, "weight_pct": 19.4},
        {"asset_name": "iShares Bitcoin Trust", "asset_type": "Crypto", "ticker": "IBIT", "quantity": 400, "current_price": 58.90, "cost_basis": 20000, "weight_pct": 5.2},
        {"asset_name": "iShares MSCI Emerging Mkts", "asset_type": "Intl Equity", "ticker": "EEM", "quantity": 800, "current_price": 48.30, "cost_basis": 35000, "weight_pct": 8.6},
        {"asset_name": "Vanguard Total Bond Market", "asset_type": "Fixed Income", "ticker": "BND", "quantity": 500, "current_price": 72.10, "cost_basis": 38000, "weight_pct": 8.0},
        {"asset_name": "Cash & Money Market", "asset_type": "Cash", "ticker": "CASH", "quantity": 1, "current_price": 125000, "cost_basis": 125000, "weight_pct": 27.8},
    ],
    "CLT-004": [
        {"asset_name": "Vanguard Total Bond Market", "asset_type": "Fixed Income", "ticker": "BND", "quantity": 2500, "current_price": 72.10, "cost_basis": 185000, "weight_pct": 18.4},
        {"asset_name": "iShares TIPS Bond ETF", "asset_type": "Fixed Income", "ticker": "TIP", "quantity": 800, "current_price": 108.40, "cost_basis": 88000, "weight_pct": 8.8},
        {"asset_name": "Vanguard Dividend Appreciation", "asset_type": "US Equity", "ticker": "VIG", "quantity": 500, "current_price": 185.20, "cost_basis": 72000, "weight_pct": 9.4},
        {"asset_name": "Vanguard S&P 500 ETF", "asset_type": "US Equity", "ticker": "VOO", "quantity": 250, "current_price": 485.20, "cost_basis": 95000, "weight_pct": 12.4},
        {"asset_name": "Municipal Bond Fund", "asset_type": "Fixed Income", "ticker": "MUB", "quantity": 1000, "current_price": 108.60, "cost_basis": 105000, "weight_pct": 11.1},
        {"asset_name": "SPDR Gold Shares", "asset_type": "Commodities", "ticker": "GLD", "quantity": 150, "current_price": 245.80, "cost_basis": 32000, "weight_pct": 3.8},
        {"asset_name": "Cash & Money Market", "asset_type": "Cash", "ticker": "CASH", "quantity": 1, "current_price": 355000, "cost_basis": 355000, "weight_pct": 36.2},
    ],
    "CLT-005": [
        {"asset_name": "Vanguard S&P 500 ETF", "asset_type": "US Equity", "ticker": "VOO", "quantity": 300, "current_price": 485.20, "cost_basis": 120000, "weight_pct": 27.0},
        {"asset_name": "iShares Core US Aggregate Bond", "asset_type": "Fixed Income", "ticker": "AGG", "quantity": 600, "current_price": 98.50, "cost_basis": 62000, "weight_pct": 10.9},
        {"asset_name": "Vanguard Total Intl Stock", "asset_type": "Intl Equity", "ticker": "VXUS", "quantity": 500, "current_price": 62.80, "cost_basis": 28000, "weight_pct": 5.8},
        {"asset_name": "Vanguard Growth ETF", "asset_type": "US Equity", "ticker": "VUG", "quantity": 200, "current_price": 365.40, "cost_basis": 58000, "weight_pct": 13.5},
        {"asset_name": "RSU Holdings (Employer)", "asset_type": "Single Stock", "ticker": "F500", "quantity": 800, "current_price": 95.50, "cost_basis": 45000, "weight_pct": 14.1},
        {"asset_name": "Cash & Money Market", "asset_type": "Cash", "ticker": "CASH", "quantity": 1, "current_price": 155000, "cost_basis": 155000, "weight_pct": 28.7},
    ],
}

OUTSIDE_ASSETS = {
    "CLT-001": [
        {"institution": "Fidelity", "account_type": "401(k) Rollover", "estimated_value": 185000, "asset_details": json.dumps({"funds": ["FXAIX", "FBALX"], "last_activity": "2025-11"})},
        {"institution": "Charles Schwab", "account_type": "Brokerage", "estimated_value": 92000, "asset_details": json.dumps({"holdings": "Individual stocks, mostly tech", "last_activity": "2026-01"})},
        {"institution": "Betterment", "account_type": "Robo-Advisor IRA", "estimated_value": 45000, "asset_details": json.dumps({"strategy": "90/10 aggressive growth", "last_activity": "2026-03"})},
    ],
    "CLT-002": [
        {"institution": "Vanguard", "account_type": "Traditional IRA", "estimated_value": 220000, "asset_details": json.dumps({"funds": ["VTSAX", "VBTLX"], "last_activity": "2025-12"})},
        {"institution": "Edward Jones", "account_type": "Brokerage", "estimated_value": 65000, "asset_details": json.dumps({"holdings": "Mixed mutual funds", "last_activity": "2025-09"})},
    ],
    "CLT-003": [
        {"institution": "Wealthfront", "account_type": "Taxable Brokerage", "estimated_value": 78000, "asset_details": json.dumps({"strategy": "Tax-loss harvesting enabled", "last_activity": "2026-02"})},
        {"institution": "Fidelity", "account_type": "Residency 403(b)", "estimated_value": 125000, "asset_details": json.dumps({"funds": ["FXAIX", "Target Date 2055"], "last_activity": "2026-04"})},
        {"institution": "Robinhood", "account_type": "Individual Brokerage", "estimated_value": 32000, "asset_details": json.dumps({"holdings": "Crypto and meme stocks", "last_activity": "2026-04"})},
    ],
    "CLT-004": [
        {"institution": "Merrill Lynch", "account_type": "Retirement Account", "estimated_value": 480000, "asset_details": json.dumps({"funds": ["Target Date 2030", "Bond ladder"], "last_activity": "2026-01"})},
        {"institution": "Fidelity", "account_type": "Inherited IRA", "estimated_value": 165000, "asset_details": json.dumps({"notes": "10-year distribution rule applies", "last_activity": "2025-08"})},
    ],
    "CLT-005": [
        {"institution": "Vanguard", "account_type": "Roth IRA", "estimated_value": 95000, "asset_details": json.dumps({"funds": ["VFIAX", "VTIAX"], "last_activity": "2026-03"})},
        {"institution": "Betterment", "account_type": "Taxable Account", "estimated_value": 42000, "asset_details": json.dumps({"strategy": "Moderate growth", "last_activity": "2026-01"})},
        {"institution": "Previous Employer", "account_type": "Orphaned 401(k)", "estimated_value": 118000, "asset_details": json.dumps({"notes": "From previous job, needs rollover", "last_activity": "2024-06"})},
    ],
}


def seed():
    """Seed the database with demo data."""
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    for client in CLIENTS:
        cursor.execute(
            """INSERT OR REPLACE INTO clients 
               (id, first_name, last_name, email, phone, age, occupation, annual_income, 
                tax_bracket, risk_tolerance, investment_horizon, total_aum, segment, life_events, goals)
               VALUES (:id, :first_name, :last_name, :email, :phone, :age, :occupation, :annual_income,
                        :tax_bracket, :risk_tolerance, :investment_horizon, :total_aum, :segment, :life_events, :goals)""",
            client
        )

    for client_id, holdings in PORTFOLIOS.items():
        # Clear existing portfolio for this client
        cursor.execute("DELETE FROM portfolios WHERE client_id = ?", (client_id,))
        for h in holdings:
            current_value = h["quantity"] * h["current_price"]
            unrealized = current_value - h["cost_basis"]
            cursor.execute(
                """INSERT INTO portfolios 
                   (client_id, asset_name, asset_type, ticker, quantity, current_price, 
                    current_value, cost_basis, unrealized_gain_loss, weight_pct)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (client_id, h["asset_name"], h["asset_type"], h["ticker"],
                 h["quantity"], h["current_price"], current_value, h["cost_basis"],
                 unrealized, h["weight_pct"])
            )

    for client_id, assets in OUTSIDE_ASSETS.items():
        cursor.execute("DELETE FROM outside_assets WHERE client_id = ?", (client_id,))
        for a in assets:
            cursor.execute(
                """INSERT INTO outside_assets
                   (client_id, institution, account_type, estimated_value, asset_details)
                   VALUES (?, ?, ?, ?, ?)""",
                (client_id, a["institution"], a["account_type"], a["estimated_value"], a["asset_details"])
            )

    conn.commit()
    conn.close()
    print("Database seeded with 5 clients, portfolios, and outside assets.")


if __name__ == "__main__":
    seed()
