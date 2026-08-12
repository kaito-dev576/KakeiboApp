from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from utils import login_required
from models import db, Category, Expense

category = Blueprint(
    "category",
    __name__,
    url_prefix="/category"
)

@category.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "POST":

        name = request.form["name"].strip()
        icon = request.form["icon"]
        category_type = request.form["type"]

        if name == "":
            flash("カテゴリー名を入力してください", "danger")
            return redirect(url_for("category.index"))

        # 同じ利用者が同名カテゴリーを複数作らないようにする
        existing = Category.query.filter_by(
            user_id=session["user_id"],
            name=name
        ).first()

        if existing:
            flash("そのカテゴリーはすでに存在します", "danger")
            return redirect(url_for("category.index"))

        category = Category(
            user_id=session["user_id"],
            name=name,
            icon=icon,
            type=category_type
        )

        db.session.add(category)
        db.session.commit()

        flash("カテゴリーを追加しました", "success")

        return redirect(url_for("category.index"))

    categories = (
        Category.query
        .filter_by(user_id=session["user_id"])
        .order_by(Category.name)
        .all()
    )

    return render_template(
        "category.html",
        categories=categories
    )

@category.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete(id):

    category_item = Category.query.get_or_404(id)

    if category_item.user_id != session["user_id"]:
        flash("操作できません", "danger")
        return redirect(url_for("category.index"))

    # 過去の取引で使われているカテゴリーは削除できないようにする
    transaction_count = Expense.query.filter_by(
        user_id=session["user_id"],
        category=category_item.name
    ).count()

    if transaction_count > 0:
        flash(
            f"「{category_item.name}」は{transaction_count}件の取引で使われているため削除できません。",
            "danger"
        )
        return redirect(url_for("category.index"))

    db.session.delete(category_item)
    db.session.commit()

    flash("カテゴリーを削除しました", "success")
    return redirect(url_for("category.index"))

@category.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit(id):

    category_item = Category.query.get_or_404(id)

    if category_item.user_id != session["user_id"]:
        flash("編集できません", "danger")
        return redirect(url_for("category.index"))

    if request.method == "POST":

        name = request.form["name"].strip()
        icon = request.form["icon"]
        category_type = request.form["type"]


        if name.strip() == "":
            flash("カテゴリー名を入力してください", "danger")
            return redirect(url_for("category.edit", id=id))

        existing = Category.query.filter(
            Category.user_id == session["user_id"],
            Category.name == name,
            Category.id != category_item.id
        ).first()

        if existing:
            flash("そのカテゴリーはすでに存在します", "danger")
            return redirect(url_for("category.edit", id=id))

        # 使用済みカテゴリーを支出から収入へ変更すると過去の取引と矛盾するため防ぐ
        if category_type != category_item.type:
            transaction_count = Expense.query.filter_by(
                user_id=session["user_id"],
                category=category_item.name
            ).count()

            if transaction_count > 0:
                flash(
                    "取引で使用しているカテゴリーは、支出・収入の種類を変更できません。",
                    "danger"
                )
                return redirect(url_for("category.edit", id=id))

        old_name = category_item.name
        Expense.query.filter_by(
            user_id=session["user_id"],
            category=old_name,
        ).update({Expense.category: name}, synchronize_session=False)

        category_item.name = name
        category_item.icon = icon
        category_item.type = category_type
        

        db.session.commit()

        flash("カテゴリーを変更しました", "success")

        return redirect(url_for("category.index"))

    return render_template(
        "edit_category.html",
        category=category_item
    )
