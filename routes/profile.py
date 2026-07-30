from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from utils import login_required
from models import db ,User
from werkzeug.security import generate_password_hash, check_password_hash


profile = Blueprint(
    "profile",
    __name__
)


@profile.route("/", methods=["GET", "POST"])
@login_required
def profile_page():

    user = User.query.get(session["user_id"])

    if request.method == "POST":

        username = request.form.get("username")
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")


        # ユーザー名変更
        if username is not None:

            if username.strip() == "":
                return render_template(
                    "profile.html",
                    user=user,
                    error="ユーザー名を入力してください"
                )

            existing_user = User.query.filter_by(
                username=username
            ).first()

            if existing_user and existing_user.id != user.id:
                return render_template(
                    "profile.html",
                    user=user,
                    error="そのユーザー名はすでに使われています"
                )

            user.username = username


        if current_password or new_password or confirm_password:

            if not all([
                current_password,
                new_password,
                confirm_password
            ]):
                return render_template(
                    "profile.html",
                    user=user,
                    error="パスワード変更の項目をすべて入力してください。"
                )

            if not check_password_hash(user.password, current_password):
                return render_template(
                    "profile.html",
                    user=user,
                    error="現在のパスワードが違います。"
                )

            if len(new_password) < 8:
                return render_template(
                    "profile.html",
                    user=user,
                    error="新しいパスワードは8文字以上で入力してください。"
                )

            if new_password != confirm_password:
                return render_template(
                    "profile.html",
                    user=user,
                    error="新しいパスワードが一致しません。"
                )

            user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("プロフィールを変更しました", "success")

        return redirect(
            url_for("profile.profile_page")
        )

    return render_template(
        "profile.html",
        user=user
    )