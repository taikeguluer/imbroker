import logging
import requests
from flask import Flask, request
from cloudevents.http import from_http

app = Flask(__name__)


@app.route("/", methods=["POST"])
def cloud_event_handler():
    event = from_http(request.headers, request.get_data())
    target = event.data["target"]
    content = event.data["content"]
    headers = {
        "Content-Type": "application/json",
    }

    req_body = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    result = requests.post(url=target, headers=headers, json=req_body)

    logging.info("1 msg is forwarder to wxwork group by robot with status code " + str(result.status_code))

    return 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
