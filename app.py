import markdown
from flask import Flask, render_template, request, send_file
import os
import requests
from dotenv import load_dotenv
from xhtml2pdf import pisa
from io import BytesIO

load_dotenv()
app = Flask(__name__)
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    course_output = ""
    if request.method == "POST":
        topic = request.form["topic"]
        prompt = f"""Create a full course on "{topic}". Include:
        - Course title
        - 10-12 modules
        - 4 lessons per module
        - A quiz with 5 questions per module (include answers)
        Format nicely in markdown."""

        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "mistralai/Mistral-7B-Instruct-v0.2",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }

        response = requests.post(
            "https://api.together.xyz/v1/chat/completions",
            headers=headers,
            json=payload
        )

        data = response.json()
        course_output = data["choices"][0]["message"]["content"]

    return render_template("index.html", course=course_output)

@app.route("/download", methods=["POST"])
def download():
    course_text = request.form["course"]
    
    # ✅ Convert Markdown to styled HTML
    html_body = markdown.markdown(course_text)
    full_html = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.5;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #003366;
                }}
                pre {{
                    background: #f4f4f4;
                    padding: 10px;
                }}
            </style>
        </head>
        <body>
            {html_body}
        </body>
    </html>
    """

    result = BytesIO()
    pisa_status = pisa.CreatePDF(full_html, dest=result)

    if pisa_status.err:
        return "Error generating PDF", 500

    result.seek(0)
    return send_file(result, as_attachment=True, download_name="course.pdf")

if __name__ == "__main__":
    app.run(debug=True)
