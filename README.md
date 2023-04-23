# Polana Chat

A simple chat app made using [FastAPI](https://github.com/tiangolo/fastapi) that includes an API and a web interface. One can use the API as a web interface or mobile application backend. As of now, no proper security measures exist, so don't use this app in production.

## Requirements

Python 3.7+

- [FastAPI](https://github.com/tiangolo/fastapi/)
- [Uvicorn](https://www.uvicorn.org/)

## Installation

```
git clone https://github.com/sibi361/polana_chat_app.git
cd polana-chat
pip install -r requirements.txt
uvicorn main:app
```

Visit http://127.0.0.1:8000 in a browser.

API documentation will be available at http://127.0.0.1:8000/docs and http://127.0.0.1:8000/redocs.

## Todo

- [ ] New Chat feature

- [ ] Login, Logout frontend

- [ ] New user registration

- [ ] fix `json.loads()` symbols error

- [ ] fix auth, set cookie with JS

- [ ] Improve frontend and add screenshots to README

- [ ] switch to websocket

- [ ] switch to SQL, unique user id with uuid module in users db, tuple (sender_id, receiver_id) as primary key in chats db

- [ ] `/getMessages` should have some sort of check like last message ID or content length before sending the entire chat log over

- [ ] switch to nodejs or something else

## License

This project is licensed under the terms of the MIT license.
