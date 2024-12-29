const ncpClientId = "{{ ncp_client_id|default:'' }}";
let isMapInitialized = false;
let map = null;

// ---------------------------
// (2) /app/* -> /app/partials/* 치환 함수
// ---------------------------
function toPartialUrl(spaPath) {
    // 예: /app/planner/ -> /app/partials/planner/
    return spaPath.replace(/^\/app/, '/app/partials');
}

// ---------------------------
// (3) 부분 템플릿 로딩 함수
// ---------------------------
function loadContent(spaPath) {
    const partialUrl = toPartialUrl(spaPath);

    fetch(partialUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.text();
        })
        .then(html => {
            document.getElementById('content1').innerHTML = html;
            // 콘텐츠 로드 후 이벤트 트리거
            document.dispatchEvent(new Event("spaContentLoaded"));
        })
        .catch(error => console.error('Error loading content:', error));
}

// ---------------------------
// (4) 페이지 로드 시 동작
// ---------------------------

function showPopup() {
    document.getElementById('popup').classList.remove('hidden');
}
function closePopup() {
    document.getElementById('popup').classList.add('hidden');
}

// ---------------------------
// (5) spaContentLoaded 이후 로직
// ---------------------------
document.addEventListener("spaContentLoaded", function () {
    const favoritesPanel = document.getElementById("favoritesPanel");
    if (favoritesPanel) {
        const placeBtn = document.getElementById('placeBtn');
        const scheduleBtn = document.getElementById('scheduleBtn');
        const placesSection = document.getElementById('placesSection');
        const scheduleSection = document.getElementById('scheduleSection');

        if (placeBtn && scheduleBtn && placesSection && scheduleSection) {
            placeBtn.addEventListener('click', function() {
                console.log("[Favorites] 장소 버튼 클릭");
                placesSection.style.display = 'block';
                scheduleSection.style.display = 'none';
            });

            scheduleBtn.addEventListener('click', function() {
                console.log("[Favorites] 일정 버튼 클릭");
                placesSection.style.display = 'none';
                scheduleSection.style.display = 'block';
            });
        }
    }

    const inputBar = document.getElementById("input_bar");
    const chatMessages = document.getElementById("chat-messages");
    const deleteBtn = document.querySelector('.delete-btn');

    if (deleteBtn) {
        deleteBtn.addEventListener('click', showPopup);
    }

    document.addEventListener("newChatMessage", function (e) {
        const newMessage = document.createElement('div');
        newMessage.className = 'bubble user';
        newMessage.innerHTML = e.detail.replace(/\n/g, "<br>");
        if (chatMessages) chatMessages.prepend(newMessage);
    });

    if (!inputBar || !chatMessages) return;

    function sendMessage() {
        const message = inputBar.value.trim();
        if (message === "") return;

        const newMessage = document.createElement("div");
        newMessage.className = "bubble user";
        newMessage.innerHTML = message.replace(/\n/g, "<br>");

        newMessage.style.display = "inline-block";
        newMessage.style.maxWidth = "80%";
        newMessage.style.wordWrap = "break-word";
        newMessage.style.lineHeight = "1.4";

        chatMessages.prepend(newMessage); 
        chatMessages.scrollTop = chatMessages.scrollHeight;

        inputBar.value = "";
        resizeInput();
    }

    function resizeInput() {
        inputBar.style.height = "auto"; 
        const scrollHeight = inputBar.scrollHeight;
        const maxHeight = 120; 
        inputBar.style.height = `${Math.min(scrollHeight, maxHeight)}px`;

        if (scrollHeight >= maxHeight) {
            inputBar.style.overflowY = "auto";
        } else {
            inputBar.style.overflowY = "hidden";
        }
    }

    inputBar.addEventListener("keydown", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        } 
        else if (e.key === "Enter" && e.shiftKey) {
            e.preventDefault();
            const cursorPosition = inputBar.selectionStart;
            inputBar.value =
                inputBar.value.slice(0, cursorPosition) + "\n" 
                + inputBar.value.slice(cursorPosition);
            resizeInput();
        }
    });

    inputBar.addEventListener("input", resizeInput);
    resizeInput();
});
