import json
import datetime
from fastapi import FastAPI, Response, Cookie, responses, Request, templating
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

users_db = {"alice": "1234", "bob": "909",
            "max": "0000"}  # fake users_db db

with open("messages_backup.json", "a") as f:
    to_write = open("messages_backup.json", "r").read()
    if len(to_write) != 0:
        f.write(to_write)

try:
    chats_db = json.load(open("messages.json", "r"))
except FileNotFoundError:
    print("### ERROR: Messages database file messages.json NOT FOUND\n")
    exit(0)

app.mount("/static", StaticFiles(directory="html"), name="static")
templates = Jinja2Templates(directory="html")


@app.get("/")
def check_user_login_status(request: Request, session: str = Cookie(None)):
    if not session:
        return responses.RedirectResponse("/login")
    return responses.RedirectResponse("/app")


@app.get("/login")
# @app.post("/login")
# from typing import Annotated
# def login(request : Request, response: Response, username: Annotated[str, Form()] = None, password: Annotated[str, Form()] = None):
def login(request: Request, username: str = None,
          password: str = None, session: str = Cookie(None)):
    response = responses.RedirectResponse("/app")
    if session:
        return response
    elif username == None or password == None:
        return {"success": False, "logged_in": False, "reason": "Welcome to Polana Chat App, please supply username and password"}
        # return templates.TemplateResponse("login.html",{"request":request})
    elif username in users_db.keys():
        if password == users_db[username]:
            expires = datetime.datetime.utcnow() + datetime.timedelta(days=7)
            response.set_cookie(key="session",
                                # TODO: have a sane auth mechanism :S
                                value=":".join([username, users_db[username]]),
                                # secure=True,  # does not set cookie sometimes
                                httponly=True,
                                samesite="strict",
                                expires=expires.strftime(
                                    "%a, %d %b %Y %H:%M:%S GMT"),
                                )
            return response
            # return {"success": True, "logged_in":"yes","logged_in_as":username, "reason":"Logged in, please refresh", "js-location": "/app"}
        else:
            return {"success": False, "logged_in": False,  "reason": "Invalid username or password"}
    else:
        # username and password check failures both return same reasons to improve security
        return {"success": False, "logged_in": False,  "reason": "Invalid username or password"}


@app.get("/status")
def provide_contact_list(request: Request, session: str = Cookie(None)):
    if not session:
        return responses.RedirectResponse("/login")
    username = str(session).split(":")[0]
    return {"success": True, "logged_in": True, "logged_in_as": username, "chats": list(chats_db["messages"][username].keys())}


@app.get("/getMessages")
def get_messages_for_given_username(user: str, session: str = Cookie(None)):
    if not session:
        return responses.RedirectResponse("/login")  # TODO: send 403
    username = str(session).split(":")[0]
    if user not in chats_db["messages"][username].keys():
        return {"success": False, "logged_in": True, "logged_in_as": username, "reason": "chat does not exist"}
    else:
        # TODO: switch to SQL
        return {"success": True, "logged_in": True, "logged_in_as": username, "messages": chats_db["messages"][username][user]}


# symbols such as \" make json.loads() produce json.decoder.JSONDecodeError
def jsonSanityTest(input):
    _dictionary = {"a": str(input)}
    _string = str(_dictionary).replace("'", '\"')
    try:
        json.loads(_string)
        return True
    except json.decoder.JSONDecodeError:
        return False


@app.get("/sendMessage")
@app.post("/sendMessage")
def send_message_to_given_username(user: str, message: str, session: str = Cookie(None)):
    if not session:
        return responses.RedirectResponse("/login")  # TODO: send 403
    username = str(session).split(":")[0]

    # could be abused to query unregistered usernames
    if user not in chats_db["messages"].keys():
        return {"success": False, "logged_in": True, "logged_in_as": username, "reason": "user does not exist"}

    if len(message) == 0:
        return {"success": False, "logged_in": True, "logged_in_as": username, "reason": "empty message not allowed"}

    ########################################################
    ################# TODO: switch to SQL ##################
    ########################################################

    if jsonSanityTest(message) is False:
        return {"success": False, "logged_in": True, "logged_in_as": username,
                "reason": "Server Error: Please report this to the administrator for further analysis",
                "original_message_content": message}

    new_message = {}
    new_message["timestamp"] = datetime.datetime.strftime(
        datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S")
    new_message["way"] = "out"
    new_message["message"] = message

    if user not in chats_db["messages"][username].keys():
        chats_db["messages"][username][user] = []
    chats_db["messages"][username][user].append(new_message)

    _new_message = {}
    _new_message["timestamp"] = new_message["timestamp"]
    # duplicate record for now, SQL switch will fix :S
    _new_message["way"] = "in"
    _new_message["message"] = message

    if username not in chats_db["messages"][user].keys():
        chats_db["messages"][user][username] = []
    chats_db["messages"][user][username].append(_new_message)

    to_write = str(chats_db)
    with open("messages_most_recent_dump.json", "w") as f:
        f.write(to_write + "\n")
    temp_json = json.loads(str(chats_db).replace("'", '\"'))
    to_write = json.dumps(temp_json, indent=4, sort_keys=True)
    with open("messages.json", "w") as f:
        f.write(to_write + "\n")

    ########################################################

    return {"success": True, "logged_in": True, "logged_in_as": username}


@app.get("/app")
def render_chat_window(request: Request, session: str = Cookie(None), response_class=responses.HTMLResponse):
    if not session:
        return responses.RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {"request": request})


# @app.get("/app2")  # for debugging
# def render_test_window(request: Request, session: str = Cookie(None), response_class=responses.HTMLResponse):
#     if not session:
#         return responses.RedirectResponse("/login")
#     return templates.TemplateResponse("test.html", {"request": request})

# import starlette
# @app.get("/logout") # does not work
# # @app.post("/login")
# def logout(request: Request, response: Response, session: str = Cookie(None)):
#     # response = responses.RedirectResponse("/")
#     response = starlette.responses.Response
#     response.delete_cookies(key="session")
#     return response
