class Config(object):
    """
    This config is for development use. Do not run this app consistently on 
    the open web without further access restrictions
    """
    DEBUG = True
    TESTING = True
    CSRF_ENABLED = True
    SECRET_KEY = ""
