import threading
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Messages are kept in memory (MVP). They are lost when the instance restarts,
# which is why app.yaml limits the app to one instance. See README: Limitations.
messages = []
lock = threading.Lock()  # gunicorn serves requests on several threads

MAX_MESSAGES = 200
MAX_NAME_LENGTH = 30
MAX_TEXT_LENGTH = 500
ALLOWED_TIMERS = {0, 10, 30}  # seconds; 0 = permanent

page = """
<!DOCTYPE html>
<html>
<head>
    <title>Disappearing Messages</title>

    <style>

        body{
            font-family: Arial, sans-serif;
            background-color:#f0f0f0;
            margin:0;
            padding:20px;
        }

        h1{
            text-align:center;
        }

        .chat{
            width:700px;
            margin:auto;
            background:white;
            padding:20px;
            border-radius:10px;
            box-shadow:0px 0px 5px gray;
        }

        #messages{
            border:1px solid gray;
            height:350px;
            overflow-y:auto;
            padding:10px;
            margin-bottom:15px;
            background:#fafafa;
        }

        .msg{
            margin-bottom:10px;
            padding:8px;
            border-bottom:1px solid #ddd;
        }

        input, select{
            padding:8px;
            margin-right:5px;
        }

        button{
            padding:8px 15px;
            cursor:pointer;
        }

        .name{
            font-weight:bold;
        }

    </style>
</head>

<body>

<div class="chat">

    <h1>Disappearing Messages Chat</h1>

    <div id="messages"></div>

    <input type="text" id="name" placeholder="Your name" maxlength="30">

    <input type="text" id="text" placeholder="Type a message" maxlength="500">

    <select id="timer">
        <option value="10">10 Seconds</option>
        <option value="30">30 Seconds</option>
        <option value="0">Permanent Message</option>
    </select>

    <button onclick="sendMessage()">Send</button>

</div>

<script>

function loadMessages(){

    fetch('/messages')
    .then(response => response.json())
    .then(data => {

        let box = document.getElementById("messages");

        box.innerHTML = "";

        // Build the elements with textContent instead of innerHTML, so a message
        // like <img src=x onerror=alert(1)> is shown as text and never runs.
        data.forEach(function(msg){

            let div = document.createElement("div");
            div.className = "msg";

            let name = document.createElement("span");
            name.className = "name";
            name.textContent = msg.name;

            let small = document.createElement("small");
            small.textContent = msg.left;

            div.append(name, ": " + msg.text, document.createElement("br"), small);
            box.appendChild(div);
        });

    });

}

function sendMessage(){

    let name = document.getElementById("name").value;
    let text = document.getElementById("text").value;
    let timer = document.getElementById("timer").value;

    if(name == "" || text == ""){
        alert("Please fill all fields");
        return;
    }

    fetch('/send', {

        method:'POST',

        headers:{
            'Content-Type':'application/json'
        },

        body:JSON.stringify({
            name:name,
            text:text,
            timer:timer
        })

    })
    .then(response => response.json().then(body => {

        if(!response.ok){
            alert(body.error);
            return;
        }

        document.getElementById("text").value = "";

        loadMessages();
    }));

}

setInterval(loadMessages,1000);

loadMessages();

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(page)


@app.route("/send", methods=["POST"])
def send():

    data = request.get_json(silent=True)  # None instead of a crash for non-JSON bodies
    if not isinstance(data, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    name = str(data.get("name", "")).strip()
    text = str(data.get("text", "")).strip()
    try:
        timer = int(data.get("timer", 10))
    except (TypeError, ValueError):
        timer = -1

    if not name or not text:
        return jsonify({"error": "Name and message are required"}), 400
    if len(name) > MAX_NAME_LENGTH or len(text) > MAX_TEXT_LENGTH:
        return jsonify({"error": "Name or message is too long"}), 400
    if timer not in ALLOWED_TIMERS:
        return jsonify({"error": "Timer must be 0, 10 or 30 seconds"}), 400

    expire = None if timer == 0 else datetime.now(timezone.utc) + timedelta(seconds=timer)

    with lock:
        messages.append({"name": name, "text": text, "expire": expire})
        del messages[:-MAX_MESSAGES]  # keep memory bounded: only the newest messages stay

    return jsonify({"message": "saved"})


@app.route("/messages")
def get_messages():

    now = datetime.now(timezone.utc)

    with lock:
        # Drop expired messages, then report the time left on the others
        messages[:] = [m for m in messages if m["expire"] is None or m["expire"] > now]
        current = list(messages)

    result = []
    for m in current:
        if m["expire"] is None:
            left = "Permanent Message"
        else:
            left = f"Disappears in {int((m['expire'] - now).total_seconds())}s"
        result.append({"name": m["name"], "text": m["text"], "left": left})

    return jsonify(result)


if __name__ == "__main__":
    # Local development only; App Engine starts the app with gunicorn (see app.yaml)
    app.run(host="127.0.0.1", port=8080, debug=True)
