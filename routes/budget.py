from datetime import date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from models import db, Budget
from utils import login_required


budget = Blueprint("budget", __name__)


@budget.route("/budget", methods=["GET", "POST"])
@login_required
def budget_page():

    today = date.today()

    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)

    if request.method == "POST":

        try:
            year = int(request.form.get("year", ""))
            month = int(request.form.get("month", ""))
            budget_amount = int(request.form.get("budget", ""))
        except (TypeError, ValueError):
            flash("年・月・予算は数字で入力してください。", "danger")
            return redirect(url_for("budget.budget_page"))

        if not 2000 <= year <= 2100:
            flash("年は2000〜2100で入力してください。", "danger")
            return redirect(url_for("budget.budget_page"))

        if not 1 <= month <= 12:
            flash("月は1〜12で入力してください。", "danger")
            return redirect(url_for("budget.budget_page"))

        if budget_amount <= 0:
            flash("予算は1円以上で入力してください。", "danger")
            return redirect(url_for("budget.budget_page"))

        # 同じ年月の予算がある場合は新規作成せず、金額だけ更新する
        existing_budget = Budget.query.filter_by(
            user_id=session["user_id"],
            year=year,
            month=month
        ).first()

        if existing_budget:
            existing_budget.budget = budget_amount
            message = "予算を更新しました。"
        else:
            new_budget = Budget(
                user_id=session["user_id"],
                year=year,
                month=month,
                budget=budget_amount
            )
            db.session.add(new_budget)
            message = "予算を設定しました。"

        db.session.commit()

        flash(message, "success")

        # 保存後は、予算が反映されたホーム画面へ戻す
        return redirect(url_for("expense.index"))

    current_budget = Budget.query.filter_by(
        user_id=session["user_id"],
        year=year,
        month=month
    ).first()

    return render_template(
        "budget.html",
        year=year,
        month=month,
        budget=current_budget
    )
