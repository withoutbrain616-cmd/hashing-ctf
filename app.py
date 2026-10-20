from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ctf.db"
app = Flask(__name__)
app.secret_key = "change-this-local-ctf-secret-key"

# Flag checks happen on the server; answers are not sent to the browser.
CHALLENGES = [
    {
        "id": 1, "title": "Hash detektivi", "points": 100, "level": "O‘rtacha",
        "topic": "SHA-256 va xesh uzunligi",
        "description": "Quyidagi qiymat SHA-256 yordamida hisoblangan matn xeshidir. Matnni terminalda qayta xeshlab, flagni toping.",
        "data": "f8004c470a6d253c80a51a6bab556a0cc26c9861d9b3004a350b0d6a4c169072",
        "hint": "echo -n 'FLAG{hash_basics}' | sha256sum",
        "flag": "FLAG{hash_basics}",
        "explanation": "SHA-256 natijasi 256 bit, ya’ni 32 bayt yoki 64 ta hex belgidan iborat."
    },
    {
        "id": 2, "title": "Parol xeshi", "points": 100, "level": "O‘rtacha",
        "topic": "MD5 va nomzod parollar",
        "description": "Tizim quyidagi MD5 xeshni saqlagan. Nomzodlarni tekshirib, mos parolni aniqlang. Flag formatida parolni yozing: FLAG{parol}.",
        "data": "637506241fdf5d9d32f4e209926928cc",
        "hint": "Nomzodlar: password, admin123, Cyber2026!, qwerty123. echo -n 'NOMZOD' | md5sum",
        "flag": "FLAG{Cyber2026!}",
        "explanation": "Bu topshiriq kichik, berilgan nomzodlar ro‘yxatida xesh mosligini tekshiradi. MD5 zamonaviy xavfsizlik uchun tavsiya etilmaydi."
    },
    {
        "id": 3, "title": "Fayl yaxlitligi", "points": 100, "level": "O‘rtacha",
        "topic": "SHA-256 checksum",
        "description": "Fayl ichida aynan FLAG{integrity_ok} matni bo‘lishi kerak. Matnni faylga yozing, uning SHA-256 xeshini hisoblang va berilgan nazorat qiymati bilan solishtiring.",
        "data": "9216ce73097215bd989d4cb19b0acd97ebb24a3e7249a6a39434f9079fe5a444",
        "hint": "printf '%s' 'FLAG{integrity_ok}' > evidence.txt && sha256sum evidence.txt",
        "flag": "FLAG{integrity_ok}",
        "explanation": "Fayl tarkibidagi bitta belgi o‘zgarsa ham, SHA-256 qiymati odatda keskin o‘zgaradi."
    },
    {
        "id": 4, "title": "Salt siri", "points": 100, "level": "O‘rtacha",
        "topic": "Salt va kamalak jadvallari",
        "description": "Bir xil parol salt qo‘shilmagan va salt qo‘shilgan holda xeshlangan. Ikkinchi kirish matni admin123SALT42. Uni SHA-256 bilan xeshlab, salt qo‘shilganda natija nima uchun o‘zgarishini tushuntiring. Flag — xulosani ifodalovchi satr.",
        "data": "SHA-256(admin123): 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9\nSHA-256(admin123SALT42): 5fe26b97303ba6dc7ec362b52d4cb06f4996a3cc18fb6fc2ba270a944a925351",
        "hint": "echo -n 'admin123SALT42' | sha256sum",
        "flag": "FLAG{salt_changes_hash}",
        "explanation": "Salt xeshlashdan oldin parolga qo‘shiladigan qiymat. Amaliy tizimda har bir parol uchun alohida, tasodifiy salt ishlatiladi."
    },
    {
        "id": 5, "title": "Kamalak jadvali", "points": 100, "level": "O‘rtacha+",
        "topic": "Tuzsiz MD5 xeshini aniqlash",
        "description": "Berilgan MD5 qiymatini jadvaldagi nomzodlar bilan solishtiring. Mos parolni topib, flag formatida yuboring: FLAG{parol}.",
        "data": "0192023a7bbd73250516f069df18b500",
        "hint": "Nomzodlar: password, admin123, qwerty, letmein. Har birini echo -n 'parol' | md5sum bilan tekshiring.",
        "flag": "FLAG{admin123}",
        "explanation": "Mos parol admin123. Oldindan hisoblangan xesh-parol juftliklari tuzsiz va keng tarqalgan parollarni aniqlashga yordam beradi."
    },
    {
        "id": 6, "title": "Kodlangan xabar", "points": 100, "level": "O‘rtacha+",
        "topic": "Base64 va xeshlash farqi",
        "description": "Quyidagi Base64 matnini dekodlang. Chiqqan flagni yuboring.",
        "data": "RkxBR3tiYXNlNjRfaXNfbm90X2VuY3J5cHRpb259",
        "hint": "echo 'KOD' | base64 -d",
        "flag": "FLAG{base64_is_not_encryption}",
        "explanation": "Base64 — qaytariladigan kodlash, shifrlash emas. Xeshlash esa odatda bir tomonlama digest hosil qiladi."
    },
]

CHALLENGES[0]["data"] = "f8004c470a6d253c80a51a6bab556a0cc26c9861d9b3004a350b0d6a4c169072"
CHALLENGES[1]["data"] = "637506241fdf5d9d32f4e209926928cc"
CHALLENGES[2]["data"] = "9216ce73097215bd989d4cb19b0acd97ebb24a3e7249a6a39434f9079fe5a444"
CHALLENGES[3]["data"] = CHALLENGES[3]["data"].replace("240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9", "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9").replace("5fe26b97303ba6dc7ec362b52d4cb06f4996a3cc18fb6fc2ba270a944a925351", "5fe26b97303ba6dc7ec362b52d4cb06f4996a3cc18fb6fc2ba270a944a925351")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                team TEXT NOT NULL,
                score INTEGER NOT NULL DEFAULT 0,
                solved TEXT NOT NULL DEFAULT '',
                updated_at TEXT NOT NULL
            )
        """)
        con.commit()

def get_solved():
    return session.get("solved", [])

def get_score():
    return len(get_solved()) * 100

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        team = request.form.get("team", "").strip()
        if not team:
            flash("Avval jamoa nomini kiriting.", "error")
        else:
            session["team"] = team[:40]
            session.setdefault("solved", [])
            flash(f"{session['team']} jamoasi musobaqaga qo‘shildi.", "success")
        return redirect(url_for("index"))

    solved = get_solved()
    cards = []
    for c in CHALLENGES:
        cards.append({
            "id": c["id"], "title": c["title"], "points": c["points"],
            "level": c["level"], "topic": c["topic"],
            "solved": str(c["id"]) in solved
        })
    return render_template("index.html", challenges=cards, team=session.get("team"),
                           score=get_score(), solved_count=len(solved))

@app.route("/challenge/<int:challenge_id>", methods=["GET", "POST"])
def challenge(challenge_id):
    c = next((x for x in CHALLENGES if x["id"] == challenge_id), None)
    if c is None:
        return render_template("404.html"), 404
    if not session.get("team"):
        flash("Avval bosh sahifada jamoa nomini kiriting.", "error")
        return redirect(url_for("index"))

    solved = get_solved()
    message = None
    if request.method == "POST":
        submitted = request.form.get("flag", "").strip()
        if str(c["id"]) in solved:
            message = ("success", "Bu topshiriq avval yechilgan.")
        elif submitted.casefold() == c["flag"].casefold():
            solved.append(str(c["id"]))
            session["solved"] = solved
            save_score()
            message = ("success", f"To‘g‘ri flag! +{c['points']} ball.")
        else:
            message = ("error", "Flag noto‘g‘ri. Buyruq natijasini va formatni qayta tekshiring.")
    return render_template("challenge.html", c=c, solved=str(c["id"]) in get_solved(),
                           score=get_score(), message=message, team=session.get("team"))

def save_score():
    team = session.get("team", "Noma’lum")
    solved = get_solved()
    score = len(solved) * 100
    with sqlite3.connect(DB_PATH) as con:
        row = con.execute("SELECT id FROM leaderboard WHERE team = ?", (team,)).fetchone()
        if row:
            con.execute("UPDATE leaderboard SET score=?, solved=?, updated_at=? WHERE id=?",
                        (score, ",".join(solved), datetime.now().isoformat(timespec="seconds"), row[0]))
        else:
            con.execute("INSERT INTO leaderboard(team, score, solved, updated_at) VALUES(?,?,?,?)",
                        (team, score, ",".join(solved), datetime.now().isoformat(timespec="seconds")))
        con.commit()


@app.route("/leaderboard")
def leaderboard():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """SELECT team, score, solved, updated_at
               FROM leaderboard
               WHERE lower(trim(team)) NOT IN (?, ?)
               ORDER BY score DESC, updated_at ASC""",
            ("zero", "vali")
        ).fetchall()
    return render_template("leaderboard.html", rows=rows)


@app.route("/reset")
def reset():
    session.clear()
    flash("Joriy brauzer sessiyasi tozalandi. Jamoa nomini qayta kiriting.", "success")
    return redirect(url_for("index"))

@app.route("/health")
def health():
    return {"status": "ok", "app": "Hashing Basics CTF"}

if __name__ == "__main__":
    init_db()
    # Default is local-only. Do not change host to 0.0.0.0 unless intentionally running
    # on a trusted classroom LAN and you understand the exposure.
    app.run(host="127.0.0.1", port=5000, debug=False)
