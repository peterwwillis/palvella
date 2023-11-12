# Parts of this module taken from https://github.com/bloomberg/python-github-webhook/tree/master
# due to that module being written for Flask.
# That code is licensed here: https://github.com/bloomberg/python-github-webhook/blob/master/LICENSE


from github_webhook import Webhook

from webrunit.lib.logging import logging as logging
from webrunit.lib.trigger.base import Trigger

type = "github_webhook"

class GitHub_Webhook(Trigger):
    """ Class of the GitHub Webhook trigger.
        Inherits the Trigger class.
    """

    type = type

    def __init__(self, **kwargs):
        """ When creating a new object, pass arbitrary key=value pairs to update the object.
        """
        logging.debug("GitHub_Webhook(%s)" % (kwargs))
        self.__dict__.update(kwargs)

        # initialize above as webhook = GitHub_Webhook(web_app=web_app, endpoint=endpoint, secret=secret)
        if app is not None:
            self.init_app(app, endpoint, secret)

    def init_app(self, app, endpoint="/postreceive", secret=None):
        self._hooks = collections.defaultdict(list)
        self._logger = logging.getLogger("webhook")
        if secret is not None:
            self.secret = secret
        # Flask function
        app.add_url_rule(rule=endpoint, endpoint=endpoint, view_func=self._postreceive, methods=["POST"])

    def _get_digest(self):
        """Return message digest if a secret key was provided"""
        return hmac.new(self._secret, request.data, hashlib.sha1).hexdigest() if self._secret else None

    def hook(self, event_type="push"):
        def decorator(func):
            self._hooks[event_type].append(func)
            return func
        return decorator

    def _postreceive(self):
        """Callback from Flask"""

        digest = self._get_digest()
        if digest is not None:
            sig_parts = _get_header("X-Hub-Signature").split("=", 1)
            if not isinstance(digest, six.text_type):
                digest = six.text_type(digest)
            if len(sig_parts) < 2 or sig_parts[0] != "sha1" or not hmac.compare_digest(sig_parts[1], digest):
                abort(400, "Invalid signature")

        event_type = _get_header("X-Github-Event")
        content_type = _get_header("content-type")
        data = (
            json.loads(request.form.to_dict(flat=True)["payload"])
            if content_type == "application/x-www-form-urlencoded"
            else request.get_json()
        )
        if data is None:
            abort(400, "Request body must contain json")
        self._logger.info("%s (%s)", _format_event(event_type, data), _get_header("X-Github-Delivery"))
        for hook in self._hooks.get(event_type, []):
            hook(data)
        return "", 204

def _get_header(key):
    """Return message header"""
    try:
        return request.headers[key]
    except KeyError:
        abort(400, "Missing header: " + key)

webhook = GitHub_Webhook(app) # Defines '/postreceive' endpoint

@webhook.hook()
def on_push(data):
    print("Got push with: {0}".format(data))

