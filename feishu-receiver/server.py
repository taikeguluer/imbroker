import json
import os
import uuid
import logging
import requests
from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv
from cloudevents.http import CloudEvent
from event import MessageReceiveEvent, UrlVerificationEvent, EventManager
from cloudevents.conversion import to_binary

load_dotenv(find_dotenv())

app = Flask(__name__)

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
ENCRYPT_KEY = os.getenv("ENCRYPT_KEY")
LARK_HOST = os.getenv("LARK_HOST")
SINK = os.getenv("K_SINK")

event_manager = EventManager()


@event_manager.register("url_verification")
def request_url_verify_handler(req_data: UrlVerificationEvent):
    if req_data.event.token != VERIFICATION_TOKEN:
        raise Exception("VERIFICATION_TOKEN is invalid")
    return jsonify({"challenge": req_data.event.challenge})


@event_manager.register("im.message.receive_v1")
def message_receive_event_handler(req_data: MessageReceiveEvent):
    message = req_data.event.message
    if message.chat_type != "group":
        logging.warning("Only group chat message can be forwarded.")
        return jsonify()
    if message.message_type != "text":
        logging.warning("Only text message can be forwarded.")
        return jsonify()
    pure_content = json.loads(message.content)
    dispatch_cloud_event(message.chat_id, pure_content["text"])

    return jsonify()


@app.errorhandler
def msg_error_handler(ex):
    logging.error(ex)
    response = jsonify(message=str(ex))
    response.status_code = (
        ex.response.status_code if isinstance(ex, requests.HTTPError) else 500
    )
    return response


@app.route("/", methods=["POST"])
def callback_event_handler():
    event_handler, event = event_manager.get_handler_with_event(VERIFICATION_TOKEN, ENCRYPT_KEY)
    return event_handler(event)


def dispatch_cloud_event(to_id, content):
    attributes = {
        "specversion": "1.0",
        "type": "com.imbroker.msg.received",
        "id": str(uuid.uuid4()),
        "source": "https://imbroker.io/#b6967144-9c39-479c-97d6-25e264ff5204/feishu-reciever",
        "datacontenttype": "application/json"
    }
    data = {
        "to_id": to_id,
        "content": content
    }
    event = CloudEvent(attributes, data)

    headers, body = to_binary(event)

    result = requests.post(url=SINK, data=body, headers=headers)

    logging.info("1 feishu text msg in a group is received and an event is forwarded with status code " + str(result.status_code))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
