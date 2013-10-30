import types
import os

from django.http import HttpResponseRedirect
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from company.django.views import render_it
from company.django.forms import DealContactForm
from company_api import Company

def main(request, template="index.html"):
    t = Company()
    _ch = t.fetch_static_channels()
    channels = [ ( key, value['location'] ) for key, value in _ch.iteritems() ]
    template_vars={'channels': channels }
    
    form=DealContactForm()

    
    if request.method == 'POST':                
        form=DealContactForm(request.POST)
        if form.is_valid():
            raise ValidationError('form is clean')

    template_vars['form']=form
    return render_it( request, template, template_vars)
