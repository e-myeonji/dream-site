from flask import Flask, render_template, request, redirect, url_for
import os
import cloudinary
import cloudinary.uploader
from supabase import create_client

app = Flask(__name__)

# 🔥 Cloudinary
cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET")
)

# 🔥 Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

# 🔥 메뉴 불러오기
def load_menu():
    try:
        res = supabase.table("menu").select("*").execute()
        return res.data
    except Exception as e:
        print("LOAD ERROR:", e)
        return []

# 🔥 메뉴 저장 (전체 교체)
def save_menu(menu):
    try:
        supabase.table("menu").delete().neq("id", 0).execute()
        for m in menu:
            supabase.table("menu").insert(m).execute()
        print("SAVE SUCCESS")
    except Exception as e:
        print("SAVE ERROR:", e)

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

            image_url = ""

            try:
                if img and img.filename:
                    res = cloudinary.uploader.upload(img)
                    image_url = res["secure_url"]
            except Exception as e:
                print("IMAGE ERROR:", e)

            menu.append({
                "name": n,
                "star": int(s),
                "image": image_url
            })

        save_menu(menu)
        return redirect(url_for("index"))

    return render_template("admin.html")

@app.route("/admin/reset", methods=["POST"])
def reset():
    supabase.table("menu").delete().neq("id", 0).execute()
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)