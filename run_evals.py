import json
import time
from agent import ask_agent

with open("eval_set.json", encoding="utf-8") as f:
    cases = json.load(f)

results = []
for case in cases:
    answer, tools = ask_agent(case["question"], return_tools=True)
    text = answer.lower()

    expected = case["expected_tool"]
    if expected == "any":
        tool_ok = True
    elif expected is None:
        tool_ok = len(tools) == 0
    else:
        tool_ok = expected in tools

    contain_ok = (not case["must_contain"]) or any(w.lower() in text for w in case["must_contain"])
    not_contain_ok = not any(w.lower() in text for w in case["must_not_contain"])

    passed = tool_ok and contain_ok and not_contain_ok
    results.append({**case, "answer": answer, "tools": tools, "passed": passed,
                    "tool_ok": tool_ok, "contain_ok": contain_ok, "not_contain_ok": not_contain_ok})
    print(f"{'PASS' if passed else 'FAIL'} | #{case['id']} | tools={tools} | {case['question'][:50]}")
    time.sleep(4)

score = sum(r["passed"] for r in results)
print(f"\nScore: {score}/{len(results)} = {score / len(results):.0%}")

with open("eval_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)