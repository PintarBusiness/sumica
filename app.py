from flask import Flask, render_template

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

@app.route("/rezervacija")
def rezervacija():
    return render_template("rezervacija.html")


if __name__ == "__main__":
    app.run(debug=True)