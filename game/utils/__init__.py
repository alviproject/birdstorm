from django.http.response import HttpResponsePermanentRedirect
from game.utils.config import config
from urllib.parse import urlunparse
from urllib.parse import urlparse
from django.conf import settings


dev_domains = {'localhost', '127.0.0.1'}


class DomainMiddleware:
    def process_request(self, request):
        url = urlparse(request.build_absolute_uri())
        if url.hostname in dev_domains:
            return
        subdomain = url.netloc.split('.')[0]
        if subdomain not in settings.SUBDOMAINS:
            new_url = urlunparse((url.scheme, 'www.'+settings.DOMAIN_NAME, url.path, url.params, url.query, url.fragment))
            return HttpResponsePermanentRedirect(new_url)