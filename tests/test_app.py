import io
import os
import unittest
from datetime import date, timedelta

os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key"

from flask import template_rendered
from werkzeug.security import generate_password_hash

from app import app
from models import Budget, Category, Expense, User, db


class KakeiboAppTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.context = app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def post(self, url, data=None, **kwargs):
        with self.client.session_transaction() as session:
            session["_csrf_token"] = "test-csrf-token"
        form = dict(data or {})
        form["csrf_token"] = "test-csrf-token"
        return self.client.post(url, data=form, **kwargs)

    def register(self, username="tester"):
        return self.post(
            "/register",
            {"username": username, "password": "password123"},
            follow_redirects=True,
        )

    def get_home_context(self):
        recorded = []

        def record(sender, template, context, **extra):
            recorded.append(context)

        template_rendered.connect(record, app)
        try:
            self.client.get("/")
        finally:
            template_rendered.disconnect(record, app)
        return recorded[-1]

    def test_register_creates_user_and_default_categories(self):
        response = self.register("new-user")
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(User.query.filter_by(username="new-user").first())
        self.assertEqual(Category.query.count(), 6)

    def test_login_and_logout(self):
        db.session.add(User(username="tester", password=generate_password_hash("password123")))
        db.session.commit()
        response = self.post("/login", {"username": "tester", "password": "password123"}, follow_redirects=True)
        self.assertIn("家計のダッシュボード", response.get_data(as_text=True))
        response = self.post("/logout", follow_redirects=True)
        self.assertIn("おかえりなさい", response.get_data(as_text=True))

    def test_transaction_crud(self):
        self.register()
        response = self.post("/add", {
            "price": "1200", "date": "2026-08-12", "type": "支出",
            "category": "食費", "memo": "ランチ",
        }, follow_redirects=True)
        self.assertIn("登録しました", response.get_data(as_text=True))
        item = Expense.query.one()
        response = self.post(f"/edit/{item.id}", {
            "price": "1500", "date": "2026-08-12", "type": "支出",
            "category": "食費", "memo": "夕食",
        }, follow_redirects=True)
        self.assertIn("取引を更新しました", response.get_data(as_text=True))
        self.assertEqual(db.session.get(Expense, item.id).price, 1500)
        self.post(f"/delete/{item.id}", follow_redirects=True)
        self.assertEqual(Expense.query.count(), 0)

    def test_user_cannot_edit_another_users_transaction(self):
        self.register()
        other = User(username="other", password=generate_password_hash("password123"))
        db.session.add(other)
        db.session.flush()
        item = Expense(user_id=other.id, type="支出", price=500, category="食費", date=date.today())
        db.session.add(item)
        db.session.commit()
        response = self.client.get(f"/edit/{item.id}")
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(db.session.get(Expense, item.id))

    def test_budget_is_saved_and_calculated(self):
        self.register()
        today = date.today()
        user = User.query.filter_by(username="tester").one()
        db.session.add(Expense(user_id=user.id, type="支出", price=3000, category="食費", date=today))
        db.session.commit()
        self.post("/budget", {"year": str(today.year), "month": str(today.month), "budget": "10000"})
        context = self.get_home_context()
        self.assertEqual(Budget.query.one().budget, 10000)
        self.assertEqual(context["remaining_budget"], 7000)
        self.assertEqual(context["budget_percentage"], 30)

    def test_month_comparison_uses_current_month(self):
        self.register()
        today = date.today()
        previous_month_end = today.replace(day=1) - timedelta(days=1)
        user = User.query.filter_by(username="tester").one()
        db.session.add_all([
            Expense(user_id=user.id, type="支出", price=4000, category="食費", date=today),
            Expense(user_id=user.id, type="支出", price=2500, category="食費", date=previous_month_end),
            Expense(user_id=user.id, type="支出", price=99000, category="食費", date=date(today.year, 1, 1)),
        ])
        db.session.commit()
        context = self.get_home_context()
        self.assertEqual(context["current_month_expense"], 4000)
        self.assertEqual(context["last_month_expense"], 2500)
        self.assertEqual(context["expense_difference"], 1500)

    def test_csv_export_and_import(self):
        self.register()
        user = User.query.filter_by(username="tester").one()
        db.session.add(Expense(user_id=user.id, type="支出", price=800, category="食費", date=date(2026, 8, 12), memo="昼食"))
        db.session.commit()
        exported = self.client.get("/export")
        self.assertIn("食費", exported.get_data(as_text=True))
        csv_data = "日付,種類,カテゴリー,金額,メモ\n2026-08-13,収入,給与,200000,8月分\n"
        response = self.post("/import", {
            "file": (io.BytesIO(csv_data.encode("utf-8")), "backup.csv")
        }, content_type="multipart/form-data", follow_redirects=True)
        self.assertIn("1件を復元しました", response.get_data(as_text=True))
        self.assertEqual(Expense.query.count(), 2)


if __name__ == "__main__":
    unittest.main()
