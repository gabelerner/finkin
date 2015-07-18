import time, os, httplib, urllib2
import sys
import uuid

join = str.join

startdate = "19960101"
newline = "\r\n"
												
def _field(tag,value):
    return "<"+tag+">"+value

def _tag(tag,*contents):
    return join(newline,["<"+tag+">"]+list(contents)+["</"+tag+">"])

def _date():
    return time.strftime("%Y%m%d%H%M%S",time.localtime())

def _genuuid():
    return str(uuid.uuid1()).upper()

class OFXClient:
    """Encapsulate an ofx client, config is a dict containg configuration"""
    def __init__(self, url, user, password, fiorg, fid):
	self.user = user
        self.password = password
        self.cookie = 3
        self.appid = "QWIN"  
        self.appver = "1900"
	self.fiorg = fiorg
	self.fid = fid
	self.url = url

    def _cookie(self):
        self.cookie += 1
        return str(self.cookie)

    """Generate signon message"""
    def _signOn(self):
        fidata = [ _field("ORG", self.fiorg) ]
        if self.fid != None:
            fidata += [ _field("FID", self.fid) ]
        return _tag("SIGNONMSGSRQV1",
                    _tag("SONRQ",
                         _field("DTCLIENT",_date()),
                         _field("USERID", self.user),
                         _field("USERPASS", self.password),
                         _field("LANGUAGE","ENG"),
                         _tag("FI", *fidata),
                         _field("APPID", self.appid),
                         _field("APPVER", self.appver),
                         ))

    def _acctreq(self):
        req = _tag("ACCTINFORQ",_field("DTACCTUP",startdate))
        return self._message("SIGNUP","ACCTINFO",req)

    def _bareq(self, acctid, startdate, enddate, accttype, bankid):
	req = _tag("STMTRQ",
		   _tag("BANKACCTFROM",
		   	_field("BANKID", bankid),
		        _field("ACCTID",acctid),
			_field("ACCTTYPE",accttype)),
		   _tag("INCTRAN",
			_field("DTSTART", startdate.strftime("%Y%m%d")),
			_field("DTEND", enddate.strftime("%Y%m%d")),
			_field("INCLUDE","Y")))
	return self._message("BANK","STMT",req)
	
    def _ccreq(self, acctid, startdate, enddate):
        req = _tag("CCSTMTRQ",
                   _tag("CCACCTFROM",_field("ACCTID",acctid)),
                   _tag("INCTRAN",
			_field("DTSTART", startdate.strftime("%Y%m%d")),
                        _field("DTEND", enddate.strftime("%Y%m%d")),
                        _field("INCLUDE","Y")))
        return self._message("CREDITCARD","CCSTMT",req)

    def _invstreq(self, brokerid, acctid):
        dtnow = time.strftime("%Y%m%d%H%M%S",time.localtime())
        req = _tag("INVSTMTRQ",
                   _tag("INVACCTFROM",
                      _field("BROKERID", brokerid),
                      _field("ACCTID",acctid)),
                   _tag("INCTRAN",
                        _field("INCLUDE","Y")),
                   _field("INCOO","Y"),
                   _tag("INCPOS",
                        _field("DTASOF", dtnow),
                        _field("INCLUDE","Y")),
                   _field("INCBAL","Y"))
        return self._message("INVSTMT","INVSTMT",req)

    def _message(self,msgType,trnType,request):
        return _tag(msgType+"MSGSRQV1",
                    _tag(trnType+"TRNRQ",
                         _field("TRNUID",_genuuid()),
                         _field("CLTCOOKIE",self._cookie()),
                         request))
    
    def _header(self):
        return join(newline,[ "OFXHEADER:100",
                           "DATA:OFXSGML",
                           "VERSION:102",
                           "SECURITY:NONE",
                           "ENCODING:USASCII",
                           "CHARSET:1252",
                           "COMPRESSION:NONE",
                           "OLDFILEUID:NONE",
                           "NEWFILEUID:"+_genuuid(),
                           ""])

    def baQuery(self, acctid, startdate, enddate, accttype, bankid):
    	"""Bank account statement request"""
        return join(newline,[self._header(),
 	                  _tag("OFX",
                                self._signOn(),
                                self._bareq(acctid, startdate, enddate, accttype, bankid))])
						
    def ccQuery(self, acctid, startdate, enddate):
        """CC Statement request"""
        return join(newline,[self._header(),
                          _tag("OFX",
                               self._signOn(),
                               self._ccreq(acctid, startdate, enddate))])

    def acctQuery(self):
        return join(newline,[self._header(),
                          _tag("OFX",
                               self._signOn(),
                               self._acctreq())])

    def invstQuery(self, brokerid, acctid):
        return join(newline,[self._header(),
                          _tag("OFX",
                               self._signOn(),
                               self._invstreq(brokerid, acctid))])

    def doQuery(self,query):
        request = urllib2.Request(self.url,
                                  query,
                                  { "Content-type": "application/x-ofx",
                                    "Accept": "*/*, application/x-ofx"
                                  })
        
        f = urllib2.urlopen(request)
        response = f.read()
        f.close()
	return response
