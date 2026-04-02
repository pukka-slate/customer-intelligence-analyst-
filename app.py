"""
Slate & Sachi — Agent System v2.0
Web interface: run with `python3 app.py`, then open http://localhost:5000
"""

import os
import anthropic
from flask import Flask, render_template, request, Response, stream_with_context, jsonify

from agent import AGENTS

app = Flask(__name__)


@app.route("/")
def index():
    # Pass agent list to template so it can build the selector
    agents = [{"id": k, "name": v["name"], "placeholder": v["placeholder"]}
              for k, v in AGENTS.items()]
    return render_template("index.html", agents=agents)


@app.route("/analyse", methods=["POST"])
def analyse():
    input_text = request.form.get("input", "").strip()
    agent_id = request.form.get("agent", "customer-intelligence")

    if not input_text:
        return Response("No input provided.", status=400)

    if agent_id not in AGENTS:
        return Response("Unknown agent.", status=400)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return Response(
            "ANTHROPIC_API_KEY is not set. Add it to your .zshrc and restart.", status=500
        )

    system_prompt = AGENTS[agent_id]["prompt"]

    def generate():
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": input_text}],
        ) as stream:
            for event in stream:
                if (
                    event.type == "content_block_delta"
                    and event.delta.type == "text_delta"
                ):
                    yield event.delta.text

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain",
        headers={"X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\nSlate & Sachi — Agent System")
    print(f"Agents loaded: {', '.join(v['name'] for v in AGENTS.values())}")
    print(f"Open your browser at: http://localhost:{port}\n")
    app.run(debug=False, port=port)
