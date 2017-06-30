"""
WSGI config for TLSensing project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/

@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TLSensing.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
