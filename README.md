# About this

Hello, I really enjoyed the test. but I ran into an ambiguous part that I hope does not affect.

> Question (i ask this to Fernando from RH):

> > because the document speaks of "debit and credit accounts" in the email report. That's means, a user can have more than one type of account/product

> Fernando Answer:

> > there can be more than one user but only one card per user.

the answer left me even more confused, but I continued with the hope that what is important is the proposed architecture and not a bit part of the final result.

## Docker compose solution

i mount the db, a kafka and 3 services that process different parts of the problem in a docker infrastructure.

i usually run `docker-compose up`  for start all containers, but other commands surely works.

after that you can move the `transactions_test.csv` to  `imports` folder.

### important

git can't track a empty folders, so plz  add  `imports/`,  `processed/`,  `reports/`  inside  `docker_project/` folder
(alternatively they can change the docker-compose.yml to point to new directories.)

### file generator

i add a script for generate transactions files.   I didn't get many instructions on this file, so the amounts are very random and might not make sense like real data would.

`python generate_file_transactions.py accounts_n=10 operations_n=100`

### email output

I don't have an email server at hand, so for now I drop the html of the email in the reports folder

### other notes

a file can be processed only once, use unique values in the db to maintain consistency.

I'm sorry, I didn't add unit tests, I usually do them for apis, but for a data import process where it should take a lot of mocking sometimes I get lost in the how.

## AWS solution

I'm sorry, due to lack of time I did not complete this part. but try to make the architecture with docker-compose similar to aws serverless. so with small changes it could work in this environment.
