from urllib import urlencode
from urlparse import urlparse, urlunparse, urlsplit
from datetime import datetime, timedelta
from pprint import pprint
import sys
import re
import cPickle as pickle
import HTMLParser

from url_conn import URLcn
from http_conn import HTTPcn
from xml2dict import XML2Dict
from base import Base
from db.dbh import DBH

class Company(Base):
    
    def __init__(self, lead={}, dbh=None):
        super(company, self).__init__(dbh=dbh)
        self.host = ['company.com',][0]
        self.apipath = '/api/v2/'
        self.apikey="(a-zA-Z0-9)*"
        
        self.channels = {
            'company-los-angeles': {'location':'Los Angeles', 'geo': 'los-angeles',},
            'company': {'location':'National', 'geo':'national',},
            'company-new-york':{'location':'New York', 'geo':'new-york',},
            }
           
        self.params_global_default = {
            'apikey': self.apikey,
            'format': 'xml',
            'publisher': 'company',
            }
        self.protocol = 'http'
        self.offers = None
        self.offer_codes = [
            'metrocode',
            'channel',
            'geography',
            'areacode',
            'ip',
            ]
        
        self.lead = lead
        self.default_channel = 'company'
        
    def fetch_static_channels(self):
        return self.channels
    
    def request_offers(self, data={}):
        params = self.params_global_default
        #params.update( {''} )
        params.update( data )
        params = urlencode( params, True )
        
        path = self.apipath + 'offers/'
        #raise Exception( params )
        url = urlunparse( (self.protocol, self.host, path, '', params, "") )
        
        c = URLcn( url )
        self.offers = c.request()
        
        return self.offers
        
    def channel_exists(self, channel):
        if channel in self.channels:
            return True 
    
    def get_offers_4dailydeals(self, channel):
        offer_channel = { 'field':'channel', 'value':channel }
        self.get_offers( offer_channel )
            
        Offers = dict()
        Offers = self.get_offers_d()
        if not Offers:
            raise ValueError('something broke')
        
        details = dict()
        details = self.channels.get( channel )
            
        _offers = dict()
        offers = list()
        
        icount = 0
        for o in Offers:
            _o = {}
            for i in ['small_image_url', 'large_image_url', 'end_date', 'title', 'headline']:
                if i in o.keys():
                    _o[i] = o[i].get('value', '')
                else:
                    _o[i]=''
            _o['name']=o['merchant']['name']['value']
            _o['sold'] = o.sold_quantity# if o.sold_quantity else '0' 
            _o['price'] = refine_dollar( o.price )
            _o['value'] = refine_dollar( o.value )
            _o['savings'] = refine_dollar( o.discount_amount )
            _o['discount'] = refine_dollar( o.discount_percentage )
            offers.append( _o )
            icount = icount + 1
            
        s = 'count: %s\noffers: %s' % ( str(icount), str( offers )) 
        return offers, details
    
    def get_offers_d(self, raw={}):
        if raw:    
            return self.offers_parse( raw )
        elif self.offers:
            return self.offers_parse( self.offers )
        else:
            return 'non data provided'
    
    def get_offers(self, *args):
        params = args[0]
        data = dict()
 
        #set which offer code will be used to pull offers
        if params['field'] in self.offer_codes:
            data[params['field']] = params['value']
 
        else:
            return
        
        return self.request_offers( data )
            
    def offers_parse(self, content):
        try:
            r=XML2Dict().fromstring(content)['response']['resource']
        except:
            return None
        
        return r
                
    def set_httplib_params(self, url, data={}, auth={}, headers={}, useChannels=False):
        #Takes company com templates and commonly formats them 
    
        apikey="a9dcfecb0d89fc4a7a08042ebc70826a"
        channels = ["company",]
        if 'channel' in data:
            channel = data.get('channel')
            if channel:
                channels.append( channel )
        
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
    
    def get_offers__http(self):
        """
        grab offers via httplib 
        
        NOTE: currently not in use.  
              Using urllib for direct url request.
              Dynamic/obj 'data' field missing from equation atm
        """
        
        #c = HTTPcn( self._get_offers__http() )
        #c.request()
        #ping_response = c.get_res()
        
        pass
        
    def _get_offers__http(self):
        #company com template
    
        data = {"publisher":"company", "metrocode":"0000"}
        url = "http://company.com/api/v2/offers/"
        
        return self.set_httplib_params( url=url, data=data )

    def send_lead(self):
        c = HTTPcn( self._send_lead() )
        response = c.request()
        if response:
            #update lead with status            
            #print 'good!!'
            return True
        else:
            #print 'wtf!!'
            return False
        
    def parse_response(self, response):
        if '200' in response:
            return True
    
    def _send_lead(self):
        url = "http://%s/api/v2/subscribers/" % self.host
        useChannels = True
        return self.set_httplib_params( url=url, data=self.lead, useChannels=useChannels)
    
    
    
    ### Deals ### 
    def get_deals(self, channel):        
        self.trace = ''
        if not channel in self.channels:
            raise Exception('Channel doesn\'t exist.')        
        
        self.trace = 'get_deals...\nch: %s' % channel
    
        data = { 'field': 'channel', 'value': channel }
            
        details = dict()
        details = self.channels.get( channel )
        
        self.trace += ',details: %s' % str( details )
                
        deals=''
        deals = self.fetch_local_deals( channel )
        if not deals:
            self.trace += '\ngoing remote route'
            deals = self.fetch_remote_deals( data, details )
        else:
            self.trace += '\ngoing local route'
        
        if deals:
            self.trace += '\nDeals found!!!'
        else:
            deals, details = self.get_deals('company')
                        
        self.trace += '\nreached final!!!!'
               
         
        #raise Exception( 'trace: %s\ndeals: %s' % ( str( self.trace), str( _deals ) ) )
        
        return deals, details
               
    def fetch_local_deals(self, channel):        
        _timestamp = datetime.now() 
        _timestamp = _timestamp.strftime("%Y-%m-%d %H:%M:%S")
        sql="""SELECT DealChannelDetails as details 
        FROM Deal.Deal_Channel_Cache        
        WHERE DealChannelName = '%s' and DealChannelTimeStamp > '%s'
        """        
        vals = ( channel, _timestamp )
        _deals = self.dbh.all( sql % vals )
        #raise Exception( len( _deals) )
        deals = ''
        if len( _deals ) > 0:
            #raise Exception( _deals[0]['details'] )
            #deals = pickle.loads( str( _deals[0]['details'] )  )
            _details = str( _deals[0]['details'] )
            #offers = t.fetch_local_deals(channel) 
            _str_deals = HTMLParser.HTMLParser().unescape(_details)
            deals = eval(_str_deals)
        
        return deals       
    
    def fetch_remote_deals(self, data, details): 
        channel = data['value']
        _offers = self.get_offers( data )        
        
        _offers_d = self.get_offers_d( _offers )
        if _offers_d == None:
            return None
            
        #raise Exception( str( len( _offers ) ) + str( _offers_d ) )
        _offers_f = self.format_offers( _offers_d )
        offers = str( _offers_f )
        self.save_deal_channel( channel, details, offers )
        
        return _offers_f    
    
    def test_save_channel(self):
        #channel = 'company'
        #_offers = 'hey there'
        #details = {'location':'National','geo':'national'}
        #offers = ''
        #offers = pickle.dumps( _offers )
        #raise Exception( offers )
        #self.save_deal_channel( channel, details, offers )
        pass
    
    def format_offers(self, offers):
        return self._format_offers(offers)
    
    def _format_offers(self, offers):
        fields = ['small_image_url', 'large_image_url', 'end_date', 'title', 
                  'headline', 'sold_quantity', 'price', 'value','discount_amount',]
        _offers = []
        #raise Exception( offers )
           
        for o in offers[1:]:
            _o = {}
            for i in fields:
                
                if i in o.keys():
                    #pass
                    _o[i] = o[i].get('value', '')
                else:
                    #pass
                    _o[i]='_str_'+o
            
            _o['name']=o['merchant']['name']['value']
            _o['discount'] = refine_dollar( o.discount_percentage )            
            _offers.append( _o )
            #i = i + 1
        return _offers
                
    def save_deal_channel(self, channel, details, offers):
        n = datetime.now()
        t = n + timedelta(0, 3600)
        _timestamp = t.strftime("%Y-%m-%d %H:%M:%S")
        sql="""INSERT INTO Deal.Deal_Channel_Cache
        ( DealChannelTimeStamp, DealChannelLocation,
        DealChannelGeo, DealChannelName, DealChannelDetails )
        VALUES ( '%s', '%s', '%s', '%s', '%s')
        """
        vals=( _timestamp, 
               details['location'], 
               details['geo'], 
               channel, 
               self.dbh.escape( offers ) ) 
        
        res = self.dbh.query( sql % vals )
        self.dbh.commit()
        return res
    
    def channel_local_exists(self, channel):
        sql="SELECT * FROM Deal.Deal_Channel_Cache where DealChannelName = '%s'"
        return self.dbh.one( sql % channel )
        
    
    ### Leads ###
    def save_lead(self, post_data={}):
        d = {'first_name':'', 'last_name':'', 'mobile_phone':'', 'channel':'',
                 'email':'', 'zipcode':0, 'ipaddress':'111.111.111.111'}
        d.update( post_data )
        self.lead = d
        sql = """INSERT INTO Deal.Lead
        (FirstName, LastName, MobilePhone, Email, ZipCode, IPAddress, Channel) 
        VALUES 
        ('%s', '%s', '%s', '%s', '%s', '%s', '%s')
        """
        vals = ( d['first_name'], d['last_name'], d['mobile_phone'],
                 d['email'], str(d['zipcode']).zfill(5), d['ipaddress'], 
                 d['channel'], )
        
        res = self.dbh.query( sql % vals )
        self.dbh.commit()
        
        if res:
            return True

            
    def update_lead(self, leadid, status):
        sql = """UPDATE Deal.Lead
        set Status = '%s'
        where LeadID = '%s'
        """
        vals = ( status, leadid )
        return self.dbh.query( sql % vals)
        
    
    
def test_submit():
    data = {'email': 'none@none.com',
            'channel': 'company-new-york',
            'mobile_phone': '##########'}    
    
    T = company()
    if T.save_lead(data):
        
        if T.send_lead():
            pass
            #offers = T.get_offers()


def refine_dollar( initial ):
    return int( abs( round( float( initial ), 0 ) ) )

def get_dump(_file):
    f = open(_file)
    r = f.read()
    f.close()
    return r 
    
def write_dump(content, _file=''):
    if not _file:
        _file="/home/user/dump"
        
    print 'opening w'
    f = open(_file, "w")
    print 'writing..'
    f.write(content)
    print 'closing..'
    f.close()
    print 'closed.'
    
        
def main():
    
    
    channel='company-san-francisco'
    details = {'location':'National','geo':'national'}
    data = { 'field': 'channel', 'value': 'company-los-angeles' }
    t = company()
    
    offers, details = t.get_deals( channel )
    
    exit()
    _save=True
    _pull=True
    if _save:
        _file = "/home/user/dump"
        raw = get_dump( _file )

        deals = t.get_offers_d( raw )
        _offers = t.format_offers(deals)
    
        #offers = pickle.dumps( t.dbh.escape( str( _offers ) ) )
        offers = t.dbh.escape( str( _offers) ) 
        #offers = self.dbh.escape( _offers )
        #raise Exception( len(offers ))
        t.save_deal_channel( channel, details, offers )
    
    if _pull:
    
        offers = t.fetch_local_deals(channel) 
        offers = HTMLParser.HTMLParser().unescape(offers)
        offers = eval(offers)
        #print offers
        pprint( offers )
        
        
    exit()
    
    #print len(deals)
    #for d in offers:
    #    print d
    exit()
    
    #raw = t.get_offers( data )
    #pprint( raw )
    #write_dump( raw )
    
    
    
    #raw = get_dump()
    #pprint( raw )
    #raw_blocks = raw.split("<merchant>")
    #c = len( raw_blocks[1:] )
    #print c
    
    for r in raw_blocks[1:]:
        print '%s\n----------------------\n' % r
        
    exit()
    
    _offers = t.get_offers_d( raw )
    c = len( _offers )
    print c
    #for o in _offers:
    #    print o
    
    
    #offers = t.get_offers_d()
    #t.get_offers_deals( data['value'])
    sys.exit()
    ### or
    
    #offers = t.get_offers_dict( raw )
    #for o in offers:
    #    print o.title
    
        
if __name__ == "__main__":
    test_submit()
    #main()

    #t = company()
    #t.test_save_channel()
    #t.fetch_remote_deals()
    
