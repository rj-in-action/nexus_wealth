"""
Nexus Wealth — Client 360 Database Layer
SQLite-based mock data store simulating Citi's Client 360 platform.
"""
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "nexus_wealth.db")


def get_connection():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            age INTEGER,
            occupation TEXT,
            annual_income REAL,
            tax_bracket TEXT,
            risk_tolerance TEXT CHECK(risk_tolerance IN ('conservative','moderate','aggressive')),
            investment_horizon TEXT,
            total_aum REAL,
            segment TEXT DEFAULT 'Mass Affluent',
            life_events TEXT,  -- JSON array
            goals TEXT,        -- JSON array
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            ticker TEXT,
            quantity REAL,
            current_price REAL,
            current_value REAL,
            cost_basis REAL,
            unrealized_gain_loss REAL,
            weight_pct REAL,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS outside_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            institution TEXT NOT NULL,
            account_type TEXT NOT NULL,
            estimated_value REAL,
            asset_details TEXT,  -- JSON
            detected_at TEXT DEFAULT (datetime('now')),
            migration_status TEXT DEFAULT 'identified',
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            recommendation_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            projected_impact TEXT,
            confidence REAL,
            reasoning_chain TEXT,  -- JSON
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );

        CREATE TABLE IF NOT EXISTS audit_trail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
            client_id TEXT NOT NULL,
            agent_name TEXT NOT NULL,
            step_number INTEGER,
            status TEXT CHECK(status IN ('started','completed','failed','pending_approval','approved','rejected')),
            input_summary TEXT,
            output_summary TEXT,
            reasoning TEXT,
            duration_ms INTEGER,
            timestamp TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id TEXT PRIMARY KEY,
            client_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            current_step INTEGER DEFAULT 0,
            total_steps INTEGER DEFAULT 8,
            started_at TEXT,
            completed_at TEXT,
            advisor_approved INTEGER DEFAULT 0,
            result_summary TEXT,  -- JSON
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
    """)

    conn.commit()
    conn.close()


# --- Query Helpers ---

def get_all_clients():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM clients ORDER BY total_aum DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_client(client_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_client_portfolio(client_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM portfolios WHERE client_id = ? ORDER BY current_value DESC",
        (client_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_client_outside_assets(client_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM outside_assets WHERE client_id = ? ORDER BY estimated_value DESC",
        (client_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pipeline_run(run_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM pipeline_runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_pipeline_run(run_id: str, client_id: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pipeline_runs (id, client_id, status, started_at) VALUES (?, ?, 'running', ?)",
        (run_id, client_id, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()


def update_pipeline_run(run_id: str, **kwargs):
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [run_id]
    conn.execute(f"UPDATE pipeline_runs SET {sets} WHERE id = ?", vals)
    conn.commit()
    conn.close()


def add_audit_entry(run_id, client_id, agent_name, step_number, status,
                    input_summary="", output_summary="", reasoning="", duration_ms=0):
    conn = get_connection()
    conn.execute(
        """INSERT INTO audit_trail 
           (run_id, client_id, agent_name, step_number, status, input_summary, output_summary, reasoning, duration_ms)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (run_id, client_id, agent_name, step_number, status, input_summary, output_summary, reasoning, duration_ms)
    )
    conn.commit()
    conn.close()


def get_audit_trail(run_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_trail WHERE run_id = ? ORDER BY step_number, timestamp",
        (run_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_client_audit_trail(client_id: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM audit_trail WHERE client_id = ? ORDER BY timestamp DESC LIMIT 50",
        (client_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_recommendation(client_id, run_id, agent_name, rec_type, title, description,
                        projected_impact="", confidence=0.0, reasoning_chain=""):
    conn = get_connection()
    conn.execute(
        """INSERT INTO recommendations 
           (client_id, run_id, agent_name, recommendation_type, title, description, projected_impact, confidence, reasoning_chain)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (client_id, run_id, agent_name, rec_type, title, description, projected_impact, confidence, reasoning_chain)
    )
    conn.commit()
    conn.close()


def get_recommendations(client_id: str, run_id: str = None):
    conn = get_connection()
    if run_id:
        rows = conn.execute(
            "SELECT * FROM recommendations WHERE client_id = ? AND run_id = ? ORDER BY created_at",
            (client_id, run_id)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM recommendations WHERE client_id = ? ORDER BY created_at DESC LIMIT 20",
            (client_id,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Initialize on import
init_db()
