import sys
import re
import httplib
from urlparse import parse_qs, urlsplit
from urllib import urlencode, quote, quote_plus
from datetime import datetime
from pprint import pprint


#'url': url,
#'data': data,
#'auth': auth,
#'headers': headers,
#'requestType': 'POST',
#'returnFormat': 'xml',
#'DEBUG': 'True',
   
# h=HttpConn(url)
# def do_request(url, param, headers={}):
#     return HTTPcn( {'url': url, 'data': param, '}).request()
# from util.http import do_request

class HTTPcn(object):
    
    def __init__(self, params={}):  
              
        #init
        self._url( params.get('url') )
        self._data( params.get('data') )
        self._headers( params.get('headers') )
        self._auth( params.get('auth') )
        self.timeout = params.get('timeout', 1)
        self.params = ''
        
        #put it all together                
        self._urlEncode()
        self._get_headers()
        self._get_conn()
               
        #response
        self.status = ''
        self.resHeaders = ''
        self.raw = ''
        self.res = ''

        self.debug = {}
        
    def _auth(self, auth):
        if isinstance(auth, dict):
            self.auth = auth
        else:
            self.auth = dict()
        
    def _headers(self, headers):
        if isinstance(headers, dict):
            self.headers = headers
        else:
            self.headers = dict()
          
    def _data(self, data):
        if isinstance(data, dict):
            self.data = data
        else:
            self.data = dict()
           
    def _url(self, url):
        self.url = url
        self.parts = []
        if self.url:
            self.parts = urlsplit( self.url )
        
    def _urlEncode(self):
        if isinstance(self.data, str ):
            #params = quote_plus(data)
            self.params = self.data
        else:
            self.params = urlencode( self.data, True )
    
    def _get_conn(self):
        if self.parts.scheme == 'https':
            self.cc = httplib.HTTPSConnection
        else:
            self.cc = httplib.HTTPConnection
    
    def _get_headers(self):
        the_path=self.parts.path
        #print 'the_path: %s' % the_path
        #print 'self.parts:'
        #pprint( self.parts )
        if self.parts.query != '':
            the_path += '?' + self.parts.query
            self.headers['Content-Length']=str(len(the_path))
        else:
            self.headers['Content-Length']=str(len(self.params))

        self.headers['host']='' #self.parts.netloc
#        self.headers['Content-type']='application/x-www-form-urlendcoded'
        self.headers['Connection']='close'
           
    def request(self):
        res = ''
        if not self.debug:
            #print 'no errors'
            res = self._do_conn()
            #if res:
                #print 'conn good'
                #self._parse()
        return res
                
    def _do_conn(self):
        result = False
        #print 'do_conn'
        resp = None
        #print '~host:%s' % self.parts.netloc
        #print '~params:%s' % str( self.params )
        #print '~headers:%s' % str( self.headers )
        try:
            conn = self.cc( self.parts.netloc, timeout=self.timeout )
            conn.request( 'POST', self.parts.path, self.params, self.headers )
            resp = conn.getresponse()
            #pprint( resp )
            self.status = resp.status
            self.raw = resp.read()
            self.resHeaders = resp.getheaders()  

        except Exception, e:
            self.debug['_do_conn'] = e
            failed=True
            #print e
            raise Exception( 'HTTPcn error: %s' % str( e ) )
            #res = self.build_response()
        #else:
        #    print 'else:'
        #    if resp:
        #        print 'is resp'
        #        self.status = resp.status
        #        self.raw = resp.read()
        #        self.resHeaders = resp.getheaders()
        
        else:
            result = True
        
        finally:
            conn.close()
            return result
                    
    def _parse(self):
        self.raw = re.sub("[\n\t\r]", "", self.raw)
        self.res = self.parse_ping( self.raw )
        
    def get_raw(self):
        return self.raw
    
    def get_res(self):
        return self.res

    def print_debug_init(self):
        print 'url: %s' % self.url
        print 'headers: %s' % self.headers
        print 'auth: %s' % self.auth
        print 'timeout %s' % self.timeout
        print 'data:'
        pprint(self.data)
        print 'parts:'
        pprint(self.parts)
        
    def print_debug_end(self):
        print 'raw: %s' % self.raw
        print 'res: %s' % self.res
        
    def print_debug(self):
        print 'debug:'
        pprint(self.debug)


### stand alone test function        
def http_request_test():
    #testing company for requesting offers
    cc = httplib.HTTPConnection
    host = "company.com"
    path = "/api/v2/offers/"
    params = {"format":"xml", "publisher":"company", "metrocode":"0000"}
    data = urlencode( params, True )
    headers = {
        "host": host,
        "Content-type": "application/x-www-form-urlencoded",
        "Content-Length":len( data ),
        }
    
    try:
        conn = cc( host, timeout=1 )
        conn.request( 'POST', path, data, headers )
        resp = conn.getresponse()
        print 'resp:'
        pprint(resp)

    except Exception, e:
        failed=True
        print e
        #self.debug['_do_conn'] = e
        #res = self.build_response()
    else:
        if resp:
            status = resp.status
            raw = resp.read()
            resHeaders = resp.getheaders()
                        
            print status
            print raw
            pprint( resHeaders )
            
    finally:
        conn.close()
        
        
### stand alone test function 
def httplib_test(data, key):
    #testing company submission of a lead
    import httplib, urllib
    params = urllib.urlencode(data)
    host = "company.com"
    path = "/api/v2/subscribers"
    headers = {
        "host": host,
        "Content-type": "application/x-www-form-urlencoded",
        "Content-Length":len( data ),
        "X-Forwarded-Ssl": "on",
        "X-API-KEY": key,
        }
    conn = httplib.HTTPConnection(host)
    conn.request("POST", path, params, headers)

    response = conn.getresponse()
    print response.status, response.reason

    data = response.read()
    conn.close()
    
    
    
def set_company_params(url, data={}, auth={}, headers={}, useChannels=False):
    #Takes company com templates and commonly formats them 
    
    apikey="(a-zA-Z0-9)*"
    channels = ["deal-national", "deal-los-angeles", "deal-san-francisco",]
        
    data.update( { "apikey":apikey } )
    if useChannels:
        data.update( { "channels":str( channels ),} )
    
    #params
    params = {
        'url': url,
        'data': data,
        'auth': auth,
        'headers': headers,
        'requestType': 'POST',
        'returnFormat': 'xml',
        'DEBUG': 'True',
    }
    
    return params 
    
def company_current_offers():
    #company com template
    
    data = {"publisher":"company", "metrocode":"0000"}
    url = "http://company.com/api/v2/offers/"
    
    return set_company_params( url=url, data=data )

def company_pushlead():
    #company com template    
    
    data = {"email":"none@none.com",}
    url = "http://company.com/api/v2/subscribers/"
    useChannels = True
    
    return set_company_params( url=url, data=data, useChannels=useChannels)
    

    
def main():
    url = ''
    data = {}
    auth = {}
    headers = {}
    params = {
            'url': url,
            'data': data,
            'auth': auth,
            'headers': headers,
            'requestType': 'POST',
            'returnFormat': 'xml',
            'DEBUG': 'True',
            }
    
    #c = HTTPcn( params )
    c = HTTPcn( company_pushlead() )
    
#    c.print_debug_init()
#    c.print_debug()
    
    c.request()
    
    c.print_debug_end()
    c.print_debug()
                    
        
        
if __name__ == "__main__":
    main()
    #http_request_test()
