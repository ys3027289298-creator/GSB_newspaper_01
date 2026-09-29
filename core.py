"""报社核心逻辑：稿件、版面、记者和印刷。"""

import json


def new_game():
    return {
        "articles": {},
        "layout_capacity": 2,
        "layout_load": 0,
        "layout": [],
        "day": 1,
        "issue_id": 0,
        "reporters": {"R1": True, "R2": False},
        "assignments": {},
        "printer_fault": False,
        "printed": 0,
        "score": 0,
        "retracted": False,
    }


def save_state(state):
    return json.dumps(state, ensure_ascii=False)


def load_state(text):
    state = json.loads(text)
    if not isinstance(state, dict) or "issue_id" not in state:
        raise ValueError("invalid state data")
    return state


def publish(state, article_id):
    if article_id in state["articles"]:
        return False
    state["articles"][article_id] = True
    return True


def layout(state, article_id):
    if article_id in state["layout"]:
        return False
    if state["layout_load"] >= state["layout_capacity"]:
        return False
    state["layout"].append(article_id)
    state["layout_load"] += 1
    return True


def fee(state, article_id, end_day):
    return max(0, end_day - state["day"])


def cancel_publish(state, article_id):
    published = article_id in state["articles"]
    laid_out = article_id in state["layout"]
    if not published and not laid_out:
        return False
    if published:
        del state["articles"][article_id]
    if laid_out:
        state["layout"].remove(article_id)
        state["layout_load"] -= 1
    return True


def assign(state, article_id, reporter):
    if not state["reporters"].get(reporter, False):
        return False
    state["assignments"][article_id] = reporter
    return True


def print_issue(state):
    if state.get("printer_fault"):
        return False
    state["issue_id"] += 1
    state["printed"] += 1
    return True


def retract(state):
    if state["retracted"]:
        return False
    state["retracted"] = True
    state["score"] -= 10
    return True


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
        parts = raw.split()
        cmd, args = parts[0], parts[1:]
        try:
            if cmd == "publish" and len(args) == 1:
                print("ok" if publish(state, args[0]) else "重复刊登")
            elif cmd == "layout" and len(args) == 1:
                print("ok" if layout(state, args[0]) else "版面已满或重复")
            elif cmd == "fee" and len(args) == 2:
                print(fee(state, args[0], int(args[1])))
            elif cmd == "cancel" and len(args) == 1:
                print("ok" if cancel_publish(state, args[0]) else "未刊登")
            elif cmd == "assign" and len(args) == 2:
                print("ok" if assign(state, args[0], args[1]) else "记者离线")
            elif cmd == "print" and not args:
                print("ok" if print_issue(state) else "印刷故障")
            elif cmd == "retract" and not args:
                print("ok" if retract(state) else "已撤稿")
            else:
                print("未知命令")
        except ValueError:
            print("参数错误")


if __name__ == "__main__":
    main()
