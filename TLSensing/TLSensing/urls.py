"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

from django.conf.urls import patterns
from django.conf.urls import include
from django.conf.urls import url

from Core import urls as core_urls

urlpatterns = patterns('',
    url(r'^', include(core_urls)),
)
