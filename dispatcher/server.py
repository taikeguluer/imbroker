import os
import logging
import requests
from flask import Flask, request
from dotenv import load_dotenv, find_dotenv
from cloudevents.http import CloudEvent, from_http
from cloudevents.conversion import to_binary

load_dotenv(find_dotenv())

app = Flask(__name__)

SINK = os.getenv("K_SINK")


@app.route("/", methods=["POST"])
def cloud_event_handler():
    event = from_http(request.headers, request.get_data())
    target_list = [{
        "type": "wxwork.robot",
        "target": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e18d9740-xxxx-yyyy-b0a3-afb314c44f76"
    }]
    for target in target_list:
        attributes = {
            "specversion": "1.0",
            "type": "com.imbroker.msg.forward." + target["type"],
            "id": event['id'],
            "source": event['source'] + "/dispatcher",
            "datacontenttype": "application/json"
        }
        data = {
            "target": target["target"],
            "content": event.data["content"]
        }
        new_event = CloudEvent(attributes, data)

        headers, body = to_binary(new_event)

        result = requests.post(url=SINK, data=body, headers=headers)

        logging.info("1 msg forwarding event is dispatched with status code " + str(result.status_code))

    return 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
