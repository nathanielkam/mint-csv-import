# Run:
Run the code by typing the following from the directory the code is located in

    python3 import.py


Virtual Environment Setup (from app repo root)
1. Make sure you have venv on your system, using the following command based on your python version 

```
python3 -m pip3 install virtualenv
```

2. Make sure you are in repo root 
    - (where import.py is)
   
3. Create a virtual environment

```
virtualenv venv
```

4. Turn on the virtual environment (these should work on both but depends on your version you may need to explicitly run the sh or bat file)
    - Mac / Linux in terminal or bash: 
   ```
   venv/Scripts/activate
   ```
    - Windows in powershell: 
   ```
   venv\Scripts\activate
   ```

## Overview: ##
Simulates bulk manual transaction adds to mint.com. Mint manual transactions are submitted as "cash transactions" which
will mean it shows in your cash / all accounts transaction list. You cannot submit manual transactions against credit
cards or other integrated bank accounts (even in Mint's UI this is not possible and ends up as cash transactions).

## Approach: ##
Simulating manual transactions from UI is based on Nate H's proof of concept from https://www.youtube.com/watch?v=8AJ3g5JGmdU

## Python: ##
Credit to https://github.com/ukjimbow for his work on Mint imports for UK users in https://github.com/ukjimbow/mint-transactions

## Process: ##
1. Import CSV
2. Process date for correct format and HTTP encode result
3. Process merchant for HTTP encode
4. Process categories. Change your bank's category name into a mint category ID (limited in scope based on the categories needed when I wrote this)
6. Process amount for positive or negative value indicating income or expense
7. Send POST Request to mint as new transaction.
8. Force Randomized Wait Time before starting next request

## Instructions: ##
1. Prepare your data to import using import.csv as an example
2. Edit import.py and replace the variables set to XXXXX's to values in your browser during a live Mint session
  - account is `mtaccount` and approximately 8 digits
  - tag1 is in form of `tagXXXXXXX`
  - tag2 is in form of `tagXXXXXXX`
  - tag3 is in form of `tagXXXXXXX`
  - cookie will be an approximately 2000 character string
  - referrer is likely always 'https://mint.intuit.com/transaction.event'
  - token is approximately 50 characters
3. If you have custom categories, they need to go along others in function category_id_switch()
