"""
@author: Francesco Bruni <brunifrancesco02@gmail.com>
@author: Enrico Nasca <enriconasca@gmail.com>
@author: Gianfranco Micoli <micoli.gianfranco@gmail.com>
"""

from django.utils.functional import wraps
from django.http import HttpResponse
#from Core.services import find_all_sensors
from Core.models import Mote
from TLSensing.settings import NOT_FOUND
from TLSensing.settings import METHOD_NOT_ALLOWED
from urlparse import urlparse, parse_qs

import logging
logger = logging.getLogger(__name__)

def defaults(view):
    """
    Simply inits an empty data dictionary and applies a simple
    exception handler to reduce boilerplate code throughout the system
    """
    @wraps(view)
    def inner(request, *args, **kwargs):
        try:
            kwargs["out"] = {}
            return view(request, *args, **kwargs)
        except Exception, e:
            msg = view.__name__ + ": " + repr(e)
            logger.error(msg)
            return HttpResponse(msg)
        return view(request, *args, **kwargs)
    return inner

def methods(method):
    """
    Elaborates view only if it's an allowed method.
    For POST requests, gathers the POST data
    """
    def actualDecorator(view):
        @wraps(view)
        def inner(request, *args, **kwargs):
            if request.method in method:
                if request.method == "POST":
                    import json
                    kwargs["post_data"] = json.loads(request.body)
                    return view(request, *args, **kwargs)
                return view(request, *args, **kwargs)
            else:
                return HttpResponse("Method not allowed", status=METHOD_NOT_ALLOWED)
        return inner
    return actualDecorator

# DEPRECATED: Still used in administration panel. Migrate to "methods". 
# Check views.py as an example
def get_post_data(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        import json
        kwargs["post_data"] = json.loads(request.body)
        return view(request, *args, **kwargs)
    return inner

# def mote_object(view):
#     """
#     A Python method to implement the decorator pattern.
#     It gets mote(s) looking for "mote_id" param in the URL request
#     and return the modified view.
    
#     @param view: the decorated view
#     """
#     @wraps(view)
#     def inner(request, *args, **kwargs):
# 	"""
# 	Handle the decoration function. 
# 	Return an HTTP 404 response if requested mote has not been found.
	
# 	@param request: the request coming from the decorated view
	
# 	@return the modified view along with mote entity(ies)	
# 	"""
#         try:
#             if "mote_id" in kwargs:
#                 kwargs["mote"] = Mote.objects.get(id=kwargs["mote_id"])
#                 return view(request, *args, **kwargs)
#             else:
#                 kwargs["motes"] = find_all_sensors()
#                 return view(request, *args, **kwargs)
#         except Mote.DoesNotExist as e:
# 	    logger.error("Requested mote (id: %s) not found" %kwargs["mote_id"]) 
#             return HttpResponse("Mote does not exist", status=NOT_FOUND)
#     return inner

def only_ajax(view):
    """
    Elaborates a view only if the request comes
    from AJAX
    """
    @wraps(view)
    def inner(request, *args, **kwargs):
        try:
            logger.info(request.path + ": " + str(request.is_ajax()))
            if request.is_ajax():
                return view(request, *args, **kwargs)
            else:
                return HttpResponse("Access denied")
        except Exception, e:
            logger.error(repr(e))
            return HttpResponse(repr(e))
    return inner

# DEPRECATED: Possibly migrate every part of the code that uses "check_context" to use
# the "defaults" decorator
def check_context(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        context = {}
        try:
            context = kwargs["context"]
        except Exception, e:        # If it's not present, wing it
            context["result"] = {"status": "", "message": ""}
            kwargs["context"] = context
        return view(request, *args, **kwargs)
    return inner

# NOT USED ANYMORE
# Check before removal
def init_context(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        context = {}
        kwargs["context"] = context
        return view(request, *args, **kwargs)
    return inner