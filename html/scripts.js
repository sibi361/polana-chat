function getStatusJsonAtInit() {
  const url = "/status";
  fetch(url, {
    method: "GET",
    // body: new FormData(document.getElementById("inputform")),
    // -- or --
    // body : JSON.stringify({
    // user : document.getElementById('user').value,
    // ...
    // })
  })
    .then(
      (response) => response.json() // .json(), etc.
      // same as function(response) {return response.text();}
    )
    .then((status) => init(status));
}

function init(status) {
  headerUsername = document.querySelector(".header-login-status");
  headerUsername.textContent = `Logged in as: ${status["logged_in_as"]}`;

  const sidebar = document.querySelector(".sidebar");
  const profiles = status["chats"];
  for (let i = 0; i < profiles.length; i++) {
    var profileBox = document.createElement("div");
    profileBox.className = "sidebar-cell";
    if (i == 0) {
      profileBox.className = "sidebar-cell sidebar-cell-selected";
    }
    profileBox.textContent = profiles[i];
    sidebar.append(profileBox);
  }

  // sidebar profile chooser
  document
    .querySelector(".sidebar")
    .addEventListener("click", function (event) {
      getProfile(event.target);
    });

  // message sender
  document
    .querySelector("#messagebox")
    .addEventListener("submit", function (event) {
      event.preventDefault();
      sendMessage();
    });

  getMessages(status["chats"][0]);
}

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

function getProfile(cell) {
  getMessages(cell.textContent);

  const sidebarCells = document.querySelectorAll(".sidebar-cell");
  if (cell.className == "sidebar-cell sidebar-cell-new-chat") {
    return;
  }
  if (cell.className != "sidebar-cell sidebar-cell-selected") {
    for (let i = 0; i < sidebarCells.length; i++) {
      sidebarCells[i].className = "sidebar-cell";
    }
    cell.className = "sidebar-cell sidebar-cell-selected";
  }
}

getStatusJsonAtInit();

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

function getMessages(username) {
  const url = `/getMessages?user=${username}`;
  fetch(url, {
    method: "GET",
  })
    .then((response) => response.json())
    .then((responseJson) => {
      if (responseJson["success"]) {
        updateChatHistory(responseJson["messages"], username);
      } else {
        if (!responseJson["logged_in"]) {
          alert("You have been logged out, proceeding to login");
          // TODO: show this as message with js, ask to save typed message, then redirect
          window.location.href = "/login";
        }
      }
    });
}

function updateChatHistory(messageList, username) {
  const messageBox = document.querySelector(".messages");
  messageBox.textContent = "";
  for (let i = 0; i < messageList.length; i++) {
    var messageCell = document.createElement("div");
    var currentMsg = messageList[i];

    messageCell.className = "message-cell";
    var messageCellLeft = document.createElement("div");
    messageCellLeft.className = "message-cell-left";
    if (currentMsg["way"] == "in") {
      messageCellLeft.textContent = username + ": " + currentMsg["message"];
    } else {
      messageCellLeft.textContent = "You: " + currentMsg["message"];
    }
    messageCell.append(messageCellLeft);

    var messageCellTime = document.createElement("div");
    messageCellTime.className = "message-cell-time";
    messageCellTime.textContent = currentMsg["timestamp"].split("T")[1];
    messageCell.append(messageCellTime);

    messageBox.append(messageCell);
  }
}

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

function bgRefreshCurrentlyOpenChat() {
  if (refresh != 0) {
    const currentProfile = document.querySelector(
      ".sidebar-cell.sidebar-cell-selected"
    );
    let username = currentProfile.textContent;
    getMessages(username);
  }
}

let refresh = 1;

setInterval(bgRefreshCurrentlyOpenChat, 500);

///////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////

function sendMessage() {
  const messageBoxInput = document.querySelector("#messagebox-input");
  const currentProfile = document.querySelector(
    ".sidebar-cell.sidebar-cell-selected"
  );
  let username = currentProfile.textContent;
  let message = messageBoxInput.value;

  if (message.length == 0) {
    return;
  }

  message = message.replace('"', '\\"');

  const url = `/sendMessage?user=${username}&message=${message}`;
  fetch(url, {
    method: "POST",
  })
    // .then((response) => response.json())
    // .then((bla) => console.log(bla["success"]));
    .then((response) => response.json())
    .then((responseJson) => {
      if (responseJson["success"]) {
        messageBoxInput.value = "";
      } else {
        alert(responseJson["reason"]);
        //   // if logged out, this will be 307 redirect and no feedback as empty response
        //   // no need to redirect to /login here as bgRefresh() handles that

        //   alert("You have been logged out, proceeding to login");
        //   window.location.href = "/login";
      }
    });
}

refresh = 1;
