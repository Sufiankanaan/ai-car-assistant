import json
import time
from google.genai import types ,errors
from rag import gemini

JUDGE_MODEL = "gemini-3.5-flash"

PROMPT = """You are grading a car assistant's answer.

Question: {question}

Retrieved context:
{context}

Answer: {answer}

Is every factual claim in the answer supported by the retrieved context?
Reply in JSON: {{"supported": true or false, "reason": "one short sentence"}}"""

with open("eval_results.json", encoding="utf-8") as f:
    results = json.load(f)

graded = []
for r in results:
    if "search_car_knowledge" not in r["tools"]:
        continue
    try:
        response = gemini.models.generate_content(
            model=JUDGE_MODEL,
            contents=PROMPT.format(question=r["question"], context="\n\n".join(r["context"]), answer=r["answer"]),
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0),
        )
    except errors.APIError as e:
        print(f"Stopped at #{r['id']}: {e.code}. Graded so far are saved.")
        break

    verdict = json.loads(response.text)
    graded.append({"id": r["id"], **verdict})
    print(f"{'SUPPORTED' if verdict['supported'] else 'NOT SUPPORTED'} | #{r['id']} | {verdict['reason']}")
    time.sleep(4)

if graded:
    ok = sum(g["supported"] for g in graded)
    print(f"\nFaithfulness: {ok}/{len(graded)}")

with open("judge_results.json", "w", encoding="utf-8") as f:
    json.dump(graded, f, indent=2, ensure_ascii=False)