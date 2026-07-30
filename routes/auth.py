from utils import login_required
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Category

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            return redirect(url_for("expense.index"))
        else:
            flash("ユーザー名またはパスワードが違います。", "danger")

    return render_template("login.html")


@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username:
            return render_template(
                "register.html",
                error="ユーザー名を入力してください。"
            )

        if len(password) < 8:
            return render_template(
                "register.html",
                error="パスワードは8文字以上で入力してください。"
            )

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template(
                "register.html",
                error="このユーザー名は既に使われています"
            )

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        initial_categories = [
            ("食費", "🍚", "支出"),
            ("交通費", "🚃", "支出"),
            ("日用品", "🛒", "支出"),
            ("趣味", "🎮", "支出"),
            ("給与", "💰", "収入"),
            ("副収入", "💵", "収入"),
        ]

        for name, icon, category_type in initial_categories:
            category = Category(
                user_id=user.id,
                name=name,
                icon=icon,
                type=category_type
            )
            db.session.add(category)

        db.session.commit()

        session["user_id"] = user.id

        return redirect(url_for("expense.index"))

    return render_template("register.html")


@auth.route("/logout")
def logout():

    session.pop("user_id", None)

    return redirect(url_for("auth.login"))

