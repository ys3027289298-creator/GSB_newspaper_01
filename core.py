"""报社核心逻辑：稿件、版面、记者和印刷。"""

import json
import random


def new_game():
    return {
        "articles": {},
        "layout_capacity": 2,
        "layout_load": 0,
        "layout_articles": [],
        "assignments": {},
        "reporters": {"R1": True, "R2": False},
        "printer_fault": False,
        "circulation": 0,
        "score": 0,
        "retracted": False,
        "day": 1,
        "issue_id": 0,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    for key, value in new_game().items():
        state.setdefault(key, value)
    return state


def publish(state, article_id):
    if not article_id or article_id in state["articles"]:
        return False
    state["articles"][article_id] = True
    return True


def layout(state, article_id):
    if article_id in state["layout_articles"]:
        return False
    if state["layout_load"] >= state["layout_capacity"]:
        return False
    state["layout_articles"].append(article_id)
    state["layout_load"] += 1
    return True


def fee(state, article_id, end_day):
    return end_day - state["day"]


def cancel_publish(state, article_id):
    released = False
    if article_id in state["layout_articles"]:
        state["layout_articles"].remove(article_id)
        state["layout_load"] -= 1
        released = True
    if article_id in state["articles"]:
        del state["articles"][article_id]
        released = True
    return released


def assign(state, article_id, reporter):
    if not state["reporters"].get(reporter, False):
        return False
    state["assignments"][article_id] = reporter
    return True


def print_issue(state):
    if state.get("printer_fault"):
        return False
    state["issue_id"] += 1
    state["circulation"] += 1
    return True


def retract(state):
    if state.get("retracted"):
        return False
    state["retracted"] = True
    state["score"] = state.get("score", 0) - 10
    return True


def handle_command(state, line):
    parts = line.split()
    if not parts:
        return "error: 空命令"
    cmd, args = parts[0], parts[1:]
    try:
        if cmd == "publish" and len(args) == 1:
            ok = publish(state, args[0])
        elif cmd == "layout" and len(args) == 1:
            ok = layout(state, args[0])
        elif cmd == "fee" and len(args) == 2:
            return "fee=%s" % fee(state, args[0], int(args[1]))
        elif cmd == "cancel" and len(args) == 1:
            ok = cancel_publish(state, args[0])
        elif cmd == "assign" and len(args) == 2:
            ok = assign(state, args[0], args[1])
        elif cmd == "print" and not args:
            ok = print_issue(state)
        elif cmd == "retract" and not args:
            ok = retract(state)
        else:
            return "error: 非法命令"
    except (KeyError, ValueError):
        return "error: 非法参数"
    return "ok" if ok else "error: 操作被拒绝"


def demo():
    rng = random.Random(20260929)
    state = new_game()
    script = [
        "publish A1",
        "publish A1",
        "layout A1",
        "layout A2",
        "layout A3",
        "assign A1 R1",
        "assign A2 R2",
        "fee A1 4",
        "print",
        "retract",
        "retract",
        "cancel A1",
        "bogus",
    ]
    for line in script:
        print("> %s" % line)
        print(handle_command(state, line))
    state["circulation"] += rng.randint(100, 200)
    print("issue=%s circulation=%s score=%s"
          % (state["issue_id"], state["circulation"], state["score"]))


def main():
    print("报社 - 命令: publish/layout/fee/cancel/assign/print/retract/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print(handle_command(state, raw))


if __name__ == "__main__":
    main()
