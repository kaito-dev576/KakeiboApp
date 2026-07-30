from utils import login_required
from datetime import date, timedelta, datetime
from sqlalchemy import func, extract
from models import db, Expense, User, Budget, Category
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

expense = Blueprint("expense", __name__)

@expense.route('/add', methods=['GET', 'POST'])
@login_required
def add():

    if request.method == "POST":

        categories = (
            Category.query
            .filter_by(user_id=session["user_id"])
            .order_by(Category.name)
            .all()
        )

        price_text = request.form["price"]
        category = request.form["category"]
        transaction_type = request.form["type"]
        memo = request.form["memo"]
        date_text = request.form.get("date")

        try:
            price = int(price_text)

        except ValueError:
            return render_template(
                "add.html",
                error="金額は数字で入力してください",
                price=price_text,
                category=category,
                transaction_type=transaction_type,
                categories=categories,
                today=date.today().strftime("%Y-%m-%d")
            )

        if price <= 0:
            return render_template(
                "add.html",
                error="金額は1円以上で入力してください",
                price=price_text,
                category=category,
                transaction_type=transaction_type,
                categories=categories,
                today=date.today().strftime("%Y-%m-%d")
            )

        if category.strip() == "":
            return render_template(
                "add.html",
                error="カテゴリーを選択してください",
                price=price_text,
                category=category,
                transaction_type=transaction_type,
                categories=categories,
                today=date.today().strftime("%Y-%m-%d")
            )


        selected_category = Category.query.filter_by(
            user_id=session["user_id"],
            name=category,
            type=transaction_type
        ).first()

        if not selected_category:
            flash("選択したカテゴリーは使用できません。", "danger")
            return redirect(url_for("expense.add"))

        expense_date = (
            date.fromisoformat(date_text)
            if date_text
            else date.today()
        )

        expense = Expense(
            user_id=session["user_id"],
            type=transaction_type,
            price=price,
            category=category,
            memo=memo,
            date=expense_date
        )

        db.session.add(expense)
        db.session.commit()

        flash("登録しました", "success")

        return redirect(url_for("expense.index"))

    categories = (
        Category.query
        .filter_by(user_id=session["user_id"])
        .order_by(Category.name)
        .all()
    )

    return render_template(
        'add.html',
        today=date.today().strftime('%Y-%m-%d'),
        categories=Category.query.filter_by(
            user_id=session["user_id"]
        ).all()
    )


@expense.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    expense = Expense.query.get_or_404(id)

    if expense.user_id != session["user_id"]:
        flash("この取引は操作できません。", "danger")
        return redirect(url_for("expense.index"))

    if request.method == "POST":

        price_text = request.form["price"]

        try:
            price = int(price_text)
        except ValueError:
            flash("金額は数字で入力してください。", "danger")
            return redirect(url_for("expense.edit", id=id))

        if price <= 0:
            flash("金額は1円以上で入力してください。", "danger")
            return redirect(url_for("expense.edit", id=id))

        selected_category = Category.query.filter_by(
            user_id=session["user_id"],
            name=request.form["category"],
            type=request.form["type"]
        ).first()

        if not selected_category:
            flash("選択したカテゴリーは使用できません。", "danger")
            return redirect(url_for("expense.edit", id=id))
    

        expense.price = price
        expense.category = request.form["category"]
        expense.memo = request.form["memo"]
        expense.type = request.form["type"]

        date_text = request.form.get("date")

        if date_text:
            expense.date = date.fromisoformat(date_text)

        db.session.commit()

        flash("取引を更新しました。", "success")

        return redirect(url_for("expense.index"))

    categories = (
        Category.query
        .filter_by(user_id=session["user_id"])
        .order_by(Category.name)
        .all()
    )

    return render_template(
        "edit.html",
        expense=expense,
        categories=categories
    )


@expense.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):

    expense = Expense.query.get_or_404(id)

    if expense.user_id != session["user_id"]:
        flash("この取引は操作できません。", "danger")
        return redirect(url_for("expense.index"))

    db.session.delete(expense)
    db.session.commit()

    flash("取引を削除しました。", "success")

    return redirect(url_for("expense.index"))


@expense.route("/")
@login_required
def index():

    user = User.query.get(session["user_id"])

    today = date.today()
    last_month = today.replace(day=1) - timedelta(days=1)
    budget = Budget.query.filter_by(
        user_id=session["user_id"],
        year=today.year,
        month=today.month
    ).first()

    category = request.args.get("category")
    transaction_type = request.args.get("type")
    query = Expense.query.filter_by(user_id=session["user_id"])
    
    

    month = request.args.get("month")
    sort = request.args.get("sort", "new")
    page = request.args.get("page", 1, type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    selected_year = request.args.get(
        "year",
        date.today().year,
        type=int
    )

    query = query.filter(
            extract("year", Expense.date) == selected_year
        )

    if month:
        year, month_num = month.split("-")

        query = query.filter(
            extract("year", Expense.date) == int(year),
            extract("month", Expense.date) == int(month_num)
        )

    if start_date:
        query = query.filter(
            Expense.date >= datetime.strptime(
                start_date,
                "%Y-%m-%d"
            ).date()
        )


    if end_date:
        query = query.filter(
            Expense.date <= datetime.strptime(
                end_date,
                "%Y-%m-%d"
            ).date()
        )


    if category:
        query = query.filter(Expense.category.contains(category))

    if transaction_type:
        query = query.filter(
            Expense.type == transaction_type
        )

    if sort == "new":
        expenses = query.order_by(
            Expense.date.desc()
        ).paginate(page=page, per_page=10)

    elif sort == "old":
        expenses = query.order_by(
            Expense.date
        ).paginate(page=page, per_page=10)

    elif sort == "high":
        expenses = query.order_by(
            Expense.price.desc()
        ).paginate(page=page, per_page=10)

    elif sort == "low":
        expenses = query.order_by(
            Expense.price
        ).paginate(page=page, per_page=10)

    income_total =(
        query.filter(Expense.type =="収入")
        .with_entities(func.sum(Expense.price))
        .scalar() or 0       
    )

    expense_total = (
        query.filter(Expense.type == "支出")
        .with_entities(func.sum(Expense.price))
        .scalar() or 0
    )

    last_month_expense = (
        Expense.query.filter_by(user_id=session["user_id"], type="支出")
        .filter(
            extract("year", Expense.date) == last_month.year,
            extract("month", Expense.date) == last_month.month
        )
        .with_entities(func.sum(Expense.price))
        .scalar() or 0
    )

    if budget:
        remaining_budget = budget.budget - expense_total
    else:
        remaining_budget = 0

    if budget:
        budget_percentage = int(
            expense_total / budget.budget * 100
        )

        if budget_percentage > 100:
            budget_percentage = 100

    else:
        budget_percentage = 0

    if budget:
        over_budget = expense_total - budget.budget
    else:
        over_budget = 0
    

    count = query.count()


    total = (
        query.with_entities(func.sum(Expense.price)).scalar()
        or 0
    )

    if count > 0:
        average = total // count
    else:
        average = 0

    category_totals = (
        query.filter(Expense.type == "支出")
        .with_entities(
            Expense.category,
            func.sum(Expense.price).label("total")
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.price).desc())
        .all()
    )

    top_category = (
        query.filter(Expense.type == "支出")
        .with_entities(
            Expense.category,
            func.sum(Expense.price).label("total")
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.price).desc())
        .first()
    )

    recent_expenses = (
        query.filter(Expense.type == "支出")
        .order_by(Expense.date.desc())
        .limit(5)
        .all()
    )

    monthly_income = (
        query.filter(Expense.type == "収入")
        .with_entities(
            extract("month", Expense.date),
            func.sum(Expense.price)
        )
        .group_by(extract("month", Expense.date))
        .all()
    )

    monthly_expense = (
        query.filter(Expense.type == "支出")
        .with_entities(
            extract("month", Expense.date),
            func.sum(Expense.price)
        )
        .group_by(extract("month", Expense.date))
        .all()
    )



    balance = income_total - expense_total
    expense_difference = expense_total - last_month_expense

    if last_month_expense > 0:
        expense_difference_percent = (
            expense_difference / last_month_expense
        ) * 100
    else:
        expense_difference_percent = None

    return render_template(
        'index.html',
        expenses = expenses,
        total = total,
        count = count,
        average = average,
        category_totals = category_totals,
        income_total=income_total,
        expense_total=expense_total,
        balance=balance,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
        user=user,
        budget=budget,
        remaining_budget=remaining_budget,
        budget_percentage=budget_percentage,
        over_budget=over_budget,
        last_month_expense=last_month_expense,
        expense_difference = expense_difference,
        expense_difference_percent=expense_difference_percent,
        top_category=top_category,
        recent_expenses=recent_expenses,
        selected_year=selected_year,
    )





