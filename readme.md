# Run: 
Run the code by typing the following from the directory the code is located in 
python3 import.py 
OR if you do not have python3 namespacing you can type
python improt.py 

##Pre-requisites needed,## 

csv
datetime
os
random
requests
time
urllib.parse 

Virtual Environment Setup (from app repo root)
1. Make sure you have venv on your system, using the following command based on your python version 
	- python -m pip install virtualenv
	- python3 -m pip3 install virtualenv
2. Make sure you are in repo root \
	- (where import.py and requirements.txt are)
3. Create a virtual environment
	- virtualenv venv
4. Turn on the virtual environment (these should work on both but depends on your version you may need to explicitly run the sh or bat file)
	- Mac / Linux in terminal or bash: venv/Scripts/activate
    - Windows in powershell: venv\Scripts\activate
5. Install Requirements
	- pip install -r requirements.txt

if you do not want to use venv you can manually install any dependencies with the following:

	pip install $name
	Example: pip install csv 

OR if you are using pip3

	pip3 install $name 
	Example: pip3 install csv 


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

