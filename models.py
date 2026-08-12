from datetime import date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Expense(db.Model):
    id = db.Column(db.Integer,primary_key = True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    type = db.Column(db.String(10), nullable=False)  
    price = db.Column(db.Integer,nullable = False)
    category = db.Column(db.String(50), nullable = False)
    memo =  db.Column(db.String(200))
    
    date = db.Column(
        db.Date,
        nullable = False,
        default = date.today
    )
    


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    name = db.Column(
        db.String(50),
        nullable=False
    )

    icon = db.Column(
        db.String(10),
        nullable=False,
        default="📁"
    )

    type = db.Column(
        db.String(10),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "name",
            name="unique_user_category"
        ),
    )

    


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    budget = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "year",
            "month",
            name="unique_user_month_budget",
        ),
    )


