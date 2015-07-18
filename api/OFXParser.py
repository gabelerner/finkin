from HTMLParser import HTMLParser

_types = { \
"CREDIT": [1, "Debit"], \
"DEBIT": [2, "Credit"], \
"INT": [3, "Interest"], \
"DIV": [4, "Divident"], \
"FEE": [5, "Fee"], \
"SRVCHG": [6, "Service charge"], \
"DEP": [7, "Deposit"], \
"ATM": [8, "ATM"], \
"POS": [9, "Point of sale"], \
"XFER": [10, "Transfer"], \
"CHECK": [11, "Check"], \
"PAYMENT": [12, "Electronic Payment"], \
"CASH": [13, "Cash withdrawal"], \
"DIRECTDEP": [14, "Direct deposit"], \
"DIRECTDEBIT": [15, "Merchant initiated debit"], \
"REPEATPMT": [16, "Repeating payment/standing order"], \
"OTHER": [17, "Other"] \
}

_categories = { \
0: "N/A", \
1: "Auto", \
2: "Bank Charges", \
3: "Bills", \
4: "Food", \
5: "Gifts", \
6: "Health", \
7: "Household",
8: "Insurance", \
9: "Leisure", \
10: "Vacation" \
}

_subcategories = {\
0: "N/A", \
1: "Maintenance", \
2: "Gasoline", \
3: "Books", \
4: "Cable/Satellite Television", \
5: "Childcare", \
6: "Clothing", \
7: "Electricity", \
8: "Garbage & Recycle", \
9: "Oil/Natural Gas", \
10: "Telephone", \
11: "Telephone (Long Distance)", \
12: "Tuition", \
13: "Water & Sewer", \
14: "Dining Out", \
15: "Groceries", \
16: "Dental", \
17: "Eyecare", \
18: "Hospital", \
19: "Prescriptions", \
20: "Maintenance", \
21: "Furnishings", \
22: "Health", \
23: "Life", \
24: "Toys & Games", \
25: "Lodging", \
26: "Travel" \
}

_sic = [ \
    [1, 1, [5511, 5521, 5531, 5532, 5533, 5599, 7523, 7524, 7531, 7532, 7533, 7534, 7535, 7536, 7537, 7538, 7539, 7542, 7549]], \
    [1, 2, [5541, 5542]], \
    [2, 0, [6051, 6760]], \
    [3, 3, [5942]], \
    [3, 4, [4841]], \
    [3, 5, [8351]], \
    [3, 6, [5611, 5621, 5631, 5632, 5641, 5651, 5655, 5661, 5681, 5691, 5697, 5698, 5699]], \
    [3, 7, [4911, 4931]], \
    [3, 8, [4953]], \
    [3, 9, [4922, 4923, 4924, 4925, 4932, 5983]], \
    [3, 10, [4812, 4813, 4814, 4815]], \
    [3, 11, [4812, 4813, 4814, 4815]], \
    [3, 12, [8211, 8220, 8221, 8222, 8241, 8243, 8244, 8249, 8299]], \
    [3, 13, [4941, 4952]], \
    [4, 14, [5811, 5812, 5813, 5814]], \
    [4, 15, [5411, 5421, 5422, 5431, 5441, 5451, 5461, 5462, 5499, 5921]], \
    [5, 0, [5947]], \
    [6, 0, [5047, 5975, 5976, 8011, 8031, 8041, 8042, 8043, 8044, 8049, 8050, 8071, 8082, 8099]], \
    [6, 16, [8021]], \
    [6, 17, [5995]], \
    [6, 18, [8062, 8063, 8069]], \
    [6, 19, [5912]], \
    [7, 20, [780, 1520, 1711, 1731, 1740, 1750, 1761, 1771, 1799, 5033, 5211, 5231, 5251, 5261, 5271, 7216, 7217, 7341, 7342, 7349, 7622, 7623, 7629, 7631, 7641, 7692, 7699]], \
    [7, 21, [5712, 5713, 5714, 5718, 5719, 5722, 5932]], \
    [8, 0, [6300, 6381, 6399, 6411]], \
    [8, 22, [6321]], \
    [8, 23, [6311]], \
    [9, 0, [5551, 5561, 5571, 5592, 5598, 5731, 5732, 5733, 5734, 5735, 5736, 5940, 5941, 5946, 5949, 5996, 7032, 7033, 7513, 7519, 7832, 7911, 7922, 7929, 7932, 7933, 7941, 7948, 7991, 7992, 7993, 7994, 7995, 7996, 7997, 7998, 7999, 8412, 8422]], \
    [9, 24, [5945]], \
    [10, 25, [7011, 7021]], \
    [10, 26, [4011, 4111, 4119, 4512, 4724, 4725, 4729]] \
]

class OFXParser(HTMLParser):
        def __init__(self, s):
            HTMLParser.__init__(self)

            self.state = ""
            self.tag = ""
	    self.signOnMessage = ""
            self.transactions = []
            self.accounts = []

            self.feed(s)
            self.close()

        def handle_starttag(self, tag, attrs):
            if tag == "signonmsgsrsv1":
                self.state = "signon"

            if tag == "code" and self.state == "signon":
                self.state = "signoncode"

	    if tag == "message" and self.state == "signon":
	        self.state = "signonmessage"

            if tag == "creditcardmsgsrsv1" or tag == "bankmsgsrsv1" or tag == "signupmsgsrsv1":
                self.state = "data"

            if tag == "code" and self.state == "data":
                self.state = "datacode"

            if tag == "stmttrn":
                self.transactions.append({})
                self.state = "trans"

            if tag == "acctinfo":
                self.accounts.append({})
                self.state = "acct"

            if self.state == "trans" and tag in ["trntype", "dtposted", "trnamt", "fitid", "sic", "name", "memo"]:
                self.tag = tag

            if self.state == "acct" and tag in ["desc", "acctid", "bankid", "accttype"]:
                self.tag = tag
                
        def handle_endtag(self, tag):
            if tag == "stmttrn":
                last = self.transactions[len(self.transactions)-1]

                t = _types[last["trntype"]]
                last["typeid"] = t[0]
                last["type"] = t[1]

                last["catid"] = 0
                last["subcatid"] = 0
		if "sic" in last:
		    for s in _sic:
		        if int(last["sic"]) in s[2]:
                            last["catid"] = s[0]
                            last["subcatid"] = s[1]
                        
                last["cat"] = _categories[last["catid"]]
                last["subcat"] = _subcategories[last["subcatid"]]                

        def handle_data(self, data):
            data = data.rstrip()
            
            if self.state == "signoncode":
                self.signOnCode = data
                self.state = "signon"

	    if self.state == "signonmessage":
 	        self.signOnMessage = data
	        self.state = "signon"

            if self.state == "datacode":
                self.dataCode = data
                self.state = "data"

            if self.state == "trans" and self.tag in ["trntype", "dtposted", "trnamt", "fitid", "sic", "name", "memo"]:
                self.transactions[len(self.transactions)-1][self.tag] = data
		self.tag = ""

            if self.state == "acct" and self.tag in ["desc", "bankid", "acctid", "accttype"]:
                self.accounts[len(self.accounts)-1][self.tag] = data
		self.tag = ""
