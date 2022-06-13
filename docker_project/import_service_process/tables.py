from sqlalchemy import table

table_account_sql = """
    CREATE TABLE IF NOT EXISTS accounts (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        account_number varchar(16) UNIQUE NOT NULL,
        type varchar(10) NOT NULL,
        first_name varchar(45) NOT NULL,
        last_name varchar(45) NOT NULL,
        dob date NOT NULL,
        email varchar(255) NOT NULL
    );
"""

table_transactions_sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        account_id uuid NOT NULL,
        transaction_ts timestamp  NOT NULL,
        transaction  float NOT NULL,
        CONSTRAINT fk_account
            FOREIGN KEY(account_id) 
            REFERENCES accounts(id)
    )
"""
