import httplib, urllib2

_token = 'TOKEN'
_urlbase = 'https://api.example.com'
_version = 'v1.1'

# fitype
TYPE_CC = 1
TYPE_BANK = 2

class FinkinClient:
	def _query(self, action, params):
		xml = '<Request>'
		for k,v in params.items():
                        if not v == None:
                                xml += '<'+k+'><![CDATA['+str(v)+']]></'+k+'>' 
		xml += '</Request>'

                url = str.join('/', [_urlbase, _version, action])
		req = urllib2.Request(url, xml, { "x-finkin-auth": _token })
		res = urllib2.urlopen(req)
		return res.read()

	def InstitutionSearch(self, name, fitype):
		params = {}
		if name != None:
			params['Name'] = name
		if fitype != None:
			params['Type'] = fitype
		return self._query('InstitutionSearch', params)	

	def AccountSearch(self, institutionID, userID, password):
                params = { 'InstitutionID': institutionID,
                           'UserID': userID,
                           'Password': password }
                return self._query('AccountSearch', params)

        def TransactionSearch(self, institutionID, userID, password, account, startDate=None, endDate=None, accountType=None, routing=None):
                params = { 'InstitutionID': institutionID,
                           'UserID': userID,
                           'Password': password,
                           'Account': account,
                           'AccountType': accountType,
                           'RoutingNumber': routing }
                if not startDate == None:
                        params['StartDate'] = startDate.strftime('%Y%m%d')
                if not endDate == None:
                        params['EndDate'] = endDate.strftime('%Y%m%d')
                return self._query('TransactionSearch', params)

	def ParseTransactionOFX(self, OFX):
                params = {}
                if OFX != None:
                        params['OFX']= OFX
                return self._query('ParseTransactionOFX', params)
