"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

from django.conf.urls import patterns
from django.conf.urls import url

from Core.views import dashboard
from Core.admin import adminviews
from Core import views

urlpatterns = patterns('',
    # Pannello di amministrazione
    url(r'^admin$', dashboard),
    url(r'^ajax/admin/(?P<page>(supervisor|motes|settings))/$', adminviews.main_subpage, name="ajax_admin_processes"),
    url(r'^admin/motes/(?P<action>(remove|add|remove_data))$', adminviews.motes_doaction),
    url(r'^admin/settings/save$', adminviews.settings_save),
    url(r'^admin/supervisor/(?P<action>(start|stop|restart))$', adminviews.supervisor_doaction),

#############################################################################
    url(r'^$', views.index),
    url(r'^section/(?P<section_name>[\w|\W]+)/(?P<argument>[\w|\W]*)$', views.render_section),
    url(r'^data/thresholds/(?P<mote_id>[\w|\W]+)$', views.thresholds),
    url(r'^data/discovery/(?P<mote_id>[\w|\W]+)$', views.discovery),
    url(r'^data/poll/(?P<mote_id>[\w|\W]+)$', views.poll),
    url(r'^run/avo/$', views.run_avo),
    url(r'^admn/log/(?P<pwd>[\w]+)$',views.log_in),
    url(r'^admn/chpwd/oldpwd/(?P<opwd>[\w]+)$',views.check_password),
    url(r'^admn/chpwd/newpwd/(?P<npwd>[\w]+)$',views.store_newpwd)
)
