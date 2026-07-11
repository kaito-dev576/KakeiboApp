import json

class Transaction:
    def __init__(self,type,category,amount,date):
        self.type = type
        self.category = category
        self.amount = amount
        self.date = date

    def __str__(self):
        return f"{self.date} | {self.type} | {self.category} | {self.amount}円"

    def to_dict(self):
        return{
            'type':self.type,
            'category':self.category,
            'amount':self.amount,
            'date':self.date
        }

    @classmethod
    def from_dict(cls,data):
        return cls(
            data['type'],
            data['category'],
            data['amount'],
            data['date']
        )



def save_transactions():
    data = []

    for transaction in transactions:
        data.append(transaction.to_dict())

    with open('kakeibo.json','w',encoding = 'utf-8') as file:
        json.dump(data,file,ensure_ascii = False,indent = 4)


def load_transactions():
    global transactions

    try:
        with open('kakeibo.json','r',encoding = 'utf-8') as file:
            data = json.load(file)

        transactions = []

        for item in data:
            transactions.append(Transaction.from_dict(item))

    except FileNotFoundError:
        transactions = []

transactions = []

load_transactions()


def show_transactions():
    if not transactions:
        print('収支データがありません。')
    else:
        print('=== 収支一覧 ===')
        for index, transaction in enumerate(transactions, start=1):
            print(f"{index}. {transaction}")


def add_transaction():
    while True:
        type = input("種類（収入/支出）: ")
 
        if type in ["収入", "支出"]:
            break

        print("「収入」または「支出」を入力してください。")


    category = input('内容:')

    while True:
        try:
            amount = int(input("金額: "))

            if amount > 0:
                break

            print("0より大きい金額を入力してください。")

        except ValueError:
            print("数字を入力してください。")

    date = input('日付(2026-07-10):')

    transaction = Transaction(type,category,amount,date)
    transactions.append(transaction)
    save_transactions()


    print("収支を追加しました！")


def show_summary():
    income_total = 0
    expense_total = 0

    for transaction in transactions:
        if transaction.type == '収入':
            income_total += transaction.amount
        elif transaction.type == '支出':
            expense_total += transaction.amount

    balance = income_total - expense_total

    print('=== 合計表示 ===')
    print(f'収入合計:{income_total}円')
    print(f'支出合計:{expense_total}円')
    print(f'残高:{balance}円')


def edit_transaction():
    if not transactions:
        print('収支データがありません。')
    else:
        show_transactions()

        number = int(input('編集する番号を入力してください:'))

        if 1 <= number <= len(transactions):
            transaction = transactions[number - 1]

            transaction.type = input(f"種類(現在:{transaction.type}):")
            transaction.category = input(f"内容(現在:{transaction.category}):")
            transaction.amount = int(input(f"金額(現在:{transaction.amount}):"))
            transaction.date = input(f"日付(現在:{transaction.date}):")

            save_transactions()

            print('収支を更新しました。')

        else:
            print('正しい番号を入力してください。')


def delete_transaction():
    if not transactions:
        print('収支データがありません。')
    else:
        show_transactions()

        number = int(input('削除する番号を入力してください:'))

        if 1 <= number <= len(transactions):
            deleted = transactions.pop(number - 1)
            save_transactions()
            print(f"{deleted.category}を削除しました。")
        else:
            print('正しい番号を入力してください。')





while True:
    print('\n==== 家計簿アプリ====')
    print('1. 収支を追加')
    print('2. 一覧表示')
    print('3. 合計表示')
    print('4. 収支を編集')
    print('5. 収支を削除')
    print('6. 終了')

    choice = input('番号を入力してください:')

    if choice == '1':
        add_transaction()
        

    elif choice =='2':
        show_transactions()


    elif choice == '3':
        show_summary()


    elif choice == '4':
        edit_transaction()
    

    elif choice == '5':
        delete_transaction()


    elif choice =='6':
        print('終了します')
        break

    else:
        print('1～6を入力してください。')