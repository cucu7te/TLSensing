"""
Django settings for TLSensing project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/

@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

from mongoengine import connect
connect('tls_sensing_db')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4+4n7!z13lu$ph8jk^b17c9c)c(==_6n(y%&-nh)k68hi(i^!n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'Core',
    'ws4redis'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'ws4redis.context_processors.default',
)

ROOT_URLCONF = 'TLSensing.urls'

WSGI_APPLICATION = 'TLSensing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE ='Europe/Rome' #'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

# Create the figures directory if necessary
if not os.path.exists(os.path.join(BASE_DIR, "figures")):
    os.makedirs(os.path.join(BASE_DIR, "figures"))
CHART_URL = os.path.join(BASE_DIR, "figures")

#set some HTTP response codes
INTERNAL_SERVER_ERROR = 500
BAD_GATEWAY = 502
GATEWAY_TIMEOUT = 504
BAD_REQUEST = 400
METHOD_NOT_ALLOWED = 405
NOT_FOUND = 404

WEBSOCKET_URL = '/ws/'
WS4REDIS_EXPIRE = 7200
WSGI_APPLICATION = 'ws4redis.django_runserver.application'

DATETIME_FORMAT = 'd/m/Y, G:i:s'  #modified for new version

# Create the log directory if necessary
if not os.path.exists(os.path.join(BASE_DIR, "logs")):
    os.makedirs(os.path.join(BASE_DIR, "logs"))
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'verbose_scheduler': {
            'format' : "[%(asctime)s] [SCHEDULER] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'services': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/services.log',
            'formatter': 'verbose'
        },
        'views': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/views.log',
            'formatter': 'verbose'
        },
        'decorators': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/decorators.log',
            'formatter': 'verbose'
        },
        'acquire_values': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/acquire_values.log',
            'formatter': 'verbose_scheduler'
        },
        'acquire_values_oneshot': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/acquire_values.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'Core.services': {
            'handlers': ['services'],
            'level': 'DEBUG',
        },
        'Core.views': {
            'handlers': ['views'],
            'level': 'DEBUG',
        },
        'Core.decorators': {
            'handlers': ['decorators'],
            'level': 'DEBUG',
        },
        'Core.management.commands.acquire_values_oneshot': {
            'handlers': ['acquire_values_oneshot'],
            'level': 'DEBUG',
        },
        'Core.management.commands.acquire_values': {
            'handlers': ['acquire_values'],
            'level': 'DEBUG',
        },
        'Core.motes.motes': {
            'handlers': ['acquire_values_oneshot'],
            'level': 'DEBUG',
        },
    }
}

PROCESSES = {
    "acquire-values": {
        'human_name': "Pull Acquisition Scheduler",
        'hide': False
    },
    "acquire-values-oneshot": {
        'human_name': "Pull Acquisition - One-Shot",
        'hide': False
    },
    "redis-server": {
        'human_name': "Redis",
        'hide': False
    },
    "tlsensing-server": {
        'human_name': "TLSensing Web Server",
        'hide': True    # Leaving it there would be like putting a self-destruct button
    }
}

ACCORDIONS = [
{ "name": "history",
  "label": "Measures",
  "mote_types": ["OpenMote", "TelosB"],
  "callback": "mote_history(mote, 'table')" },
{ "name": "stats",
  "label": "Statistics",
  "mote_types": ["OpenMote", "TelosB"],
  "callback": "mote_stats(mote)" },
{ "name": "notifications",
  "label": "Notifications",
  "mote_types": ["OpenMote", "TelosB"],
  "callback": "notifications(mote, 10)" },
{ "name": "base",
  "label": "Graphs",
  "mote_types": ["OpenMote", "TelosB"],
  "callback": "graphs(mote, 'base')" },
{ "name": "acc",
  "label": "Accelerometer Graphs",
  "mote_types": ["OpenMote"],
  "callback": "graphs(mote, 'acc')" },
{ "name": "acc_details",
  "label": "Accelerometer Detailed Graphs",
  "mote_types": ["OpenMote"],
  "callback": "graphs(mote, 'acc_details')" }
]

USERSETTINGS = {
    "pullacquisition_interval": {
        'default_value': 15,
        'delta_message': "Pull Acquisision Interval changed. This setting will apply after the next scheduled acquisition has ended. To apply immediately, restart the Pull Acquisition Scheduler",
        'human_name': "Pull Acquisision Interval (in minutes)",
        'related_processes': ["acquire-values"]
        },
    "pullacquisition_coapport": {
        'default_value': 5683,
        'delta_message': "",
        'human_name': "Pull Acquisition CoAP Port",
        'related_processes': ["acquire-values"]
        },
    "pushserver_coapport": {
        'default_value': 5684,
        'delta_message': "Restart the Push Server to apply settings",
        'human_name': "Push Server CoAP Port",
        'related_processes': [""]
        },
    "sampledmeasures": {
        'default_value': 10,
        'delta_message': "",
        'human_name': "Sampled No. of Measures",
        'related_processes': [""]
        }
}

USERSETTINGS_PATH = os.environ['VIRTUAL_ENV'] + "/TLSensing/usersettings.conf"

MEASURE_TYPES = [
    {"field": "temperature",
     "maxt_field": "max_temp",
     "mint_field": "min_temp",
     "shortlabel": "temperature",
     "label": 'Temperature<br/><span style="font-weight: normal ">(&#176C)</span>',
     "onelinerlabel": 'Temperature <span style="font-weight: normal ">(&#176C)</span>',
     "mote_types": ["OpenMote", "TelosB"]},
    {"field": "humidity",
     "maxt_field": "max_humi",
     "mint_field": "min_humi",
     "shortlabel": "humidity",
     "label": 'Relative Humidity<br/><span style="font-weight: normal">(%)</span>',
     "onelinerlabel": 'Relative Humidity <span style="font-weight: normal">(%)</span>',
     "mote_types": ["OpenMote", "TelosB"]},
    {"field": "light",
     "maxt_field": "max_light",
     "mint_field": "min_light",
     "shortlabel": "light",
     "label": 'Light<br/><span style="font-weight: normal">(lux)</span>',
     "onelinerlabel": 'Light <span style="font-weight: normal">(lux)</span>',
     "mote_types": ["OpenMote", "TelosB"]},
    {"field": "accel_x",
     "maxt_field": "max_acc_x",
     "mint_field": "min_acc_x",
     "shortlabel": "acceleration x-axis",
     "label": 'Accelerometer<br/>x-axis<br/><span style="font-weight: normal">(mg)</span>',
     "onelinerlabel": 'Accel. x-axis <span style="font-weight: normal">(mg)</span>',
     "mote_types": ["OpenMote"]},
    {"field": "accel_y",
     "maxt_field": "max_acc_y",
     "mint_field": "min_acc_y",
     "shortlabel": "acceleration y-axis",
     "label": 'Accelerometer<br/>y-axis<br/><span style="font-weight: normal">(mg)</span>',
     "onelinerlabel": 'Accel. y-axis <span style="font-weight: normal">(mg)</span>',
     "mote_types": ["OpenMote"]},
    {"field": "accel_z",
     "maxt_field": "max_acc_z",
     "mint_field": "min_acc_z",
     "shortlabel": "acceleration z-axis",
     "label": 'Accelerometer<br/>z-axis<br/><span style="font-weight: normal">(mg)</span>',
     "onelinerlabel": 'Accel. z-axis <span style="font-weight: normal">(mg)</span>',
     "mote_types": ["OpenMote"]}
]

COAP_QUERIES = {
    "T": {
        "label": "Temperature",
        "measure_types": ["temperature"],
        "mote_types": ["OpenMote", "TelosB"]
    },
    "H": {
        "label": "Relative Humidity",
        "measure_types": ["humidity"],
        "mote_types": ["OpenMote", "TelosB"]
    },
    "L": {
        "label": "Light",
        "measure_types": ["light"],
        "mote_types": ["OpenMote", "TelosB"]
    },
    "A": {
        "label": "Acceleration",
        "measure_types": ["accel_x", "accel_y", "accel_z"],
        "mote_types": ["OpenMote"]
    }
}

MOTE_TYPES = {
    "TelosB": {
        "label": "TelosB"
    },
    "OpenMote": {
        "label": "OpenMote"
    }
}

SUPERVISOR_URL = 'http://localhost:9001/RPC2'

#be careful with appended path. Be sure the coap dir is in the path below.
import sys
import os
sys.path.append(os.environ['VIRTUAL_ENV'] + '/TLSensing/coap')
