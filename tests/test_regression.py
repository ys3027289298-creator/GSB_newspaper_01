import unittest

import core


class TestRegression(unittest.TestCase):
    def test_illegal_command(self):
        state = core.new_game()
        self.assertTrue(core.handle_command(state, "bogus").startswith("error"))
        self.assertTrue(core.handle_command(state, "publish").startswith("error"))
        self.assertTrue(core.handle_command(state, "fee A1 x").startswith("error"))

    def test_empty_data(self):
        state = core.load_state("{}")
        self.assertEqual(state["issue_id"], 0)
        self.assertEqual(state["layout_load"], 0)
        self.assertFalse(core.publish(state, ""))
        self.assertFalse(core.cancel_publish(state, "missing"))

    def test_capacity_boundary(self):
        state = core.new_game()
        self.assertTrue(core.layout(state, "A1"))
        self.assertTrue(core.layout(state, "A2"))
        self.assertFalse(core.layout(state, "A3"))
        core.cancel_publish(state, "A2")
        self.assertTrue(core.layout(state, "A3"))

    def test_duplicate_inputs(self):
        state = core.new_game()
        self.assertTrue(core.publish(state, "A1"))
        self.assertFalse(core.publish(state, "A1"))
        self.assertTrue(core.layout(state, "A1"))
        self.assertFalse(core.layout(state, "A1"))
        self.assertEqual(state["layout_load"], 1)
        self.assertTrue(core.retract(state))
        self.assertFalse(core.retract(state))
        self.assertEqual(state["score"], -10)

    def test_save_load_roundtrip(self):
        state = core.new_game()
        core.publish(state, "A1")
        core.layout(state, "A1")
        core.print_issue(state)
        loaded = core.load_state(core.save_state(state))
        self.assertEqual(loaded, state)


if __name__ == "__main__":
    unittest.main()
