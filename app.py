import os
from flask import Flask, session, render_template
from models import db, User
from routes.auth import auth
from routes.expense import expense
from routes.budget import budget
from routes.export import export
from routes.profile import profile
from routes.category import category


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kakeibo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

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


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)

