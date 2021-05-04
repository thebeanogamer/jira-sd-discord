from flask import Flask, abort, request
from flask.wrappers import Response
from yaml import load, BaseLoader
from os import environ
from httpx import post

app = Flask(__name__)

with open(environ.get("CONFIG", "./config.yml")) as config_file:
    config = load(config_file.read(), Loader=BaseLoader)


@app.route("/create/<string:url>", methods=["GET", "POST"])
def create(url: str):
    if request.headers.get("Token", "") == config["TOKEN"]:
        if url in [x["SOURCE"] for x in config["WEBHOOKS"]["CREATE"]]:
            webhook = next(
                item for item in config["WEBHOOKS"]["CREATE"] if item["SOURCE"] == url)
            incoming = request.get_json()
            forward = post(webhook["DESTINATION"], json={
                "embeds": [
                    {
                        "title": f"[{incoming['key']}] {incoming['fields']['summary']}",
                        "description": incoming["fields"]["description"],
                        "url": config["BASE"] + incoming["key"],
                        "color": 5814783,
                        "author": {
                            "name": incoming["fields"]["creator"]["displayName"],
                            "icon_url": incoming["fields"]["creator"]["avatarUrls"]["48x48"],
                        },
                    }
                ]
            })
            return Response(status=forward.status_code)
        else:
            abort(404)
    else:
        abort(401)


@app.route("/comment/<string:url>", methods=["GET", "POST"])
def comment(url: str):
    if request.headers.get("Token", "") == config["TOKEN"]:
        if url in [x["SOURCE"] for x in config["WEBHOOKS"]["COMMENT"]]:
            webhook = next(
                item for item in config["WEBHOOKS"]["COMMENT"] if item["SOURCE"] == url)
            incoming = request.get_json()
            comment = incoming["fields"]["comment"]["comments"][-1]
            forward = post(webhook["DESTINATION"], json={
                "embeds": [
                    {
                        "title": f"[{incoming['key']}] {incoming['fields']['summary']}",
                        "description": comment["body"],
                        "url": config["BASE"] + incoming["key"],
                        "color": 5814783,
                        "author": {
                            "name": comment["author"]["displayName"],
                            "icon_url": comment["author"]["avatarUrls"]["48x48"],
                        },
                    }
                ]
            })
            return Response(status=forward.status_code)
        else:
            abort(404)
    else:
        abort(401)


def main():
    app.run(host="0.0.0.0", port=80)
