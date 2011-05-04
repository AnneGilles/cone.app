from datetime import datetime
from pyramid.threadlocal import get_current_request


def app_config():
    import cone.app
    return cone.app.cfg


class DatetimeHelper(object):
    
    def w_value(self, val):
        if isinstance(val, datetime):
            return self.dt_to_iso(val)
        if not isinstance(val, unicode):
            val = str(val).decode('utf-8')
        return val
    
    def r_value(self, val):
        try:
            return self.dt_from_iso(val)
        except ValueError:
            if not isinstance(val, unicode):
                val = str(val).decode('utf-8')
            return val
    
    def dt_from_iso(self, str):
        return datetime.strptime(str, '%Y-%m-%dT%H:%M:%S')
    
    def dt_to_iso(self, dt):
        iso = dt.isoformat()
        if iso.find('.') != -1:
            iso = iso[:iso.rfind('.')]
        return iso

def instance_property(attribute_name):
    """Decorator like ``property``, but underlying function is only called once
    per instance.  
    """
    def decorator(func):
        def wrapper(self):
            if not hasattr(self, attribute_name):
                setattr(self, attribute_name, func(self))
            return getattr(self, attribute_name)
        wrapper.__doc__ = func.__doc__
        return property(wrapper)
    return decorator