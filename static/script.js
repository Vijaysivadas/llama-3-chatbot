document.getElementById("{{data['chat_id']}}").classList.add('activeChat')
       
function editName(idData, event) {
    event.preventDefault();
    var myModal = new bootstrap.Modal(document.getElementById('myModal'), {
        keyboard: false
    })
    myModal.show()
    
    editForm = document.getElementById('editNameForm')
    idData = idData.split("#")
    chat_id = idData[1]
    if (idData[2] === 'inPage') {
        context = 'inPage'
    }
    else if (idData[2] === 'notinPage') {
        context = 'notinPage'
    }
    editForm.addEventListener('submit', function (event) {
        event.preventDefault()
        newName = document.getElementById('editnewName').value
        fetch('http://127.0.0.1:5000/edit', {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ chat_id: chat_id, context: context, name: newName })

        }).then(response => response.json())
            .then(data => {
                
                document.getElementById('name'+chat_id).innerHTML = data.chatName
                document.getElementById('chatTitle').innerHTML = data.chatName

                myModal.hide()
                var myModalEl = document.getElementById('myModal')
                myModalEl.addEventListener('hidden.bs.modal', function (event) {
                    editForm.reset()
                })

            })

    });

}
function deleteChat(idData, event) {
    event.preventDefault();
    idData = idData.split("#")
    chat_id = idData[1]
    if(chat_id==="{{data['chat_id']}}"){
         context = 'inPage'
    }
    else{
        context = 'notinPage'
    }
    fetch('http://127.0.0.1:5000/delete', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ chat_id: chat_id, context: context })

    })
    .then(response => {
       
        if(response.redirected){
    window.location.href = response.url;
}
        alert('The chat has been deleted !')
        chat = document.getElementById('chatslink'+chat_id)
        chat.innerHTML = ''
        chat.parentNode.removeChild(chat)
    })

}



function chatLinkactive(chat_id) {
    link = document.getElementById(chat_id);
    link.childNodes.item("activechat").classList.add('active');
    link.classList.add('activeChat')
}
function changeState() {
    el = document.getElementById('speakbtn')
    if (el.ariaPressed === "false") {
        el.ariaPressed = true
        el.classList.add('pressed')
    } else if (el.ariaPressed === "true") {
        el.ariaPressed = false
        el.classList.remove('pressed')
    }
}
function speak(text) {
    speakbtn = document.getElementById('speakbtn')
    const ariaPressed = speakbtn.ariaPressed;
    if (ariaPressed === "true") {
        fetch("http://127.0.0.1:5000/speak", {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })

        }).then(response => response.json()) 
            .then(data => {
                
                ttsaudio = document.getElementById('tts-audio')
                ttsaudio.src = data.audio + "?time="+new Date().getTime();
                ttsaudio.load()

                ttsaudio.play()
            })

    }

}
function appendUserMessage(usrinput) {
    const replyItem = document.createElement('li');
    replyItem.className = 'repaly';

    const replyParagraph = document.createElement('p');
    replyParagraph.textContent = usrinput;

    replyItem.appendChild(replyParagraph);
    document.querySelector('#chat-messages').appendChild(replyItem);
}
function appendAIMessage(message) {
    const senderItem = document.createElement('li');
    senderItem.className = 'sender';

    const senderParagraph = document.createElement('p');
    senderParagraph.textContent = message;

    senderItem.appendChild(senderParagraph);

    document.querySelector('#chat-messages').appendChild(senderItem);

}
function appendChat(subject) {
    const anchor = document.createElement('a');
    anchor.href = `/chat?chat_id=${subject.chat_id}`;
    anchor.id = subject.chat_id;
    anchor.className = 'd-flex align-items-center p-3 chats-link';
    anchor.onclick = function () {
        chatLinkactive(subject.chat_id);
        
    };

    const imgDiv = document.createElement('div');
    imgDiv.className = 'flex-shrink-0';

    const img = document.createElement('img');
    img.className = 'img-fluid';
    img.src = '/static/img/chat (1).png';
    img.width = 30;
    img.alt = 'user img';

    const activeChatSpan = document.createElement('span');
    activeChatSpan.id = 'activechat';

    imgDiv.appendChild(img);
    imgDiv.appendChild(activeChatSpan);

    const textDiv = document.createElement('div');
    textDiv.className = 'flex-grow-1 ms-3';

    const h3 = document.createElement('h3');
    h3.textContent = subject.name != null ? subject.name : 'New chat';

    const editLink = document.createElement('a');
    editLink.href = '';
    editLink.id = `edit#${subject.id}#notinPage`;
    editLink.className = 'editChat';
    editLink.textContent = 'Edit';
    editLink.onclick = function(event){
        editName(editLink.id,event)
    }

    const deleteLink = document.createElement('a');
    deleteLink.href = '';
    deleteLink.id = `delete#${subject.chat_id}#inPage`;
    deleteLink.className = 'deleteChat';
    deleteLink.textContent = 'Delete';
    deleteLink.onclick = function(event){
        deleteChat(deleteLink.id,event)
    }

    textDiv.appendChild(h3);
    textDiv.appendChild(editLink);
    textDiv.appendChild(deleteLink);

    anchor.appendChild(imgDiv);
    anchor.appendChild(textDiv);


    chat = document.getElementById('chatlist-container')
    chat.insertBefore(anchor, chat.firstChild)
}
function aityping() {
    const chatBubble = document.createElement('div');
    chatBubble.className = 'chat-bubble';
    chatBubble.classList.add('my-message');
    chatBubble.classList.add('message');
    chatBubble.classList.add('float-left');
    chatBubble.id = "chat-bubble"
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing';

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot';
        typingIndicator.appendChild(dot);
    }

    chatBubble.appendChild(typingIndicator);

    document.getElementById('chat-messages').appendChild(chatBubble);
}

var form = document.getElementById("chatForm");

form.addEventListener('submit', handleForm);

function handleForm(event) {
    event.preventDefault();
    usrinput = document.getElementById('text_input').value


    appendUserMessage(usrinput)
    aityping()
    fetch("http://127.0.0.1:5000/chat", {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: usrinput, chat_id: "{{data['chat_id']}}" })

    }).then(response => response.json()) 
        .then(data => {
            document.getElementById('chat-bubble').remove()
            appendAIMessage(data.message)
            speak(data.message)

        });

}
form.addEventListener('submit', handleForm);