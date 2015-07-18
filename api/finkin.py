from ofx import OFXClient
from OFXParser import OFXParser
import datetime
import time
import traceback
import cgi
import calendar

newline = "\r\n"

def _opentag(tag, attr):
        s = "<" + tag
        for k in attr.keys():
                s += " "+k+"=\""+attr[k]+"\""
        s += ">"
        return s

def _closetag(tag):
        return "</"+tag+">"

def _field(tag, attr, value):
        return _opentag(tag, attr)+cgi.escape(value)+_closetag(tag)

def _tag(tag, attr, *contents):
        return str.join(newline,[_opentag(tag, attr)]+list(contents)+[_closetag(tag)])

def subtract_date(date, year=0, month=0):
    day = date.day
    year, month = divmod(year*12 + month, 12)
    if date.month <= month:
	year = date.year - year - 1
	month = date.month - month + 12
    else:
	year = date.year - year
	month = date.month - month
    lastday = calendar.monthrange(year, month)[1]
    if day > lastday:
	day = lastday
    return date.replace(year = year, month = month, day = day)

class Finkin:
        def _response(self, success, *contents):
                return _tag('Response', { 'Success': '1' if success else '0' }, *contents)

	def _debug(self, message):
                return self._response(False, _field('Debug', {}, message))

        def _error(self, message):
                return self._response(False, _field('Error', {}, message))

        def _success(self, *contents):
                return self._response(True, *contents)

        def InstitutionSearch(self, params):
		name = None
		if (params.has_key('Name')):
			name = str(params['Name'])
		else:
			return self._error('Missing parameter \'Name\'')

		type = None
		if (params.has_key('Type')):
			t = int(params['Type'])
			if t in [1,2,3]:
				type = t

		institutions = []
		for inst in FinkinDA(params.has_key('debug')).InstitutionSearch(name, type):
			institutions.append(_tag('Institution', {}, \
						_field('ID', {}, str(inst['ID'])), \
						_field('Name', {}, str(inst['Name'])), \
						_field('Type', {}, str(inst['Type']))))
                return self._success(_tag('Institutions', {}, *institutions))

	def AccountSearch(self, params):
                institutionID = None
                if (params.has_key('InstitutionID')):
                        try:
                                institutionID = int(params['InstitutionID'])
                        except TypeError:
                                return self._error('Parameter \'InstitutionID\' must be a number')
                else:
                        return self._error('Missing parameter \'InstitutionID\'')

                userID = None
                if (params.has_key('UserID')):
                        userID = params['UserID']
                else:
                        return self._error('Missing parameter \'UserID\'')

                password = None
                if (params.has_key('Password')):
                        password = params['Password']
                else:
                        return self._error('Missing parameter \'Password\'')

		da = FinkinDA(params.has_key('debug'))
		da.StartLog(params, institutionID)
                try:
                        ret = da.AccountSearch(institutionID, userID, password)
			da.EndLog(params, 1, ret.signOnCode, ret.dataCode, ret.signOnMessage or 'Success')
		except FinkinDebugException as fde:
			return self._debug(fde.message)
                except FinkinException as fe:
			da.EndLog(params, -1, 0, 0, fe.message)
                        return self._error(fe.message)
                except:
			da.EndLog(params, -1, 0, 0, traceback.format_exc())
                        return self._error('Server error')

                if (ret.signOnCode != '0'):
                        return self._error('Sign on error #' + str(ret.signOnCode))

                if (ret.dataCode != '0'):
                        return self._error('Response error #' + str(ret.dataCode))

                accounts = []
                for t in ret.accounts:
                        accounts.append(_tag('Account', {}, \
                                                _field('ID', {}, str(t.get('acctid',''))), \
                                                _field('Description', {}, str(t.get('desc',''))), \
                                                _field('RoutingNumber', {}, str(t.get('bankid',''))), \
						_field('AccountType', {}, str(t.get('accttype',''))), \
                                                ))
                return self._success(_tag('Accounts', {}, *accounts))

	def ParseTransactionOFX(self, params):
		OFX = None
                if (params.has_key('OFX')):
                        OFX = params['OFX']
                else:
                        return self._error('Missing parameter \'OFX\'')

		try:
                        ret = OFXParser(OFX)
                except FinkinDebugException as fde:
                        return self._debug(fde.message)
                except FinkinException as fe:
                        return self._error(fe.message)
                except:
                        return self._error(traceback.format_exc())
                        return self._error('Server error')

                transactions = []
                for t in ret.transactions:
                        transactions.append(_tag('Transaction', {}, \
                                                _field('ID', {}, str(t['fitid'])), \
                                                _field('DatePosted', {}, str(t['dtposted'])), \
                                                _field('Name', {}, str(t.get('name', t.get('memo', 'N/A')))), \
                                                _field('Type', { 'ID': str(t['typeid']) }, str(t['type'])), \
                                                _field('Amount', {}, str(t['trnamt'])), \
                                                _field('Category', { 'ID': str(t.get('catid',0)) }, str(t.get('cat','N/A'))), \
                                                _field('SubCategory', { 'ID': str(t.get('subcatid','N/A')) }, str(t.get('subcat','N/A'))), \
                                                ))
                return self._success(_tag('Transactions', {}, *transactions))

        def TransactionSearch(self, params):
		institutionID = None
		if (params.has_key('InstitutionID')):
			try:
				institutionID = int(params['InstitutionID'])
			except TypeError:
				return self._error('Parameter \'InstitutionID\' must be a number')
		else:
			return self._error('Missing parameter \'InstitutionID\'')

		userID = None
		if (params.has_key('UserID')):
			userID = params['UserID']
		else:
			return self._error('Missing parameter \'UserID\'')

		password = None
		if (params.has_key('Password')):
			password = params['Password']
		else:
			return self._error('Missing parameter \'Password\'')

		account = None
		if (params.has_key('Account')):
			account = params['Account']
		else:
			return self._error('Missing parameter \'Account\'')

		accountType = None
		if (params.has_key('AccountType')):
			accountType = params['AccountType']

		routing = None
		if (params.has_key('RoutingNumber')):
			routing = params['RoutingNumber']

		endDate = datetime.date.today()
		startDate = subtract_date(endDate, month=1)
		if (params.has_key('StartDate')):
			try:
				startDate = datetime.strptime(params['StartDate'], '%Y%m%d')
			except:
				pass
		if (params.has_key('EndDate')):
			try:
				endDate = datetime.strptime(params['EndDate'], '%Y%m%d')
			except:
				pass
		if (endDate < startDate or (endDate - startDate).days > 31):
			endDate = startDate + datetime.timedelta(31)

		da = FinkinDA(params.has_key('debug'))
		da.StartLog(params, institutionID)
		try:
			ret = da.TransactionSearch(institutionID, userID, password, account, startDate, endDate, accountType, routing)
			da.EndLog(params, 1, ret.signOnCode, ret.dataCode, ret.signOnMessage or 'Success')
		except FinkinDebugException as fde:
			return self._debug(fde.message)
		except FinkinException as fe:
			da.EndLog(params, -1, 0, 0, fe.message)
			return self._error(fe.message)
		except:
			da.EndLog(params, -1, 0, 0, traceback.format_exc())
			return self._error('Server error')

		if (ret.signOnCode != '0'):
			return self._error('Sign on error #' + str(ret.signOnCode))

		if (ret.dataCode != '0'):
			return self._error('Response error #' + str(ret.dataCode))
		
		transactions = []
		for t in ret.transactions:
			transactions.append(_tag('Transaction', {}, \
                                                _field('ID', {}, str(t['fitid'])), \
						_field('DatePosted', {}, str(t['dtposted'])), \
                                                _field('Name', {}, str(t['name'])), \
                                                _field('Type', { 'ID': str(t['typeid']) }, str(t['type'])), \
						_field('Amount', {}, str(t['trnamt'])), \
                                                _field('Category', { 'ID': str(t['catid']) }, str(t['cat'])), \
                                                _field('SubCategory', { 'ID': str(t['subcatid']) }, str(t['subcat'])), \
						))
                return self._success(_tag('Transactions', {}, *transactions))

import MySQLdb
import MySQLdb.cursors
class FinkinDA:
	def __init__(self, debug):
		self._conn = MySQLdb.connect(host="localhost",user="user",passwd="password",db="finkin",cursorclass=MySQLdb.cursors.DictCursor)
		self._db = self._conn.cursor()
		self.debug = debug

	def __del__(self):
		self._db.close()
		self._conn.close()

	def StartLog(self, params, institutionID):
		if (not params.has_key('log')):
			return
                self._db.execute("""INSERT INTO Log (UserID, InstitutionID, StartTime, Type) VALUES (%s, %s, %s, %s)""", (params['log-user'], institutionID, time.time(), params['log-type'],))
                self.logID = self._conn.insert_id()

        def EndLog(self, params, status, signOnCode, dataCode, message):
		if (not params.has_key('log')):
                        return
                self._db.execute("""UPDATE Log SET EndTime=%s, Status=%s, SignOnCode=%s, DataCode=%s, Message=%s WHERE ID=%s""", (time.time(), status, signOnCode, dataCode, message, self.logID))

	def Auth(self, token):
		self._db.execute("""SELECT * FROM Users WHERE Token = %s""", (token,))
		ret = 0
		if self._db.rowcount == 1:
			ret = self._db.fetchone()
			ret = ret['ID']
		return ret

	def InstitutionSearch(self, name, type):
		name = name.replace("*","%")
		min_type = type
		max_type = type
		if (type == None):
			min_type = 1
			max_type = 3

		self._db.execute("""SELECT * FROM Institutions WHERE Name LIKE %s AND Type >= %s AND Type <= %s AND Type IN (1,2) AND OFXUrl != '' LIMIT 100""", (name, min_type, max_type))
		return self._db.fetchall()

	def AccountSearch(self, institutionID, userID, password):
                self._db.execute("""SELECT * FROM Institutions WHERE ID = %s""", (institutionID,))
                if self._db.rowcount == 0:
                        raise FinkinException("Cannot find Institution with ID=" + str(institutionID))
                inst = self._db.fetchone()

		ofx = OFXClient(inst['OFXUrl'], userID, password, inst['Organization'], str(inst['FID']))
		q = ofx.acctQuery()
		r = ofx.doQuery(q)
		if (self.debug):
			raise FinkinDebugException(q + "\n\n" + r)
		return OFXParser(r)

	def TransactionSearch(self, institutionID, userID, password, account, startDate, endDate, accountType, routing):
		self._db.execute("""SELECT * FROM Institutions WHERE ID = %s""", (institutionID,))
		if self._db.rowcount == 0:
			raise FinkinException("Cannot find Institution with ID=" + str(institutionID))
		inst = self._db.fetchone()

		if (inst['Type'] == 2 and accountType == None):
			raise FinkinException("Missing parameter \'AccountType\' for bank query")
                if (inst['Type'] == 2 and routing == None):
                        raise FinkinException("Missing parameter \'RoutingNumber\' for bank query")

		ofx = OFXClient(inst['OFXUrl'], userID, password, inst['Organization'], str(inst['FID']))
		if (inst['Type'] == 2): #bank
			q = ofx.baQuery(account, startDate, endDate, accountType, routing)
		if (inst['Type'] == 1): #cc
			q = ofx.ccQuery(account, startDate, endDate)
		#if (inst['Type'] == 3): #invst
		#	q = ofx.invstQuery(broker, account)

		r = ofx.doQuery(q)
		if (self.debug):
			raise FinkinDebugException(q + "\n\n" + r)
		return OFXParser(r)

class FinkinException(Exception):
	def __init__(self, message):
		self.message = message

class FinkinDebugException(Exception):
	def __init__(self, message):
		self.message = message
