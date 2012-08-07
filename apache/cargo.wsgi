import os, sys

#Calculate the path based on the location of the WSGI script.
apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.dirname(project)
sys.path.append(workspace) 
sys.path.append(project)
path = '/var/www/cargo/cargo'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'cargo.apache.settings_production'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

print >> sys.stderr, sys.path
