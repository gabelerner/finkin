#!/usr/bin/python

import web
import finkin

urls = ("/", "default", "/v1.0/(.+)", "api_1_0", "/v1.1/(.+)", "api_1_1")
app = web.application(urls, globals())

class default:
    def GET(self):
        web.header('Content-Type', 'text/html')
        return '<html><body>finkin api 1.1</body></html>'

import xml.dom.minidom

class api_base:
    def _o(self, s):
        web.header('Content-Type', 'application/xml')
        return '<?xml version="1.0" encoding="UTF-8"?>\r\n' + s

    def _getParamsOrError(self):
        params = {}

        try:
                body = xml.dom.minidom.parseString(web.data())
                request = body.getElementsByTagName("Request")[0]
                for param in request.childNodes:
                        if (param.nodeType == param.ELEMENT_NODE):
                                params[param.tagName] = param.childNodes[0].data
        except:
                raise web.badrequest()

        if (not web.ctx.environ.has_key('HTTP_X_FINKIN_AUTH')):
                raise web.unauthorized()

        if (web.ctx.environ.has_key('HTTP_X_FINKIN_DEBUG')):
                params['debug'] = True

        fda = finkin.FinkinDA(False)
	userID = fda.Auth(web.ctx.environ['HTTP_X_FINKIN_AUTH'])
        if (userID == 0):
                raise web.unauthorized()
	params['log-user'] = userID

        return params

    def GET(self, f):
        return web.notfound()

class api_1_1(api_base):
    def POST(self, f):
        params = self._getParamsOrError()
        fin = finkin.Finkin()
	params['log'] = 1
        if (f == "InstitutionSearch"):
		params['log-type'] = 1
                return self._o(fin.InstitutionSearch(params))
        if (f == "TransactionSearch"):
		params['log-type'] = 2
                return self._o(fin.TransactionSearch(params))
        if (f == "AccountSearch"):
		params['log-type'] = 3
                return self._o(fin.AccountSearch(params))
	if (f == "ParseTransactionOFX"):
		params['log-type'] = 4
		return self._o(fin.ParseTransactionOFX(params))
	raise web.notfound()

class api_1_0(api_base): 
    def POST(self, f):
	params = self._getParamsOrError()
	fin = finkin.Finkin()
	if (f == "InstitutionSearch"):
		return self._o(fin.InstitutionSearch(params))
	if (f == "TransactionSearch"):
		return self._o(fin.TransactionSearch(params))
	if (f == "AccountSearch"):
		return self._o(fin.AccountSearch(params))

	raise web.notfound()

web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
if __name__ == "__main__":
    app.run()
