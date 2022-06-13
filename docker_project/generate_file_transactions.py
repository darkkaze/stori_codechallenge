import argparse
import csv
import random
import uuid
from datetime import date

from faker import Faker

fake = Faker()


def main(accounts_n: int, operations_n: int):
    accounts = gen_accounts(accounts_n)
    to_csv = []
    for account in accounts:
        operations = gen_operations(operations_n)
        for operation in operations:
            to_csv.append(dict(**account, **operation))
    to_csv = sorted(to_csv, key=lambda _: _["transaction_ts"])
    with open("transactions_test.csv", "w") as output:
        writer = csv.DictWriter(output, fieldnames=to_csv[0].keys())
        writer.writeheader()
        writer.writerows(to_csv)
        print("(output: transactions_test.csv) done :D")


def gen_accounts(n: int):
    accounts = []
    for x in range(n):
        accounts.append(
            {
                "account_number": fake.credit_card_number(),
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "dob": fake.date_between(date(1960, 1, 1), date(2004, 12, 31)),
                "email": fake.email(),
                "type": random.choice(["credit", "debit"]),
            }
        )
    return accounts


def gen_operations(n: int):
    operations = []
    for x in range(n):
        operations.append(
            {
                "operation_id": str(uuid.uuid4()),
                "transaction_ts": fake.date_time_between(
                    date(2021, 1, 1), date(2021, 12, 31)
                ),
                "transaction": round(random.uniform(-10000, 10000), 2),
            }
        )
    return operations


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--accounts_n",
        default=10,
        type=int,
        help="number of accounts the file will have",
    )
    parser.add_argument(
        "--operations_n",
        default=100,
        type=int,
        help="number of operations that an account have",
    )
    args = parser.parse_args()
    main(args.accounts_n, args.operations_n)
