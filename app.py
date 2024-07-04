from model import llama, loadLlama, TTS
from flask import (
    Flask,
    render_template,
    request,
    Response,
    session,
    redirect,
    url_for,
    jsonify,
)
import json

# import mysql.connector as mc
import re
import threading
import asyncio
from db import DataBase
import os


app = Flask(__name__)
loadEvent = threading.Event()
infEvent = threading.Event()

# @app.before_request
# loadLlama()
def backgroundtasks():
    # app.before_request_funcs[None].remove(backgroundtasks)
    start_background_tasks()


def start_background_tasks():
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=load_model_background, args=(loop,))
    t.start()
    


def load_model_background(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(loadLlama())
    global loadEvent
    loadEvent.set()
backgroundtasks()

app.secret_key = "#chatbotproject###$$$"
app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "admin"
app.config["MYSQL_DB"] = "chatbot"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

db = DataBase(app)


@app.route("/")
def index():
    if "loggedin" in session:
        return redirect("/newchat")
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]
        account = db.selectOne(
            "*", "users", ["name = %s and password = %s", (username, password)]
        )

        if account:
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["name"]
            msg = "Logged in successfully !"
            return redirect("/")
        else:
            msg = "Incorrect username / password !"
    return render_template("login.html", msg=msg)


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        username = request.form["username"]
        password = request.form["password"]

        account = db.selectOne("*", "users", ["name = %s", (username,)])

        if account:
            msg = "Account already exists !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "name must contain only characters and numbers !"
        else:
            db.insert("users", ['name','password'], [username, password])
            msg = 'You have successfully registered ! <a href="/login"> Login here </a>'

    elif request.method == "POST":
        msg = "Please fill out the form !"
    return render_template("register.html", msg=msg)


@app.route("/createchat", methods=["GET"])
def createChat():
    chat_id = session.get("chat_id")
    if chat_id is not None:
        session.pop("chat_id", None)
        return redirect("/newchat")
    else:
        return redirect("newchat")


@app.route("/newchat", methods=["POST", "GET"])
def newchat():
   
    chat_id = session.get("chat_id")
    username = session["username"]
    if request.method == "GET":
        #maybe handle if id is not in db
        names = db.select(
            ["name", "id"], "history", ["usrid = {}".format(session["id"]), False]
        )
        chatlist = list()
        for i in names:
            chatlist.append(i)
        if chat_id is not None:
            return redirect('/chat?chat_id='+str(chat_id))
      

        return render_template("new_chat.html", chatlist=chatlist)

    if request.method == "POST":
        if "message" not in request.get_json():
            return redirect("/newchat")
        data = request.get_json()
        usermsg = data["message"]

        if chat_id is not None:
            lastmsgs = db.select(
                ["body"],
                "history",
                ["usrid = {} and id = {}".format(session["id"], chat_id), False],
            )[0]["body"]
            lastmsg = "\n".join(lastmsgs.split("####|msgsep|####")[-5:])
            prompt = (
                "Here is the last conversation between user and assistant : \n"
                + lastmsg
                + "\nRespond to this latest message :\n"
                + session["username"]
                + ": "
                + usermsg
            )
            f = open("prompt.txt", "r")
            sysmsg = f.read()
            loadEvent.wait()
            response = llama(prompt=prompt, sys_prompt=sysmsg)
            message = (
                response[0]["generated_text"]
                .split("<|eot_id|><|start_header_id|>assistant<|end_header_id|>")[1]
                .strip()
            )
          
            usermsgformatted = (
                session["username"] + ": " + usermsg + "\n" + "Assistant: " + message
            )
            db.update(
                "history",
                "body",
                lastmsgs + "\n####|msgsep|####\n" + usermsgformatted,
                ["id=%s", chat_id],
            )


            # audio = TTS(message, "static/uploads")
            # audioURL = request.url_root + "/" + audio
            message = {"message": message, "newchat": False}
            return app.response_class(
                response=json.dumps(message), status=200, mimetype="application/json"
            )
        else:
            prompt = (
                "Here is a conversation between user and assistant\nRespond to this message :\n"
                + session["username"]
                + ": "
                + usermsg
            )
            f = open("prompt.txt", "r")
            sysmsg = f.read()
            loadEvent.wait()
            
            response = llama(prompt=prompt, sys_prompt=sysmsg)
            message = (
                response[0]["generated_text"]
                .split("<|eot_id|><|start_header_id|>assistant<|end_header_id|>")[1]
                .strip()
            )
            usermsgformatted = (
                session["username"] + ": " + usermsg + "\n" + "Assistant: " + message
            )
            chatName = (
                llama(
                    usermsgformatted,
                    sys_prompt="You are good at giving names for a chatsummary.Give clear and consice short names for a given chat. The chat will be given to you. You should return only a suitable name for the chat nothing else. The name should match the chattopic. Now give a name for the following chat.",
                )[0]["generated_text"]
                .split("<|eot_id|><|start_header_id|>assistant<|end_header_id|>")[1]
                .strip()
            )
            db.insert(
                "history",
                ["body", "usrid", "name"],
                [usermsgformatted, session["id"], chatName],
            )
            chat_id = db.getInsertedId()
            session["chat_id"] = str(chat_id)
          
            message = {
                "message": message,
                "chat_id": chat_id,
                "name": chatName,
                "newchat": True,
            }
            return app.response_class(
                response=json.dumps(message), status=200, mimetype="application/json"
            )


@app.route("/chat", methods=["POST", "GET"])
def chat():

    if request.method == "GET":
        chat_id = request.args.get("chat_id")
        if chat_id is None:
            return redirect("/newchat")

        names = db.select(
            ["name", "id"], "history", ["usrid = {}".format(session["id"]), False]
        )
        chatlist = list()
        chatName=''
        for i in names:
            if str(i['id'])==chat_id:
                chatName = i['name']
            chatlist.append(i)
        data = db.select("*", "history", ["id = {}".format(chat_id), False])[0]
        if(len(data)<=0):
            return render_template('404.html',chatlist=chatlist)
        lastChats = data["body"].split("####|msgsep|####")
        chats = []
        for lc in lastChats:
            msglist = lc.split("Assistant: ")
            msg = [msglist[0][msglist[0].find(":") + 1 :].strip(), msglist[1].strip()]
            chats.append({"user": msg[0], "assistant": msg[1]})

        
        data = {"chats": chats, "chat_id": chat_id, "chatlist": chatlist,"chatName":chatName}

        return render_template("chat.html", data=data)

    if request.method == "POST":
        data = request.get_json()
        usermsg = data["message"]
        chat_id = data["chat_id"]

        lastmsgs = db.select(
            ["body"],
            "history",
            ["usrid = {} and id = {}".format(session["id"], chat_id), False],
        )[0]["body"]
        lastmsg = "\n".join(lastmsgs.split("####|newmsg|####")[-5:])
        prompt = (
            "Here is the last conversation between user and assistant : \n"
            + lastmsg
            + "\nRespond to this latest message :\n"
            + session["username"]
            + ": "
            + usermsg
        )
        f = open("prompt.txt", "r")
        sysmsg = f.read()
        loadEvent.wait()
        # maybe set a  timeout
        response = llama(prompt=prompt, sys_prompt=sysmsg)
        message = response[0]["generated_text"].split(
            "<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
        )[1]
        usermsgformatted = (
            session["username"] + ": " + usermsg + "\n" + "Assistant: " + message
        )
        db.update(
                "history",
                "body",
                lastmsgs + "\n####|msgsep|####\n" + usermsgformatted,
                ["id=%s", chat_id],
            )

        message = {"message": message}
      
        return app.response_class(
            response=json.dumps(message), status=200, mimetype="application/json"
        )
@app.route('/speak',methods=['POST'])
def speak():
    data = request.get_json()
    text = data['text']
    print(text)
    if text!= None:
        audio = TTS(text,'static/uploads')
        audioURL = request.url_root + "/" + audio
        response = {'audio':audioURL}
        return app.response_class(
                response=json.dumps(response), status=200, mimetype="application/json"
            )
    else:
        return app.response_class(
            response=json.dumps({"error":"No text provided"}), status=404, mimetype="application/json"
        )
@app.route('/delete', methods=['POST'])
def delete():
    data = request.get_json()
    chat_id = data['chat_id']
    context = data['context']
    db.delete('history', ["id=%s",(chat_id,)])
   
    if str(session.get('chat_id'))==chat_id:
        session.pop("chat_id", None)
 
    if context == "inPage":
        return redirect('/newchat')
    elif context == "notinPage":
        return app.response_class(
            response=json.dumps({"chat_id":chat_id}), status=200, mimetype="application/json"
        )
@app.route('/edit',methods=['POST'])
def edit():
    
    data = request.get_json()
    chat_id = data['chat_id']
    context = data['context']
    newName = data['name']
   
    db.update('history','name',newName,["id=%s",(chat_id)])
   
    return app.response_class(
        response=json.dumps({'chatName':newName})
    )

if __name__ == "__main__":

    app.run(debug=False)
