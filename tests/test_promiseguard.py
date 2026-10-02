import importlib.util
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).parents[1] / "mcp-server" / "server.py"
spec = importlib.util.spec_from_file_location("promiseguard_server", MODULE)
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class PromiseGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.tmp_dir / "store.db"
        server.DB_PATH = str(self.db_path)
        server.init_promiseguard_schema(reset=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_recovery_shortlist_and_invalid_chronology(self):
        res = server.find_recovery_cases(branch="Cubao", limit=20)
        self.assertEqual(res["sandbox_date"], "2026-10-02")
        self.assertEqual(res["cases"][0]["ticket_id"], "TCK-0007")
        invalid_ids = {x["ticket_id"] for x in res["excluded_invalid_chronology"]}
        self.assertIn("TCK-0003", invalid_ids)

    def test_prepare_plan_blocks_unsupported_promises(self):
        plan = server.prepare_recovery_plan("TCK-0007")
        checks = {row["label"]: row["status"] for row in plan["promise_check"]}
        self.assertEqual(checks["Actual delivery facts verified"], "safe")
        self.assertEqual(checks["Proposed owner is active"], "safe")
        self.assertEqual(checks["No reliable new ETA"], "blocked")
        self.assertEqual(checks["Refund authorization unavailable"], "blocked")

    def test_stale_plan_protection(self):
        plan = server.prepare_recovery_plan("TCK-0007")
        with sqlite3.connect(server.DB_PATH) as con:
            con.execute("UPDATE pg_tickets SET updated_at=? WHERE id=?", ("2026-10-02T10:00:00+08:00", "TCK-0007"))
            con.commit()

        stale = server.apply_recovery_action("TCK-0007", "CSR-001", plan["plan_token"])
        self.assertEqual(stale["status"], "stale_plan")

    def test_idempotent_apply_and_verified_readback(self):
        plan = server.prepare_recovery_plan("TCK-0007")
        first = server.apply_recovery_action("TCK-0007", "CSR-001", plan["plan_token"])
        second = server.apply_recovery_action("TCK-0007", "CSR-001", plan["plan_token"])

        self.assertEqual(first["status"], "applied")
        self.assertEqual(second["status"], "already_applied")
        self.assertEqual(first["action_id"], second["action_id"])

        verified = server.get_recovery_result(first["action_id"])
        self.assertEqual(verified["ticket_id"], "TCK-0007")
        self.assertIsNone(verified["owner_before"])
        self.assertEqual(verified["owner_after"], "CSR-001")
        self.assertEqual(verified["status_before"], "open")
        self.assertEqual(verified["status_after"], "pending")
        self.assertIsNone(verified["first_response_at_after"])
        self.assertEqual(verified["resolution_state"], "assigned-not-resolved")


if __name__ == "__main__":
    unittest.main()
