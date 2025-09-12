from flask import Flask, render_template, request, g, jsonify
import sqlite3

app = Flask(__name__)

@app.route("/")
def domov():
    return render_template("index.html")

@app.route("/onas")
def onas():
    return render_template("onas.html")

@app.route("/ponudbe")
def ponudbe():
    return render_template("ponudbe.html")

@app.route("/galerija")
def galerija():
    return render_template("galerija.html")

@app.route("/kontakt")
def kontakt():
    return render_template("kontakt.html")

@app.route("/lokacija")
def lokacija():
    return render_template("lokacija.html")


#Tukaj je flask za rezervacijo
DATABASE = "rezervacije.db"


# --- Povezava z bazo ---
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


# --- Ustvari tabelo ---
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rezervacije (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dogodek TEXT NOT NULL,
                datum TEXT NOT NULL,
                ura TEXT NOT NULL,
                ime TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mail TEXT NOT NULL,
                osebe INTEGER NOT NULL,
                podrobnosti TEXT
            )
        """)
        db.commit()


# --- Glavna stran rezervacije ---
@app.route("/rezervacija", methods=["GET", "POST"])
def rezervacija():
    db = get_db()
    cursor = db.cursor()

    if request.method == "POST":
        data = request.form.to_dict()

        cursor.execute("""
            INSERT INTO rezervacije 
            (dogodek, datum, ura, ime, telefon, mail, osebe, podrobnosti)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("dogodek"),
            data.get("datum"),
            data.get("ura"),
            data.get("ime"),
            data.get("telefon"),
            data.get("mail"),
            data.get("osebe"),
            data.get("podrobnosti"),
        ))
        db.commit()

        return "<h2>Rezervacija uspešna!</h2><p>Vaš termin je shranjen.</p>"

    # Poberemo vse zasedene datume
    cursor.execute("SELECT datum FROM rezervacije")
    rezervirani = [row[0] for row in cursor.fetchall()]

    return render_template("rezervacija.html", rezervirani=rezervirani)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)