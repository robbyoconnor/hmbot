import json, re, requests, os, sys, logging, bottle

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('hmbot')
logger.setLevel(logging.DEBUG)

slack_token         = os.environ['SLACK_TOKEN']
verification_token  = os.environ['VERIFICATION_TOKEN']

def api_call(method, **kwargs):
    """
    Perform a Slack Web API call. It is supposed to have roughly the same
    semantics as the official slackclient Python library, but 
    """
    kwargs['token'] = slack_token
    r = requests.post("https://slack.com/api/" + method, data=kwargs)
    r.raise_for_status()
    response = r.json()
    if not response.get('ok'):
        logger.error(f"Slack error: {response.get('error')}")
        raise Exception(f"Slack error: {response.get('error')}")

    if response.get('warning'):
        logger.warning(f"Slack warning: {response.get('warning')}")

    return response

def handle_message(message):
    if 'type' not in message:
        logger.info(f"type missing in message {message}")
        return

    if message['token'] != verification_token:
        logger.error(f"verification token {message['token']} is wrong")
        return
        
    t = message['type']
    
    if t == 'url_verification':
        return message['challenge']
    elif t == 'event_callback':
        return handle_event(message['event'])
    else:
        logger.debug(f"unknown message type {t} in message {message}")

def handle_event(event):
    logger.info(f"handling event {event}")

@bottle.post('/')
def slack_event_api():
    # bottle is nice and simply but has a horrible design where request and
    # response are global objects.
    try:
        return handle_message(bottle.request.json) or ''
    except:
        logger.error("Error in handle_event", exc_info=True)
        return ''

# Auto reloading doesn't work that well because it crashes if you have a typo.
bottle.run(host='0.0.0.0', port=os.environ.get('PORT', 8080), reload=True)
