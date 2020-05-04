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
import requests
import time
import urllib.parse

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

"""
#################################
Mint Client Credentials 
#################################

You will need the tags, cookie, and token to simulate a UI form submission. You can get these by opening developer tools > network analysis tab and doing 
a test submission in mint.com. From there look for the post request to "updateTransaction.xevent" and grab the credentials from the header and body
"""
account = 'XXXXXXX' # grab from POST request form body in devtools
tag1 = 'tagXXXXXX' # in form of tagXXXXXXX
tag2 = 'tagXXXXXXX' # in form of tagXXXXXXX
tag3 = 'tagXXXXXXX' # in form of tagXXXXXXX
cookie = 'XXXXXXX' # grab from POST request header in devtools 
referrer = 'XXXXXXX' # grab from POST request header in devtools 
token = 'XXXXXXX' # grab from POST request form body in devtools 
"""
#################################
Import CSV using the pythons csv reader 
#################################
"""
csv_object = csv.reader(open(csv_name,'rU'))
next(csv_object)

for row in csv_object:

	# Initialize Variables
	date = (row[0]) 
	postDate = (row[1])
	merchant = (row[2])
	catID = (row[3])
	typeID = (row[4])
	amount = (float(row[5]))
	expense = 'true'
	curl_input = 'Error: Did not Generate'
	curl_output = 'Error: Did not run' 

	"""
	#################################
	Process Date for format and HTTP Encode
	#################################
	"""

	# Convert Commonwealth to US Date System 
	if uk_to_us == 1: # based on setting
		dateconv = time.strptime(date,"%d/%m/%Y") # not needed for US to US
		date = (time.strftime("%m/%d/%Y",dateconv)) # converted new US date format from UK

	# Require "/" for date delimiter and HTTP Encode Character, supports "/", ".", "-"
	# We are not using url encode library here because we custom map other delimiters 
	dateoutput = date.replace("/", "%2F")
	dateoutput = date.replace(".", "%2F")
	dateoutput = date.replace("-", "%2F")

	"""
	#################################
	Process Merchant with HTTP Encode
	#################################
	"""
	merchant = urllib.parse.quote(merchant)

	"""
	#################################
	Process Categories 
	#################################

	Support is limited to the categories I needed at the time, if you need to map more you can. To get category ids: 
	 1. Go to mint 
	 2. Add a transactions
	 3. Right click "inspect-element" on the category you want
	 4. The ID is in the <li> item that encapsulates the a href
	 5. Add mapping here based on string match from your CSV to the catID you got from mint (following existing examples)
	"""

	# Category ID Mapping Function 
	def category_id_switch(import_category):

		# Define mapping of import categories to : Mint Category IDs
		switcher={
			'Gas':1401,
			'Food & Drink':7,
			'Groceries':701,
			'Bills & Utilities':13,
			'Shopping':2,
			'Health & Wellness':5,
			'Personal':4,
			'Credit Card Payment':2101,
			'Travel':15,
			'Entertainment':1,
			'Automotive':14,
			'Education':10,
			'Professional Services':17,
			'Home':12,
			'Fees & Adjustments':16,
			'Gifts & Donations':8,
		} 
		# Get the mint category ID from the map 
		return switcher.get(import_category,20) # For all other unmapped cases return uncategorized category "20" 

	# Category NAME Mapping Function 
	def category_name_switch(mint_id):

		# Define mapping of import categories to : Mint Category IDs
		switcher={
			1401:'Gas  & Fuel',
			7:'Food & Dining',
			701:'Groceries',
			13:'Bills & Utilities',
			2:'Shopping',
			5:'Health & Fitness',
			4:'Personal Care',
			2101:'Credit Card Payment',
			15:'Travel',
			1:'Entertainment',
			14:'Auto & Transport',
			10:'Education',
			17:'Business Services',
			12:'Home',
			16:'Frees & Charges',
			8:'Gifts & Donations',
		} 
		# Get the mint category NAME from the map 
		return switcher.get(mint_id,'Uncategorized') # For all other unmapped cases return uncategorized category "20" 

	# typeID payment overrides all categories 
	if typeID == "Payment":
		catID = '2101' # Since I was importing credit cards I have mine set to credit card payment. If you are doing bank accounts you many want to change this to payment general
	
	# if type is NOT payment then do a category check 
	else:

		# if there IS no cat it is uncategorized 
		if len(catID) == 0: 
			catID = '20' # mint's uncategorized category

		# If there is a category check it against mapping	
		else : 
			# Use a switch since there may be MANY category maps 
			catID = str(category_id_switch(catID))


	# Set mint category name by looking up name in ID map 
	category = category_name_switch(catID)
	category = urllib.parse.quote(category)

	"""
	#################################
	Process Amount seeing if transaction is an expense or income.   
	#################################
	"""
	if amount < 0: 
		expense = 'true' # when amount is less than 0 this is an expense, ie money left your account, ex like buying a sandwich. 					
	else: 
		expense = 'false' # when amount is greater than 0 this is income, ie money went INTO your account, ex like a paycheck. 				
	amount = str(amount) # convert amount to string so it can be concatenated in POST request 

	"""
	#################################
	Build CURL POST Request
	TODO: Swap command string generation for parametized curl class 
	#################################
	"""

	# Break curl lines 
	curl_line = " "

	# fragment curl command 
	curl_command = "curl -i -s -k -X POST 'https://mint.intuit.com/updateTransaction.xevent'" + curl_line 
	curl_host = "-H 'Host: mint.intuit.com'" + curl_line
	curl_user_agent = "-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'" + curl_line
	curl_accept = "-H 'Accept: */*'" + curl_line
	curl_accept_language = "-H 'Accept-Language: en-US,en;q=0.5'" + curl_line
	curl_compressed = "--compressed" + curl_line
	curl_x_requested_with = "-H 'X-Requested-With: XMLHttpRequest'" + curl_line
	curl_content_type = "-H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8'" + curl_line
	curl_referer = "-H 'Referer: https://mint.intuit.com/transaction.event?accountId=" + referrer + "'" + curl_line
	curl_cookie = "-H 'Cookie: " + cookie + "'" + curl_line 
	curl_connection = "-H 'Connection: close' " + curl_line
	curl_data =  "--data" + curl_line

	# Fragment the curl form data 	
	form_p1 = "'cashTxnType=on&mtCheckNo=&" + tag1 + "=0&" + tag2 + "=0&" + tag3 + "=0&"
	form_p2 = "task=txnadd&txnId=%3A0&mtType=cash&mtAccount=" + account + "&symbol=&note=&isInvestment=false&"
	form_p3 = "catId="+catID+"&category="+category+"&merchant="+merchant+"&date="+dateoutput+"&amount="+amount+"&mtIsExpense="+expense+"&mtCashSplitPref=2&"
	form_p4 = "token=" + token + "'"

	# Piece together curl form data 
	curl_form = form_p1 + form_p2 + form_p3 + form_p4 

	# Combine all curl fragments together into an entire curl command 
	curl_input = curl_command + curl_host + curl_user_agent + curl_accept + curl_accept_language + curl_compressed + curl_x_requested_with + curl_content_type + curl_referer + curl_cookie + curl_connection + curl_data + curl_form 

	"""
	#################################
	Submit CURL POST Request
	#################################
	"""
	curl_output = str(os.system(curl_input)) # use os sytem to run a curl request submitting the form post

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
		print ('CURL Request:', curl_input) # what was sent to mint 
		print ('CURL Response:', curl_output) # what was returned from mint OR curl ERROR
		print ('\n\n==============\n') # new line break

	"""
	#################################
	Force a random wait between 2 and 5 seconds per requests to simulate UI and avoid rate limiting
	#################################
	"""
	time.sleep(random.randint(min_wait, max_wait))