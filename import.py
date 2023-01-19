"""
#################################
Pre-requisites needed
#################################

If you are missing any of the following you can install with:

	pip install $name
	Example: pip install csv 

OR if you are using pip3

	pip3 install $name 
	Example: pip3 install csv 
"""

import csv
import datetime
import os
import random
import requests as rq
import time
import urllib.parse
import json

"""
#################################
Overview: 
#################################

Simulates bulk manual transaction adds to mint.com. Mint manual transactions are submitted as "cash transactions" which 
will mean it shows in your cash / all accounts transaction list. You cannot submit manual transactions against credit 
cards or other integrated bank accounts (even in Mint's UI this is not possible and ends up as cash transction). 

Approach Credits: 
Simulating manual transactions from UI is based on Nate H's proof of concept from https://www.youtube.com/watch?v=8AJ3g5JGmdU

Python Credits:
Credit to https://github.com/ukjimbow for his work on Mint imports for UK users in https://github.com/ukjimbow/mint-transactions

Process Documentation: 
1. Import CSV
2. Process date for correct format and HTTP encode result 
3. Process merchant for HTTP encode
4. Process cateogories change your banks category name into a mint category ID (limited in scope based on the categories
5 needed when I wrote this)
6. Process amount for positive or negative value indicating income or expense 
7. Send POST Request to mint as new transaction. 
8. Force Randomized Wait Time before starting next request

Future Development:
1. Replace curl command string generation with parametized curl class constructor 
2. Add support for the rest of the manual transaction items

"""

"""
#################################
Settings 
#################################
"""
csv_name = 'import.csv' # name of csv you you want import to mint [string.csv]
verbose_output = 1 # should verbose messages be printed [0,1] 
uk_to_us = 0 # do you need to change dates from UK to US format [0,1]
min_wait = 0 # min wait time in seconds between requests, int[0-n]
max_wait = 2 # max wait time in seconds between requests, int[0-n]
# default_note = "Bulk import" # Optional - set default note on transactions
default_note = "Bulk import from Chase Sapphire" # Optional - set default note on transactions
verify_ssl = False # Optional - useful for debugging through a proxy like Fiddler. Should otherwise be True

"""
#################################
Mint Client Credentials 
#################################
"""
authorization = open('authorization.txt', 'r').readline()
cookie = open('cookie.txt', 'r').readline()

headers = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'",
	"Accept-Language": "en-US,en;q=0.5",
	"Authorization": authorization,
	"Referer": "https://mint.intuit.com/transactions",
	"Cookie": cookie,
	"Connection": "close"
}


categoriesResponse = rq.get('https://mint.intuit.com/pfm/v1/categories', headers=headers, verify=verify_ssl)
categories_json = categoriesResponse.json()

categories_prefix = categories_json['Category'][0]['id'].split("_")[0] + "_"

"""
#################################
Import CSV using the pythons csv reader 
#################################
"""
csv_object = csv.reader(open(csv_name, 'r'))
next(csv_object)

for row in csv_object:

	# Initialize Variables
	date = (row[0]) 
	postDate = (row[1])
	merchant = (row[2])
	catName = (row[3])
	typeID = (row[4])
	amount = (float(row[5]))
	expense = True

	"""
	#################################
	Process Date for format and HTTP Encode
	#################################
	"""

	# Convert Commonwealth to US Date System 
	if uk_to_us == 1: # based on setting
		dateconv = time.strptime(date,"%d/%m/%Y") # not needed for US to US
	else:
		dateconv = time.strptime(date,"%m/%d/%Y")
	
	dateoutput = (time.strftime("%Y-%m-%d",dateconv)) # converted to yyyy-mm-dd
	"""
	#################################
	Process Categories 
	#################################

	If you need to map more you can do so below.
	"""

	# Category ID Mapping Function 
	def category_id_switch(import_category):
		#Chase categories - incomplete
		chase={
			'Gas': categories_prefix + '1401',
			'Food & Drink': categories_prefix + '7',
			'Groceries': categories_prefix + '701',
			'Bills & Utilities': categories_prefix + '13',
			'Shopping': categories_prefix + '2',
			'Health & Wellness': categories_prefix + '5',
			'Personal': categories_prefix + '4',
			'Credit Card Payment': categories_prefix + '2101',
			'Travel': categories_prefix + '15',
			'Entertainment': categories_prefix + '1',
			'Automotive': categories_prefix + '14',
			'Education': categories_prefix + '10',
			'Professional Services': categories_prefix + '17',
			'Home': categories_prefix + '12',
			'Fees & Adjustments': categories_prefix + '16',
			'Gifts & Donations': categories_prefix + '8',
		}

		# American Express Categories - Incomplete
		# American Express doesn't provide category information for payments, so I recommend manually changing those to "Payment"
		amex = {
			'Merchandise & Supplies-Groceries': categories_prefix + '701',
			'Transportation-Fuel': categories_prefix + '1401',
			'Fees & Adjustments-Fees & Adjustments': categories_prefix + '16',
			'Merchandise & Supplies-Wholesale Stores': categories_prefix + '2',
			'Restaurant-Restaurant': categories_prefix + '707',
			'Payment': categories_prefix + '2101',
		}

		# Load categories from mint
		mint = dict()
		for cat in categories_json['Category']:
			mint[cat['name']]: cat['id']
		
		switcher = dict()
		switcher.update(chase)
		switcher.update(amex)
		switcher.update(mint)
		# Get the mint category ID from the map 
		result = switcher.get(import_category)
		
		if result != None:
			return result
		else:
			return switcher.get("Uncategorized")

	# typeID payment overrides all categories 
	if typeID == "Payment":
		catID = '2101' # Since I was importing credit cards I have mine set to credit card payment. If you are doing bank accounts you many want to change this to payment general
	
	# if type is NOT payment then do a category check 
	else:

		# if there IS no cat it is uncategorized 
		if len(catName) == 0: 
			catID = '20' # mint's uncategorized category

		# If there is a category check it against mapping	
		else : 
			# Use a switch since there may be MANY category maps 
			catID = str(category_id_switch(catName))


	# Set mint category name by looking up name in ID map 
	category = catName
	category = urllib.parse.quote(category)

	"""
	#################################
	Process Amount seeing if transaction is an expense or income.   
	#################################
	"""
	if amount < 0: 
		expense = True # when amount is less than 0 this is an expense, ie money left your account, ex like buying a sandwich. 					
	else: 
		expense = False # when amount is greater than 0 this is income, ie money went INTO your account, ex like a paycheck. 				
	amount = str(amount) # convert amount to string so it can be concatenated in POST request 

	"""
	#################################
	Build POST Request
	#################################
	"""


	form_json = {
			"date": dateoutput,
			"description": merchant,
			"category": {
					"id": catID,
					"name": None
			},
			"accountId": None,
			"amount": amount,
			"parentId": None,
			"type": "CashAndCreditTransaction",
			"id": None,
			"isExpense": expense,
			"isPending": False,
			"isDuplicate": False,
			"tagData": None,
			"splitData": None,
			"manualTransactionType": "CASH",
			"notes": default_note,
			"checkNumber": None,
			"isLinkedToRule": False,
			"shouldPullFromAtmWithdrawals": False
	}


	"""
	#################################
	Submit POST Request
	#################################
	"""
	# response = None
	response = rq.post("https://mint.intuit.com/pfm/v1/transactions", headers=headers, json=form_json, verify=verify_ssl)

	"""
	#################################
	Verbose Output for Debug
	#################################
	"""
	if verbose_output == 1:
		print ('Transaction Date:', dateoutput) # date of transaction
		print ('Merchant', merchant) # merchant Description 
		print ('Category ID:', catID) # category of transaction
		print ('Category Name:', category) # category of transaction
		print ('Amount:', amount) # amount being processed
		print ('Expense:', expense) # in amount expense
		print ('Request:', form_json) # what was sent to mint 
		print ('Response:', response) # what was returned from mint OR curl ERROR
		print ('\n\n==============\n') # new line break

	if response.status_code >= 400:
		print ('Import failed on ', form_json)
		exit()
	"""
	#################################
	Force a random wait between 2 and 5 seconds per requests to simulate UI and avoid rate limiting
	#################################
	"""
	time.sleep(random.randint(min_wait, max_wait))
