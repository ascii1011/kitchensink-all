import urllib

class URLcn(object):
    
    def __init__(self, url):
        self.url = url
        
    def request(self):
        if self.url:
            
            conn = urllib.urlopen( self.url )
            content = conn.read()
        
            conn.close()
            return content
        else:
            return 'urllib_conn->error'
             
        
if __name__ == "__main__":        
    url = 'http://www.google.com'
    c = URLcn(url)
    
    print c.request()
