import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

NOTION_TOKEN = "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"
HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json"
}

SEARCH_URL = "https://api.notion.com/v1/search"

INDEX_HTML = """
<!doctype html>
<style>
body { background-color: #1a1a1a; color: white; font-family: Arial, sans-serif; margin: 40px; }
input[type="text"] { width: 70%; padding: 12px; font-size: 16px; border: 2px solid #444; border-radius: 8px; background: #333; color: white; }
input[type="submit"] { padding: 12px 24px; font-size: 16px; background: #007bff; color: white; border: none; border-radius: 8px; cursor: pointer; margin-left: 10px; }
input[type="submit"]:hover { background: #0056b3; }
h2, h3 { color: #ffffff; }
ul { list-style: none; padding: 0; }
li { margin: 10px 0; padding: 15px; background: #2a2a2a; border-radius: 8px; border-left: 4px solid #fae3af; }
a { color: #4dabf7; text-decoration: none; font-size: 16px; }
a:hover { color: #ffffff; text-decoration: underline; }
</style>
<title>Поиск по Notion</title>
<h2>🔍 Поиск по Notion</h2>
<form method="post">
  <input type="text" name="query" placeholder="Джон Сноу, Старки..." autofocus required>
  <input type="submit" value="Искать">
</form>
{% if results %}
  <h3>Результаты ({{results|length}}):</h3>
  <ul>
    {% for page in results %}
      <li><a href="https://www.notion.so/{{page['id']|replace('-', '')}}" target="_blank">{{page['title']}}</a></li>
    {% endfor %}
  </ul>
{% endif %}
"""


def search_notion(query):
    data = {
        "query": query,
        "filter": {"value": "page", "property": "object"}
    }
    try:
        response = requests.post(SEARCH_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        results = []
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
        return []

    for res in response.json().get("results", []):
        title = "Без названия"
        props = res.get("properties")
        if props:
            for key, prop in props.items():
                if prop.get("type") == "title" and prop.get("title"):
                    title = "".join([t.get("plain_text", "") for t in prop["title"]])
                    break
        results.append({"id": res["id"], "title": title})
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        query = request.form.get("query")
        results = search_notion(query)
    return render_template_string(INDEX_HTML, results=results)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
