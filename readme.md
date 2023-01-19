For a complete overview of how the Mint CSV Importer was developed check out - https://nathanielkam.com/import-transactions-to-mint-using-python/

# Run
1. Prepare your data to import using `import.csv` as an example
2. Populate `authorization.txt` and `cookie.txt` with header values from a live Mint session in your browser
3. If you want to explicitly map bank categories, you can define that in function category_id_switch()
3. Run the code by typing the following from the directory the code is located in:
```sh
python3 import.py
```

## Virtual Environment Setup (from app repo root)
1. Make sure you have venv on your system, using the following command based on your python version
	- `python3 -m pip3 install virtualenv`
2. Make sure you are in repo root \
	- (where import.py and requirements.txt are)
3. Create a virtual environment
	- `virtualenv venv`
4. Turn on the virtual environment (these should work on both but depends on your version you may need to explicitly run the sh or bat file)
	- Mac / Linux in terminal or bash: `venv/Scripts/activate`
    - Windows in powershell: `venv\Scripts\activate`
5. Install Requirements
	- `pip3 install -r requirements.txt`


# Overview
Simulates bulk manual transaction adds to mint.com. Mint manual transactions are submitted as "cash transactions" which
will mean it shows in your cash / all accounts transaction list. You cannot submit manual transactions against credit
cards or other integrated bank accounts (even in Mint's UI this is not possible and ends up as cash transction).

## Approach: ##
Simulating manual transactions from UI is based on Nate H's proof of concept from https://www.youtube.com/watch?v=8AJ3g5JGmdU

### Process: ###
1. Import CSV
2. Process date for correct format and HTTP encode result
3. Process merchant for HTTP encode
4. Process categories. Change your banks category name into a mint category ID (limited in scope based on the categories needed when I wrote this)
6. Process amount for positive or negative value indicating income or expense
7. Send POST Request to mint as new transaction.
8. Force Randomized Wait Time before starting next request

## Pre-requisites needed:

1. csv
1. datetime
1. random
1. requests
1. time
1. urllib.parse
1. json

# Credit
Credit to https://github.com/ukjimbow for his work on Mint imports for UK users in https://github.com/ukjimbow/mint-transactions
