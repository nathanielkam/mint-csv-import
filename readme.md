# Run: 
Run the code by typing the following from the directory the code is located in 
python3 import.py 
OR if you do not have python3 namespacing you can type
python improt.py 

##Overview: ## 
Simulates bulk manual transaction adds to mint.com. Mint manual transactions are submitted as "cash transactions" which 
will mean it shows in your cash / all accounts transaction list. You cannot submit manual transactions against credit 
cards or other integrated bank accounts (even in Mint's UI this is not possible and ends up as cash transction). 

##Approach: ##
Simulating manual transactions from UI is based on Nate H's proof of concept from https://www.youtube.com/watch?v=8AJ3g5JGmdU

##Python: ##
Credit to https://github.com/ukjimbow for his work on Mint imports for UK users in https://github.com/ukjimbow/mint-transactions

##Process: ##
1. Import CSV
2. Process date for correct format and HTTP encode result 
3. Process merchant for HTTP encode
4. Process cateogories change your banks category name into a mint category ID (limited in scope based on the categories
5 needed when I wrote this)
6. Process amount for positive or negative value indicating income or expense 
7. Send POST Request to mint as new transaction. 
8. Force Randomized Wait Time before starting next request

##Pre-requisites needed,## 

csv
datetime
os
random
requests
time
urllib.parse

if you are missing any of the following you can install with:

	pip install $name
	Example: pip install csv 

OR if you are using pip3

	pip3 install $name 
	Example: pip3 install csv 
