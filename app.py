from flask import Flask, render_template, request, redirect, url_for
import os
import cloudinary
import cloudinary.uploader
import psycopg2
import psycopg2.extras

app = Flask(__name__)

# 🔥 환경변수 확인 로그 (디버깅용)
print("DB:", os.environ.get("DATABASE_URL"))
print("CLOUD:", os.environ.get("CLOUD_NAME"))

# 🔥 Cloudinary 설정
cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET")
)

# 🔥 DB 연결
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_conn():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("DB CONNECTION ERROR:", e)
        return None

# 🔥 테이블 생성 (안정화 버전)
def init_db():
    try:
        conn = get_conn()
        if conn is None:
            return
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS menu (
                id SERIAL PRIMARY KEY,
                name TEXT,
                star INTEGER,
                image TEXT
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("DB INIT SUCCESS")
    except Exception as e:
        print("DB INIT ERROR:", e)

init_db()

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "1234")

# 🔥 메뉴 불러오기
def load_menu():
    try:
        conn = get_conn()
        if conn is None:
            return []
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM menu")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        print("LOAD ERROR:", e)
        return []

# 🔥 메뉴 저장
def save_menu(menu):
    try:
        conn = get_conn()
        if conn is None:
            return
        cur = conn.cursor()
        cur.execute("DELETE FROM menu")
        for m in menu:
            cur.execute(
                "INSERT INTO menu (name, star, image) VALUES (%s,%s,%s)",
                (m["name"], m["star"], m["image"])
            )
        conn.commit()
        cur.close()
        conn.close()
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
                print("IMAGE UPLOAD ERROR:", e)

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
    try:
        conn = get_conn()
        if conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM menu")
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print("RESET ERROR:", e)

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