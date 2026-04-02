"""
Slate & Sachi — Customer Intelligence Agent v2.0
Web interface: run with `python app.py`, then open http://localhost:5000
"""

import os
import anthropic
from flask import Flask, render_template, request, Response, stream_with_context

from agent import SYSTEM_PROMPT

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyse", methods=["POST"])
def analyse():
    input_text = request.form.get("input", "").strip()

    if not input_text:
        return Response("No input provided.", status=400)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return Response(
            "ANTHROPIC_API_KEY environment variable is not set.", status=500
        )

    def generate():
        client = anthropic.Anthropic(api_key=api_key)
        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
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
    print(f"\nSlate & Sachi — Customer Intelligence Agent")
    print(f"Open your browser at: http://localhost:{port}\n")
    app.run(debug=False, port=port)
