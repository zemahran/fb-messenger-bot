import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello worlddd!", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id):

    log("sending a reply to {recipient}".format(recipient=recipient_id))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = {
      "attachment":{
      "type":"template",
      "payload":{
        "template_type":"generic",
        "elements":[
           {
            "title":"Welcome to Moneyfellows Online Assistant!",
            "image_url": "https://moneyfellows.com/img/web_logo_large.png",
            "subtitle":"How can we help you?",
            "default_action": {
              "type": "web_url",
              "url": "https://moneyfellows.com/",
              "webview_height_ratio": "tall",
            },
            "buttons":[
              {
                "type": "postback",
                "title": "What is Moneyfellows?",
                "payload": "DEVELOPER_DEFINED_PAYLOAD"
              }
            ]
          },
          {
           "title":"Welcome!",
           #"image_url": "https://moneyfellows.com/img/web_logo_large.png",
           #"subtitle":"We have the right hat for everyone.",
           "default_action": {
             "type": "web_url",
             "url": "https://moneyfellows.com/",
             "webview_height_ratio": "tall",
           },
           "buttons":[
             {
               "type": "postback",
               "title": "Are there any fees?",
               "payload": "DEVELOPER_DEFINED_PAYLOAD"
             }
           ]
         },
         {
          "title":"Welcome!",
          #"image_url": "https://moneyfellows.com/img/web_logo_large.png",
          #"subtitle":"We have the right hat for everyone.",
          "default_action": {
            "type": "web_url",
            "url": "https://moneyfellows.com/",
            "webview_height_ratio": "tall",
          },
          "buttons":[
            {
              "type": "postback",
              "title": "How do I get the money?",
              "payload": "DEVELOPER_DEFINED_PAYLOAD"
            }
          ]
        }
        ]
      }
    }
    }

    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": response
    })

    r = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=EAADHka8kP6EBAGqb4zjU72AsbxmUZCL7WQR6BxoUlc0ZBYR7LbqLMA28iPUDkVJZBCRefvq5AzBaMZBuDXFK2dQD6X5lPhjmMbyTlnjCd7QY7UHZCy0KKuPciFGktPzo3eZCC5UaIhqz5SFhZCqDBDTIGyeZANTkb6WnIlBgvlYNs5D0bVddwOTh", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        #log(r.text)

def handle_postback(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print("{}: {}".format(datetime.now(), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
