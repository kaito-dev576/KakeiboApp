# 家計簿アプリ

Flaskで作成した、ユーザーごとに収入・支出・月間予算を管理できるWebアプリです。

## 主な機能

- ユーザー登録・ログイン・ログアウト
- パスワードのハッシュ化・変更
- 収入・支出の登録、編集、削除
- 年月・カテゴリー検索、並び替え、ページネーション
- 月ごとの予算管理と使用率表示
- カテゴリーの追加、編集、削除
- カテゴリー別円グラフ・月別収支グラフ
- CSVバックアップ・復元
- ダークモード
- 404・500エラー画面
- ユーザー別のデータ分離とCSRF対策
- 今月と先月の支出比較
- 主要機能を確認する自動テスト

## 使用技術

- Python 3.13
- Flask 3.1
- Flask-SQLAlchemy
- SQLite（ローカル開発）
- PostgreSQL（Render）
- Bootstrap 5
- Chart.js
- Gunicorn

## プロジェクト構成

```text
KakeiboApp/
├── app.py              # Flaskアプリの設定・起動
├── models.py           # データベースモデル
├── utils.py            # ログイン確認などの共通処理
├── routes/             # 機能ごとのBlueprint
├── static/css/         # アプリ共通のデザイン
├── templates/          # HTMLテンプレート
├── tests/              # 自動テスト
├── render.yaml         # Renderの公開設定
├── requirements.txt
├── main.py             # 開発初期に作成したCLI版
└── kakeibo.json        # CLI版のサンプルデータ
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

ブラウザで `http://127.0.0.1:5000` を開きます。

## 自動テスト

次のコマンドで、認証・取引操作・ユーザー間のデータ保護・予算計算・月比較・CSVを確認できます。

```powershell
python -m unittest discover -s tests -v
```

## 工夫した点

- すべての取引・予算・カテゴリーをユーザー単位で分離
- POST操作にCSRF対策を適用
- 検索結果の集計と、今月の予算・前月比較を分離して誤集計を防止
- CSVバックアップと復元により、利用者自身でデータを持ち出せる設計
- スマートフォンでも情報を確認しやすいレスポンシブデザイン

## Renderへの公開

リポジトリ直下の `render.yaml` から、WebサービスとPostgreSQLを作成できます。Render上では`SECRET_KEY`が自動生成されます。

無料のRender PostgreSQLは作成から30日で期限切れになるため、この構成はポートフォリオのデモ用途を想定しています。

## CSVバックアップについて

CSV出力から取引データをダウンロードできます。CSV復元ではバックアップCSVを読み込んで取引を復元できます。同じCSVを複数回読み込むと取引も重複するため注意してください。
