from flask import Flask, render_template, request, g, jsonify, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from dotenv import load_dotenv
import os
from flask_mail import Mail, Message

# pip install -r requirements.txt

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

@app.route("/lokacija")
def lokacija():
    return render_template("lokacija.html")

@app.route("/pogoji")
def pogoji():
    return render_template("pogoji.html")

@app.route("/piskotki")
def piskotki():
    return render_template("piskotki.html")

@app.route("/varnost")
def varnost():
    return render_template("varnost.html")


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

#izbris rezervacij
@app.route("/izbrisi_rezervacijo/<int:id>", methods=["POST"])
@login_required
def izbrisi_rezervacijo(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM rezervacije WHERE id = ?", (id,))
    db.commit()
    flash("Rezervacija je bila uspešno izbrisana!", "success")
    return redirect(url_for("admin"))

# --- Rute ---
@app.route("/")
def index():
    return render_template("index.html")

#Tukaj je flask za admin, prijava, odjava

app.secret_key = "nekaj-zelo-tajnega"

login_manager = LoginManager(app)
login_manager.login_view = "prijava"

# --- Naloži .env ---
load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


# --- Model uporabnika ---
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# --- Uporabniki iz .env ---
uporabniki = {
    ADMIN_USERNAME: User(id=1, username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
}


@login_manager.user_loader
def load_user(user_id):
    for u in uporabniki.values():
        if str(u.id) == str(user_id):
            return u
    return None


# --- Unauthorized handler (nadomesti privzeto "Please log in") ---
@login_manager.unauthorized_handler
def unauthorized_callback():
    # Samo preusmeri na prijavo brez privzetega sporočila
    return redirect(url_for("prijava"))


# --- Prijava ---
@app.route("/prijava", methods=["GET", "POST"])
def prijava():
    napaka = None

    if request.method == "POST":
        uporabnisko_ime = request.form.get("username")
        geslo = request.form.get("password")

        user = uporabniki.get(uporabnisko_ime)

        if user and user.password == geslo:
            login_user(user)
            # odstranjen flash za uspešno prijavo
            return redirect(url_for("admin"))
        else:
            napaka = "Napačno uporabniško ime ali geslo!"

    return render_template("prijava.html", napaka=napaka)


# --- Odjava ---
@app.route("/odjava")
@login_required
def odjava():
    logout_user()
    # odstranjen flash za uspešno odjavo
    return redirect(url_for("index"))


# --- Admin ---
@app.route("/admin")
@login_required
def admin():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM rezervacije ORDER BY datum, ura")
    vse_rezervacije = cursor.fetchall()
    return render_template("admin.html", user=current_user, rezervacije=vse_rezervacije)


# --- konfiguracija maila ---
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # za Gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")   # tvoj email
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")   # geslo ali App Password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("EMAIL_USER")

mail = Mail(app)

@app.route("/kontakt", methods=["GET", "POST"])
def kontakt():
    if request.method == "POST":
        ime = request.form.get("ime")
        telefon = request.form.get("telefon")
        mail_uporabnika = request.form.get("mail")
        sporocilo = request.form.get("sporocilo")

        # sestavimo email
        msg = Message(
            subject=f"Kontaktno sporočilo od {ime}",
            recipients=[os.getenv("EMAIL_USER")],  # tvoj email
            body=f"Ime in priimek: {ime}\n"
                 f"Telefon: {telefon}\n"
                 f"E-mail: {mail_uporabnika}\n\n"
                 f"Sporočilo:\n{sporocilo}"
        )

        try:
            mail.send(msg)
            flash("Sporočilo je bilo uspešno poslano!", "success")
        except Exception as e:
            print(e)
            flash("Prišlo je do napake pri pošiljanju.", "danger")

        return redirect(url_for("kontakt"))

    return render_template("kontakt.html")



if __name__ == "__main__":
    init_db()
    app.run(debug=True)