from flask import Flask, render_template, request, redirect, url_for
import json, os
from werkzeug.utils import secure_filename

app = Flask(__name__)

DATA_FILE = "menu.json"
UPLOAD_FOLDER = "static/cards"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_menu():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_menu(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    menu = load_menu()
    return render_template("index.html", count=len(menu))

@app.route("/admin", methods=["GET","POST"])
def admin():
    if request.args.get("pw") != ADMIN_PASSWORD:
        return "접근 불가"

    if request.method == "POST":
        names = request.form.getlist("name")
        stars = request.form.getlist("star")
        images = request.files.getlist("image")

        menu = []

        for n, s, img in zip(names, stars, images):
            if not n.strip():
                continue

            filename = secure_filename(img.filename)

            if filename:
                img.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            menu.append({
                "name": n,
                "star": int(s),
                "image": filename
            })

        save_menu(menu)
        return redirect(url_for("index"))

    return render_template("admin.html")

@app.route("/admin/reset", methods=["POST"])
def reset():
    save_menu([])
    return redirect("/admin?pw=1234")

@app.route("/animation")
def animation():
    count = request.args.get("count", 1)
    return render_template("animation.html", count=count)

@app.route("/reveal")
def reveal():
    menu = load_menu()
    return render_template("reveal.html", menu=menu)

@app.route("/result")
def result():
    return render_template("result.html")

# 🔥 Render용 (중요)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)