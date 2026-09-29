import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import core


def run_menu(lines):
    inputs = iter(lines)
    buf = io.StringIO()
    with patch("builtins.input", lambda prompt="": next(inputs)):
        with redirect_stdout(buf):
            core.main()
    return buf.getvalue()


class TestRegression(unittest.TestCase):
    def test_invalid_command_and_empty_input(self):
        out = run_menu(["bogus", "", "publish", "quit"])
        self.assertIn("未知命令", out)

    def test_menu_bad_fee_param(self):
        out = run_menu(["fee A1 notanum", "quit"])
        self.assertIn("参数错误", out)

    def test_empty_data(self):
        state = core.new_game()
        self.assertFalse(core.cancel_publish(state, "A9"))
        self.assertFalse(core.assign(state, "A1", "R9"))
        self.assertEqual(core.fee(state, "A1", 0), 0)
        with self.assertRaises(ValueError):
            core.load_state("[]")

    def test_capacity_boundary(self):
        state = core.new_game()
        self.assertTrue(core.layout(state, "A1"))
        self.assertTrue(core.layout(state, "A2"))
        self.assertFalse(core.layout(state, "A3"))
        core.cancel_publish(state, "A1")
        self.assertTrue(core.layout(state, "A3"))
        self.assertEqual(state["layout_load"], 2)

    def test_duplicate_inputs(self):
        state = core.new_game()
        self.assertTrue(core.publish(state, "A1"))
        self.assertFalse(core.publish(state, "A1"))
        self.assertTrue(core.layout(state, "A1"))
        self.assertFalse(core.layout(state, "A1"))
        state["score"] = 100
        self.assertTrue(core.retract(state))
        self.assertFalse(core.retract(state))
        self.assertEqual(state["score"], 90)

    def test_save_load_roundtrip(self):
        state = core.new_game()
        core.publish(state, "A1")
        core.print_issue(state)
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded, state)


if __name__ == "__main__":
    unittest.main()
