# -*- coding: utf-8 -*-

import logging
import os

from fastapi import FastAPI, HTTPException, Request
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)


logger = logging.getLogger("linebot")
logger.setLevel(logging.DEBUG)

app = FastAPI()

line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
parser = WebhookParser(os.environ["CHANNEL_SECRET"])


@app.post("/callback")
async def callback_handler(request: Request):
    logger.debug("receive request")
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = await request.body()
    body = body.decode()

    try:
        events = parser.parse(body, signature)
        logger.debug(f"get {len(events)} events")
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            logger.info("Ignore non-TextMessage")
            continue

        message = TextSendMessage(text=event.message.text)
        print(message)
        line_bot_api.reply_message(
            event.reply_token,
            message
        )

    return "OK"


@app.get("/", status_code=200)
def index():
    return "OK"

