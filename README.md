# 収支管理アプリ

Flaskで作成した、収入と支出をユーザーごとに管理できるWebアプリです。年間の収入・支出・残高と月別推移を一画面で確認でき、取引一覧だけをカテゴリー・種類・対象月・並び順で絞り込めます。

- 公開URL: https://kakeibo-app-ndf1.onrender.com/login
- GitHub: https://github.com/kaito-dev576/KakeiboApp

## デモアカウント

- ユーザー名: `portfolio-demo`
- パスワード: `Portfolio2026!`

共有アカウントのため、個人情報は入力しないでください。

## 画面

### PC表示

![PC版ダッシュボード](docs/screenshots/dashboard-pc.png)

### スマートフォン表示

![スマートフォン版ダッシュボード](docs/screenshots/dashboard-mobile.png)

## 主な機能

- ユーザー登録・ログイン・ログアウト
- パスワードのハッシュ化とアカウント設定
- 収入・支出の登録、編集、削除
- 収入合計・支出合計・残高の年間集計
- Chart.jsによる月別収支グラフ
- カテゴリー・種類・対象月による取引一覧の絞り込み
- 日付・金額による並び替えとページネーション
- ユーザーごとのデータ分離
- CSRF対策
- レスポンシブ対応
- 404・500エラー画面
- 自動テストとGitHub Actions

検索条件は取引一覧だけに適用されます。合計カードと月別グラフは選択年全体の値を維持するため、検索後も年間状況を見失わない設計です。

## 使用技術

- Python 3.13
- Flask 3.1
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- SQLite（ローカル）
- PostgreSQL（Render）
- Bootstrap 5
- Chart.js
- Gunicorn
- GitHub Actions

## プロジェクト構成

```text
KakeiboApp/
├── app.py                 # アプリ設定と起動
├── models.py              # データベースモデル
├── utils.py               # ログイン確認などの共通処理
├── routes/                # Blueprintで分割した画面処理
├── templates/             # HTMLテンプレート
├── static/                # CSS・favicon
├── tests/                 # 自動テスト
├── migrations/            # データベース変更履歴
├── docs/screenshots/      # README掲載画像
├── .github/workflows/     # GitHub Actions
├── render.yaml            # Render公開設定
└── requirements.txt
```

## ローカルでの起動方法

```powershell
git clone https://github.com/kaito-dev576/KakeiboApp.git
cd KakeiboApp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
python app.py
```

ブラウザで `http://127.0.0.1:5050` を開きます。

## 自動テスト

```powershell
python -m unittest discover -s tests -v
```

次の内容を自動確認しています。

- ユーザー登録と初期カテゴリー作成
- ログイン・ログアウト
- 取引の登録・編集・削除
- 追加画面と編集画面の入力項目
- 種類とカテゴリーの組み合わせ検証
- 他ユーザーの取引に対する編集・削除の拒否
- 検索条件が取引一覧だけに適用されること
- 月間比較と予算計算
- CSVバックアップ・復元

GitHubへ変更を送ると、GitHub Actionsでも同じテストが自動実行されます。

## 設計上の工夫

### 検索と年間集計の分離

取引一覧用の検索条件と、合計カード・月別グラフ用の年間集計を別のクエリにしました。カテゴリーや対象月で検索しても、年間全体の収支は変化しません。

### ユーザーごとのデータ保護

取引・カテゴリー・予算をユーザーIDに関連付けています。URLのIDを変更しても他ユーザーの取引を編集・削除できないよう、サーバー側でも所有者を確認します。

### 入力内容の一貫性

取引追加と編集で同じ項目・順番・デザインを使用しています。収入は「給与」、支出は「遊び」「自己投資」に限定し、不正な組み合わせはサーバー側でも拒否します。

### 安全な更新と公開

Flask-Migrateでデータベース構造の変更履歴を管理し、Renderでは公開前にマイグレーションを実行します。主要機能は自動テストで後退を防止しています。

## Renderへの公開

`render.yaml`にWebサービスとPostgreSQLの設定を記載しています。Renderでは`SECRET_KEY`を自動生成し、`/health`をヘルスチェックに使用します。

無料プランのデータベースには期限や制限があるため、公開デモの状態は定期的に確認してください。
