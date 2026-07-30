import csv
import io
from datetime import date, datetime

from flask import Blueprint, Response, session, request, redirect, url_for, flash, render_template
from models import db, Expense, Category
from utils import login_required

export = Blueprint("export", __name__)


@export.route("/export")
@login_required
def export_csv():

    expenses = (
        Expense.query
        .filter_by(user_id=session["user_id"])
        .order_by(Expense.date.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "日付",
        "種類",
        "カテゴリー",
        "金額",
        "メモ"
    ])

    for expense in expenses:
        writer.writerow([
            expense.date,
            expense.type,
            expense.category,
            expense.price,
            expense.memo
        ])

    response = Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8"
    )

    filename = f"kakeibo_backup_{date.today():%Y%m%d}.csv"

    response.headers["Content-Disposition"] = (
        f"attachment; filename={filename}"
    )

    return response


@export.route("/import", methods=["GET", "POST"])
@login_required
def import_csv():

    if request.method == "POST":
        file = request.files.get("file")

        if not file or file.filename == "":
            flash("CSVファイルを選択してください。", "danger")
            return redirect(url_for("export.import_csv"))

        if not file.filename.endswith(".csv"):
            flash("CSVファイルを選択してください。", "danger")
            return redirect(url_for("export.import_csv"))

        try:
            content = file.stream.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(content))
        except UnicodeDecodeError:
            flash("UTF-8形式のCSVファイルを選択してください。", "danger")
            return redirect(url_for("export.import_csv"))

        imported_count = 0
        skipped_count = 0

        for row in reader:
            try:
                expense_date = datetime.strptime(
                    row["日付"],
                    "%Y-%m-%d"
                ).date()

                transaction_type = row["種類"]
                category_name = row["カテゴリー"]
                price = int(row["金額"])
                memo = row.get("メモ", "")

                if (
                    transaction_type not in ["支出", "収入"]
                    or not category_name
                    or price <= 0
                ):
                    skipped_count += 1
                    continue

                category = Category.query.filter_by(
                    user_id=session["user_id"],
                    name=category_name
                ).first()

                if not category:
                    category = Category(
                        user_id=session["user_id"],
                        name=category_name,
                        icon="🏷️",
                        type=transaction_type
                    )
                    db.session.add(category)

                elif category.type != transaction_type:
                    skipped_count += 1
                    continue

                expense = Expense(
                    user_id=session["user_id"],
                    date=expense_date,
                    type=transaction_type,
                    category=category_name,
                    price=price,
                    memo=memo
                )

                db.session.add(expense)
                imported_count += 1

            except (KeyError, ValueError):
                skipped_count += 1

        db.session.commit()

        flash(
            f"{imported_count}件を復元しました。"
            f"読み込めなかったデータは{skipped_count}件です。",
            "success"
        )

        return redirect(url_for("expense.index"))

    return render_template("import.html")