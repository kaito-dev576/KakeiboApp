from flask import Blueprint, render_template, request, redirect, url_for, session
from models import db, Budget
from utils import login_required

budget = Blueprint("budget", __name__)

@budget.route("/budget",methods=["GET","POST"])
@login_required
def budget_page():

    


    if request.method == "POST":

        year = int(request.form["year"])
        month = int(request.form["month"])
        budget = int(request.form["budget"])

        

        existing_budget = Budget.query.filter_by(
            user_id=session["user_id"],
            year=year,
            month=month
        ).first()

        if existing_budget:
            existing_budget.budget = budget
        else:
            new_budget = Budget(
                user_id=session["user_id"],
                year=year,
                month=month,
                budget=budget
            )

            db.session.add(new_budget)
        db.session.commit()

        return redirect(url_for("expense.index"))

    return render_template("budget.html")



