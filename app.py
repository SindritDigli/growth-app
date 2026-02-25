from flask import Flask, render_template, request, redirect, session
import sqlite3
import json

app = Flask(__name__)
app.secret_key = "una_chiave_super_segreta_123"

@app.route("/")
def home():
    if not session.get("logged_in"):
        return redirect("/login")
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]

        if password == "170481":
            session["logged_in"] = True
            return redirect("/")
        else:
            return "Password sbagliata"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/routine", methods=["GET", "POST"])
def routine():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        frequency = request.form["frequency"]

        cursor.execute(
            "INSERT INTO routines (name, frequency, completed) VALUES (?, ?, 0)",
            (name, frequency)
        )
        conn.commit()

    cursor.execute("SELECT * FROM routines ORDER BY completed ASC, id DESC")
    routines = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM routines")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM routines WHERE completed = 1")
    completed = cursor.fetchone()[0]
    
    percentage = 0
    if total > 0:
        percentage = round((completed / total) * 100)

    conn.close()

    return render_template("routine.html", routines=routines, percentage=percentage)

@app.route("/delete_routine/<int:id>")
def delete_routine(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM routines WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/routine")

@app.route("/toggle_routine/<int:id>")
def toggle_routine(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT completed FROM routines WHERE id = ?", (id,))
    current = cursor.fetchone()[0]

    new_value = 0 if current == 1 else 1

    cursor.execute("UPDATE routines SET completed = ? WHERE id = ?", (new_value, id))
    conn.commit()
    conn.close()

    return redirect("/routine")

@app.route("/edit_routine/<int:id>", methods=["GET", "POST"])
def edit_routine(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        frequency = request.form["frequency"]

        cursor.execute(
            "UPDATE routines SET name = ?, frequency = ? WHERE id = ?",
            (name, frequency, id)
        )
        conn.commit()
        conn.close()
        return redirect("/routine")

    cursor.execute("SELECT * FROM routines WHERE id = ?", (id,))
    routine = cursor.fetchone()
    conn.close()

    return render_template("edit_routine.html", routine=routine)

@app.route("/goals", methods=["GET", "POST"])
def goals():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        progress = request.form["progress"]

        progress = int(progress)
        status = "Completato" if progress == 100 else "In corso"
        
        cursor.execute("""
            INSERT INTO goals (title, category, progress, status)
            VALUES (?, ?, ?, ?)
        """, (title, category, progress, status))

        conn.commit()

    cursor.execute("""
    SELECT * FROM goals
    ORDER BY 
        CASE WHEN status = 'In corso' THEN 0 ELSE 1 END,
        progress DESC
    """)
    goals = cursor.fetchall()

    conn.close()

    return render_template("goals.html", goals=goals)

@app.route("/delete_goal/<int:id>")
def delete_goal(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM goals WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/goals")

@app.route("/edit_goal/<int:id>", methods=["GET", "POST"])
def edit_goal(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        category = request.form["category"]
        progress = int(request.form["progress"])

        status = "Completato" if progress == 100 else "In corso"

        cursor.execute("""
            UPDATE goals
            SET title = ?, category = ?, progress = ?, status = ?
            WHERE id = ?
        """, (title, category, progress, status, id))

        conn.commit()
        conn.close()
        return redirect("/goals")

    cursor.execute("SELECT * FROM goals WHERE id = ?", (id,))
    goal = cursor.fetchone()
    conn.close()

    return render_template("edit_goal.html", goal=goal)

@app.route("/phase", methods=["GET", "POST"])
def phase():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        status = "In corso"

        cursor.execute("INSERT INTO phase (name, description, status) VALUES (?, ?, ?)", (name, description, status))
        conn.commit()

    cursor.execute("SELECT * FROM phase ORDER BY start_date DESC")
    phases = cursor.fetchall()

    cursor.execute("SELECT * FROM phase WHERE status='In corso' ORDER BY start_date DESC LIMIT 1")
    current_phase = cursor.fetchone()

    conn.close()

    return render_template("phase.html", phases=phases, current_phase=current_phase)

@app.route("/delete_phase/<int:id>")
def delete_phase(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phase WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/phase")

@app.route("/edit_phase/<int:id>", methods=["GET", "POST"])
def edit_phase(id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE phase
            SET name = ?, description = ?, status = ?
            WHERE id = ?
        """, (name, description, status, id))
        conn.commit()
        conn.close()
        return redirect("/phase")

    cursor.execute("SELECT * FROM phase WHERE id = ?", (id,))
    phase = cursor.fetchone()
    conn.close()
    return render_template("edit_phase.html", phase=phase)

@app.route("/progress", methods=["GET", "POST"])
def progress():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        value = int(request.form["value"])
        cursor.execute("INSERT INTO progress (value) VALUES (?)", (value,))
        conn.commit()

    cursor.execute("SELECT value FROM progress ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    days = [row[0] for row in rows]

    # 👁 VIEWPORT ULTIMI 60 GIORNI
    MAX_VISIBLE_DAYS = 60
    if len(days) > MAX_VISIBLE_DAYS:
        days = days[-MAX_VISIBLE_DAYS:]

    # 📈 CALCOLO CUMULATIVA
    cumulative = []
    total = 0
    for d in days:
        total += d
        cumulative.append(total)

    # 📊 MEDIA MOBILE
    moving_average = []
    window = 5

    for i in range(len(cumulative)):
        start = max(0, i - window + 1)
        window_slice = cumulative[start:i+1]
        moving_average.append(sum(window_slice) / len(window_slice))

    # 🚨 ALERT SPIRALI
    alert = None

    if len(days) >= 2:
        if days[-1] == -1 and days[-2] == -1:
            alert = "⚠ Due peggioramenti consecutivi."

    if len(days) >= 3:
        if days[-1] == 0 and days[-2] == 0 and days[-3] == 0:
            alert = "⚠ Tre mantenimenti consecutivi. Attenzione alla stagnazione."

    x_values = list(range(len(days)))

    return render_template(
        "progress.html",
        x_values=x_values,
        cumulative=cumulative,
        deltas=days,
        total_days=len(days),
        moving_average=moving_average,
        alert=alert
    )

@app.route("/delete_last_point")
def delete_last_point():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM progress WHERE id = (SELECT MAX(id) FROM progress)")
    conn.commit()
    conn.close()
    return redirect("/progress")

@app.route("/reset_progress")
def reset_progress():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM progress")
    conn.commit()
    conn.close()
    return redirect("/progress")

@app.route("/save_progress")
def save_progress():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM progress ORDER BY id ASC")
    rows = cursor.fetchall()
    days = [row[0] for row in rows]

    cursor.execute(
        "INSERT INTO progress_history (data) VALUES (?)",
        (json.dumps(days),)
    )

    cursor.execute("DELETE FROM progress")
    conn.commit()
    conn.close()

    return redirect("/progress")

@app.route("/progress_history")
def progress_history():
    if not session.get("logged_in"):
        return redirect("/login")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM progress_history ORDER BY id DESC")
    history = cursor.fetchall()
    conn.close()

    return render_template("progress_history.html", history=history)

if __name__ == "__main__":
    app.run(debug=True)