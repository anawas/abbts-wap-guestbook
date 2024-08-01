from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_httpauth import HTTPBasicAuth

import dbconnection as db

app = Flask(__name__)
auth = HTTPBasicAuth()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", entries=db.get_entries())


@app.route("/admin", methods=["GET"])
@auth.login_required
def admin():
    return render_template("admin.html", entries=db.get_entries())


@app.route("/logout", methods=["GET"])
def logout():
    """
    Hier ist ein Workaround nötig:
    Wir wollen auf die Einstiegsseite zurück. Dazu könnten wir
    einen Redirect verwenden: return redirect("/"). Diese Funktion
    geht aber nur mit Statuscodes 3xx. Wir müssen aber den Code
    401 zurückgeben, um dem Browser anzugeben, dass er den Login 
    vergessen soll. Daher nutzen wir eine leere Seite, die den
    Redirect im Meta-Tag macht. Dann ruft der Browser die Seite auf.
    Siehe: https://developer.mozilla.org/en-US/docs/Web/HTTP/Redirections
    """
    return render_template("back.html"), 401


@auth.verify_password
def verify_password(username, password):
    username = db.is_user_admin(username, password)
    return username


@app.route("/delete/<user>", methods=["GET"])
@auth.login_required
def delete(user):
    db.delete_user(user)
    return redirect("/admin")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if request.method == "GET":
        return render_template("submit.html")
    # Lese den Wert des Eingabefelds mit name="username"
    username = request.form['username']
    if username == "":
        username = "anonymous"

    message = request.form['message']

    # Hier die Daten z.B. in eine DB speichern
    db.add_entry(username, message, datetime.now())
    return redirect("/")


if __name__ == "__main__":
    context = ('certificates/mydomain.crt', 'certificates/mydomain.key')
    app.run(host="0.0.0.0", port="8090", debug=True, ssl_context=context)
