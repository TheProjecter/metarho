import mimeparse.py

MIME_TYPE = {
    'rss': ['application/rss+xml', 'text/xml'],
    'json': ['application/json', 'text/json'],
    'atom': ['application/atom+xml'],
    'rdf': ['application/rdf+xml'],
}

def negotiate_response(mime_types, new_fn):
    '''
    If request is in mime_types then return new_fn instead of view_fn.

    :param mime_types: A list containing mime types to associate return
                       new_fn on.
    :param new_fn: Bound method to return if requested mime type is in mime_type.
    
    '''
    def decorator(view_fn):
        if request.META.get('HTTP_ACCEPT', 'text/html') in mime_types:
            return new_fn(request, *args, **kwargs)
        return view_fn(*args, **kwargs)
    return decorator

def format_based_response(format, new_fn):
    '''
    Provides compatability with URLs from things like wordpress that
    request content type via a querystring param like '?format=rss'

    :param format: String indicating format to return new_fn for.
    :param new_fn: Bound method to return if format querystring matches format.

    '''
    def decorator(view_fn):
        if request.GET.get('format', None) == format:
            return new_fn(request, *args, **kwargs)
        return view_fn(*args, **kwargs)
    
    return decorator