import os
import hmac
import secrets

from flask import Flask, abort, render_template, request, session
from models import db, User
from routes.auth import auth
from routes.expense import expense
from routes.budget import budget
from routes.export import export
from routes.profile import profile
from routes.category import category


app = Flask(__name__)
secret_key = os.environ.get("SECRET_KEY")

if not secret_key and os.environ.get("RENDER"):
    raise RuntimeError("SECRET_KEY must be set in production.")

app.config["SECRET_KEY"] = secret_key or "development-only-secret-key"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = bool(os.environ.get("RENDER"))

database_url = os.environ.get("DATABASE_URL", "sqlite:///kakeibo.db")

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

db.init_app(app)


def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)

    return session["_csrf_token"]


app.jinja_env.globals["csrf_token"] = generate_csrf_token


@app.before_request
def protect_from_csrf():
    if request.method != "POST":
        return None

    expected_token = session.get("_csrf_token", "")
    submitted_token = request.form.get("csrf_token", "")

    if not expected_token or not hmac.compare_digest(
        expected_token,
        submitted_token,
    ):
        abort(400)

    return None


@app.route("/health")
def health_check():
    return {"status": "ok"}

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500

@app.context_processor
def inject_user():

    if "user_id" in session:
        user = User.query.get(session["user_id"])
        return dict(user=user)

    return dict(user=None)

app.register_blueprint(auth)
app.register_blueprint(expense)
app.register_blueprint(export)   
app.register_blueprint(budget)
app.register_blueprint(profile, url_prefix="/profile")
app.register_blueprint(category)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")

