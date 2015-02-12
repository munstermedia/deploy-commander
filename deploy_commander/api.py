# api.py

import falcon


class BitbucketHookResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ('\nSome nice hook! '
                     'This is gonna rock!.\n'
                     '\n'
                     '    ~ Ference van Munster\n\n')

# falcon.API instances are callable WSGI apps
app = falcon.API()

bitbucket_hook = BitbucketHookResource()

# things will handle all requests to the '/things' URL path
app.add_route('/api/1.0/hook/bitbucket', bitbucket_hook)