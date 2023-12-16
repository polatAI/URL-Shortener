import random
import string
from flask import Flask, render_template, redirect, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
import mysql.connector
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config["SECRET_KEY"] = "your_secret_key"
csrf.init_app(app)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "urlshortener"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

# Database connection setup
conn = mysql.connector.connect(
    host=app.config["MYSQL_HOST"],
    user=app.config["MYSQL_USER"],
    password=app.config["MYSQL_PASSWORD"],
    database=app.config["MYSQL_DB"]
)

cursor = conn.cursor()

class URLShortenForm(FlaskForm):
    long_url = StringField('Long URL', validators=[DataRequired()])

def generate_short_url(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def is_short_url_taken(short_url):
    cursor.execute("SELECT * FROM url WHERE short_url = %s", (short_url,))
    return cursor.fetchone() is not None

def generate_unique_short_url():
    while True:
        short_url = generate_short_url()
        if not is_short_url_taken(short_url):
            return short_url

@app.route("/", methods=["GET", "POST"])
def index():
    form = URLShortenForm()

    if request.method == "POST" and form.validate_on_submit():
        long_url = form.long_url.data
        short_url = generate_unique_short_url()

        cursor.execute("INSERT INTO url (long_url, short_url) VALUES (%s, %s)", (long_url, short_url))
        conn.commit()

        return render_template("result.html", short_url=f"{request.url_root}{short_url}")

    return render_template("index.html", form=form)

@app.route("/<short_url>")
def redirect_url(short_url):
    cursor.execute("SELECT * FROM url WHERE short_url = %s", (short_url,))
    url_entry = cursor.fetchone()

    if url_entry:
        return redirect(url_entry[1])  # 'long_url' sütunu 1. indekste
    else:
        return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
