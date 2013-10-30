#!/usr/bin/which python2.6
"""
Provides a pseudo language used to handle find/replace type functionality
in text strings.  An example of this would be strings that are stored
in a database which need to have dynamic data.  A helper function called
find_replace is provided for easy access to the Formatting class

Example:
 mystring = 'today is {{DateTime:date_format(\"%m/%d/%Y\")'
 print( find_replace( {'DateTime': datetime.datetime.today()}, mystring ) )
"""
import re
from datetime import datetime, timedelta, date, time
from urllib import quote_plus
import time
from dateutil.parser import parse as dateparse
import traceback
from parentclass import eblob,logit,dblob
from pprint import pprint

class Pseudo(object):
    
    def __init__(self, key, value, the_lead=None ):
        self.key = key
        self.value = value
        self.the_lead = the_lead
        
    def phone(self, separator='-'):
        """Parses phone field and separates it by passed parameter
        
        >>> Formatting('6466885022').phone()
        '646-688-5022'
        """
        phone=str(self.value)
        if len(phone) < 9:
            logit(self.value, 'bad_format.log')
            return self.value
        return separator.join([phone[:3],phone[3:6], phone[6:]])

    def ssn(self, separator='-'):
        """
        
        >>> Formatting('123456789').ssn()
        '123-45-6789'
        """
        #strip off null characters incase this is an old version of the decriptor
        self.value=self.value.replace(chr(0), '')
        if len(self.value) != 9:
            return ''
        return separator.join([self.value[:3], self.value[3:5], self.value[5:9]])

    def months_to_date(self, format="%Y-%m-%d"):
        """
        Convert an integer representing months to a date in the past
        """
        return (date.today() - timedelta(int(self.value)*365/12)).strftime(format)

    
    def months_to_year(self, *args, **kwargs):
        """Converts an integer representing months into in integer
        representing years.

        >>> Formatting(40).months_to_year()
        '3'
        """
        yrs=self.months_format('Y')
        if yrs == '0':
            return '1'
        return yrs
    

    def sub_string(self, params):
        """
        Returns a sub-string of self.value depending on the
        parameters passed.  You can pass either 1, 2, or 3
        parameters to this function depending on the desired
        functionality.

        >>> Formatting('hello').sub_string('1')
        'e'
        >>> Formatting('hello').sub_string('0,2')
        'he'
        >>> Formatting('hello').sub_string('0,4,2')
        'hl'
          
        """
        self.value=str(self.value)
        if ',' in params:
            params=[ int(x.strip()) for x in params.split(',')]
            #logit(params, 'substr.log')
            if len(params)<3:
                return self.value[params[0]:params[1]]
            else:
                return self.value[params[0]:params[1]:params[2]]
        else:
            return self.value[int(params)]
        
    def format_hitpath(self, params):
        return str(self.value).split('-')[0]
            
    def months_format(self, format ):
        """
        Converts an integer representing months into either years
        or remaining months after years have been calculated depending
        on the passed format. If the passed parameters contain either YY or MM,
        this function will zero fill the string to the second place.

        Acceptable parameters:
          'Y','YY','M','MM'

        >>> Formatting(24).months_format('YY')
        '02'
        >>> Formatting(72).months_format('Y')
        '6'
        >>> Formatting(39).months_format('MM')
        '03'
        >>> Formatting(182).months_format('M')
        '2'
        
        """
        try:
            months= int(self.value)
        except:
            raise ValueError(self.key)

        yrs = str(months / 12)
        mth = str( months%12 )
        # Replace years
        retval = str(format).replace("YY", yrs.zfill(2)).replace("Y", yrs.zfill(1) )
        # Replace months
        retval = retval.replace("MM", mth.zfill(2) ).replace("M", mth.zfill(1) )
        
        return str(retval)
    
    def zfill(self, length ):
        try:
            return str(self.value).zfill( int(length) )
        except:
            return self.value
    
    def strip_char( self, character ):
        """
        Removes a character from the string
        
        >>> Formatting('Hi Mom').strip_char('o')
        'Hi Mm'

        """
        #return str(self.value).strip(character)
        return str(self.value).replace(character, '')
    

    def replace_char(self, params):
        """
        Performs a case-sensitive character replacement

        >>> Formatting('Hey tHere').replace_char('H,h')
        'hey there'
        
        """
        before,after = params.split(',')
        return str(self.value).replace(before, after)

    def date_format(self, format):
        """
        Will return the passed datetime object in the desired format

        >>> Formatting('2003-11-19').date_format('%m-%d-%Y')
        '11-19-2003'

        """
        if hasattr(self.value, 'strftime') is True:
            return self.value.strftime(format)
        else:
            if re.match(r'\d{4}-\d{1,2}-\d{1,2}', self.value):
                return datetime.strptime( str(self.value), '%Y-%m-%d').strftime(format)
            else:
                return ''
        
    def field_map(self, params):
        """
        Formatting('Own').field_map( 'Rent:2|Own:1' )
        """
        #need to strip out extra quotes
        params = re.sub(r"['\"]", "", str(params))
        if '|' not in params and ':' in params:
            return params.split(':')[1]
        
        if '|' not in str(params) and ':' not in str(params):
            return self.value
        
        chunks=params.split('|')

        default=chunks[0].split(':')[1]
        self.value=str(self.value)
        for block in chunks:
            old,new = block.split(':')
            if str(self.value).lower() == str(old).lower():
                return str(new)
        return default


    def value_match(self, params ):
        """
        Match a value and return the passed mapping.
        If no match is found, return the first mapping result as the default
        If no mapping pairs were passed, return the passed value.
        >>> Formatting('own').value_match('own=O,rent=R,other=X')
        'O'
        >>> Formatting('parents').value_match('Other=X,Rent=R,Own=O')
        'X'
        """
        params = re.sub(r"['\"]", "", params)
        res=self.value
        cnt=1
        for block in params.split(','):
            field, retval = block.split('=')
            if cnt==1:
                res=str(retval)
            if str(self.value).lower() == str(field).lower():
                res=str(retval)
                break
            cnt+=1
        return res

    def date_from_months(self, format ):
        date = datetime.now() - timedelta(weeks=(int(self.value)*4))
        return date.strftime( format ).strip("'").strip('"')

    # def date_to_months(self, empty):
    #     return ( date.today() - timedelta( int(self.value)))
    
    def date_to_months(self, SinceDate=None):
        """
        Find the difference in months between either a date supplied or today
        Else 0
        """
        if not self.value:
            return 0
        
        if SinceDate:
            delta = SinceDate - self.value
        else:
            delta = datetime.today() - self.value 
        return str(int(delta.days / 30 ))
        
    def date_to_years(self, empty):
        
        if hasattr(self.value, 'strftime') is True:
            dob = self.value
        else:
            try:
                dob = dateparse( self.value ).date()
            except:
                return self.value
            #dob = datetime.strptime(str(self.value), '%Y-%m-%d').date()
            
        today = date.today()
        
        delta = today - dob
        years = delta.days/365
        return str(int(years))

    def boolean(self, empty=None):
        yes=('yes','true','1')
        if str(self.value).lower() in yes:
            return 'true'
        else:
            return 'false'

    def bool_to_int(self, empty=None):
        return '1' if self.boolean() == 'true' else '0'
    
    def encrypt(self, nothing=None):
        encval = eblob(str(self.value))
        return quote_plus(encval).replace('%','%%')

    def decrypt(self, nothing=None):
        return dblob(str(self.value)).replace(chr(0), '')

    def yn(self, empty):
        return self.yesno(empty)[0]
    
    def yesno(self, empty):
        retval = 'Yes' if self.boolean() == 'true' else 'No'
        if empty != '':
            retval = retval.upper()
        return retval

    def upper(self,empty=None):
        return str(self.value).upper()
    
    def Capitalize(self, empty=None):
        return str(self.value).capitalize()
    
    def gte(self, params ):
        if len(params.split(',')) < 3:
            raise ValueError( "You must pass three arguments to get()" )
        min_val,is_true,is_false = params.split(',')
        return is_true if int(self.value) >= int(min_val) else is_false

def find_replace( lead,  data, verbose=False, formatting_obj=None ):
    """
    going to search for the {{FieldName:Function_Name(params)}}
    then pass all that to re.sub which you can pass a callback to
    
    Need to be able to handle both data structures and strings
    """
    regex = re.compile(r"\{\{\s?(?P<FieldName>[a-z0-9_\-\.]+)\:(?P<functionName>\w+)\((?P<params>[\w\-\'\"\s\=\,%\/\:\|]+)?\)\s?\}\}", re.I)

    if not formatting_obj:
        formatting_obj=Formatting
    else:
        if not issubclass(formatting_obj, Formatting):
            raise ValueError( "%s must be a subclass of Formatting" % formatting_obj )
    if isinstance( data, str ):
        regex = re.compile(r"\{\{\s?(?P<FieldName>[a-z0-9_\-\.]+)\:(?P<func1>\w+)\((?P<params1>[\w\-\'\"\s\=\,%\/\:\|]+)?\)(\:(?P<func2>\w+)\((?P<params2>[\w\-\'\"\s\=\,%\/\:\|]+)?\))?(\:(?P<func3>\w+)\((?P<params3>[\w\-\'\"\s\=\,%\/\:\|]+)?\))?\s?\}\}", re.I)
        _m = re.compile(r'\{\{.*?\}\}', re.I)
        matches = _m.findall(data)
        if matches:
            for m in matches:
                
                if regex.match(m):
                    _t = regex.match(m).groupdict()
                    try:
                        f = formatting_obj( _t['FieldName'], lead[_t['FieldName']], the_lead=lead )
                    except:
                        raise ValueError( { _t['FieldName']: lead.keys() } )
                    
                    if _t['params1'] is None:
                        p1=''
                    else:
                        p1= re.sub(r"['\"]","",_t['params1']) 
                    theValue = getattr(f, _t['func1'])( p1 )
                    if _t['func2']:
                        if _t['params2'] is None:
                            p2=''
                        else:
                            p2=re.sub( r"['\"]","",_t['params2'])
                        theValue = getattr(formatting_obj(_t['FieldName'], theValue, the_lead=lead) , _t['func2'])(p2)
                    if _t['func3']:
                        if _t['params3'] is None:
                            p3=''
                        else:
                            p3=re.sub( r"['\"]","",_t['params3'])
                        theValue = getattr(formatting_obj(_t['FieldName'], theValue, the_lead=lead) , _t['func3'])(p3)
                    if theValue is None:
                        theValue=''
                    try:
                        data = re.sub( re.escape(m), str(theValue), data, re.I)
                    except:
                        logit("%s\n%s" % (m, traceback.format_exc()), 'autoinsurance/ping_exception.log')
                        
                        
    else:
        try:
            for i in data:
                data[i] = find_replace( data[i] )
        except Exception, e: pass

    if verbose:
        return data % lead

    
    return data

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
