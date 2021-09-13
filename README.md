# QISBot

![Docker Pulls](https://img.shields.io/docker/pulls/robinatus/qisbot.svg)

Tired of manually checking for exam results?
Then QISBot will help you!
It will check your registered exams every hour between 9:00 AM and 5:00 PM and message you via Telegram.

## Setup
1. Create a Telegram Bot and obtain the **bot_token** (described [here](https://core.telegram.org/bots#6-botfather))
2. Send your bot a sample message
3. Visit *https://api.telegram.org/bot**YourBOTToken**/getUpdates* and insert your **bot_token**
4. Copy the **chat_token** (alias *chat id*)
5. Insert your **bot_token**, **chat_token**, **y-number**, and **TUBS-password** into the following docker-compose file

```
services:
  qisbot:
    container_name: qisbot
    image: robinatus/qisbot:latest
    restart: unless-stopped
    environment:
      - USER=yXXXXXXX
      - PASSWORD=password
      - BOT_TOKEN=bot_token
      - CHAT_TOKEN=chat_token

```