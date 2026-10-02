# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp>=1.2,<2"]
# ///
"""Suki PromiseGuard MCP server.

Focused MVP for delivery-related complaint recovery:
- find_recovery_cases
- prepare_recovery_plan
- publish_recovery_card
- apply_recovery_action
- get_recovery_result
"""

from __future__ import annotations

import datetime as dt
import os
import sqlite3
import uuid
from typing import Any

from mcp.server.fastmcp import FastMCP

ROOT = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(ROOT, "..", "data", "store.db"))

mcp = FastMCP("suki")


def conn() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def now_iso() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()


def plan_token(ticket_id: str, updated_at: str) -> str:
    return f"{ticket_id}:{updated_at}"


def init_promiseguard_schema(reset: bool = False) -> None:
    with conn() as con:
        if reset:
            con.executescript(
                """
                DROP TABLE IF EXISTS pg_audit_log;
                DROP TABLE IF EXISTS pg_recovery_actions;
                DROP TABLE IF EXISTS pg_staffing;
                DROP TABLE IF EXISTS pg_refund_policy;
                DROP TABLE IF EXISTS pg_csrs;
                DROP TABLE IF EXISTS pg_tickets;
                DROP TABLE IF EXISTS pg_deliveries;
                DROP TABLE IF EXISTS pg_orders;
                DROP TABLE IF EXISTS pg_meta;
                """
            )

        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS pg_meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pg_orders (
              id TEXT PRIMARY KEY,
              branch TEXT NOT NULL,
              placed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pg_deliveries (
              id TEXT PRIMARY KEY,
              order_id TEXT NOT NULL REFERENCES pg_orders(id),
              outcome TEXT NOT NULL,
              promised_at TEXT,
              actual_at TEXT,
              latest_eta TEXT,
              replacement_order_id TEXT
            );

            CREATE TABLE IF NOT EXISTS pg_tickets (
              id TEXT PRIMARY KEY,
              order_id TEXT NOT NULL REFERENCES pg_orders(id),
              delivery_id TEXT NOT NULL REFERENCES pg_deliveries(id),
              branch TEXT NOT NULL,
              status TEXT NOT NULL,
              priority INTEGER NOT NULL,
              created_at TEXT NOT NULL,
              first_response_at TEXT,
              owner_id TEXT,
              customer_name TEXT NOT NULL,
              summary TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pg_csrs (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              branch TEXT NOT NULL,
              active INTEGER NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pg_staffing (
              branch TEXT NOT NULL,
              date TEXT NOT NULL,
              required INTEGER NOT NULL,
              scheduled INTEGER NOT NULL,
              PRIMARY KEY(branch, date)
            );

            CREATE TABLE IF NOT EXISTS pg_refund_policy (
              branch TEXT PRIMARY KEY,
              authorization TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pg_recovery_actions (
              id TEXT PRIMARY KEY,
              ticket_id TEXT NOT NULL REFERENCES pg_tickets(id),
              plan_token TEXT NOT NULL,
              owner_before TEXT,
              owner_after TEXT NOT NULL,
              status_before TEXT NOT NULL,
              status_after TEXT NOT NULL,
              response_draft TEXT NOT NULL,
              created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS pg_audit_log (
              id TEXT PRIMARY KEY,
              action_id TEXT NOT NULL REFERENCES pg_recovery_actions(id),
              event TEXT NOT NULL,
              details_json TEXT NOT NULL,
              created_at TEXT NOT NULL
            );
            """
        )

        seeded = con.execute("SELECT COUNT(*) AS n FROM pg_meta").fetchone()["n"]
        if seeded > 0:
            return

        con.execute("INSERT INTO pg_meta(key, value) VALUES (?, ?)", ("sandbox_date", "2026-10-02"))

        con.executemany(
            "INSERT INTO pg_csrs(id, name, branch, active) VALUES (?, ?, ?, ?)",
            [
                ("CSR-001", "Mika Santos", "Cubao", 1),
                ("CSR-002", "Paolo Reyes", "Cubao", 1),
                ("CSR-003", "Rina Cruz", "Cubao", 0),
                ("CSR-004", "Aila Ramos", "BGC", 1),
            ],
        )

        con.executemany(
            "INSERT INTO pg_refund_policy(branch, authorization) VALUES (?, ?)",
            [("Cubao", "manual_only"), ("BGC", "manual_only")],
        )

        con.executemany(
            "INSERT INTO pg_staffing(branch, date, required, scheduled) VALUES (?, ?, ?, ?)",
            [("Cubao", "2026-10-02", 4, 3), ("BGC", "2026-10-02", 3, 3)],
        )

        con.executemany(
            "INSERT INTO pg_orders(id, branch, placed_at) VALUES (?, ?, ?)",
            [
                ("ORD-1001", "Cubao", "2026-09-18T09:00:00+08:00"),
                ("ORD-1002", "Cubao", "2026-09-19T08:45:00+08:00"),
                ("ORD-1003", "Cubao", "2026-09-20T10:30:00+08:00"),
                ("ORD-1004", "Cubao", "2026-09-22T14:15:00+08:00"),
                ("ORD-1005", "Cubao", "2026-09-23T11:20:00+08:00"),
                ("ORD-1006", "Cubao", "2026-09-24T12:05:00+08:00"),
                ("ORD-1007", "Cubao", "2026-09-17T08:10:00+08:00"),
                ("ORD-1008", "Cubao", "2026-09-25T17:00:00+08:00"),
                ("ORD-1009", "Cubao", "2026-09-26T09:40:00+08:00"),
                ("ORD-1010", "Cubao", "2026-09-27T16:25:00+08:00"),
                ("ORD-1011", "Cubao", "2026-09-28T15:00:00+08:00"),
            ],
        )

        con.executemany(
            """
            INSERT INTO pg_deliveries(id, order_id, outcome, promised_at, actual_at, latest_eta, replacement_order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("DLV-1001", "ORD-1001", "late", "2026-09-19T12:00:00+08:00", "2026-09-19T17:45:00+08:00", None, None),
                ("DLV-1002", "ORD-1002", "failed", "2026-09-20T11:00:00+08:00", None, None, None),
                ("DLV-1003", "ORD-1003", "unresolved", "2026-09-21T16:00:00+08:00", None, None, None),
                ("DLV-1004", "ORD-1004", "returned", "2026-09-23T18:00:00+08:00", "2026-09-23T19:10:00+08:00", None, None),
                ("DLV-1005", "ORD-1005", "failed", "2026-09-24T18:00:00+08:00", None, None, None),
                ("DLV-1006", "ORD-1006", "late", "2026-09-25T18:00:00+08:00", "2026-09-25T21:30:00+08:00", None, None),
                ("DLV-1007", "ORD-1007", "failed", "2026-09-18T11:00:00+08:00", None, None, None),
                ("DLV-1008", "ORD-1008", "failed", "2026-09-26T20:00:00+08:00", None, None, None),
                ("DLV-1009", "ORD-1009", "unresolved", "2026-09-27T15:00:00+08:00", None, None, None),
                ("DLV-1010", "ORD-1010", "late", "2026-09-28T20:00:00+08:00", "2026-09-29T00:05:00+08:00", None, None),
                ("DLV-1011", "ORD-1011", "failed", "2026-09-29T19:00:00+08:00", None, None, None),
            ],
        )

        con.executemany(
            """
            INSERT INTO pg_tickets(
              id, order_id, delivery_id, branch, status, priority, created_at,
              first_response_at, owner_id, customer_name, summary, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("TCK-0001", "ORD-1001", "DLV-1001", "Cubao", "open", 2, "2026-09-20T09:00:00+08:00", None, None, "Pat Dela Cruz", "Delivery arrived far beyond ETA", "2026-09-20T09:00:00+08:00"),
                ("TCK-0002", "ORD-1002", "DLV-1002", "Cubao", "open", 3, "2026-09-21T08:00:00+08:00", None, None, "Mia Vergara", "Package never arrived", "2026-09-21T08:00:00+08:00"),
                ("TCK-0003", "ORD-1003", "DLV-1003", "Cubao", "open", 3, "2026-09-19T07:00:00+08:00", None, None, "Jon Reyes", "No delivery update", "2026-09-19T07:00:00+08:00"),
                ("TCK-0004", "ORD-1004", "DLV-1004", "Cubao", "pending", 2, "2026-09-24T11:10:00+08:00", "2026-09-24T11:30:00+08:00", "CSR-002", "Ella Flores", "Package returned unexpectedly", "2026-09-24T11:30:00+08:00"),
                ("TCK-0005", "ORD-1005", "DLV-1005", "Cubao", "open", 1, "2026-09-25T13:30:00+08:00", None, None, "Kiko Ramos", "Rider marked delivered but not received", "2026-09-25T13:30:00+08:00"),
                ("TCK-0006", "ORD-1006", "DLV-1006", "Cubao", "pending", 2, "2026-09-26T09:50:00+08:00", None, "CSR-001", "Lara Tan", "Delivery delayed", "2026-09-26T09:50:00+08:00"),
                ("TCK-0007", "ORD-1007", "DLV-1007", "Cubao", "open", 3, "2026-09-18T12:40:00+08:00", None, None, "Ana Lopez", "Still waiting for replacement", "2026-09-18T12:40:00+08:00"),
                ("TCK-0008", "ORD-1008", "DLV-1008", "Cubao", "open", 2, "2026-09-27T08:15:00+08:00", None, None, "Ivan Sy", "Failed attempt no follow-up", "2026-09-27T08:15:00+08:00"),
                ("TCK-0009", "ORD-1009", "DLV-1009", "Cubao", "open", 2, "2026-09-28T07:50:00+08:00", None, None, "Neil Abad", "Tracking stopped", "2026-09-28T07:50:00+08:00"),
                ("TCK-0010", "ORD-1010", "DLV-1010", "Cubao", "pending", 1, "2026-09-29T10:00:00+08:00", "2026-09-29T10:15:00+08:00", "CSR-002", "Ruby Ong", "Asking for compensation", "2026-09-29T10:15:00+08:00"),
                ("TCK-0011", "ORD-1011", "DLV-1011", "Cubao", "open", 2, "2026-09-30T09:00:00+08:00", None, None, "Pia Mateo", "No rider update", "2026-09-30T09:00:00+08:00"),
            ],
        )


def _sandbox_date(con: sqlite3.Connection) -> dt.date:
    return dt.date.fromisoformat(con.execute("SELECT value FROM pg_meta WHERE key='sandbox_date'").fetchone()[0])


def _fetch_ticket(con: sqlite3.Connection, ticket_id: str):
    return con.execute(
        """
        SELECT t.*, o.placed_at AS order_placed_at, d.outcome, d.latest_eta, d.replacement_order_id,
               d.promised_at, d.actual_at
        FROM pg_tickets t
        JOIN pg_orders o ON o.id = t.order_id
        JOIN pg_deliveries d ON d.id = t.delivery_id
        WHERE t.id = ?
        """,
        (ticket_id,),
    ).fetchone()


def _active_csrs(con: sqlite3.Connection, branch: str):
    return con.execute("SELECT id, name FROM pg_csrs WHERE branch=? AND active=1 ORDER BY id", (branch,)).fetchall()


def _pick_owner(con: sqlite3.Connection, branch: str):
    rows = con.execute(
        """
        SELECT c.id, c.name, COUNT(t.id) AS load
        FROM pg_csrs c
        LEFT JOIN pg_tickets t ON t.owner_id = c.id AND t.status IN ('open','pending')
        WHERE c.branch = ? AND c.active = 1
        GROUP BY c.id, c.name
        ORDER BY load ASC, c.id ASC
        """,
        (branch,),
    ).fetchall()
    return rows[0] if rows else None


@mcp.tool()
def reset_promiseguard_data() -> dict[str, Any]:
    """Reset the PromiseGuard sandbox tables to the deterministic demo dataset."""
    init_promiseguard_schema(reset=True)
    return {"status": "ok", "message": "PromiseGuard sandbox reset"}


@mcp.tool()
def find_recovery_cases(branch: str = "Cubao", limit: int = 10) -> dict[str, Any]:
    """Return a ranked shortlist of delivery recovery tickets for one branch.

    Ranking priority: urgent > unanswered > older.
    Also flags invalid chronology (ticket created before order date).
    """
    init_promiseguard_schema()
    limit = max(1, min(int(limit), 25))

    with conn() as con:
        sandbox_date = _sandbox_date(con)
        rows = con.execute(
            """
            SELECT t.id AS ticket_id, t.status, t.priority, t.created_at, t.first_response_at,
                   t.summary, t.customer_name, t.order_id, t.delivery_id,
                   o.placed_at AS order_placed_at, d.outcome
            FROM pg_tickets t
            JOIN pg_orders o ON o.id = t.order_id
            JOIN pg_deliveries d ON d.id = t.delivery_id
            WHERE t.branch = ? AND t.status IN ('open','pending')
            """,
            (branch,),
        ).fetchall()

    valid: list[dict[str, Any]] = []
    invalid: list[dict[str, Any]] = []

    for r in rows:
        if dt.datetime.fromisoformat(r["created_at"]) < dt.datetime.fromisoformat(r["order_placed_at"]):
            invalid.append(
                {
                    "ticket_id": r["ticket_id"],
                    "reason": "ticket_created_before_order",
                    "ticket_created_at": r["created_at"],
                    "order_placed_at": r["order_placed_at"],
                }
            )
            continue

        age_days = (sandbox_date - dt.datetime.fromisoformat(r["created_at"]).date()).days
        unanswered = 1 if r["first_response_at"] is None else 0
        open_state = 1 if r["status"] == "open" else 0
        score = (r["priority"] * 5) + (unanswered * 20) + age_days + (open_state * 2)
        valid.append(
            {
                "ticket_id": r["ticket_id"],
                "customer_name": r["customer_name"],
                "summary": r["summary"],
                "status": r["status"],
                "priority": r["priority"],
                "ticket_age_days": age_days,
                "response_status": "unanswered" if unanswered else "responded",
                "delivery_outcome": r["outcome"],
                "order_id": r["order_id"],
                "delivery_id": r["delivery_id"],
                "score": score,
            }
        )

    valid.sort(key=lambda x: (x["score"], x["ticket_age_days"], x["priority"]), reverse=True)

    return {
        "branch": branch,
        "sandbox_date": "2026-10-02",
        "count": min(limit, len(valid)),
        "cases": valid[:limit],
        "excluded_invalid_chronology": invalid,
        "ranking_rules": [
            "higher priority first",
            "unanswered before answered",
            "older tickets first",
        ],
    }


@mcp.tool()
def prepare_recovery_plan(ticket_id: str) -> dict[str, Any]:
    """Build evidence-backed recovery plan and Promise Check for one ticket.

    Blocks unsupported promises when no reliable ETA or refund authorization exists.
    """
    init_promiseguard_schema()

    with conn() as con:
        ticket = _fetch_ticket(con, ticket_id)
        if not ticket:
            return {"status": "not_found", "ticket_id": ticket_id}

        if dt.datetime.fromisoformat(ticket["created_at"]) < dt.datetime.fromisoformat(ticket["order_placed_at"]):
            return {"status": "invalid_case", "ticket_id": ticket_id, "reason": "ticket_created_before_order"}

        staffing = con.execute(
            "SELECT required, scheduled FROM pg_staffing WHERE branch=? ORDER BY date DESC LIMIT 1",
            (ticket["branch"],),
        ).fetchone()
        policy = con.execute("SELECT authorization FROM pg_refund_policy WHERE branch=?", (ticket["branch"],)).fetchone()
        owner = _pick_owner(con, ticket["branch"])
        active_owners = _active_csrs(con, ticket["branch"])

        has_eta = ticket["latest_eta"] is not None
        refund_authorized = bool(policy and policy["authorization"] == "auto")
        staffing_gap = 0 if not staffing else max(0, staffing["required"] - staffing["scheduled"])

        promise_check = [
            {"label": "Actual delivery facts verified", "status": "safe", "reason": f"Delivery outcome is '{ticket['outcome']}'"},
            {"label": "Proposed owner is active", "status": "safe" if owner else "blocked", "reason": "No active CSR available" if not owner else f"{owner['name']} is active"},
            {"label": "No reliable new ETA", "status": "blocked" if not has_eta else "safe", "reason": "No ETA in delivery data" if not has_eta else f"ETA: {ticket['latest_eta']}"},
            {"label": "Refund authorization unavailable", "status": "blocked" if not refund_authorized else "safe", "reason": "Branch policy is manual approval" if not refund_authorized else "Auto refund allowed"},
        ]

        blocked_promises = [
            {
                "text": "Your replacement will arrive in 30 minutes.",
                "reason": "No replacement order or reliable ETA exists in the data.",
            }
        ]
        if not refund_authorized:
            blocked_promises.append(
                {
                    "text": "Your refund has been approved and processed.",
                    "reason": "Refund authorization is unavailable in current policy data.",
                }
            )

        draft = (
            f"Hi {ticket['customer_name']}, we reviewed ticket {ticket_id}. "
            f"Order {ticket['order_id']} is currently marked as {ticket['outcome']}. "
            "Your case has been assigned for review and escalated to delivery operations. "
            "We will update you once verified delivery information is available."
        )

        return {
            "ticket_id": ticket_id,
            "branch": ticket["branch"],
            "plan_token": plan_token(ticket_id, ticket["updated_at"]),
            "what_happened": {
                "delivery_outcome": ticket["outcome"],
                "promised_at": ticket["promised_at"],
                "actual_at": ticket["actual_at"],
                "status": ticket["status"],
            },
            "evidence": {
                "ticket_id": ticket_id,
                "order_id": ticket["order_id"],
                "delivery_id": ticket["delivery_id"],
                "staffing": {
                    "required": staffing["required"] if staffing else None,
                    "scheduled": staffing["scheduled"] if staffing else None,
                    "gap": staffing_gap,
                    "note": "Staffing gap observed; causality not proven.",
                },
            },
            "uncertainties": [
                "Whether staffing caused the delay",
                "Whether refund is authorized",
                "Whether a new ETA is available",
            ],
            "proposed_action": {
                "owner_id": owner["id"] if owner else None,
                "owner_name": owner["name"] if owner else None,
                "set_status": "pending",
            },
            "active_owners": [{"id": r["id"], "name": r["name"]} for r in active_owners],
            "promise_check": promise_check,
            "safe_promises": [
                "Your case has been assigned to our customer service team for review.",
                "We are escalating this with delivery operations.",
            ],
            "blocked_promises": blocked_promises,
            "response_draft": draft,
        }


@mcp.tool()
def publish_recovery_card(ticket_id: str) -> dict[str, Any]:
    """Return GUI-ready evidence card payload for PromiseGuard."""
    plan = prepare_recovery_plan(ticket_id)
    if plan.get("status") in {"not_found", "invalid_case"}:
        return {"title": "SUKI PROMISEGUARD", **plan}

    return {
        "title": "SUKI PROMISEGUARD",
        "subtitle": "Customer recovery case",
        "ticket_id": plan["ticket_id"],
        "plan_token": plan["plan_token"],
        "evidence": plan["evidence"],
        "recovery_plan": plan["proposed_action"],
        "promise_check": plan["promise_check"],
        "response_preview": plan["response_draft"],
        "notes": ["Draft only—not sent", "Assigned—not resolved"],
    }


@mcp.tool()
def apply_recovery_action(ticket_id: str, owner_id: str, plan_token_value: str) -> dict[str, Any]:
    """Apply approved assignment/escalation transaction with stale-plan protection.

    Idempotent: same ticket+plan+owner returns existing action without duplicate writes.
    """
    init_promiseguard_schema()

    with conn() as con:
        ticket = _fetch_ticket(con, ticket_id)
        if not ticket:
            return {"status": "not_found", "ticket_id": ticket_id}

        existing = con.execute(
            """
            SELECT id FROM pg_recovery_actions
            WHERE ticket_id=? AND plan_token=? AND owner_after=?
            ORDER BY created_at DESC LIMIT 1
            """,
            (ticket_id, plan_token_value, owner_id),
        ).fetchone()
        if existing:
            return {
                "status": "already_applied",
                "ticket_id": ticket_id,
                "action_id": existing["id"],
                "result": get_recovery_result(existing["id"]),
            }

        expected = plan_token(ticket_id, ticket["updated_at"])
        if plan_token_value != expected:
            return {
                "status": "stale_plan",
                "ticket_id": ticket_id,
                "expected_plan_token": expected,
                "provided_plan_token": plan_token_value,
            }

        owner = con.execute(
            "SELECT id, active FROM pg_csrs WHERE id=? AND branch=?",
            (owner_id, ticket["branch"]),
        ).fetchone()
        if not owner or owner["active"] != 1:
            return {"status": "invalid_owner", "ticket_id": ticket_id, "owner_id": owner_id}

        action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
        at = now_iso()
        status_after = "pending" if ticket["status"] == "open" else ticket["status"]
        response = prepare_recovery_plan(ticket_id)["response_draft"]

        con.execute("UPDATE pg_tickets SET owner_id=?, status=?, updated_at=? WHERE id=?", (owner_id, status_after, at, ticket_id))
        con.execute(
            """
            INSERT INTO pg_recovery_actions(
              id, ticket_id, plan_token, owner_before, owner_after,
              status_before, status_after, response_draft, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (action_id, ticket_id, plan_token_value, ticket["owner_id"], owner_id, ticket["status"], status_after, response, at),
        )
        con.execute(
            "INSERT INTO pg_audit_log(id, action_id, event, details_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (f"AUD-{uuid.uuid4().hex[:8].upper()}", action_id, "recovery_action_applied", '{"ticket_id":"%s","owner_after":"%s","status_after":"%s"}' % (ticket_id, owner_id, status_after), at),
        )
        con.commit()

        return {"status": "applied", "ticket_id": ticket_id, "action_id": action_id, "result": get_recovery_result(action_id)}

@mcp.tool()
def get_recovery_result(action_id: str) -> dict[str, Any]:
    """Read back persisted owner/status changes and audit record for one action."""
    init_promiseguard_schema()

    with conn() as con:
        row = con.execute(
            """
            SELECT a.id AS action_id, a.ticket_id, a.owner_before, a.owner_after,
                   a.status_before, a.status_after, a.response_draft,
                   t.first_response_at AS first_response_at_after
            FROM pg_recovery_actions a
            JOIN pg_tickets t ON t.id = a.ticket_id
            WHERE a.id = ?
            """,
            (action_id,),
        ).fetchone()
        if not row:
            return {"status": "not_found", "action_id": action_id}

        audit = con.execute("SELECT id, event, created_at FROM pg_audit_log WHERE action_id=? ORDER BY created_at", (action_id,)).fetchall()

    return {
        "action_id": row["action_id"],
        "ticket_id": row["ticket_id"],
        "owner_before": row["owner_before"],
        "owner_after": row["owner_after"],
        "status_before": row["status_before"],
        "status_after": row["status_after"],
        "first_response_at_after": row["first_response_at_after"],
        "response_draft": row["response_draft"],
        "delivery_to_customer_sent": False,
        "resolution_state": "assigned-not-resolved",
        "audit": [{"id": r["id"], "event": r["event"], "created_at": r["created_at"]} for r in audit],
    }


if __name__ == "__main__":
    init_promiseguard_schema()
    mcp.run()
