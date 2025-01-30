let isMapInitialized = false;
let map = null;
let lastLoadedPath = null;
let globalMarkerData = []; // 전역 변수로 선언
let isPlaceInputOpen = false;
let isScheduleInputOpen = false;

window.onload = function () {
    // localStorage의 특정 키 삭제
    // localStorage.removeItem('chatMessage');

    // 또는 모든 데이터 삭제
    // localStorage.clear();
};

// (1) 지도 초기화 함수
function initializeMap(markerData) {
    if (isMapInitialized) return;
    
    const mapScript = document.createElement('script');
    let lang = "";
    switch (countryId) {
        case "KR":
            lang = "ko";
            break;
        case "JP":
            lang = "ja";
            break;
        case "CN":
            lang = "zh";
            break;
        case "US":
            lang = "en";
            break;
    }
    const url = new URL(window.location.href);
    if (url.searchParams.get('lang')) {
        lang = url.searchParams.get('lang');
        url.searchParams.set('lang', null);
    }
    markerData = JSON.parse(url.searchParams.get('globalMarkerData'));
    mapScript.src = `https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId=${ncpClientId}&language=${lang}`;
    mapScript.onload = function () {
        map = new naver.maps.Map('map', {
            center: new naver.maps.LatLng(37.5296, 126.9644), // 용산역 좌표
            zoom: 13,
            language: lang,
        });
        isMapInitialized = true;

        // 마커 추가
        let markerIndex = 0; // 마커 인덱스 초기화
        if (markerData) {
            markerData.forEach(data => {
                const markerIconUrl = `/static/images/markers/marker${(markerIndex % 10) + 1}.png`;
                const marker = new naver.maps.Marker({
                    position: data.position,
                    map: map,
                    title: data.title,
                    // title: data.names[lang],
                    icon: {
                        content: `<img src="${markerIconUrl}" style="width:32px; height:36px;">`, // HTML 직접 사용
                        // url: markerIconUrl,
                        // size: new naver.maps.Size(36, 36), // 마커 크기
                        // origin: new naver.maps.Point(0, 0),
                        anchor: new naver.maps.Point(18, 36), // 마커 위치 조정
                    },
                });

                markerIndex++;

                // 마커 클릭 이벤트
                naver.maps.Event.addListener(marker, 'click', function () {
                    switch (countryId) {
                        case "KR": alert(`${data.title}입니다!`); break;
                        case "JP": alert(`${data.title}です!`); break;
                        case "CN": alert(`是${data.title}!`); break;
                        case "US": alert(`This place is ${data.title}!`); break;
                    }
                    // infoWindow.open(map, marker); // 마커 클릭 시 정보창 열기
                });
            });

            // 선 연결
            for (let i = 0; i < markerData.length - 1; i++) {
                const polyline = new naver.maps.Polyline({
                    map: map,
                    path: [markerData[i].position, markerData[i + 1].position], // 인접한 마커 연결
                    strokeColor: '#000000', // 선 색상
                    strokeWeight: 0, // 선 두께
                    strokeStyle: 'solid', // 선 스타일 (solid, dashed, dotted 등)
                });
            }
        }
    };
    mapScript.onerror = function () {
        console.error("Failed to load Naver Map script.");
    };

    document.head.appendChild(mapScript);
}

// (2) /app/* -> /app/partials/* 치환 함수
function toPartialUrl(spaPath) {
    // 예: /app/planner/ -> /app/partials/planner/
    return spaPath.replace(/^\/app/, '/app/partials');
}

// 현재 활성화된 nav-btn 표시 함수
function highlightActiveLink(spaPath) {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        const url = btn.getAttribute('data-url');
        if (!url) return;  // home-btn이 data-url이 없으므로 건너뜀

        if (url === spaPath) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
}

function loadContent(spaPath) {
    if (lastLoadedPath === spaPath) {
        console.log("중복된 경로로 로드 중단:", spaPath, ",lastPath:", lastLoadedPath);
        return;
    }

    lastLoadedPath = spaPath;
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

            // spaContentLoaded 이벤트 트리거
            document.dispatchEvent(new Event("spaContentLoaded"));
        })
        .catch(error => console.error('Error loading content:', error));
}

function updateIconsBasedOnTheme() {
    const isLightTheme = document.body.getAttribute("data-theme") === "light";
    
    const navIcons = document.querySelectorAll(".nav-icon");
    navIcons.forEach(icon => {
        const newSrc = isLightTheme ? icon.getAttribute("data-light") : icon.getAttribute("data-dark");
        icon.setAttribute("src", newSrc);
    });

    const editIcon = document.querySelector(".edit-icon");
    if (editIcon) {
        const newEditSrc = isLightTheme ? editIcon.getAttribute("data-light") : editIcon.getAttribute("data-dark");
        editIcon.setAttribute("src", newEditSrc);
    }

    const deletePlaceBtns = document.querySelectorAll("#deletePlaceBtn");
    deletePlaceBtns.forEach(button => {
        button.src = isLightTheme ? "/static/images/delete_light.png" : "/static/images/delete_dark.png";
    });
}

document.addEventListener("DOMContentLoaded", function () {            
    // 지도 초기화
    initializeMap();
    updateIconsBasedOnTheme();

    let currentPath = window.location.pathname;

    // /app/ 만 입력되었다면 디폴트: /app/planner/ 로 가정
    if (currentPath === '/app/') {
        currentPath = '/app/planner/';
        history.replaceState(null, '', currentPath);
    }
    loadContent(currentPath);

    // 네비게이션 버튼 클릭 시
    document.querySelectorAll('.nav-btn').forEach(button => {
        button.addEventListener('click', function (event) {
            event.preventDefault();
            const spaPath = this.getAttribute('data-url'); // 이동하려는 URL

            if (!spaPath) return; // URL이 없는 경우 무시
            
            if (isLoggedIn === false) {
                // 비로그인 상태일 경우 alert 창 띄우기
                const confirmLogin = confirm("로그인이 필요한 화면입니다. 로그인하시겠습니까?");
                if (confirmLogin) {
                    // 확인 버튼을 눌렀을 경우 로그인 페이지로 이동
                    const currentPath = window.location.pathname; // 현재 페이지 경로
                    window.location.href = `/login/?next=${encodeURIComponent(spaPath)}`;
                }
                // 취소 버튼을 누르면 아무 일도 하지 않음
            } else {
                // 로그인 상태라면 해당 페이지로 이동
                history.pushState(null, '', spaPath);
                loadContent(spaPath); // 네비게이션 바의 페이지 로딩
            }
        });
    });

    // Home 버튼 처리
    const homeButton = document.getElementById('home-btn');
    if (homeButton) {
        document.getElementById('home-btn').addEventListener('click', function () {
            window.location.href = '/';
        });
    }            

    // 팝업 창 기능
    document.getElementById('cancel-delete').addEventListener('click', closePopup);
    document.getElementById('confirm-delete').addEventListener('click', function () {
        switch (countryId) {
            case "KR": alert('계정이 삭제되었습니다!'); break;
            case "JP": alert('アカウント削除！'); break;
            case "CN": alert('账号已删除!'); break;
            case "US": alert('Account deleted!'); break;
        }
        closePopup();
    });

    // 뒤로가기/앞으로가기 처리
    window.addEventListener('popstate', function () {
        loadContent(window.location.pathname);
    });   
    
    const mapPanel = document.getElementById("map-panel");
    const dragHandle = document.getElementById("drag-handle");

    let isDragging = false; // 드래그 상태
    let startY = 0; // 마우스 시작 Y 좌표
    let startHeight = 0; // mapPanel 시작 높이

    // 드래그 시작
    dragHandle.addEventListener("mousedown", function (e) {
        isDragging = true;
        startY = e.clientY; // 마우스 시작 위치 저장
        startHeight = mapPanel.offsetHeight; // mapPanel의 시작 높이 저장

        document.body.style.userSelect = "none"; // 드래그 중 텍스트 선택 방지
    });

    // 드래그 진행
    document.addEventListener("mousemove", function (e) {
        if (!isDragging) return;
        
        const deltaY = e.clientY - startY; // 마우스 이동 거리
        const newHeight = startHeight - deltaY; // 새로운 패널 높이 계산
        
        const maxHeight = window.innerHeight * 9 / 10; // 화면 전체 높이의 90%
        const minHeight = 45; // 최소 높이 제한
        
        if (newHeight >= minHeight && newHeight <= maxHeight) {
            mapPanel.style.height = `${newHeight}px`; // mapPanel 높이 업데이트

            // 버튼 텍스트 업데이트
            const toggleUIBtn = document.getElementById("toggleUIBtn");
            toggleUIBtn.textContent = newHeight > minHeight ? "⮟" : "⮝";

            // 버튼 컨테이너 위치 조정
            const buttonContainer = document.getElementById("day-button-container");
            if (buttonContainer) {
                const mapPanelTop = mapPanel.getBoundingClientRect().top;
                buttonContainer.style.top = `${mapPanelTop - buttonContainer.offsetHeight - 15}px`;
            }
        }
        else if (newHeight < minHeight) {
            mapPanel.style.height = `45px`;

            const toggleUIBtn = document.getElementById("toggleUIBtn");
            toggleUIBtn.textContent = "⮝";
        }
    });

    // 드래그 종료
    document.addEventListener("mouseup", function () {
        if (isDragging) {
            isDragging = false;
            document.body.style.userSelect = ""; // 텍스트 선택 복구
        }
    });        
});

function getCSRFToken() {
    const cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        if (cookie.startsWith("csrftoken=")) {
            return cookie.split("=")[1];
        }
    }
    return null;
}

function showPopup() {
    document.getElementById('popup').classList.remove('hidden');
}

function closePopup() {
    document.getElementById('popup').classList.add('hidden');
}

document.addEventListener("spaContentLoaded", async function () {
    const content1 = document.querySelector('.panel');
    const map = document.getElementById("map");
    const toggleButton = document.getElementById("toggleButton");
    const scrollToBottomBtn = document.getElementById("scrollToBottomBtn");
    const chatMessages = document.getElementById("chat-messages");
    let isLoading = false; // 로딩 상태를 관리하는 전역 변수
    let activeAbortController = null; // 현재 활성화된 AbortController
    let isChatHidden = false;
    let isScrollPaused = false; // 스크롤 이벤트 잠시 멈춤 플래그

    function scrollHandler() {
        if (isScrollPaused) return; // 스크롤 이벤트 멈춘 상태라면 실행하지 않음

        if (!isChatHidden) {
            const isAtBottom = chatMessages.scrollTop + chatMessages.clientHeight >= chatMessages.scrollHeight - 10;
            if (!isAtBottom) {
                scrollToBottomBtn.classList.remove("hidden"); // ▼ 버튼 보이기
            } else {
                scrollToBottomBtn.classList.add("hidden"); // ▼ 버튼 숨김
            }
        } else {
            scrollToBottomBtn.classList.add("hidden"); // 채팅창이 숨겨진 경우 ▼ 버튼 숨김
        }
    }

    if (toggleButton) {
        toggleButton.addEventListener("click", function () {
            if (isChatHidden) {
                // 채팅 패널 다시 표시
                isScrollPaused = true; // 스크롤 이벤트 잠시 멈춤
                content1.style.width = "400px";
                map.style.flexGrow = "1";
                toggleButton.innerHTML = "&lt;&nbsp;";

                setTimeout(() => {
                    isScrollPaused = false; // 일정 시간 후 스크롤 이벤트 재개
                    // chatMessages.dispatchEvent(new Event("scroll")); // 스크롤 강제 트리거
                }, 100); // 100ms 대기 후 재개
            } else {
                // 채팅 패널 숨김
                content1.style.width = "0";
                map.style.flexGrow = "2";
                toggleButton.innerHTML = "&gt;&nbsp;";
                if (scrollToBottomBtn) {
                    scrollToBottomBtn.classList.add("hidden"); // ▼ 버튼 숨김
                }
            }
            isChatHidden = !isChatHidden; // 상태 변경
        });
    }

    if (chatMessages && scrollToBottomBtn) {
        chatMessages.addEventListener("scroll", scrollHandler);
        scrollToBottomBtn.addEventListener("click", function () {
            // ▼ 버튼 클릭 시 채팅창 맨 아래로 스크롤
            chatMessages.scrollTop = chatMessages.scrollHeight;
            scrollToBottomBtn.classList.add("hidden"); // 버튼 숨김
        });
    }
    
    // 1) Planner Panel
    const plannerPanel = document.getElementById("plannerPanel");
    if (plannerPanel) {
        console.log("[Planner] panel detected!");                
        const resetButton = document.getElementById("resetButton");
        const plannerTitle = document.getElementById("planner-title");
        const changeTitle = document.getElementById("change-title");
        const chatMessages = document.getElementById('chat-messages');
        const initialMessage = localStorage.getItem('chatMessage');
        const newMessage = document.createElement("div");
        const inputBar = document.getElementById("input_bar");  
        const urlParams = new URLSearchParams(window.location.search);
        const chatId = urlParams.get("chat_id");

        if (isLoggedIn) { // 로그인된 경우
            if (chatId) {
                try {
                    // 서버에서 제목 가져오기
                    const response = await fetch(`/app/partials/planner/get_title/?chat_id=${encodeURIComponent(chatId)}`);
                    const result = await response.json();

                    if (result.success && result.title) {
                        plannerTitle.textContent = result.title; // 제목 업데이트
                    } else {
                        console.error("Failed to fetch title:", result.error || "Unknown error");
                        plannerTitle.textContent = "Default Title"; // 실패 시 기본값
                    }
                    // 채팅 내용 가져오기
                    fetch(`/app/partials/planner/get_chat_content/?chat_id=${encodeURIComponent(chatId)}`)
                        .then(response => {
                            if (!response.ok) {
                                throw new Error(`Failed to fetch chat content: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then(data => {
                            if (data.success && data.content) {
                                parseAndDisplayChatContent(data.content); // 채팅 내용 파싱 및 UI 표시
                            } else {
                                console.log("No content for the provided chat_id.");
                            }
                        })
                        .catch(error => {
                            console.error("Error fetching chat content:", error);
                        });
                } catch (error) {
                    console.error("Error fetching title or chat content:", error);
                    plannerTitle.textContent = "Default Title"; // 오류 시 기본값
                }
            } else {
                // chat_id가 없는 경우, 새로운 제목 생성
                try {
                    const response = await fetch("/app/partials/chatting/");
                    const html = await response.text();

                    const tempDiv = document.createElement("div");
                    tempDiv.innerHTML = html;

                    const chatItems = tempDiv.querySelectorAll(".chat-item");
                    const chatCount = chatItems.length;

                    const newTitle = `chat${chatCount + 1}`;
                    plannerTitle.textContent = newTitle;
                } catch (error) {
                    console.error("Error calculating chat count:", error);
                    plannerTitle.textContent = "chat1"; // 기본값 설정
                }
            }
        } 
        else {
            try {
                const response = await fetch("/app/partials/chatting/");
                const html = await response.text();

                const tempDiv = document.createElement("div");
                tempDiv.innerHTML = html;

                const chatItems = tempDiv.querySelectorAll(".chat-item");
                const chatCount = chatItems.length;

                plannerTitle.textContent = `chat1`;
            } catch (error) {
                console.error("Error calculating chat count:", error);
            }
        }

        if (initialMessage) {
            // 로딩 상태로 설정
            isLoading = true;
            inputBar.disabled = true; // 입력창 비활성화

            saveChatToDB(`<나>${initialMessage}`);
            newMessage.className = "bubble right-bubble";
            newMessage.innerHTML = initialMessage.replace(/\n/g, "<br>");
            chatMessages.appendChild(newMessage);
            
            const loadingBubble = document.createElement("div");
            loadingBubble.classList.add("bubble", "left-bubble", "loading-bubble");
            loadingBubble.innerHTML = `
                <div class="loader">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;
            chatMessages.appendChild(loadingBubble);
                    
            if (activeAbortController) {
                activeAbortController.abort();
            }
            // 새로운 AbortController 생성
            activeAbortController = new AbortController();
            const { signal } = activeAbortController;
            fetchGPTResponse(initialMessage, signal);
        }             

        if (plannerTitle) {
            plannerTitle.addEventListener("dblclick", function () {
                changeTitle.value = plannerTitle.textContent;
                changeTitle.style.display = "block"; // 입력창 표시
                plannerTitle.style.display = "none"; // 기존 텍스트 숨김
                changeTitle.focus();
            });

            // 2) Enter: 제목 저장, ESC: 취소
            changeTitle.addEventListener("keydown", async function (e) {
                if (e.key === "Enter") {
                    const newTitle = changeTitle.value.trim();
                    const titleText = document.getElementById("planner-title"); 
                    
                    if (!newTitle) {
                        switch (countryId) {
                            case "KR": alert('제목을 입력해주세요.'); break;
                            case "JP": alert('タイトルを入力してください。'); break;
                            case "CN": alert('请输入标题'); break;
                            case "US": alert('Please enter the title'); break;
                        }
                        return;
                    }

                    plannerTitle.style.display = "block"; // 기존 텍스트 표시
                    changeTitle.style.display = "none"; // 입력창 숨김

                    try {
                        // 중복 확인 API 호출
                        const response = await fetch("/app/partials/planner/check_duplicate_title/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": getCSRFToken(),
                            },
                            body: JSON.stringify({ title: newTitle }),
                        });

                        const result = await response.json();

                        if (result.is_duplicate) {
                            switch (countryId) {
                                case "KR": alert('중복된 제목입니다. 다른 제목을 입력해주세요.'); break;
                                case "JP": alert('重複したタイトルです。 別のタイトルを入力してください。'); break;
                                case "CN": alert('重复的标题 。 请输入其他标题。'); break;
                                case "US": alert('Duplicate title, please enter a different title.'); break;
                            }
                            return;
                        }

                        // 제목 업데이트 API 호출
                        const updateResponse = await fetch("/app/partials/planner/update_title/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": getCSRFToken(),
                            },
                            body: JSON.stringify({ chat_id: chatId, title: newTitle }),
                        });

                        const updateResult = await updateResponse.json();
                        if (updateResult.success) {
                            plannerTitle.textContent = newTitle;
                            plannerTitle.style.display = "block";
                            changeTitle.style.display = "none";
                        } else {
                            console.error("Failed to update title:", updateResult.error || "Unknown error");
                        }
                    } catch (error) {
                        console.error("Error checking/updating title:", error);
                    }
                } else if (e.key === "Escape") {
                    plannerTitle.style.display = "block"; // 기존 텍스트 표시
                    changeTitle.style.display = "none";  // 입력창 숨김
                }                    
            });
        }                

        resetButton.addEventListener("click", function () {
            // URL에서 chat_id 추출
            const urlParams = new URLSearchParams(window.location.search);
            const chatId = urlParams.get("chat_id");

            if (!chatId) {
                return;
            }

            // 사용자 확인
            const confirmReset = confirm("정말 이 채팅 내용을 초기화하시겠습니까?");
            if (!confirmReset) return;

            // 서버로 삭제 요청
            fetch("/app/partials/planner/init_chat/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ chat_id: chatId }),
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        switch (countryId) {
                            case "KR": alert('채팅 내용이 초기화되었습니다.'); break;
                            case "JP": alert('チャット内容が初期化されました。'); break;
                            case "CN": alert('聊天内容已初始化 。'); break;
                            case "US": alert('Your chat has been reset.'); break;
                        }
                        // UI에서 내용을 비웁니다.
                        const chatMessages = document.getElementById("chat-messages");
                        if (chatMessages) chatMessages.innerHTML = "";
                    } else {
                        switch (countryId) {
                            case "KR": alert("초기화 실패: " + (data.error || "알 수 없는 오류")); break;
                            case "JP": alert("初期化失敗: " + (data.error || "不明な誤り")); break;
                            case "CN": alert("初始化失败: " + (data.error || "未知的错误")); break;
                            case "US": alert("Initialization failed: " + (data.error || "Unknown error")); break;
                        }
                    }
                })
                .catch(error => {
                    console.error("Error resetting chat content:", error);
                    switch (countryId) {
                        case "KR": alert("서버 오류가 발생했습니다. 다시 시도해주세요."); break;
                        case "JP": alert("サーバーエラーが発生しました。 もう一度お試しください。"); break;
                        case "CN": alert("服务器出错 。 请再试一次。"); break;
                        case "US": alert("A server error has occurred. Please try again."); break;
                    }
                });
        });
    }
    
    // 2) Chatting Panel
    const chattingPanel = document.getElementById("chattingPanel");
    if (chattingPanel) {
        console.log("[Chatting] panel detected!");

        const chatList = document.querySelector(".chat-list");

        function updateChatListScroll() {
            if (chatList.children.length > 10) {
                chatList.classList.remove("fewer-than-ten");
            } else {
                chatList.classList.add("fewer-than-ten");
            }
        }

        // 페이지 로드 시 실행
        updateChatListScroll();

        // 채팅 아이템이 추가되거나 제거될 때 실행 (예시 이벤트 리스너)
        document.addEventListener("chatListUpdated", updateChatListScroll);

        // 채팅 삭제 버튼 눌렀을 때 채팅을 삭제함
        const deleteIcons = document.querySelectorAll(".delete-icon");
        deleteIcons.forEach((icon) => {
            icon.addEventListener("click", async function (e) {
                e.stopPropagation();

                const chatId = this.dataset.id;
                if (!chatId) return;

                const confirmed = confirm("Are you sure you want to delete this chat?");
                if (!confirmed) return;

                try {
                    const response = await fetch("/app/partials/chatting/delete/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                        body: JSON.stringify({ chatting_id: chatId }),
                    });

                    const result = await response.json();
                    if (result.success) {
                        switch (countryId) {
                            case "KR": alert('채팅이 성공적으로 삭제되었습니다!'); break;
                            case "JP": alert('チャットが正常に削除されました！'); break;
                            case "CN": alert('聊天被成功删除！'); break;
                            case "US": alert('Chat deleted successfully!'); break;
                        }
                        this.closest(".chat-item").remove(); // UI에서 삭제
                    } else {
                        switch (countryId) {
                            case "KR": alert(`에러: ${result.error || '채팅 삭제 실패'}`); break;
                            case "JP": alert(`誤謬: ${result.error || 'チャット削除失敗'}`); break;
                            case "CN": alert(`五柳: ${result.error || '删除聊天失败'}`); break;
                            case "US": alert(`Error: ${result.error || 'Failed to delete chat.'}`); break;
                        }
                    }
                } catch (error) {
                    switch (countryId) {
                        case "KR": alert('오류가 발생했습니다. 다시 시도해 주세요.'); break;
                        case "JP": alert('エラーが発生しました。 もう一度お試しください。'); break;
                        case "CN": alert('发生错误 。 请再试一次。'); break;
                        case "US": alert('Chat deleted successfully!'); break;
                    }
                }
            });
        });

        // chat-item 클릭 -> /app/planner/?chat_id=xxx 형태 (250118:뭐하는 코드지?)
        document.querySelectorAll(".chat-item").forEach(item => {
            item.addEventListener("click", function() {
                const chatId = this.getAttribute("data-chat-id");
                const targetUrl = `/app/planner/?chat_id=${encodeURIComponent(chatId)}`;
                history.pushState(null, '', targetUrl);
                loadContent(targetUrl);
            });
        });
    }
    
    // 3) Favorites Panel
    const favoritesPanel = document.getElementById("favoritesPanel");
    if (favoritesPanel) {
        console.log("[Favorites] favoritesPanel detected!");
        // --------------------------------
        // (A) 탭 전환 로직
        // --------------------------------
        const backBtn = document.getElementById('backBtn');
        const bookmarkTitle = document.getElementById('bookmark_title');
        const placeBtn = document.getElementById('placeBtn');
        const scheduleBtn = document.getElementById('scheduleBtn');
        const topmenu = document.querySelector('.top-menu');
        const placesSection = document.getElementById('placesSection');
        const scheduleSection = document.getElementById('scheduleSection');
        const bodyElement = document.body; // 테마를 확인하기 위한 body 요소
        const editTitle = document.getElementById("edit-title");

        //즐겨찾기 페이지에서 뒤로 가기 버튼 눌렀을 때 기능
        backBtn.addEventListener('click', () => {
            backBtn.style.display = "none";
            bookmarkTitle.style.display = "none";
            placeBtn.style.display = "block";
            scheduleBtn.style.display = "block";
            topmenu.style.justifyContent = "space-evenly";
            document.querySelector('.folder-list').style.display = "block";
            document.querySelector('.bookmark-place-item').style.display = "none";
            document.querySelector('.bookmark-schedule-item').style.display = "none";

            const AllFolderLists = favoritesPanel.querySelectorAll('.folder-list');
            const bookmarkPlaceItemDiv = document.querySelector(".bookmark-place-item");
            const bookmarkScheduleItemDiv = document.querySelector(".bookmark-schedule-item");
            
            if (AllFolderLists) {
                AllFolderLists.forEach(folderList => {
                    folderList.style.display = "block";
                });
            }
        });

        editTitle.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                editPanelTitleOK();
            }
            else if (event.key === 'Escape') {
                editPanelTitleNO();
            }
        });

        //즐겨찾기 페이지에서 장소 / 일정 버튼 눌렀을 때 기능
        if (placeBtn && scheduleBtn && placesSection && scheduleSection) {
            placeBtn.addEventListener('click', function() {
                placesSection.style.display = 'block';
                scheduleSection.style.display = 'none';

                placeBtn.style.backgroundColor = '#999';
                scheduleBtn.style.backgroundColor = '';

                topmenu.style.justifyContent = "space-evenly";
                backBtn.style.display = "none";
                bookmarkTitle.style.display = "none";
                placeBtn.style.display = "block";
                scheduleBtn.style.display = "block";
            });

            scheduleBtn.addEventListener('click', function() {
                scheduleSection.style.display = 'block';
                placesSection.style.display = 'none';

                scheduleBtn.style.backgroundColor = '#999';
                placeBtn.style.backgroundColor = '';

                topmenu.style.justifyContent = "space-evenly";
                backBtn.style.display = "none";
                bookmarkTitle.style.display = "none";
                placeBtn.style.display = "block";
                scheduleBtn.style.display = "block";
            });

            placeBtn.click();
        }
        
        // --------------------------------
        // (C) 장소 폴더 만들기 로직
        // --------------------------------
        
        const plusPlace = document.getElementById("plus-place");
        addFolderEventHandler(
            "plus-place",
            "#placesSection",
            "새 폴더 이름 입력 (Enter)",
            true,
            { light: "/static/images/folder_light.png", dark: "/static/images/folder_dark.png" }
        );
        
        // --------------------------------
        // (D) 일정 만들기 로직
        // --------------------------------
        
        const plusSchedule = document.getElementById("plus-schedule");
        addFolderEventHandler(
            "plus-schedule",
            "#scheduleSection",
            "새 일정 이름 입력 (Enter)",
            false,
            { light: "/static/images/schedule_light.png", dark: "/static/images/schedule_dark.png" }
        );
        // --------------------------------------------------------
        // (E) 페이지 로드 시, 기존 아이템들에도 삭제 이벤트 연결
        // --------------------------------------------------------
        // 만약 "기존 아이템"에도 삭제 아이콘이 있다면 적용
        const allFolderLists = favoritesPanel.querySelectorAll('.folder-list');
        allFolderLists.forEach(listEl => {
            // 해당 섹션이 "장소" 섹션이면 plusPlace를, 
            // "일정" 섹션이면 plusSchedule을 연결해야 함
            let plusBtn = null;
            if (listEl.closest('#placesSection')) {
                plusBtn = plusPlace;
            } else if (listEl.closest('#scheduleSection')) {
                plusBtn = plusSchedule;
            }
            // 아이템 스캔
            const items = listEl.querySelectorAll('.folder-item');
            items.forEach(item => attachDeleteEvent(item, listEl, plusBtn));

            // 초기 스크롤/버튼상태 갱신
            updateFolderListUI(listEl, plusBtn);
        });

        const folderItems = document.querySelectorAll(".folder-item");
        // 각 folder-item에 클릭 이벤트 추가
        folderItems.forEach(item => {
            item.addEventListener("click", async function () {
                if (event.target.classList.contains("delete-icon")) {
                    return; // 삭제 버튼 클릭 시 folder-item의 이벤트 실행 차단
                }
                
                // 새 폴더 버튼은 해당 안하니까 패스
                if (item.id !== "plus-place" && item.id !== "plus-schedule") {
                    const backBtn = document.getElementById('backBtn');
                    const backbookmarkTitleBtn = document.getElementById('bookmark_title');
                    const placeBtn = document.getElementById('placeBtn');
                    const scheduleBtn = document.getElementById('scheduleBtn');
                    const topmenu = document.querySelector('.top-menu');
                    const AllFolderLists = favoritesPanel.querySelectorAll('.folder-list');
                    const bookmarkPlaceItemDiv = document.querySelector(".bookmark-place-item");
                    const bookmarkScheduleItemDiv = document.querySelector(".bookmark-schedule-item");
                    
                    if (AllFolderLists) {
                        AllFolderLists.forEach(folderList => {
                            folderList.style.display = "none";
                        });
                    }
                    
                    topmenu.style.justifyContent = "start";
                    backBtn.style.display = "block";
                    backbookmarkTitleBtn.style.display = "block";
                    backbookmarkTitleBtn.textContent = item.textContent.trim().replace(/\s{2,}/g, '').replace(/\u00a0+/g, '');
                    placeBtn.style.display = "none";
                    scheduleBtn.style.display = "none";

                    // bookmark-place-item과 bookmark-schedule-item 초기화
                    if (bookmarkPlaceItemDiv) {                            
                        bookmarkPlaceItemDiv.style.display = "none";
                        bookmarkPlaceItemDiv.innerHTML = ""; // 기존 자식 요소 제거
                    }
                    if (bookmarkScheduleItemDiv) {
                        bookmarkScheduleItemDiv.style.display = "none";
                        bookmarkScheduleItemDiv.innerHTML = ""; // 기존 자식 요소 제거
                    }
                    
                    const bookmarkId = this.id; // 클릭된 div의 ID 가져오기
                    if (!bookmarkId || bookmarkId === "plus-place" || bookmarkId === "plus-schedule") {
                        return; // "새 폴더" 버튼 클릭 시 무시
                    }

                    try {
                        // 서버에 bookmark_id로 데이터 요청
                        const response = await fetch(`/app/partials/favorites/get_bookmark_items/${bookmarkId}/`, {
                            method: "GET",
                            headers: {
                                "Content-Type": "application/json",
                            },
                        });

                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }

                        const data = await response.json();
                        if (data.type === "place") {
                            // 장소 즐겨찾기
                            if (bookmarkPlaceItemDiv) {
                                bookmarkPlaceItemDiv.style.display = "block";

                                data.rows.forEach(row => {
                                    const itemDiv = document.createElement("div");
                                    itemDiv.className = "place-item";
                                    itemDiv.id = row.id;
                                    itemDiv.innerHTML = `
                                        <p style="display: flex; align-items: center;"><strong>이름:</strong> ${row.name}</p>
                                    `;
                                    itemDiv.addEventListener("click", async () => {
                                        // const editPanelTitleBtn = document.getElementById("editPanelTitleBtn");
                                        // editPanelTitleBtn.style.display = "contents";
                                        //DB에서 해당 데이터 불러오기
                                        document.querySelectorAll(".place-item").forEach(folder => {                                                
                                            folder.style.backgroundColor = ""; // 원래 색으로 복원 (CSS 초기값)
                                        });
                                        document.getElementById("getBookmarkListBtn").textContent = "★";
                                        itemDiv.style.backgroundColor = "#999";

                                        const bookmarkId = this.id; // folder-item의 ID 값
                                        if (!bookmarkId || bookmarkId === "plus-place" || bookmarkId === "plus-schedule") {
                                            return; // "새 폴더" 버튼은 클릭 이벤트 무시
                                        }

                                        try {
                                            // 서버에 bookmark_id로 데이터 요청
                                            const response = await fetch(`/app/partials/favorites/bookmark-place-detail/${row.id}/`, {
                                                method: "GET",
                                                headers: {
                                                    "Content-Type": "application/json",
                                                },
                                            });

                                            if (!response.ok) {
                                                throw new Error(`HTTP error! status: ${response.status}`);
                                            }
                                            
                                            // UI 업데이트: map-panel-content 또는 다른 요소에 데이터 표시
                                            const data = await response.json(); // JSON 응답 파싱
                                            const mapPanelContent = document.querySelector(".map-panel-content");
                                            if (!mapPanelContent) {
                                                console.error("map-panel-content element not found");
                                                return;
                                            }

                                            // 기존 내용 제거
                                            mapPanelContent.innerHTML = "";

                                            // 장소 정보 표시
                                            if (data) {
                                                const panelTitle = document.getElementById("panel-title");                                                        
                                                panelTitle.textContent = row.name;
                                                const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
                                                const dayButtonContainer = document.getElementById("day-button-container");
                                                if (dayButtonContainer) {
                                                    dayButtonContainer.textContent = "";
                                                }
                                                getBookmarkListBtn.classList.remove("schedule");
                                                getBookmarkListBtn.classList.add("place");
                                                getBookmarkListBtn.setAttribute("bookmark_id", row.bookmark);
                                                getBookmarkListBtn.setAttribute("bookmarkplace_id", row.id);
                                                getBookmarkListBtn.setAttribute("json_data", null);
                                                const placeSection = document.createElement("div");
                                                placeSection.className = "place-section";
                                                placeSection.innerHTML = `
                                                    <h3>장소 정보</h3>
                                                    <p><strong>이름:</strong> ${data.name}</p>
                                                    <p><strong>주소:</strong> ${data.address}</p>
                                                    <p><strong>설명:</strong> ${data.description || "설명이 없습니다."}</p>
                                                `;
                                                mapPanelContent.appendChild(placeSection);
                                                if (data.longitude && data.latitude && data.name) {
                                                    const markerData = [];
                                                    markerData.push({
                                                        position: new naver.maps.LatLng(data.latitude, data.longitude),
                                                        title: data.name,
                                                        icon: `https://chart.googleapis.com/chart?chst=d_map_pin_number&chld=${markerData.length + 1}|FF0000|000000`,
                                                    });
                                                    addMarkersToMap(markerData);
                                                }
                                                else if (data.address && data.name) {
                                                    const addresses = [];
                                                    addresses.push({
                                                        address: data.address,
                                                        title: data.name,
                                                    })
                                                    globalMarkerData = await getCoordinates(addresses);
                                                    addMarkersToMap(globalMarkerData);
                                                }
                                                else {
                                                    console.log("data에 든 게 하나도 없으니 마커를 띄우길 포기");
                                                }
                                            } else {
                                                const noDataMessage = document.createElement("p");
                                                noDataMessage.textContent = "해당 데이터가 없습니다.";
                                                mapPanelContent.appendChild(noDataMessage);
                                            }
                                        } catch (error) {
                                            console.error("Error fetching bookmark place data:", error);
                                        }
                                    });

                                    // 삭제 버튼 추가
                                    const deleteButton = document.createElement('img');
                                    deleteButton.src = document.body.getAttribute('data-theme') === 'light' 
                                        ? '/static/images/delete_light.png' 
                                        : '/static/images/delete_dark.png';
                                    deleteButton.style.cursor = 'pointer';
                                    deleteButton.style.marginLeft = 'auto';
                                    deleteButton.style.marginRight = '10px';
                                    deleteButton.style.opacity = '0.7';
                                    deleteButton.width = 25;
                                    deleteButton.height = 25;

                                    // 삭제 버튼 이벤트 추가
                                    deleteButton.addEventListener('click', (event) => {
                                        event.stopPropagation();
                                        // UI에서 제거
                                        bookmarkPlaceItemDiv.removeChild(itemDiv);

                                        //DB에서도 해당 데이터 제거
                                        deleteBookmarklist(row);
                                    });

                                    deleteButton.addEventListener('mouseover', () => {
                                        deleteButton.style.opacity = '1.0';
                                    });

                                    deleteButton.addEventListener('mouseleave', () => {
                                        deleteButton.style.opacity = '0.7';
                                    });

                                    itemDiv.appendChild(deleteButton);
                                    bookmarkPlaceItemDiv.appendChild(itemDiv);
                                });
                            }
                        } 
                        else if (data.type === "schedule") {
                            // 일정 즐겨찾기
                            if (bookmarkScheduleItemDiv) {
                                bookmarkScheduleItemDiv.style.display = "block";

                                data.rows.forEach(row => {
                                    const itemDiv = document.createElement("div");
                                    itemDiv.className = "schedule-item";
                                    itemDiv.id = row.id;
                                    itemDiv.innerHTML = `
                                        <p style="display: flex; align-items: center;"><strong>이름:</strong> ${row.name}</p>
                                    `;
                                    itemDiv.addEventListener("click", async () => {
                                        const editPanelTitleBtn = document.getElementById("editPanelTitleBtn");
                                        editPanelTitleBtn.style.display = "contents";
                                        document.querySelectorAll(".schedule-item").forEach(folder => {                                                
                                            folder.style.backgroundColor = ""; // 원래 색으로 복원 (CSS 초기값)
                                        });

                                        document.getElementById("getBookmarkListBtn").textContent = "★";
                                        itemDiv.style.backgroundColor = "#999";

                                        const bookmarkId = this.id; // folder-item의 ID 값
                                        if (!bookmarkId || bookmarkId === "plus-place" || bookmarkId === "plus-schedule") {
                                            return; // "새 폴더" 버튼은 클릭 이벤트 무시
                                        }

                                        try {
                                            // 서버에 bookmark_id로 데이터 요청
                                            const response = await fetch(`/app/partials/favorites/bookmark-schedule-detail/${row.id}/`, {
                                                method: "GET",
                                                headers: {
                                                    "Content-Type": "application/json",
                                                },
                                            });

                                            if (!response.ok) {
                                                throw new Error(`HTTP error! status: ${response.status}`);
                                            }

                                            // UI 업데이트: map-panel-content 또는 다른 요소에 데이터 표시
                                            const data = await response.json(); // JSON 응답 파싱
                                            const mapPanelContent = document.querySelector(".map-panel-content");
                                            if (!mapPanelContent) {
                                                console.error("map-panel-content element not found");
                                                return;
                                            }

                                            // 기존 내용 제거
                                            mapPanelContent.innerHTML = "";

                                            // 일정 정보 표시
                                            if (data) {
                                                const panelTitle = document.getElementById("panel-title");
                                                panelTitle.textContent = row.name;
                                                const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
                                                getBookmarkListBtn.classList.remove("place");
                                                getBookmarkListBtn.classList.add("schedule");
                                                getBookmarkListBtn.setAttribute("bookmark_id", row.bookmark);
                                                getBookmarkListBtn.setAttribute("bookmarkschedule_id", row.id);
                                                const jsonData = data.json_data;
                                                if (typeof json_data === "string") {
                                                    jsonData = JSON.parse(data.json_data);
                                                }    
                                                getBookmarkListBtn.setAttribute("json_data", jsonData);
                                                generateDayButtons(jsonData);
                                                generateDynamicPlanContent(jsonData);
                                            } else {
                                                const noDataMessage = document.createElement("p");
                                                noDataMessage.textContent = "해당 데이터가 없습니다.";
                                                mapPanelContent.appendChild(noDataMessage);
                                            }
                                        } catch (error) {
                                            console.error("Error fetching bookmark place data:", error);
                                        }
                                    });

                                    // 삭제 버튼 추가
                                    const deleteButton = document.createElement('img');
                                    deleteButton.src = document.body.getAttribute('data-theme') === 'light' 
                                        ? '/static/images/delete_light.png' 
                                        : '/static/images/delete_dark.png';
                                    deleteButton.style.cursor = 'pointer';
                                    deleteButton.style.marginLeft = 'auto';
                                    deleteButton.style.marginRight = '10px';
                                    deleteButton.style.opacity = '0.7';
                                    deleteButton.width = 25;
                                    deleteButton.height = 25;

                                    // 삭제 버튼 이벤트 추가
                                    deleteButton.addEventListener('click', (event) => {
                                        event.stopPropagation();
                                        // UI에서 제거  
                                        itemDiv.remove();

                                        //DB에서도 해당 데이터 제거
                                        console.log("bookmarkplace_id:", row.bookmark); //bm_00001
                                        console.log("data:", row.id); 
                                        deleteBookmarklist(row);
                                    });

                                    deleteButton.addEventListener('mouseover', () => {
                                        deleteButton.style.opacity = '1.0';
                                    });

                                    deleteButton.addEventListener('mouseleave', () => {
                                        deleteButton.style.opacity = '0.7';
                                    });

                                    itemDiv.appendChild(deleteButton);
                                    bookmarkScheduleItemDiv.appendChild(itemDiv);
                                });
                            }
                        }
                        else {
                            console.log("No data found");
                        }
                    } catch (error) {
                        console.error("Error fetching bookmark data:", error);
                    }
                }
            });
        });
    
    } // if (favoritesPanel)
    
    // 4) Settings Panel
    const settingsPanel= document.getElementById("settingsPanel");
    if (settingsPanel) {
        console.log("[settings] panel detected!");
        const lightBox = document.getElementById('light');
        const darkBox = document.getElementById('dark');
        const lightRadio = document.querySelector("input[name='theme'][value='light']");
        const darkRadio = document.querySelector("input[name='theme'][value='dark']");
        const themeRadios = document.querySelectorAll('input[name="theme"]');

        function selectTheme(theme) {
            lightBox.classList.remove('selected');
            darkBox.classList.remove('selected');

            if (theme === 'light') {
                lightBox.classList.add('selected');
                lightRadio.checked = true;
            } else if (theme === 'dark') {
                darkBox.classList.add('selected');
                darkRadio.checked = true;
            }
        }

        lightBox.addEventListener('click', () => selectTheme('light'));
        darkBox.addEventListener('click', () => selectTheme('dark'));

        // 테마 선택 변경 시 서버에 업데이트
        themeRadios.forEach(radio => {
            radio.addEventListener("change", () => {
                const isLightTheme = radio.value === "light";
                document.body.setAttribute("data-theme", isLightTheme ? "light" : "dark");
                updateIconsBasedOnTheme();
                
                fetch("/app/partials/settings/update_theme/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                    body: JSON.stringify({ is_white_theme: isLightTheme }),
                })
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error("Theme update failed.");
                        }
                        console.log("Theme updated successfully.");
                    })
                    .catch((err) => console.error("Error updating theme:", err));
            });
        });

        const initialTheme = document.body.getAttribute("data-theme") === "light";
        updateIconsBasedOnTheme(initialTheme);

        const languageSelect = document.getElementById('language');
        if (languageSelect) {
            languageSelect.addEventListener('change', async () => {
                const selectedLanguage = languageSelect.value;

                try {
                    const response = await fetch('/app/partials/settings/update_language/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken(), // CSRF 토큰 추가
                        },
                        body: JSON.stringify({ language: selectedLanguage }),
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    if (result.success) {
                        switch (countryId) {
                            case "KR": alert('언어가 성공적으로 업데이트되었습니다!'); break;
                            case "JP": alert('言語が正常に更新されました！'); break;
                            case "CN": alert('语言更新成功！'); break;
                            case "US": alert('Language updated successfully!'); break;
                        }
                    }
                } catch (error) {
                    console.error("Error updating language:", error);
                    switch (countryId) {
                        case "KR": alert('언어를 업데이트하지 못했습니다. 다시 시도해 주세요.'); break;
                        case "JP": alert('言語の更新に失敗しました。 もう一度お試しください。'); break;
                        case "CN": alert('语言更新失败 。 请再试一次。'); break;
                        case "US": alert('Failed to update language. Please try again.'); break;
                    }
                }
            });
        }
    }

    // 5) Profile Panel
    const profilePanel = document.getElementById("profilePanel");
    if (profilePanel) {
        console.log("[profile] panel detected!");

        const profileImage = document.getElementById("profile-image");
        const popup = document.getElementById("image-popup");
        const popupImages = document.querySelectorAll(".popup-image");
        
        // 프로필 이미지를 클릭하면 팝업 표시
        profileImage.addEventListener("click", function () {
            popup.classList.remove("hidden");
            toggleButton.classList.add("hidden");
        });

        // 팝업 이미지 클릭 시 서버로 thumbnail_id 업데이트
        popupImages.forEach(image => {
            image.addEventListener("click", function () {
                const selectedId = this.dataset.id;

                // 서버로 AJAX 요청
                fetch("/app/partials/profile/update_thumbnail/", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken()
                    },
                    body: JSON.stringify({ thumbnail_id: selectedId })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            // 성공 시 프로필 이미지 업데이트
                            profileImage.src = `/static/images/profiles/profile_${selectedId}.jpg`;                                    
                        } else {
                            switch (countryId) {
                                case "KR": alert('프로필 이미지 업데이트 실패'); break;
                                case "JP": alert('プロフィール画像の更新に失敗'); break;
                                case "CN": alert('更新配置文件失败'); break;
                                case "US": alert('Failed to update profile image'); break;
                            }
                        }
                        popup.classList.add("hidden");
                        toggleButton.classList.remove("hidden");
                    })
                    .catch(err => {
                        console.error("Error updating profile image:", err);
                    });
            });
        });

        // 팝업 외부 클릭 시 닫기
        if (popup) {
            popup.addEventListener("click", function (e) {
                if (e.target === popup) {
                    popup.classList.add("hidden");
                    toggleButton.classList.remove("hidden");
                }
            });
        }

        // 1) 닉네임 수정
        const nicknameText  = document.getElementById('nickname-text');
        const nicknameInput = document.getElementById('nickname-input');
        const editButton    = document.getElementById('edit-btn');
        const logoutBtn     = document.getElementById("logout-btn");

        let oldNickname = nicknameText ? nicknameText.textContent : "";

        let escNote = document.createElement("div");
        escNote.style.color = "#999";      // 예시 스타일
        escNote.style.fontSize = "0.9rem"; // 예시
        escNote.textContent = "(ENTER: edit / ESC: cancel)";

        if (editButton && nicknameText && nicknameInput) {
            editButton.addEventListener("click", function() {
                // 연필 버튼 클릭 시
                oldNickname = nicknameText.textContent; // 현재 닉네임 저장
                nicknameText.classList.add("hidden");   // 숨김
                nicknameInput.classList.remove("hidden");
                nicknameInput.value = oldNickname;      // 입력창 초기값
                nicknameInput.focus();

                const wrapper = document.querySelector(".nickname-wrapper");
                if (wrapper) {
                    wrapper.appendChild(escNote);
                }
            });

            // (1) Enter -> 저장
            nicknameInput.addEventListener("keydown", function(e) {
                if (e.key === "Enter") {
                    const newNickname = nicknameInput.value.trim();
                    if (newNickname) {
                        nicknameText.textContent = newNickname;
                    }
                    nicknameText.classList.remove("hidden");
                    nicknameInput.classList.add("hidden");

                    // 안내 문구 제거
                    removeEscNote();

                    // 서버로 AJAX 요청
                    fetch("/app/partials/profile/update_nickname/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken(),
                        },
                        body: JSON.stringify({ nickname: newNickname }),
                    })
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json(); // JSON 파싱
                    })
                    .then((data) => {
                        if (data.success) {
                            // 성공 시 UI 업데이트
                            nicknameText.textContent = newNickname;
                        } else {
                            switch (countryId) {
                                case "KR": alert('닉네임 수정 실패'); break;
                                case "JP": alert('ニックネーム修正失敗'); break;
                                case "CN": alert('修改昵称失败'); break;
                                case "US": alert('Failed to modify the nickname'); break;
                            }
                        }
                    })
                    .catch((err) => {
                        console.error("서버 통신 오류:", err);
                    })
                    .finally(() => {
                        // 입력창 숨기고 라벨 보이기
                        nicknameInput.classList.add("hidden");
                        nicknameText.classList.remove("hidden");
                    });
                }
                // (2) ESC -> 취소 (원래 닉네임 복원)
                else if (e.key === "Escape") {
                    nicknameInput.value = oldNickname;
                    nicknameText.classList.remove("hidden");
                    nicknameInput.classList.add("hidden");

                    // 안내 문구 제거
                    removeEscNote();
                }
            });
        }

        // (4) 안내 문구 제거 함수
        function removeEscNote() {
            if (escNote && escNote.parentNode) {
                escNote.parentNode.removeChild(escNote);
            }
        }

        // (5) 로그아웃 버튼
        if (logoutBtn) {
            logoutBtn.addEventListener("click", function() {
                switch (countryId) {
                    case "KR": alert('로그아웃 되었습니다.'); break;
                    case "JP": alert('ログアウトされました。'); break;
                    case "CN": alert('已注销。'); break;
                    case "US": alert('Log out'); break;
                }
                window.location.href = "/";
            });
        }
    }
    
    // 6) 채팅 입력창 로직
    const inputBar = document.getElementById("input_bar");  
    const deleteBtn = document.querySelector('.delete-btn');
    const sendBtn = document.querySelector('.send-button');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', showPopup);
    }

    if (inputBar) {
        inputBar.addEventListener("keydown", function (e) {
            inputBarKeyDown(e, isLoading, inputBar);
        });
        inputBar.addEventListener("input", resizeInput);
        // resizeInput();
    }          
    
    if (sendBtn) {
        sendBtn.addEventListener("click", function (e) {
            if (isLoading) {
                e.preventDefault(); // 로딩 중일 때 입력 방지
                switch (countryId) {
                    case "KR": alert('현재 봇 응답이 생성 중입니다. 잠시만 기다려주세요!'); break;
                    case "JP": alert('現在、ボット応答が作成中です。 少々お待ちください！'); break;
                    case "CN": alert('目前正在生成机器人响应。 请稍等！'); break;
                    case "US": alert('The bot response is currently generating. Please wait!'); break;
                }
                return;
            }

            e.preventDefault();    
            const chatMessages = document.getElementById("chat-messages");
            chatMessages.scrollTop = chatMessages.scrollHeight;           
            sendMessage();
        });
    }
    
    function inputBarKeyDown(e, isLoading, inputBar) {
        if (e.key === "Enter" && !e.shiftKey) {
            if (isLoading) {
                e.preventDefault(); // 로딩 중일 때 입력 방지
                switch (countryId) {
                    case "KR": alert('현재 봇 응답이 생성 중입니다. 잠시만 기다려주세요!'); break;
                    case "JP": alert('現在、ボット応答が作成中です。 少々お待ちください！'); break;
                    case "CN": alert('目前正在生成机器人响应。 请稍等！'); break;
                    case "US": alert('The bot response is currently generating. Please wait!'); break;
                }
                return;
            }

            e.preventDefault();    
            const chatMessages = document.getElementById("chat-messages");
            chatMessages.scrollTop = chatMessages.scrollHeight;           
            sendMessage();
            return false;
        } 
        else if (e.key === "Enter" && e.shiftKey) {
            e.preventDefault();
            const cursorPosition = inputBar.selectionStart;
            inputBar.value =
                inputBar.value.slice(0, cursorPosition) + "\n"
                + inputBar.value.slice(cursorPosition);
            // resizeInput();
            return false;
        }
    }

    async function sendMessage() {
        if (isLoading) return; // 로딩 중일 때 메시지 전송 방지

        const message = inputBar.value.trim(); // 사용자가 입력한 메시지
        
        let chatHistory = "";
        if (message === "") return;

        const result = await saveChatToDB(`<나>${message}`);
        if (result) {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const chatId = urlParams.get("chat_id");    
                const response = await fetch(`/app/partials/planner/get_chat/?chat_id=${chatId}`, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCSRFToken(),
                    },
                });
    
                const data = await response.json();
                if (response.ok && data.success) {
                    chatHistory = data.content;
                    
                    // 로딩 상태로 설정
                    isLoading = true;
                    inputBar.disabled = true; // 입력창 비활성화
    
                    // 사용자의 메시지를 채팅창에 추가
                    const userMessage = document.createElement("div");
                    userMessage.className = "bubble right-bubble";
                    userMessage.innerHTML = message.replace(/\n/g, "<br>");
                    chatMessages.appendChild(userMessage);                
    
                    inputBar.value = ""; // 입력창 초기화
    
                    const loadingBubble = document.createElement("div");
                    loadingBubble.classList.add("bubble", "left-bubble", "loading-bubble");
                    loadingBubble.innerHTML = `
                        <div class="loader">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    `;
                    chatMessages.appendChild(loadingBubble);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
    
                    if (activeAbortController) {
                        activeAbortController.abort();
                    }
                    // 새로운 AbortController 생성
                    activeAbortController = new AbortController();
                    const { signal } = activeAbortController;
                    chatHistory = parse_chat_history(chatHistory);
                    fetchGPTResponse(message, signal, chatHistory);
                } else {
                    console.error(`/app/partials/planner/get_chat/ 실패 chatId=${chatId}, response=${response}`);
                }
            } catch {
                console.error("/app/partials/planner/get_chat/ failed");
            }
        } else {
            const chatContainer = document.querySelector(".chat-container");
            if (chatContainer) {
                const errorBubble = document.createElement("div");
                errorBubble.className = "error-bubble";
                errorBubble.innerHTML = "채팅 내역이 꽉 찼습니다! 이 채팅은 저장되지 않습니다.<br>기존 채팅 내역을 사용해주세요.<br>현재 채팅에는 글 초기화 버튼이 작동하지 않습니다.";
                errorBubble.style.position = "relative";
                errorBubble.style.padding = "10px";
                errorBubble.style.margin = "10px 0";
                errorBubble.style.backgroundColor = "#ffcccc";
                errorBubble.style.color = "#900";
                errorBubble.style.border = "1px solid #f00";
                errorBubble.style.borderRadius = "5px";
                errorBubble.style.fontSize = "14px";

                // 이미 말풍선이 존재하면 추가하지 않음
                if (!chatContainer.querySelector(".error-bubble")) {
                    chatContainer.insertBefore(errorBubble, chatContainer.firstChild); // 맨 위에 추가
                }
            }
            console.log("wowowowow");
            // 로딩 상태로 설정
            isLoading = true;
            inputBar.disabled = true; // 입력창 비활성화

            // 사용자의 메시지를 채팅창에 추가
            const userMessage = document.createElement("div");
            userMessage.className = "bubble right-bubble";
            userMessage.innerHTML = message.replace(/\n/g, "<br>");
            chatMessages.appendChild(userMessage);                

            inputBar.value = ""; // 입력창 초기화

            const loadingBubble = document.createElement("div");
            loadingBubble.classList.add("bubble", "left-bubble", "loading-bubble");
            loadingBubble.innerHTML = `
                <div class="loader">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;
            chatMessages.appendChild(loadingBubble);
            chatMessages.scrollTop = chatMessages.scrollHeight;

            if (activeAbortController) {
                activeAbortController.abort();
            }
            // 새로운 AbortController 생성
            activeAbortController = new AbortController();
            const { signal } = activeAbortController;
            chatHistory = parse_chat_history(chatHistory);
            fetchGPTResponse(message, signal, chatHistory);
        }
    }

    function parse_chat_history(chatHistory) {
        const tokens = chatHistory.split(/(<나>|<봇>)/);

        const result = [];
        let currentRole = null;

        for (let chunk of tokens) {
            // 앞뒤 공백 제거
            chunk = chunk.trim();

            // 비어있으면 무시
            if (!chunk) {
            continue;
            }

            if (chunk === '<나>') {
            currentRole = 'user';
            } else if (chunk === '<봇>') {
            currentRole = 'assistant';
            } else {
            // chunk가 실제 대화 내용
            if (currentRole === null) {
                // 처음부터 <나>나 <봇>이 없이 문자열이 시작됐다면 user로 간주
                currentRole = 'user';
            }
            result.push({ role: currentRole, content: chunk });
            }
        }
        return result;
    }

    function updateChatBubble(botMessage, chunk) {
        const chatMessages = document.querySelector("#chat-messages"); // 채팅 메시지 영역                

        botMessage.innerHTML = chunk;
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function fetchGPTResponse(userInput, signal, chatHistory = null) {
        try {
            const response = await fetch("/app/partials/planner/run-gpt/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
                body: JSON.stringify({ 
                    question: userInput,
                    chat_history: chatHistory,
                }),
                signal,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // 스트리밍 데이터 읽기
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");

            const chatMessages = document.querySelector("#chat-messages"); 
            let buffer = ""; // 청크를 임시로 저장할 버퍼
            let botBubble = document.createElement("div"); // 새 말풍선을 생성
            botBubble.className = "bubble left-bubble";
            botBubble.textContent = "";
            botBubble.classList.add("bubble", "left-bubble");
            document.querySelector(".loading-bubble").remove(); // 로딩 채팅 창 없애기
            chatMessages.appendChild(botBubble);

            botBubble.addEventListener("mouseenter", function (event) {
                if (botBubble.className.includes("left-bubble")) {
                    this.style.backgroundColor = "#589258"; // 기본 하이라이트 색상
                }
            });

            botBubble.addEventListener("mouseleave", function (event) {
                if (botBubble.className.includes("left-bubble")) {
                    this.style.backgroundColor = ""; // 원래 배경색 복구
                }
            });

            botBubble.addEventListener("click", function (event) {
                const messageContent = this.innerHTML.trim(); // 메시지 내용 가져오기
                const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");

                if (botBubble.className.includes("left-bubble")) {
                    // 서식을 유지한 상태로 출력
                    const panelTitle = document.getElementById("panel-title");
                    panelTitle.textContent = "";
                    const formattedMessage = messageContent
                        .replace(/<br\s*\/?>/gi, "\n") // <br> 태그를 줄바꿈으로 변환
                        .replace(/&nbsp;/g, " ");     // &nbsp;를 공백으로 변환

                    const jsonData1 = parseScheduleJson_KR(formattedMessage);
                    const jsonData2 = parseItineraryToJson_JP(formattedMessage);
                    const jsonData3 = parseItineraryToJson_CN(formattedMessage);
                    const jsonData4 = parseItineraryToJson_US(formattedMessage);
                    const jsonData5 = parsePlaceJson_KR(formattedMessage);
                    const jsonData6 = parsePlaceJson_JP(formattedMessage);
                    const jsonData7 = parsePlaceJson_CN(formattedMessage);
                    const jsonData8 = parsePlaceJson_US(formattedMessage);

                    let jsonScheduleData = [];
                    if (Array.isArray(jsonData1) && jsonData1.length > 0) {
                        jsonScheduleData = jsonData1;
                    } else if (Array.isArray(jsonData2) && jsonData2.length > 0) {
                        jsonScheduleData = jsonData2;
                    } else if (Array.isArray(jsonData3) && jsonData3.length > 0) {
                        jsonScheduleData = jsonData3;
                    } else if (Array.isArray(jsonData4) && jsonData4.length > 0) {
                        jsonScheduleData = jsonData4;
                    }

                    let jsonPlaceData = [];
                    if (!isEmptyJson(jsonData5)) {
                        jsonPlaceData = jsonData5;
                    } else if (!isEmptyJson(jsonData6)) {
                        jsonPlaceData = jsonData6;
                    } else if (!isEmptyJson(jsonData7)) {
                        jsonPlaceData = jsonData7;
                    } else if (!isEmptyJson(jsonData8)) {
                        jsonPlaceData = jsonData8;
                    }
                    if (jsonScheduleData.length !== 0) {
                        generateDayButtons(jsonScheduleData);
                        generateDynamicPlanContent(jsonScheduleData);
                        getBookmarkListBtn.textContent = "☆";
                        getBookmarkListBtn.setAttribute("json_data", JSON.stringify(jsonScheduleData));
                    }
                    else if (jsonPlaceData.length !== 0) {
                        generatePlaceContent(jsonPlaceData);
                        getBookmarkListBtn.textContent = "☆";
                        getBookmarkListBtn.setAttribute("json_data", JSON.stringify(jsonPlaceData));
                    }
                }
            });

            while (true) {
                const { done, value } = await reader.read(); // 스트림 읽기
                if (done) break; // 스트림 끝 도달

                const chunk = decoder.decode(value, { stream: true }); // 청크 디코딩
                buffer += chunk; // 버퍼에 데이터 추가
                // console.log("chunk:", chunk);
                updateChatBubble(botBubble, buffer); // 실시간으로 말풍선 업데이트
            }

            // 마지막 남은 버퍼 처리
            if (buffer.trim()) {                    
                updateChatBubble(botBubble, buffer + "\n");
            }

            saveChatToDB(`<봇>${buffer}`);
        } catch (error) {
            if (error.name === "AbortError") {
                console.log("요청이 취소되었습니다.");
            } else {
                console.error("Error fetching GPT response:", error);
            }
            return null;
        } finally {
            isLoading = false;
            inputBar.disabled = false; // 입력창 활성화
            inputBar.focus();
        }
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
});

async function saveChatToDB(chatContent) {
    // 현재 URL에서 chat_id 추출
    localStorage.removeItem('chatMessage');
    const urlParams = new URLSearchParams(window.location.search);
    const chatId = urlParams.get("chat_id");
    if (!chatId) return;

    return fetch("/app/partials/planner/save_chat/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(), // Django CSRF 토큰
        },
        body: JSON.stringify({
            chat: chatContent,
            chat_id: chatId, // URL에서 가져온 chat_id를 전송
        }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    })
    .then(data => {
        if (!data.success) {
            console.error("Failed to save chat to DB:", data.error);
            if (data.error === "채팅 내역이 꽉 찼습니다!") {
                console.log("채팅 내역이 꽉 찼습니다!");
            }

            return null;
        } 
        else {
            if (data.chatting_id) {
                console.log("chat id:", data.chatting_id, "Chat saved successfully:", data.message || "Success", chatContent);
                // 기존의 chat_id가 있었다면 URL을 업데이트
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set("chat_id", data.chatting_id); 
                window.history.replaceState(null, "", newUrl.toString());
                lastLoadedPath = newUrl.toString();
                
                return data.chatting_id;
            }
            if (data.new_chat_id) {
                console.log("chat id:", data.chatting_id, "New Chat ID:", data.message || "Success", chatContent);
                // 새 chat_id가 생성되었다면 URL을 업데이트
                const newChatId = data.new_chat_id;
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set("chat_id", newChatId);
                window.history.replaceState(null, "", newUrl.toString());
                lastLoadedPath = newUrl.toString();

                return newChatId;
            }
        }
    })
    .catch(error => {
        console.error("Error saving chat to DB:", error);
        return null;
    });
}

function typeText(element, text, loadingBubble, speed = 5) {
    let index = 0;

    // 로딩 버블 제거
    if (loadingBubble && loadingBubble.parentNode) {
        loadingBubble.parentNode.removeChild(loadingBubble);
    }

    // 타이핑 애니메이션 처리
    function typeNextChar() {
        if (index < text.length) {
            const char = text[index] === "\n" ? document.createElement("br") : document.createTextNode(text[index]);
            if (char instanceof Node) {
                element.appendChild(char);
            }
            index++;

            // 스크롤을 강제하지 않고도 실행
            // element.scrollTop = element.scrollHeight;

            setTimeout(typeNextChar, speed);
        } else {
            // 애니메이션 종료 후 로딩 상태 해제
            isLoading = false;
        }
    }
    typeNextChar();
}

function isEmptyJson(jsonObj) {
    return Object.values(jsonObj).every(value => 
        value === "" || 
        (Array.isArray(value) && value.length === 0) || 
        (typeof value === "object" && value !== null && Object.keys(value).length === 0)
    );
}

function parseAndDisplayChatContent(chatContent) {
    if (!chatContent) {
        console.warn("chatContent가 비어있습니다.");
        return;
    }

    // HTML Escape 처리 제거
    chatContent = chatContent
        .replace(/&lt;/g, "<")
        .replace(/&gt;/g, ">")
        .replace(/&amp;/g, "&");

    // <나>, <봇> 기준으로 데이터 분리
    const tokens = chatContent.split(/(<나>|<봇>)/g).filter(token => token.trim() !== "");

    const chatMessages = document.getElementById("chat-messages");
    if (!chatMessages) {
        console.error("#chat-messages 요소를 찾을 수 없습니다.");
        return;
    }

    // 기존 DOM 초기화
    chatMessages.innerHTML = "";

    // 대화 내용 파싱 및 렌더링
    let currentSpeaker = null;
    tokens.forEach(token => {
        if (token === "<나>") {
            currentSpeaker = "user";
        } else if (token === "<봇>") {
            currentSpeaker = "bot";
        } else {
            // 메시지 텍스트 처리
            const bubble = document.createElement("div");
            bubble.classList.add("bubble");
            bubble.addEventListener("mouseenter", function (event) {
                if (bubble.className.includes("left-bubble")) {
                    this.style.backgroundColor = "#589258"; // 기본 하이라이트 색상
                }
            });

            // 마우스 아웃 이벤트
            bubble.addEventListener("mouseleave", function (event) {
                if (bubble.className.includes("left-bubble")) {
                    this.style.backgroundColor = ""; // 원래 배경색 복구
                }
            });

            bubble.addEventListener("click", function (event) {
                const messageContent = this.innerHTML.trim(); // 메시지 내용 가져오기
                const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
                if (bubble.className.includes("left-bubble")) {
                    const panelTitle = document.getElementById("panel-title");
                    panelTitle.textContent = "";

                    // 서식을 유지한 상태로 출력
                    const formattedMessage = messageContent
                        .replace(/<br\s*\/?>/gi, "\n") // <br> 태그를 줄바꿈으로 변환
                        .replace(/&nbsp;/g, " ");     // &nbsp;를 공백으로 변환

                    const jsonData1 = parseScheduleJson_KR(formattedMessage);
                    const jsonData2 = parseItineraryToJson_JP(formattedMessage);
                    const jsonData3 = parseItineraryToJson_CN(formattedMessage);
                    const jsonData4 = parseItineraryToJson_US(formattedMessage);
                    const jsonData5 = parsePlaceJson_KR(formattedMessage);
                    const jsonData6 = parsePlaceJson_JP(formattedMessage);
                    const jsonData7 = parsePlaceJson_CN(formattedMessage);
                    const jsonData8 = parsePlaceJson_US(formattedMessage);

                    let jsonScheduleData = [];
                    if (Array.isArray(jsonData1) && jsonData1.length > 0) {
                        jsonScheduleData = jsonData1;
                    } else if (Array.isArray(jsonData2) && jsonData2.length > 0) {
                        jsonScheduleData = jsonData2;
                    } else if (Array.isArray(jsonData3) && jsonData3.length > 0) {
                        jsonScheduleData = jsonData3;
                    } else if (Array.isArray(jsonData4) && jsonData4.length > 0) {
                        jsonScheduleData = jsonData4;
                    }

                    let jsonPlaceData = [];
                    if (!isEmptyJson(jsonData5)) {
                        jsonPlaceData = jsonData5;
                    } else if (!isEmptyJson(jsonData6)) {
                        jsonPlaceData = jsonData6;
                    } else if (!isEmptyJson(jsonData7)) {
                        jsonPlaceData = jsonData7;
                    } else if (!isEmptyJson(jsonData8)) {
                        jsonPlaceData = jsonData8;
                    }
                    if (jsonScheduleData.length !== 0) {
                        
                        generateDayButtons(jsonScheduleData);
                        generateDynamicPlanContent(jsonScheduleData);
                        getBookmarkListBtn.setAttribute("json_data", JSON.stringify(jsonScheduleData));
                    }
                    else if (jsonPlaceData.length !== 0) {
                        generatePlaceContent(jsonPlaceData);
                        getBookmarkListBtn.setAttribute("json_data", JSON.stringify(jsonPlaceData));
                    }
                }
            });

            // 서식 그대로 출력
            const formattedText = token
                .replace(/\\n/g, "<br>")   // 줄바꿈
                .replace(/\\r/g, "")      // \r 제거
                .replace(/ {2}/g, "&nbsp;&nbsp;"); // 연속된 띄어쓰기 처리

            bubble.innerHTML = formattedText;

            // 스피커에 따라 스타일 지정
            if (currentSpeaker === "user") {
                bubble.classList.add("right-bubble");
            } else if (currentSpeaker === "bot") {
                bubble.classList.add("left-bubble");
            }

            chatMessages.appendChild(bubble);
        }
    });
}

function parseScheduleJson_KR(text) {
    text = text.replace(/([^\n])(\s*- \*\*\d+일차\*\*:)/g, "$1\n$2");
    const lines = text.split("\n");
    const result = [];
    let currentDay = null;
    let currentMeal = null;
    let currentSection = null;

    lines.forEach(line => {
        const trimmedLine = line.trim();
        // console.log("t:", trimmedLine);
        if (!trimmedLine) return; // 빈 줄 무시

        // dayMatch 처리
        const dayMatch = trimmedLine.match(/^\- \*\*(\d+)일차\*\*/);
        if (dayMatch) {
            currentDay = {
                day: parseInt(dayMatch[1]),
                meals: {}
            };
            result.push(currentDay);
        }

        const mealMatch = trimmedLine.match(/^\- \*\*(아침|점심|저녁)\*\*/);
        if (mealMatch) {
            currentMeal = mealMatch[1];
            if (currentDay && !currentDay.meals[currentMeal]) {
                currentDay.meals[currentMeal] = {
                    "식사 장소": {
                        "음식점 이름": null,
                        "음식점 주소": null,
                        "영업 시간": null,
                        "음식점 특징": null,
                        "기타 정보": null,
                    },
                    "명소": {
                        "명소 이름": null,
                        "명소 주소": null,
                        "영업 시간": null,
                        "명소 특징": null,
                        "기타 정보": null,
                    },
                    "카페": {
                        "카페 이름": null,
                        "카페 주소": null,
                        "영업 시간": null,
                        "카페 정보": null,
                        "카페 특징": null,
                    },
                    "숙소": {
                        "숙소 이름": null,
                        "숙소 특징": null,
                        "숙소 위치": null,
                        "숙소 정보": null,
                    },
                    "쇼핑몰": {
                        "쇼핑몰 이름": null,
                        "쇼핑몰 주소": null,
                        "쇼핑몰 정보": null,
                    },
                };
            }
            currentSection = null;
        } 

        // Key-Value 처리
        const keyValueMatch = trimmedLine.match(/- \*\*(.*?)\*\*: (.*)/);
        if (keyValueMatch && currentDay && currentMeal) {
            const [, key, value] = keyValueMatch;
            const mealSection = currentDay.meals[currentMeal];
            
            if (key.includes("식사 장소")) {
                mealSection["식사 장소"]["음식점 이름"] = value;
                currentSection = "식사 장소";
            } else if (key === "명소") {
                mealSection["명소"]["명소 이름"] = value;
                currentSection = "명소";
            } else if (key === "카페") {
                mealSection["카페"]["카페 이름"] = value;
                currentSection = "카페";
            } else if (key === "숙소") {
                mealSection["숙소"]["숙소 이름"] = value;
                currentSection = "숙소";
            } else if (key === "쇼핑몰") {
                mealSection["쇼핑몰"]["쇼핑몰 이름"] = value;
                currentSection = "쇼핑몰";
            } 

            if (currentSection) {
                if (currentSection === "식사 장소") {
                    if (key === "주소") mealSection["식사 장소"]["음식점 주소"] = value;
                    if (key === "영업 시간") mealSection["식사 장소"]["영업 시간"] = value;
                    if (key === "음식점 특징") mealSection["식사 장소"]["음식점 특징"] = value;
                    if (key === "기타 정보") mealSection["식사 장소"]["기타 정보"] = value;
                } else if (currentSection === "명소") {
                    if (key === "주소") mealSection["명소"]["명소 주소"] = value;
                    if (key === "영업 시간") mealSection["명소"]["영업 시간"] = value;
                    if (key === "명소 특징") mealSection["명소"]["명소 특징"] = value;
                    if (key === "기타 정보") mealSection["명소"]["기타 정보"] = value;
                }  else if (currentSection === "카페") {
                    if (key === "주소") mealSection["카페"]["카페 주소"] = value;
                    if (key === "영업 시간") mealSection["카페"]["영업 시간"] = value;
                    if (key === "카페 정보") mealSection["카페"]["카페 정보"] = value;
                    if (key === "카페 특징") mealSection["카페"]["카페 특징"] = value;
                }  else if (currentSection === "숙소") {
                    if (key === "숙소 특징") mealSection["숙소"]["숙소 특징"] = value;
                    if (key === "숙소 위치") mealSection["숙소"]["숙소 위치"] = value;
                    if (key === "숙소 정보") mealSection["숙소"]["숙소 정보"] = value;
                }  else if (currentSection === "쇼핑몰") {
                    if (key === "쇼핑몰 주소") mealSection["쇼핑몰"]["쇼핑몰 주소"] = value;
                    if (key === "쇼핑몰 정보") mealSection["쇼핑몰"]["쇼핑몰 정보"] = value;
                }
            } 
        } 
    });
    
    return result;
}

function parseItineraryToJson_JP(text) {
    text = text.replace(/([^\n])(\s*- \*\*\d+日目\*\*:)/g, "$1\n$2");
    const lines = text.split("\n");
    const result = [];
    let currentDay = null;
    let currentMeal = null;
    let currentSection = null;

    lines.forEach(line => {
        const trimmedLine = line.trim();
        // console.log("t:", trimmedLine);
        if (!trimmedLine) return; // 빈 줄 무시

        // dayMatch 처리
        const dayMatch = trimmedLine.match(/^\- \*\*(\d+)日目\*\*/);
        if (dayMatch) {
            currentDay = {
                day: parseInt(dayMatch[1]),
                meals: {}
            };
            result.push(currentDay);
        }

        const mealMatch = trimmedLine.match(/^\- \*\*(朝|昼|夜)\*\*/);
        if (mealMatch) {
            currentMeal = mealMatch[1];
            if (currentDay && !currentDay.meals[currentMeal]) {
                currentDay.meals[currentMeal] = {
                    "食場所": {
                        "レストラン名": null,
                        "レストラン住所": null,
                        "営業時間": null,
                        "レストランの特徴": null,
                        "その他情報": null,
                    },
                    "観光名所": {
                        "名所名": null,
                        "名所住所": null,
                        "営業時間": null,
                        "名所の特徴": null,
                        "その他情報": null,
                    },
                    "カフェ": {
                        "カフェ名": null,
                        "カフェ住所": null,
                        "営業時間": null,
                        "カフェ情報": null,
                        "カフェの特徴": null,
                    },
                    "宿泊施設": {
                        "宿泊施設名": null,
                        "宿泊施設の特徴": null,
                        "宿泊施設の位置": null,
                        "宿泊施設情報": null,
                    },
                    "ショッピングモール": {
                        "ショッピングモール名": null,
                        "ショッピングモール住所": null,
                        "ショッピングモール情報": null,
                    },
                };
            }
            currentSection = null;
        } 

        // Key-Value 처리
        const keyValueMatch = trimmedLine.match(/- \*\*(.*?)\*\*: (.*)/);
        if (keyValueMatch && currentDay && currentMeal) {
            const [, key, value] = keyValueMatch;
            const mealSection = currentDay.meals[currentMeal];

            if (key.includes("食場所")) {
                mealSection["食場所"]["レストラン名"] = value;
                currentSection = "食場所";
            } else if (key === "観光名所") {
                mealSection["観光名所"]["名所名"] = value;
                currentSection = "観光名所";
            } else if (key === "カフェ") {
                mealSection["カフェ"]["カフェ名"] = value;
                currentSection = "カフェ";
            } else if (key === "宿泊施設") {
                mealSection["宿泊施設"]["宿泊施設名"] = value;
                currentSection = "宿泊施設";
            } else if (key === "ショッピングモール") {
                mealSection["ショッピングモール"]["ショッピングモール名"] = value;
                currentSection = "ショッピングモール";
            } 

            if (currentSection) {
                if (currentSection === "食場所") {
                    if (key === "住所") mealSection["食場所"]["レストラン住所"] = value;
                    if (key === "営業時間") mealSection["食場所"]["営業時間"] = value;
                    if (key === "レストランの特徴") mealSection["食場所"]["レストランの特徴"] = value;
                    if (key === "その他情報") mealSection["食場所"]["その他情報"] = value;
                } else if (currentSection === "観光名所") {
                    if (key === "住所") mealSection["観光名所"]["名所住所"] = value;
                    if (key === "営業時間") mealSection["観光名所"]["営業時間"] = value;
                    if (key === "名所の特徴") mealSection["観光名所"]["名所の特徴"] = value;
                    if (key === "その他情報") mealSection["観光名所"]["その他情報"] = value;
                }  else if (currentSection === "カフェ") {
                    if (key === "住所") mealSection["カフェ"]["カフェ住所"] = value;
                    if (key === "営業時間") mealSection["カフェ"]["営業時間"] = value;
                    if (key === "カフェ情報") mealSection["カフェ"]["カフェ情報"] = value;
                    if (key === "カフェの特徴") mealSection["カフェ"]["カフェの特徴"] = value;
                }  else if (currentSection === "宿泊施設") {
                    if (key === "宿泊施設の特徴") mealSection["宿泊施設"]["宿泊施設の特徴"] = value;
                    if (key === "宿泊施設の位置") mealSection["宿泊施設"]["宿泊施設の位置"] = value;
                    if (key === "宿泊施設情報") mealSection["宿泊施設"]["宿泊施設情報"] = value;
                }  else if (currentSection === "ショッピングモール") {
                    if (key === "ショッピングモール住所") mealSection["ショッピングモール"]["ショッピングモール住所"] = value;
                    if (key === "ショッピングモール情報") mealSection["ショッピングモール"]["ショッピングモール情報"] = value;
                }
            } 
        } 
    });
    
    return result;
}

function parseItineraryToJson_CN(text) {
    text = text.replace(/([^\n])(\s*- \*\*第\d+天\*\*:)/g, "$1\n$2");
    const lines = text.split("\n");
    const result = [];
    let currentDay = null;
    let currentMeal = null;
    let currentSection = null;
    
    lines.forEach(line => {
        const trimmedLine = line.trim();
        // console.log("t:", trimmedLine);
        if (!trimmedLine) return; // 빈 줄 무시

        // dayMatch 처리
        const dayMatch = trimmedLine.match(/^\- \*\*第(\d+)天\*\*/);
        if (dayMatch) {
            currentDay = {
                day: parseInt(dayMatch[1]),
                meals: {}
            };
            result.push(currentDay);
        }

        const mealMatch = trimmedLine.match(/^\- \*\*(早晨|中午|晚上)\*\*/);
        if (mealMatch) {
            currentMeal = mealMatch[1];
            if (currentDay && !currentDay.meals[currentMeal]) {
                currentDay.meals[currentMeal] = {
                    "餐地点": {
                        "餐厅名称": null,
                        "餐厅地址": null,
                        "营业时间": null,
                        "餐厅特点": null,
                        "其他信息": null,
                    },
                    "景点": {
                        "景点名称": null,
                        "景点地址": null,
                        "营业时间": null,
                        "景点特点": null,
                        "其他信息": null,
                    },
                    "咖啡馆": {
                        "咖啡馆名称": null,
                        "咖啡馆地址": null,
                        "营业时间": null,
                        "咖啡馆信息": null,
                        "咖啡馆特点": null,
                    },
                    "住宿": {
                        "住宿名称": null,
                        "住宿特点": null,
                        "住宿位置": null,
                        "住宿信息": null,
                    },
                    "购物中心": {
                        "购物中心名称": null,
                        "购物中心地址": null,
                        "购物中心信息": null,
                    },
                };
            }
            currentSection = null;
        } 

        // Key-Value 처리
        const keyValueMatch = trimmedLine.match(/- \*\*(.*?)\*\*: (.*)/);
        if (keyValueMatch && currentDay && currentMeal) {
            const [, key, value] = keyValueMatch;
            const mealSection = currentDay.meals[currentMeal];
            
            if (key.includes("餐地点")) {
                mealSection["餐地点"]["餐厅名称"] = value;
                currentSection = "餐地点";
            } else if (key === "景点") {
                mealSection["景点"]["景点名称"] = value;
                currentSection = "景点";
            } else if (key === "咖啡馆") {
                mealSection["咖啡馆"]["咖啡馆名称"] = value;
                currentSection = "咖啡馆";
            } else if (key === "住宿") {
                mealSection["住宿"]["住宿名称"] = value;
                currentSection = "住宿";
            } else if (key === "购物中心") {
                mealSection["购物中心"]["购物中心名称"] = value;
                currentSection = "购物中心";
            } 

            if (currentSection) {
                if (currentSection === "餐地点") {
                    if (key === "地址") mealSection["餐地点"]["餐厅地址"] = value;
                    if (key === "营业时间") mealSection["餐地点"]["营业时间"] = value;
                    if (key === "餐厅特点") mealSection["餐地点"]["餐厅特点"] = value;
                    if (key === "其他信息") mealSection["餐地点"]["其他信息"] = value;
                } else if (currentSection === "景点") {
                    if (key === "地址") mealSection["景点"]["景点地址"] = value;
                    if (key === "营业时间") mealSection["景点"]["营业时间"] = value;
                    if (key === "景点特点") mealSection["景点"]["景点特点"] = value;
                    if (key === "其他信息") mealSection["景点"]["其他信息"] = value;
                }  else if (currentSection === "咖啡馆") {
                    if (key === "地址") mealSection["咖啡馆"]["咖啡馆地址"] = value;
                    if (key === "营业时间") mealSection["咖啡馆"]["营业时间"] = value;
                    if (key === "咖啡馆信息") mealSection["咖啡馆"]["咖啡馆信息"] = value;
                    if (key === "咖啡馆特点") mealSection["咖啡馆"]["咖啡馆特点"] = value;
                }  else if (currentSection === "住宿") {
                    if (key === "住宿特点") mealSection["住宿"]["住宿特点"] = value;
                    if (key === "住宿位置") mealSection["住宿"]["住宿位置"] = value;
                    if (key === "住宿信息") mealSection["住宿"]["住宿信息"] = value;
                }  else if (currentSection === "购物中心") {
                    if (key === "购物中心地址") mealSection["购物中心"]["购物中心地址"] = value;
                    if (key === "购物中心信息") mealSection["购物中心"]["购物中心信息"] = value;
                }
            } 
        } 
    });
    
    return result;
}

function parseItineraryToJson_US(text) {
    text = text.replace(/([^\n])(\s*- \*\*Day \d+\*\*:)/g, "$1\n$2");
    const lines = text.split("\n");
    const result = [];
    let currentDay = null;
    let currentMeal = null;
    let currentSection = null;

    lines.forEach(line => {
        const trimmedLine = line.trim();
        // console.log("t:", trimmedLine);
        if (!trimmedLine) return; // 빈 줄 무시

        // dayMatch 처리
        const dayMatch = trimmedLine.match(/^\- \*\*Day (\d+)\*\*/);
        if (dayMatch) {
            currentDay = {
                day: parseInt(dayMatch[1]),
                meals: {}
            };
            result.push(currentDay);
        }

        const mealMatch = trimmedLine.match(/^\- \*\*(Morning|Afternoon|Evening)\*\*/);
        if (mealMatch) {
            currentMeal = mealMatch[1];
            if (currentDay && !currentDay.meals[currentMeal]) {
                currentDay.meals[currentMeal] = {
                    "Location": {
                        "Restaurant Name": null,
                        "Restaurant Address": null,
                        "Opening Hours": null,
                        "Restaurant Features": null,
                        "Additional Information": null,
                    },
                    "Attraction": {
                        "Attraction Name": null,
                        "Attraction Address": null,
                        "Opening Hours": null,
                        "Attraction Features": null,
                        "Additional Information": null,
                    },
                    "Cafe": {
                        "Cafe Name": null,
                        "Cafe Address": null,
                        "Opening Hours": null,
                        "Cafe Information": null,
                        "Cafe Features": null,
                    },
                    "Accommodation": {
                        "Accommodation Name": null,
                        "Accommodation Features": null,
                        "Accommodation Location": null,
                        "Accommodation Information": null,
                    },
                    "Shopping Mall": {
                        "Shopping Mall Name": null,
                        "Shopping Mall Address": null,
                        "Shopping Mall Information": null,
                    },
                };
            }
            currentSection = null;
        } 

        // Key-Value 처리
        const keyValueMatch = trimmedLine.match(/- \*\*(.*?)\*\*: (.*)/);
        if (keyValueMatch && currentDay && currentMeal) {
            const [, key, value] = keyValueMatch;
            const mealSection = currentDay.meals[currentMeal];
            
            if (key.includes("Location")) {
                mealSection["Location"]["Restaurant Name"] = value;
                currentSection = "Location";
            } else if (key === "Attraction") {
                mealSection["Attraction"]["Attraction Name"] = value;
                currentSection = "Attraction";
            } else if (key === "Cafe") {
                mealSection["Cafe"]["Cafe Name"] = value;
                currentSection = "Cafe";
            } else if (key === "Accommodation") {
                mealSection["Accommodation"]["Accommodation Name"] = value;
                currentSection = "Accommodation";
            } else if (key === "Shopping Mall") {
                mealSection["Shopping Mall"]["Shopping Mall Name"] = value;
                currentSection = "Shopping Mall";
            } 

            if (currentSection) {
                if (currentSection === "Location") {
                    if (key === "Address") mealSection["Location"]["Restaurant Address"] = value;
                    if (key === "Opening Hours") mealSection["Location"]["Opening Hours"] = value;
                    if (key === "Restaurant Features") mealSection["Location"]["Restaurant Features"] = value;
                    if (key === "Additional Information") mealSection["Location"]["Additional Information"] = value;
                } else if (currentSection === "Attraction") {
                    if (key === "Address") mealSection["Attraction"]["Attraction Address"] = value;
                    if (key === "Opening Hours") mealSection["Attraction"]["Opening Hours"] = value;
                    if (key === "Attraction Features") mealSection["Attraction"]["Attraction Features"] = value;
                    if (key === "Additional Information") mealSection["Attraction"]["Additional Information"] = value;
                }  else if (currentSection === "Cafe") {
                    if (key === "Address") mealSection["Cafe"]["Cafe Address"] = value;
                    if (key === "Opening Hours") mealSection["Cafe"]["Opening Hours"] = value;
                    if (key === "Cafe Information") mealSection["Cafe"]["Cafe Information"] = value;
                    if (key === "Cafe Features") mealSection["Cafe"]["Cafe Features"] = value;
                }  else if (currentSection === "Accommodation") {
                    if (key === "Accommodation Features") mealSection["Accommodation"]["Accommodation Features"] = value;
                    if (key === "Accommodation Location") mealSection["Accommodation"]["Accommodation Location"] = value;
                    if (key === "Accommodation Information") mealSection["Accommodation"]["Accommodation Information"] = value;
                }  else if (currentSection === "Shopping Mall") {
                    if (key === "Shopping Mall Address") mealSection["Shopping Mall"]["Shopping Mall Address"] = value;
                    if (key === "Shopping Mall Information") mealSection["Shopping Mall"]["Shopping Mall Information"] = value;
                }
            } 
        } 
    });
    
    return result;
}

function parsePlaceJson_KR(text) {
    // 결과를 담을 객체
    const result = {
        "장소": "",
        "주소": "",
        "전화 번호": "",
        "영업 시간": [],    // 여러 줄이 있을 수 있으니 배열로 구성
        "정보": "",
        "메뉴": [],         // 여러 메뉴가 있을 수 있으니 배열로 구성
        "장점": "",
        "SNS": "",
        "기타": ""
    };
  
    // 줄 단위로 분할
    const lines = text.split("\n");
  
    // 현재 어떤 섹션을 파싱 중인지 추적
    let currentSection = null;
  
    lines.forEach((rawLine) => {
        const line = rawLine.trim();
        if (!line) {
            return; // 빈 줄이면 무시
        }
    
        // 1) **장소:**
        const placeMatch = line.match(/^\*\*장소:\** (.*)/);
        if (placeMatch) {
            result["장소"] = placeMatch[1].trim();
            currentSection = "장소"; // 혹시 이후 줄들도 장소에 포함시키고 싶다면 사용
            return;
        }
    
        // 2) **주소**:
        const addressMatch = line.match(/^\-\s*\*\*주소\**: (.*)/);
        if (addressMatch) {
            result["주소"] = addressMatch[1].trim();
            currentSection = "주소";
            return;
        }
    
        // 3) **전화 번호**:
        const phoneMatch = line.match(/^\-\s*\*\*전화 번호\**: (.*)/);
        if (phoneMatch) {
            result["전화 번호"] = phoneMatch[1].trim();
            currentSection = "전화 번호";
            return;
        }
    
        // 4) **영업 시간**: (여러 줄에 걸쳐 있을 수 있음)
        const timeMatch = line.match(/^\-\s*\*\*영업 시간\**: (.*)/);
        if (timeMatch) {
            // 첫 줄에도 내용이 있으면 배열에 넣는다
            const firstContent = timeMatch[1].trim();
            if (firstContent) {
            result["영업 시간"].push(firstContent);
            }
            currentSection = "영업 시간";
            return;
        }
    
        // 5) **정보**: 
        const infoMatch = line.match(/^\*\*정보\**: ?(.*)/);
        if (infoMatch) {
            result["정보"] = infoMatch[1].trim(); // 첫 줄
            currentSection = "정보";
            return;
        }
    
        // 6) **메뉴**:
        const menuMatch = line.match(/^\*\*메뉴\**: ?(.*)/);
        if (menuMatch) {
            // 메뉴에 바로 내용이 있을 수도 있지만 보통은 없고, 
            // 어쨌든 currentSection="메뉴"로 설정
            currentSection = "메뉴";
            return;
        }
    
        // 7) **장점**:
        const advantageMatch = line.match(/^\*\*장점\**: ?(.*)/);
        if (advantageMatch) {
            result["장점"] = advantageMatch[1].trim();
            currentSection = "장점";
            return;
        }

        // 8) **SNS**:
        const snsMatch = line.match(/^\*\*SNS\**: ?(.*)/);
        if (snsMatch) {
            result["SNS"] = snsMatch[1].trim();
            currentSection = "SNS";
            return;
        }
    
        // 9) **기타**:
        const etcMatch = line.match(/^\*\*기타\**: ?(.*)/);
        if (etcMatch) {
            result["기타"] = etcMatch[1].trim();
            currentSection = "기타";
            return;
        }
    
        // === 여기까지 특정 라인에서 섹션을 찾는 로직 ===
        // === 여기서부터는 현재 섹션에 따라 내용 처리 ===
    
        // 현재 섹션이 "영업 시간"인 경우, 줄을 계속 배열에 추가
        if (currentSection === "영업 시간") {
            // 예: "- 월~금: 13:00 - 24:00" 같은 걸 파싱
            // 맨 앞에 '- ' 이 있을 수 있으니 제거
            const lineContent = line.replace(/^-+/, "").trim();
            result["영업 시간"].push(lineContent);
            
            return;
        }
    
        // 현재 섹션이 "정보"인 경우, 여러 줄이 있을 수 있으므로 이어붙이기
        if (currentSection === "정보") {
            // 이미 한 줄 들어갔다면 줄바꿈 붙여서 누적
            if (result["정보"]) {
                result["정보"] += "\n" + line;
            } else {
                result["정보"] = line;
            }
            return;
        }
    
        // 현재 섹션이 "메뉴"라면, 예: "- 활고등어회 소: 45,000원"
        if (currentSection === "메뉴") {
            // '-'로 시작하는 패턴 추출
            // 예: "- 활고등어회 소: 45,000원"
            // => name: "활고등어회 소", price: "45,000원"
            const menuItemMatch = line.match(/^\-\s*(.*?):\s*(.*)/);
            if (menuItemMatch) {
                const itemName = menuItemMatch[1].trim();
                const itemPrice = menuItemMatch[2].trim();
                result["메뉴"].push({
                    "메뉴명": itemName,
                    "가격": itemPrice
                });
            } else {
            // 만약 "- "없이 "점심 메뉴"만 이어지는 경우 처리 or 무시
            // 여기서는 단순히 라인을 무시하거나, 
            // 필요한 경우 이어붙일 수도 있음
            }
            return;
        }
    
        // "장점" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "장점") {
            // 이미 한 줄 있으면 줄바꿈 하여 이어 붙이기
            if (result["장점"]) {
                result["장점"] += "\n" + line;
            } else {
                result["장점"] = line;
            }
            return;
        }
    
        // "기타" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "기타") {
            if (result["기타"]) {
                result["기타"] += "\n" + line;
            } else {
                result["기타"] = line;
            }
            return;
        }
    });
  
    return result;
}

function parsePlaceJson_JP(text) {
    // 결과를 담을 객체
    const result = {
        "場所": "",
        "住所": "",
        "電話番号": "",
        "営業時間": [],    // 여러 줄이 있을 수 있으니 배열로 구성
        "詳細": "",
        "おすすめメニュー": [],         // 여러 메뉴가 있을 수 있으니 배열로 구성
        "利点": "",
        "SNS": "",
        "その他情報": ""
    };
  
    // 줄 단위로 분할
    const lines = text.split("\n");
  
    // 현재 어떤 섹션을 파싱 중인지 추적
    let currentSection = null;
  
    lines.forEach((rawLine) => {
        const line = rawLine.trim();
        if (!line) {
            return; // 빈 줄이면 무시
        }
    
        // 1) **장소:**
        const placeMatch = line.match(/^\*\*場所:\** (.*)/);
        if (placeMatch) {
            result["場所"] = placeMatch[1].trim();
            currentSection = "場所"; // 혹시 이후 줄들도 장소에 포함시키고 싶다면 사용
            return;
        }
    
        // 2) **주소**:
        const addressMatch = line.match(/^\-\s*\*\*住所\**: (.*)/);
        if (addressMatch) {
            result["住所"] = addressMatch[1].trim();
            currentSection = "住所";
            return;
        }
    
        // 3) **전화 번호**:
        const phoneMatch = line.match(/^\-\s*\*\*電話番号\**: (.*)/);
        if (phoneMatch) {
            result["電話番号"] = phoneMatch[1].trim();
            currentSection = "電話番号";
            return;
        }
    
        // 4) **영업 시간**: (여러 줄에 걸쳐 있을 수 있음)
        const timeMatch = line.match(/^\-\s*\*\*営業時間\**: (.*)/);
        if (timeMatch) {
            // 첫 줄에도 내용이 있으면 배열에 넣는다
            const firstContent = timeMatch[1].trim();
            if (firstContent) {
            result["営業時間"].push(firstContent);
            }
            currentSection = "営業時間";
            return;
        }
    
        // 5) **정보**: 
        const infoMatch = line.match(/^\*\*詳細\**: ?(.*)/);
        if (infoMatch) {
            result["詳細"] = infoMatch[1].trim(); // 첫 줄
            currentSection = "詳細";
            return;
        }
    
        // 6) **메뉴**:
        const menuMatch = line.match(/^\*\*おすすめメニュー\**: ?(.*)/);
        if (menuMatch) {
            // 메뉴에 바로 내용이 있을 수도 있지만 보통은 없고, 
            // 어쨌든 currentSection="메뉴"로 설정
            currentSection = "おすすめメニュー";
            return;
        }
    
        // 7) **장점**:
        const advantageMatch = line.match(/^\*\*利点\**: ?(.*)/);
        if (advantageMatch) {
            result["利点"] = advantageMatch[1].trim();
            currentSection = "利点";
            return;
        }

        // 8) **SNS**:
        const snsMatch = line.match(/^\*\*SNS\**: ?(.*)/);
        if (snsMatch) {
            result["SNS"] = snsMatch[1].trim();
            currentSection = "SNS";
            return;
        }
    
        // 9) **기타**:
        const etcMatch = line.match(/^\*\*その他情報\**: ?(.*)/);
        if (etcMatch) {
            result["その他情報"] = etcMatch[1].trim();
            currentSection = "その他情報";
            return;
        }
    
        // === 여기까지 특정 라인에서 섹션을 찾는 로직 ===
        // === 여기서부터는 현재 섹션에 따라 내용 처리 ===
    
        // 현재 섹션이 "영업 시간"인 경우, 줄을 계속 배열에 추가
        if (currentSection === "営業時間") {
            // 예: "- 월~금: 13:00 - 24:00" 같은 걸 파싱
            // 맨 앞에 '- ' 이 있을 수 있으니 제거
            const lineContent = line.replace(/^-+/, "").trim();
            result["営業時間"].push(lineContent);
            
            return;
        }
    
        // 현재 섹션이 "정보"인 경우, 여러 줄이 있을 수 있으므로 이어붙이기
        if (currentSection === "詳細") {
            // 이미 한 줄 들어갔다면 줄바꿈 붙여서 누적
            if (result["詳細"]) {
                result["詳細"] += "\n" + line;
            } else {
                result["詳細"] = line;
            }
            return;
        }
    
        // 현재 섹션이 "메뉴"라면, 예: "- 활고등어회 소: 45,000원"
        if (currentSection === "おすすめメニュー") {
            // '-'로 시작하는 패턴 추출
            // 예: "- 활고등어회 소: 45,000원"
            // => name: "활고등어회 소", price: "45,000원"
            const menuItemMatch = line.match(/^\-\s*(.*?):\s*(.*)/);
            if (menuItemMatch) {
                const itemName = menuItemMatch[1].trim();
                const itemPrice = menuItemMatch[2].trim();
                result["おすすめメニュー"].push({
                    "メニュー名": itemName,
                    "値段": itemPrice
                });
            } else {
            // 만약 "- "없이 "점심 메뉴"만 이어지는 경우 처리 or 무시
            // 여기서는 단순히 라인을 무시하거나, 
            // 필요한 경우 이어붙일 수도 있음
            }
            return;
        }
    
        // "장점" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "利点") {
            // 이미 한 줄 있으면 줄바꿈 하여 이어 붙이기
            if (result["利点"]) {
                result["利点"] += "\n" + line;
            } else {
                result["利点"] = line;
            }
            return;
        }
    
        // "기타" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "その他情報") {
            if (result["その他情報"]) {
                result["その他情報"] += "\n" + line;
            } else {
                result["その他情報"] = line;
            }
            return;
        }
    });
  
    return result;
}

function parsePlaceJson_CN(text) {
    // 결과를 담을 객체
    const result = {
        "地点": "",
        "地址": "",
        "电话号码": "",
        "营业时间": [],    // 여러 줄이 있을 수 있으니 배열로 구성
        "详情": "",
        "推荐菜单": [],         // 여러 메뉴가 있을 수 있으니 배열로 구성
        "优点": "",
        "社交媒体": "",
        "其他信息": ""
    };
  
    // 줄 단위로 분할
    const lines = text.split("\n");
  
    // 현재 어떤 섹션을 파싱 중인지 추적
    let currentSection = null;
  
    lines.forEach((rawLine) => {
        const line = rawLine.trim();
        if (!line) {
            return; // 빈 줄이면 무시
        }
    
        // 1) **장소:**
        const placeMatch = line.match(/^\*\*地点\**: (.*)/);
        if (placeMatch) {
            result["地点"] = placeMatch[1].trim();
            currentSection = "地点"; // 혹시 이후 줄들도 장소에 포함시키고 싶다면 사용
            return;
        }
    
        // 2) **주소**:
        const addressMatch = line.match(/^\-\s*\*\*地址\**: (.*)/);
        if (addressMatch) {
            result["地址"] = addressMatch[1].trim();
            currentSection = "地址";
            return;
        }
    
        // 3) **전화 번호**:
        const phoneMatch = line.match(/^\-\s*\*\*电话号码\**: (.*)/);
        if (phoneMatch) {
            result["电话号码"] = phoneMatch[1].trim();
            currentSection = "电话号码";
            return;
        }
    
        // 4) **영업 시간**: (여러 줄에 걸쳐 있을 수 있음)
        const timeMatch = line.match(/^\-\s*\*\*营业时间\**: (.*)/);
        if (timeMatch) {
            // 첫 줄에도 내용이 있으면 배열에 넣는다
            const firstContent = timeMatch[1].trim();
            if (firstContent) {
            result["营业时间"].push(firstContent);
            }
            currentSection = "营业时间";
            return;
        }
    
        // 5) **정보**: 
        const infoMatch = line.match(/^\*\*详情\**: ?(.*)/);
        if (infoMatch) {
            result["详情"] = infoMatch[1].trim(); // 첫 줄
            currentSection = "详情";
            return;
        }
    
        // 6) **메뉴**:
        const menuMatch = line.match(/^\*\*推荐菜单\**: ?(.*)/);
        if (menuMatch) {
            // 메뉴에 바로 내용이 있을 수도 있지만 보통은 없고, 
            // 어쨌든 currentSection="메뉴"로 설정
            currentSection = "推荐菜单";
            return;
        }
    
        // 7) **장점**:
        const advantageMatch = line.match(/^\*\*优点\**: ?(.*)/);
        if (advantageMatch) {
            result["优点"] = advantageMatch[1].trim();
            currentSection = "优点";
            return;
        }

        // 8) **SNS**:
        const snsMatch = line.match(/^\*\*社交媒体\**: ?(.*)/);
        if (snsMatch) {
            result["社交媒体"] = snsMatch[1].trim();
            currentSection = "社交媒体";
            return;
        }
    
        // 9) **기타**:
        const etcMatch = line.match(/^\*\*其他信息\**: ?(.*)/);
        if (etcMatch) {
            result["其他信息"] = etcMatch[1].trim();
            currentSection = "其他信息";
            return;
        }
    
        // === 여기까지 특정 라인에서 섹션을 찾는 로직 ===
        // === 여기서부터는 현재 섹션에 따라 내용 처리 ===
    
        // 현재 섹션이 "영업 시간"인 경우, 줄을 계속 배열에 추가
        if (currentSection === "营业时间") {
            // 예: "- 월~금: 13:00 - 24:00" 같은 걸 파싱
            // 맨 앞에 '- ' 이 있을 수 있으니 제거
            const lineContent = line.replace(/^-+/, "").trim();
            result["营业时间"].push(lineContent);
            
            return;
        }
    
        // 현재 섹션이 "정보"인 경우, 여러 줄이 있을 수 있으므로 이어붙이기
        if (currentSection === "详情") {
            // 이미 한 줄 들어갔다면 줄바꿈 붙여서 누적
            if (result["详情"]) {
                result["详情"] += "\n" + line;
            } else {
                result["详情"] = line;
            }
            return;
        }
    
        // 현재 섹션이 "메뉴"라면, 예: "- 활고등어회 소: 45,000원"
        if (currentSection === "推荐菜单") {
            // '-'로 시작하는 패턴 추출
            // 예: "- 활고등어회 소: 45,000원"
            // => name: "활고등어회 소", price: "45,000원"
            const menuItemMatch = line.match(/^\-\s*(.*?):\s*(.*)/);
            if (menuItemMatch) {
                const itemName = menuItemMatch[1].trim();
                const itemPrice = menuItemMatch[2].trim();
                result["推荐菜单"].push({
                    "菜单名": itemName,
                    "价格": itemPrice
                });
            } else {
            // 만약 "- "없이 "점심 메뉴"만 이어지는 경우 처리 or 무시
            // 여기서는 단순히 라인을 무시하거나, 
            // 필요한 경우 이어붙일 수도 있음
            }
            return;
        }
    
        // "장점" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "优点") {
            // 이미 한 줄 있으면 줄바꿈 하여 이어 붙이기
            if (result["优点"]) {
                result["优点"] += "\n" + line;
            } else {
                result["优点"] = line;
            }
            return;
        }
    
        // "기타" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "其他信息") {
            if (result["其他信息"]) {
                result["其他信息"] += "\n" + line;
            } else {
                result["其他信息"] = line;
            }
            return;
        }
    });
  
    return result;
}

function parsePlaceJson_US(text) {
    // 결과를 담을 객체
    const result = {
        "Place": "",
        "Address": "",
        "Phone Number": "",
        "Opening Hours": [],    // 여러 줄이 있을 수 있으니 배열로 구성
        "Details": "",
        "Recommended Menu": [],         // 여러 메뉴가 있을 수 있으니 배열로 구성
        "Advantages": "",
        "SNS": "",
        "Additional Information": ""
    };
  
    // 줄 단위로 분할
    const lines = text.split("\n");
  
    // 현재 어떤 섹션을 파싱 중인지 추적
    let currentSection = null;
  
    lines.forEach((rawLine) => {
        const line = rawLine.trim();
        if (!line) {
            return; // 빈 줄이면 무시
        }
    
        // 1) **장소:**
        const placeMatch = line.match(/^\*\*Place:\** (.*)/);
        if (placeMatch) {
            result["Place"] = placeMatch[1].trim();
            currentSection = "Place"; // 혹시 이후 줄들도 장소에 포함시키고 싶다면 사용
            return;
        }
    
        // 2) **주소**:
        const addressMatch = line.match(/^\-\s*\*\*Address\**: (.*)/);
        if (addressMatch) {
            result["Address"] = addressMatch[1].trim();
            currentSection = "Address";
            return;
        }
    
        // 3) **전화 번호**:
        const phoneMatch = line.match(/^\-\s*\*\*Phone Number\**: (.*)/);
        if (phoneMatch) {
            result["Phone Number"] = phoneMatch[1].trim();
            currentSection = "Phone Number";
            return;
        }
    
        // 4) **영업 시간**: (여러 줄에 걸쳐 있을 수 있음)
        const timeMatch = line.match(/^\-\s*\*\*Opening Hours\**: (.*)/);
        if (timeMatch) {
            // 첫 줄에도 내용이 있으면 배열에 넣는다
            const firstContent = timeMatch[1].trim();
            if (firstContent) {
            result["Opening Hours"].push(firstContent);
            }
            currentSection = "Opening Hours";
            return;
        }
    
        // 5) **정보**: 
        const infoMatch = line.match(/^\*\*Details\**: ?(.*)/);
        if (infoMatch) {
            result["Details"] = infoMatch[1].trim(); // 첫 줄
            currentSection = "Details";
            return;
        }
    
        // 6) **메뉴**:
        const menuMatch = line.match(/^\*\*Recommended Menu\**: ?(.*)/);
        if (menuMatch) {
            // 메뉴에 바로 내용이 있을 수도 있지만 보통은 없고, 
            // 어쨌든 currentSection="메뉴"로 설정
            currentSection = "Recommended Menu";
            return;
        }
    
        // 7) **장점**:
        const advantageMatch = line.match(/^\*\*Advantages\**: ?(.*)/);
        if (advantageMatch) {
            result["Advantages"] = advantageMatch[1].trim();
            currentSection = "Advantages";
            return;
        }

        // 8) **SNS**:
        const snsMatch = line.match(/^\*\*SNS\**: ?(.*)/);
        if (snsMatch) {
            result["SNS"] = snsMatch[1].trim();
            currentSection = "SNS";
            return;
        }
    
        // 9) **기타**:
        const etcMatch = line.match(/^\*\*Additional Information\**: ?(.*)/);
        if (etcMatch) {
            result["Additional Information"] = etcMatch[1].trim();
            currentSection = "Additional Information";
            return;
        }
    
        // === 여기까지 특정 라인에서 섹션을 찾는 로직 ===
        // === 여기서부터는 현재 섹션에 따라 내용 처리 ===
    
        // 현재 섹션이 "영업 시간"인 경우, 줄을 계속 배열에 추가
        if (currentSection === "Opening Hours") {
            // 예: "- 월~금: 13:00 - 24:00" 같은 걸 파싱
            // 맨 앞에 '- ' 이 있을 수 있으니 제거
            const lineContent = line.replace(/^-+/, "").trim();
            result["Opening Hours"].push(lineContent);
            
            return;
        }
    
        // 현재 섹션이 "정보"인 경우, 여러 줄이 있을 수 있으므로 이어붙이기
        if (currentSection === "Details") {
            // 이미 한 줄 들어갔다면 줄바꿈 붙여서 누적
            if (result["Details"]) {
                result["Details"] += "\n" + line;
            } else {
                result["Details"] = line;
            }
            return;
        }
    
        // 현재 섹션이 "메뉴"라면, 예: "- 활고등어회 소: 45,000원"
        if (currentSection === "Recommended Menu") {
            // '-'로 시작하는 패턴 추출
            // 예: "- 활고등어회 소: 45,000원"
            // => name: "활고등어회 소", price: "45,000원"
            const menuItemMatch = line.match(/^\-\s*(.*?):\s*(.*)/);
            if (menuItemMatch) {
                const itemName = menuItemMatch[1].trim();
                const itemPrice = menuItemMatch[2].trim();
                result["Recommended Menu"].push({
                    "Menu Name": itemName,
                    "Price": itemPrice
                });
            } else {
            // 만약 "- "없이 "점심 메뉴"만 이어지는 경우 처리 or 무시
            // 여기서는 단순히 라인을 무시하거나, 
            // 필요한 경우 이어붙일 수도 있음
            }
            return;
        }
    
        // "장점" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "Advantages") {
            // 이미 한 줄 있으면 줄바꿈 하여 이어 붙이기
            if (result["Advantages"]) {
                result["Advantages"] += "\n" + line;
            } else {
                result["Advantages"] = line;
            }
            return;
        }
    
        // "기타" 섹션인 경우도 여러 줄 붙일 수 있음
        if (currentSection === "Additional Information") {
            if (result["Additional Information"]) {
                result["Additional Information"] += "\n" + line;
            } else {
                result["Additional Information"] = line;
            }
            return;
        }
    });
  
    return result;
}

function attachDeleteEvent(folderItem, parentList, plusButton) {
    const deleteIcon = folderItem.querySelector('.delete-icon');
    if (!deleteIcon) return;

    deleteIcon.addEventListener('click', function() {
        // (A) bookmark_id 가져오기
        const bookmarkId = deleteIcon.getAttribute('data-id');
        if (!bookmarkId) {
            console.warn("No data-id found for this item, cannot delete in DB.");
            return;
        }

        // (B) 서버에 DELETE 요청(AJAX)
        fetch("/app/partials/favorites/delete/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()  // CSRF 토큰
            },
            body: JSON.stringify({
                bookmark_id: bookmarkId
            })
        })
        .then(response => {
            if (!response.ok) {
                // 예: 404, 500 등이면 throw
                throw new Error(`HTTP error: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // (C) 성공하면 UI에서 제거
                folderItem.remove();
                // parentList.removeChild(folderItem);
                updateFolderListUI(parentList, plusButton);
                console.log("북마크 삭제 성공:", bookmarkId);
            }
        })
        .catch(err => {
            console.error("서버 통신 오류:", err);
            switch (countryId) {
                case "KR": alert('서버 오류가 발생했습니다.'); break;
                case "JP": alert('サーバーエラーが発生しました。'); break;
                case "CN": alert('服务器出错 。'); break;
                case "US": alert('A server error has occurred.'); break;
            }
        });
    });
}

function updateFolderListUI(folderList, plusButton) {
    if (!folderList) return;

    const items = folderList.querySelectorAll('.folder-item');
    const count = items.length;

    // 버튼 비활성화: 10개 이상이면 disabled
    if (plusButton) {
        if (count >= 11) {
            plusButton.style.pointerEvents = 'none';
            plusButton.style.opacity = '0.4';
            // 또는 plusButton.setAttribute('disabled', true);
        } else {
            plusButton.style.pointerEvents = 'auto';
            plusButton.style.opacity = '1';
            // plusButton.removeAttribute('disabled');
        }
    }
}

function addFolderEventHandler(plusElementId, sectionSelector, placeholderText, isPlaceValue, imagePaths) {
    const plusElement = document.getElementById(plusElementId);
    if (plusElement) {
        plusElement.addEventListener('click', function () {
            // 이미 입력창이 열려있으면 무시
            if (isPlaceValue ? isPlaceInputOpen : isScheduleInputOpen) return;
            if (isPlaceValue) isPlaceInputOpen = true;
            else isScheduleInputOpen = true;

            const folderList = document.querySelector(`${sectionSelector} .folder-list`);
            if (!folderList) return;

            // 새 입력창 아이템
            const inputItem = document.createElement("div");
            inputItem.className = "folder-item";

            const inputElem = document.createElement("input");
            inputElem.type = "text";
            inputElem.placeholder = placeholderText;
            inputElem.style.width = "200px";

            inputItem.appendChild(inputElem);

            folderList.insertBefore(inputItem, plusElement);

            updateFolderListUI(folderList, plusElement);

            inputElem.focus();

            // Enter로 확정
            inputElem.addEventListener("keydown", function (e) {
                if (e.key === "Enter") {
                    e.preventDefault();
                    const textValue = inputElem.value.trim();
                    const isLightTheme = document.body.getAttribute("data-theme") === "light";

                    if (isPlaceValue) isPlaceInputOpen = false;
                    else isScheduleInputOpen = false;

                    // 입력이 없으면 취소
                    if (textValue === "") {
                        folderList.removeChild(inputItem);
                        updateFolderListUI(folderList, plusElement);
                        return;
                    }

                    // 서버로 AJAX 호출
                    fetch("/app/partials/favorites/add/", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "X-CSRFToken": getCSRFToken()
                        },
                        body: JSON.stringify({
                            title: textValue,
                            is_place: isPlaceValue,
                        })
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then((data) => {
                        if (data.success) {
                            // 생성 성공 시, 새 아이템 생성
                            const newItem = document.createElement("div");
                            newItem.className = "folder-item";
                            newItem.id = data.folderId; // 서버에서 반환된 folderId를 id로 설정
                            newItem.innerHTML = `
                                <img src="${isLightTheme ? imagePaths.light : imagePaths.dark}"
                                    alt="icon" width="50px" height="50px">
                                &nbsp;&nbsp;&nbsp;&nbsp;${textValue}
                                <img src="${isLightTheme ? "/static/images/delete_light.png" : "/static/images/delete_dark.png"}"
                                    alt="delete" width="50px" height="50px" class="delete-icon" data-id="${data.folderId}">
                            `;
                            folderList.replaceChild(newItem, inputItem);

                            newItem.addEventListener('click', (event) => {
                                if (event.target.classList.contains("delete-icon")) {
                                    return; // 삭제 버튼 클릭 시 folder-item의 이벤트 실행 차단
                                }
                                
                                // 새 폴더 버튼은 해당 안하니까 패스
                                const backBtn = document.getElementById('backBtn');
                                const backbookmarkTitleBtn = document.getElementById('bookmark_title');
                                const placeBtn = document.getElementById('placeBtn');
                                const scheduleBtn = document.getElementById('scheduleBtn');
                                const topmenu = document.querySelector('.top-menu');
                                const AllFolderLists = favoritesPanel.querySelectorAll('.folder-list');
                                const bookmarkPlaceItemDiv = document.querySelector(".bookmark-place-item");
                                const bookmarkScheduleItemDiv = document.querySelector(".bookmark-schedule-item");
                                
                                if (AllFolderLists) {
                                    AllFolderLists.forEach(folderList => {
                                        folderList.style.display = "none";
                                    });
                                }
                                
                                topmenu.style.justifyContent = "start";
                                backBtn.style.display = "block";
                                backbookmarkTitleBtn.style.display = "block";
                                backbookmarkTitleBtn.textContent = newItem.textContent.trim().replace(/\s{2,}/g, '').replace(/\u00a0+/g, '');
                                placeBtn.style.display = "none";
                                scheduleBtn.style.display = "none";

                                // bookmark-place-item과 bookmark-schedule-item 초기화
                                if (bookmarkPlaceItemDiv) {                            
                                    bookmarkPlaceItemDiv.style.display = "none";
                                    bookmarkPlaceItemDiv.innerHTML = ""; // 기존 자식 요소 제거
                                }
                                if (bookmarkScheduleItemDiv) {
                                    bookmarkScheduleItemDiv.style.display = "none";
                                    bookmarkScheduleItemDiv.innerHTML = ""; // 기존 자식 요소 제거
                                }
                            })
                            attachDeleteEvent(newItem); // 삭제 이벤트 연결
                            updateFolderListUI(folderList, plusElement);

                            console.log("생성 성공:", data.folderId);
                        } else {
                            switch (countryId) {
                                case "KR": alert('북마크 생성 실패'); break;
                                case "JP": alert('ブックマーク作成失敗'); break;
                                case "CN": alert('书签创建失败'); break;
                                case "US": alert('Bookmark creation failed'); break;
                            }
                            folderList.removeChild(inputItem);
                        }
                    })
                    .catch((err) => {
                        console.error("서버 통신 오류:", err);
                        folderList.removeChild(inputItem);
                    });
                }
            });
        });
    }
}

// 네이버 Geocoding API를 통해 경도와 위도를 가져오는 함수
async function getCoordinates(addresses) {
    if (!Array.isArray(addresses)) {
        console.error("Addresses must be an array.");
        return [];
    }
    const markerData = [];
    const promises = addresses.map(async ({ address, title }) => {
        if (!address) return; // address가 없는 경우 건너뜀

        const coordinates = await fetchCoordinates(address);
        if (coordinates) {
            const [lat, lng] = coordinates;
            markerData.push({
                position: new naver.maps.LatLng(lat, lng),
                title: title,
                icon: `https://chart.googleapis.com/chart?chst=d_map_pin_number&chld=${markerData.length + 1}|FF0000|000000`,
            });
        }
    });

    await Promise.all(promises); // 모든 비동기 작업이 완료될 때까지 대기
    return markerData;
}

async function generatePlaceContent(jsonData) {
    if (!jsonData["장소"] && !jsonData["場所"] && !jsonData["地点"] && !jsonData["Place"] &&
        !jsonData["주소"] && !jsonData["住所"] && !jsonData["地址"] && !jsonData["Address"] &&
        !jsonData["정보"] && !jsonData["詳細"] && !jsonData["详情"] && !jsonData["Details"]) {
        return;
    }
    removeContent();
    const mapPanelContent = document.querySelector('.map-panel-content');
    //터미널에 추가된 내용이 스케줄이라는 것을 체크하기 위함
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    const panelTitle = document.getElementById("panel-title");
    let placeName = "";
    let placeAddress = "";
    let placeDetails = "";

    getBookmarkListBtn.classList.remove("schedule");
    getBookmarkListBtn.classList.add("place");
    if (!mapPanelContent) {
        console.error('map-panel-content 요소를 찾을 수 없습니다.');
        return;
    }
    if (panelTitle) {
        if (jsonData["장소"]) {
            panelTitle.textContent = jsonData["장소"];
        } else if (jsonData["場所"]) {
            panelTitle.textContent = jsonData["場所"];
        } else if (jsonData["地点"]) {
            panelTitle.textContent = jsonData["地点"];
        } else if (jsonData["Place"]) {
            panelTitle.textContent = jsonData["Place"];
        }
    }

    function createPlaceSection(jsonData) {
        // <div class="place-section">
        const section = document.createElement("div");
        section.className = "place-section";

        // <h3>장소 정보</h3>
        const heading = document.createElement("h3");
        console.log("countryId:", countryId);
        if (countryId == "KR" ) {
            heading.textContent = "장소 정보";
        } else if (countryId == "JP") {
            heading.textContent = "場所情報";
        } else if (countryId == "CN") {
            heading.textContent = "地点信息";    
        } else if (countryId == "US") {
            heading.textContent = "Place Info";
        }
        section.appendChild(heading);

        // <p><strong>이름:</strong> 용산전자상가</p>
        const nameParagraph = document.createElement("p");
        const nameStrong = document.createElement("strong");
        
        nameParagraph.appendChild(nameStrong);
        if (countryId == "KR") {
            nameStrong.textContent = "이름: "; 
        } else if (countryId == "JP") {
            nameStrong.textContent = "名: ";
        } else if (countryId == "CN") {
            nameStrong.textContent = "名字: ";
        } else if (countryId == "US") {
            nameStrong.textContent = "Name: ";
        }

        if (jsonData["장소"]) {
            nameParagraph.innerHTML += jsonData["장소"];
            placeName = jsonData["장소"];
        } else if (jsonData["場所"]) {
            nameParagraph.innerHTML += jsonData["場所"];
            placeName = jsonData["場所"];
        } else if (jsonData["地点"]) {
            nameParagraph.innerHTML += jsonData["地点"];
            placeName = jsonData["地点"];
        } else if (jsonData["Place"]) {
            nameParagraph.innerHTML += jsonData["Place"];
            placeName = jsonData["Place"];
        }
        section.appendChild(nameParagraph);

        // <p><strong>주소:</strong> 서울특별시 용산구 청파로 74</p>
        const addressParagraph = document.createElement("p");
        const addressStrong = document.createElement("strong");

        addressParagraph.appendChild(addressStrong);
        if (countryId == "KR") {
            addressStrong.textContent = "주소: ";
        } else if (countryId == "JP") {
            addressStrong.textContent = "住所: "; 
        } else if (countryId == "CN") {
            addressStrong.textContent = "地址: ";
        } else if (countryId == "US") {
            addressStrong.textContent = "Address: ";            
        }        

        if (jsonData["주소"]) {
            addressParagraph.innerHTML += jsonData["주소"];
            placeAddress = jsonData["주소"];
        } else if (jsonData["住所"]) {
            addressParagraph.innerHTML += jsonData["住所"];
            placeAddress = jsonData["住所"];
        } else if (jsonData["地址"]) {
            addressParagraph.innerHTML += jsonData["地址"];
            placeAddress = jsonData["地址"];
        } else if (jsonData["Address"]) {
            addressParagraph.innerHTML += jsonData["Address"];
            placeAddress = jsonData["Address"];
        }        
        section.appendChild(addressParagraph);

        // <p><strong>설명:</strong> 설명이 없습니다.</p>
        const descriptionParagraph = document.createElement("p");
        const descriptionStrong = document.createElement("strong");

        descriptionParagraph.appendChild(descriptionStrong);
        if (countryId == "KR") {
            descriptionStrong.textContent = "정보: ";
        } else if (countryId == "JP") {
            descriptionStrong.textContent = "詳細: ";
        } else if (countryId == "CN") {
            descriptionStrong.textContent = "详情: ";
        } else if (countryId == "US") {
            descriptionStrong.textContent = "Details: ";
        }        

        if (jsonData["정보"]) {
            descriptionParagraph.innerHTML += jsonData["정보"];
            placeDetails = jsonData["정보"];
        } else if (jsonData["詳細"]) {
            descriptionParagraph.innerHTML += jsonData["詳細"];
            placeDetails = jsonData["詳細"];
        } else if (jsonData["详情"]) {
            descriptionParagraph.innerHTML += jsonData["详情"];
            placeDetails = jsonData["详情"];
        } else if (jsonData["Details"]) {
            descriptionParagraph.innerHTML += jsonData["Details"];
            placeDetails = jsonData["Details"];
        }
        section.appendChild(descriptionParagraph);

        return section;
    }

    // 생성된 HTML을 DOM에 추가
    const placeSection = createPlaceSection(jsonData);
    mapPanelContent.appendChild(placeSection);
    let addresses = [];
    addresses.push({
        address: placeAddress,
        title: placeName,
    });
    const globalMarkerData = await getCoordinates(addresses);
    addMarkersToMap(globalMarkerData);
}

async function generateDynamicPlanContent(jsonData) {
    removeContent(false);
    const mapPanelContent = document.querySelector('.map-panel-content');
    //터미널에 추가된 내용이 스케줄이라는 것을 체크하기 위함
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    getBookmarkListBtn.classList.remove("place");
    getBookmarkListBtn.classList.add("schedule");
    if (!mapPanelContent) {
        console.error('map-panel-content 요소를 찾을 수 없습니다.');
        return;
    }

    // 마커 데이터를 저장하는 배열
    let markerData = [];

    const languageMappings = [
        {
            locationKey: "식사 장소",
            addressKey: "음식점 주소",
            nameKey: "음식점 이름",
            attractionKey: "명소",
            attractionAddressKey: "명소 주소",
            attractionNameKey: "명소 이름",
            cafeKey: "카페",
            cafeAddressKey: "카페 주소",
            cafeNameKey: "카페 이름",
            accommodationKey: "숙소",
            accommodationAddressKey: "숙소 위치",
            accommodationNameKey: "숙소 이름",
            shoppingMallKey: "쇼핑몰",
            shoppingMallAddressKey: "쇼핑몰 주소",
            shoppingMallNameKey: "쇼핑몰 이름",
        },
        {
            locationKey: "食場所",
            addressKey: "レストラン住所",
            nameKey: "レストラン名",
            attractionKey: "観光名所",
            attractionAddressKey: "名所住所",
            attractionNameKey: "名所名",
            cafeKey: "カフェ",
            cafeAddressKey: "カフェ住所",
            cafeNameKey: "カフェ名",
            accommodationKey: "宿泊施設",
            accommodationAddressKey: "宿泊施設の位置",
            accommodationNameKey: "宿泊施設名",
            shoppingMallKey: "ショッピングモール",
            shoppingMallAddressKey: "ショッピングモール住所",
            shoppingMallNameKey: "ショッピングモール名",
        },
        {
            locationKey: "餐地点",
            addressKey: "餐厅地址",
            nameKey: "餐厅名称",
            attractionKey: "景点",
            attractionAddressKey: "景点地址",
            attractionNameKey: "景点名称",
            cafeKey: "咖啡馆",
            cafeAddressKey: "咖啡馆地址",
            cafeNameKey: "咖啡馆名称",
            accommodationKey: "住宿",
            accommodationAddressKey: "住宿位置",
            accommodationNameKey: "住宿名称",
            shoppingMallKey: "购物中心",
            shoppingMallAddressKey: "购物中心地址",
            shoppingMallNameKey: "购物中心名称",
        },
        {
            locationKey: "Location",
            addressKey: "Restaurant Address",
            nameKey: "Restaurant Name",
            attractionKey: "Attraction",
            attractionAddressKey: "Attraction Address",
            attractionNameKey: "Attraction Name",
            cafeKey: "Cafe",
            cafeAddressKey: "Cafe Address",
            cafeNameKey: "Cafe Name",
            accommodationKey: "Accommodation",
            accommodationAddressKey: "Accommodation Location",
            accommodationNameKey: "Accommodation Name",
            shoppingMallKey: "Shopping Mall",
            shoppingMallAddressKey: "Shopping Mall Address",
            shoppingMallNameKey: "Shopping Mall Name",
        },
    ];

    function extractParenthesisContent(str) {
        const match = str.match(/\((.*?)\)/); // 정규식을 사용하여 첫 번째 괄호 안의 내용 추출
        return match ? match[1] : str; // 매칭된 값이 있으면 반환, 없으면 null 반환
    }
    
    async function renderDayContent(day) {
        // JSON 데이터에서 주소 정보 추출
        const addresses = [];
        Object.keys(day.meals).forEach(mealType => {
            const mealData = day.meals[mealType];
            languageMappings.forEach((
            { 
                locationKey, addressKey, nameKey, 
                attractionKey, attractionAddressKey, attractionNameKey, 
                cafeKey, cafeAddressKey, cafeNameKey, 
                accommodationKey, accommodationAddressKey, accommodationNameKey, 
                shoppingMallKey, shoppingMallAddressKey, shoppingMallNameKey,
            }) => {
                if (mealData[locationKey] && mealData[locationKey][addressKey]) {
                    mealData[locationKey][addressKey] = extractParenthesisContent(mealData[locationKey][addressKey]);
                }
                if (mealData[attractionKey] && mealData[attractionKey][attractionAddressKey]) {
                    mealData[attractionKey][attractionAddressKey] = extractParenthesisContent(mealData[attractionKey][attractionAddressKey]);
                }
                if (mealData[cafeKey] && mealData[cafeKey][cafeAddressKey]) {
                    mealData[cafeKey][cafeAddressKey] = extractParenthesisContent(mealData[cafeKey][cafeAddressKey]);
                }
                if (mealData[accommodationKey] && mealData[accommodationKey][accommodationAddressKey]) {
                    mealData[accommodationKey][accommodationAddressKey] = extractParenthesisContent(mealData[accommodationKey][accommodationAddressKey]);
                }
                if (mealData[shoppingMallKey] && mealData[shoppingMallKey][shoppingMallAddressKey]) {
                    mealData[shoppingMallKey][shoppingMallAddressKey] = extractParenthesisContent(mealData[shoppingMallKey][shoppingMallAddressKey]);
                }

                if (mealData[locationKey] && mealData[locationKey][addressKey]) {
                    addresses.push({
                        address: mealData[locationKey][addressKey],
                        title: mealData[locationKey][nameKey],
                    });
                }
                if (mealData[attractionKey] && mealData[attractionKey][attractionAddressKey]) {
                    addresses.push({
                        address: mealData[attractionKey][attractionAddressKey],
                        title: mealData[attractionKey][attractionNameKey],
                    });
                }
                if (mealData[cafeKey] && mealData[cafeKey][cafeAddressKey]) {
                    addresses.push({
                        address: mealData[cafeKey][cafeAddressKey],
                        title: mealData[cafeKey][cafeNameKey],
                    });
                }
                if (mealData[accommodationKey] && mealData[accommodationKey][accommodationAddressKey]) {
                    addresses.push({
                        address: mealData[accommodationKey][accommodationAddressKey],
                        title: mealData[accommodationKey][accommodationNameKey],
                    });
                }
                if (mealData[shoppingMallKey] && mealData[shoppingMallKey][shoppingMallAddressKey]) {
                    addresses.push({
                        address: mealData[shoppingMallKey][shoppingMallAddressKey],
                        title: mealData[shoppingMallKey][shoppingMallNameKey],
                    });
                }
            });
        });

        // 지도 내용 초기화
        mapPanelContent.innerHTML = '';
        const planContent = document.createElement('div');
        planContent.className = 'plan-content';
        mapPanelContent.appendChild(planContent);

        Object.keys(day.meals).forEach(mealType => {
            const mealData = day.meals[mealType];
            const mealSection = document.createElement('div');
            mealSection.className = 'meal-section';
            mealSection.innerHTML = `<h4>${mealType}</h4>`;

            Object.keys(mealData).forEach(section => {
                const sectionData = mealData[section];
                if (sectionData) {
                    const name = sectionData["음식점 이름"] || sectionData["명소 이름"] || 
                                sectionData["카페 이름"] || sectionData["숙소 이름"] || sectionData["쇼핑몰 이름"] ||
                                sectionData["レストラン名"] || sectionData["名所名"] || 
                                sectionData["カフェ名"] || sectionData["宿泊施設名"] || sectionData["ショッピングモール名"] ||
                                sectionData["餐厅名称"] || sectionData["景点名称"] || 
                                sectionData["咖啡馆名称"] || sectionData["住宿名称"] || sectionData["购物中心名称"] ||
                                sectionData["Restaurant Name"] || sectionData["Attraction Name"] || 
                                sectionData["Cafe Name"] || sectionData["Accommodation Name"] || sectionData["Shopping Mall Name"]; 
                    const address = sectionData["음식점 주소"] || sectionData["명소 주소"] || 
                                sectionData["카페 주소"] || sectionData["숙소 위치"] || sectionData["쇼핑몰 주소"] ||
                                sectionData["レストラン住所"] || sectionData["名所住所"] || 
                                sectionData["カフェ住所"] || sectionData["宿泊施設の位置"] || sectionData["ショッピングモール住所"] ||
                                sectionData["餐厅地址"] || sectionData["景点地址"] || 
                                sectionData["咖啡馆地址"] || sectionData["住宿位置"] || sectionData["购物中心地址"] ||
                                sectionData["Restaurant Address"] || sectionData["Attraction Address"] || 
                                sectionData["Cafe Address"] || sectionData["Accommodation Location"] || sectionData["Shopping Mall Address"]; 
                    const overview = sectionData["음식점 특징"] || sectionData["명소 특징"] || sectionData["카페 특징"] || sectionData["숙소 특징"] || 
                                sectionData["レストランの特徴"] || sectionData["名所の特徴"] || sectionData["カフェの特徴"] || sectionData["宿泊施設の特徴"] || 
                                sectionData["餐厅特点"] || sectionData["景点特点"] || sectionData["咖啡馆特点"] || sectionData["住宿特点"] || 
                                sectionData["Restaurant Features"] || sectionData["Attraction Features"] || sectionData["Cafe Features"] || sectionData["Accommodation Features"]; 
                    const info = sectionData["카페 정보"] || sectionData["숙소 정보"] || sectionData["쇼핑몰 정보"] ||
                                sectionData["カフェ情報"] || sectionData["宿泊施設情報"] || sectionData["ショッピングモール情報"] ||
                                sectionData["咖啡馆信息"] || sectionData["住宿信息"] || sectionData["购物中心信息"] || 
                                sectionData["Cafe Information"] || sectionData["Accommodation Information"] || sectionData["Shopping Mall Information"]; 
                    const openhour = sectionData["영업 시간"] || sectionData["営業時間"] || 
                                sectionData["营业时间"] || sectionData["Opening Hours"];

                    if (name && address) {
                        const listItem = document.createElement('p');
                        listItem.innerHTML = `<strong>${name}</strong> (${address})`;

                        const buttonContainer = document.createElement('div');
                        buttonContainer.className = "button-container";
                        buttonContainer.setAttribute('overview', overview);
                        buttonContainer.setAttribute('address', address);
                        buttonContainer.style.display = 'inline-flex';
                        buttonContainer.style.alignItems = 'center';
                        buttonContainer.style.flexWrap = "nowrap";

                        // 즐겨찾기 등록 버튼 추가
                        const bookmarkButton = document.createElement('button');
                        bookmarkButton.style.cursor = 'pointer';
                        bookmarkButton.style.marginLeft = '5px';
                        bookmarkButton.style.border = "none";
                        bookmarkButton.textContent = "☆";
                        bookmarkButton.style.justifyContent = "center";
                        bookmarkButton.addEventListener('click', () => {
                            getBookmarkList("true", `${name}`, `${address}`);
                        });

                        // 삭제 버튼 추가
                        const deleteButton = document.createElement('img');
                        deleteButton.id = "deletePlaceBtn";
                        deleteButton.src = document.body.getAttribute('data-theme') === 'light' 
                            ? '/static/images/delete_light.png' 
                            : '/static/images/delete_dark.png';
                        deleteButton.style.cursor = 'pointer';
                        deleteButton.width = 16;
                        deleteButton.height = 16;
                        deleteButton.style.display = "inline-flex"; // Flexbox에 적합
                        deleteButton.style.alignItems = "center";
                        deleteButton.style.justifyContent = "center";

                        // 삭제 버튼 이벤트 추가
                        deleteButton.addEventListener('click', () => {
                            // UI에서 제거
                            mealSection.removeChild(listItem);

                            // JSON 데이터에서 해당 항목 제거
                            if (section === ("식사 장소" || "명소" || "카페" || "숙소" || "쇼핑몰" ||
                                             "食場所" || "観光名所" || "カフェ" || "宿泊施設" || "ショッピングモール" ||
                                             "餐地点" || "景点" || "咖啡馆" || "住宿" || "购物中心" ||
                                             "Location" || "Attraction" || "Cafe" || "Accommodation" || "Shopping Mall")) {
                                delete mealData[section];
                            }

                            // 전역 markerData에서 해당 마커 제거
                            globalMarkerData = globalMarkerData.filter(marker => marker.title !== name);

                            // 지도 업데이트
                            addMarkersToMap(globalMarkerData);

                            // 디버깅용 로그
                            // console.log("Updated globalMarkerData:", globalMarkerData);
                            // console.log("Updated JSON data:", day);
                        });

                        buttonContainer.appendChild(bookmarkButton);
                        buttonContainer.appendChild(deleteButton);
                        listItem.appendChild(buttonContainer);
                        mealSection.appendChild(listItem);
                    }
                }
            });

            planContent.appendChild(mealSection);
        });

        // 주소로 마커 데이터 생성
        try {
            globalMarkerData = await getCoordinates(addresses); // 전역 변수 업데이트
            addMarkersToMap(globalMarkerData); // 지도 업데이트
        } catch (error) {
            console.error("Error generating marker data:", error);
        }
    }

    // 버튼 생성 및 이벤트 바인딩
    generateDayButtons(jsonData, (day) => {
        markerData = []; // 새로운 일차 선택 시 기존 마커 데이터 초기화
        console.log("Day object passed to renderDayContent:", day);
        renderDayContent(day); // 선택된 일차의 데이터 렌더링
    });
}

function generateDayButtons(jsonData, renderDayContentCallback) {
    const mapPanel = document.getElementById('map-panel');
    if (!mapPanel) {
        console.error('map-panel 요소를 찾을 수 없습니다.');
        return;
    }

    let buttonContainer = document.getElementById('day-button-container');
    if (!buttonContainer) {
        buttonContainer = document.createElement('div');
        buttonContainer.id = 'day-button-container';
        buttonContainer.style.position = 'absolute';
        buttonContainer.style.top = `${mapPanel.getBoundingClientRect().top - 50}px`;
        buttonContainer.style.left = '40px';
        buttonContainer.style.display = 'flex';
        buttonContainer.style.gap = '10px';
        buttonContainer.style.zIndex = '100';

        const mapContainer = document.getElementById('map-container');
        if (mapContainer) {
            mapContainer.appendChild(buttonContainer);
        } else {
            console.error('map-container 요소를 찾을 수 없습니다.');
            return;
        }
    } else {
        buttonContainer.innerHTML = ''; // 기존 버튼 초기화
    }

    if (typeof jsonData === "string") {
        jsonData = JSON.parse(jsonData);
    }
    
    let firstButton = null;
    jsonData.forEach((day, index) => {
        const dayButton = document.createElement('button');
        switch (countryId) {
            case "KR":
                dayButton.textContent = `${day.day}일차`; break;
            case "JP":
                dayButton.textContent = `${day.day}日目`; break;
            case "CN":
                dayButton.textContent = `第${day.day}天`; break;
            case "US":
                dayButton.textContent = `Day${day.day}`; break;
        }
        dayButton.style.padding = '8px 16px';
        dayButton.style.border = 'none';
        dayButton.style.borderRadius = '20px';
        dayButton.style.backgroundColor = '#ddd';
        dayButton.style.cursor = 'pointer';

        dayButton.addEventListener('click', () => {
            const allButtons = buttonContainer.querySelectorAll('button');
            allButtons.forEach(btn => {
                btn.style.backgroundColor = '#ddd';
                btn.style.border = 'none';
            });
            dayButton.style.border = '1.5px solid black';
            dayButton.style.backgroundColor = 'white';

            if (typeof renderDayContentCallback === 'function') {
                renderDayContentCallback(day);
            }
        });

        if (index === 0) {
            firstButton = dayButton;
        }

        buttonContainer.appendChild(dayButton);
    });

    if (firstButton) {
        firstButton.click();
    } else {
        console.error('생성된 버튼이 없습니다.');
    }
}

function addMarkersToMap(markerData) {
    if (!map || !isMapInitialized) {
        console.error("Map is not initialized yet!");
        return;
    }
    
    // 기존 마커 제거
    if (window.currentMarkers) {
        window.currentMarkers.forEach(marker => marker.setMap(null));
    }
    window.currentMarkers = []; // 새로운 마커 배열 초기화

    // 기존 선 제거
    if (window.currentPolylines) {
        window.currentPolylines.forEach(polyline => polyline.setMap(null));
    }
    window.currentPolylines = []; // 새로운 선 배열 초기화

    window.markerData = markerData;

    // 새 마커 추가
    let markerIndex = 0; // 마커 인덱스 초기화
    markerData.forEach(data => {
        const markerIconUrl = `/static/images/markers/marker${(markerIndex % 10) + 1}.png`;
        const marker = new naver.maps.Marker({
            position: data.position,
            map: map,
            title: data.title,
            // title: data.names[lang],
            icon: {
                content: `<img src="${markerIconUrl}" style="width:32px; height:36px;">`, // HTML 직접 사용
                // url: markerIconUrl,
                // size: new naver.maps.Size(36, 36), // 마커 크기
                // origin: new naver.maps.Point(0, 0),
                anchor: new naver.maps.Point(18, 36), // 마커 위치 조정
            },
        });

        markerIndex++;

        // 마커 클릭 이벤트
        naver.maps.Event.addListener(marker, 'click', function () {
            switch (countryId) {
                case "KR": alert(`${data.title}입니다!`); break;
                case "JP": alert(`${data.title}です!`); break;
                case "CN": alert(`是${data.title}!`); break;
                case "US": alert(`This place is ${data.title}!`); break;
            }
            // infoWindow.open(map, marker); // 마커 클릭 시 정보창 열기
        });

        // 현재 마커를 전역 배열에 저장
        window.currentMarkers.push(marker);
    });

    // 새 선 추가
    if (markerData.length > 1) {
        for (let i = 0; i < markerData.length - 1; i++) {
            const polyline = new naver.maps.Polyline({
                map: map,
                path: [markerData[i].position, markerData[i + 1].position], // 인접한 마커 연결
                strokeColor: '#000000', // 선 색상
                strokeWeight: 0, // 선 두께
                strokeStyle: 'solid', // 선 스타일 (solid, dashed, dotted 등)
            });

            // 현재 선을 전역 배열에 저장
            window.currentPolylines.push(polyline);
        }
    }
    
    // 지도 범위를 업데이트
    if (markerData.length > 0) {
        const bounds = new naver.maps.LatLngBounds();
        markerData.forEach(marker => bounds.extend(marker.position));
        map.fitBounds(bounds, { top: 50, right: 50, bottom: 50, left: 50 });
    }
}

async function fetchCoordinates(address) {
    // Proxy API 엔드포인트 URL 설정 (Django 백엔드의 엔드포인트 예시)
    const url = `http://127.0.0.1:8000/proxy/geocode/?address=${encodeURIComponent(address)}`;

    try {
        const response = await fetch(url); // Fetch 요청 전송
        if (!response.ok) {
            throw new Error(`Failed to fetch: ${response.status}`);
        }
        const data = await response.json(); // JSON 응답 파싱

        // 좌표 데이터를 반환
        if (data.addresses && data.addresses.length > 0) {
            const { x: lng, y: lat } = data.addresses[0]; // x: 경도, y: 위도
            return [parseFloat(lat), parseFloat(lng)];
        } else {
            console.error(`No valid coordinates found for address: ${address}`, data);
            return null;
        }
    } catch (error) {
        console.error(`Error fetching coordinates for ${address}:`, error);
        return null;
    }
}

async function getBookmarkList(is_place="", name=``, address=``) {
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    const isSchedule = getBookmarkListBtn.classList.contains("schedule"); // 장소인지 확인
    const bookmarkID = getBookmarkListBtn.getAttribute("bookmark_id");
    let isPlace = getBookmarkListBtn.classList.contains("place"); // 장소인지 확인

    if (is_place) {
        isPlace = is_place;
    }

    if (isPlace || isSchedule) {               
        try {
            const response = await fetch(`/app/partials/favorites/get_bookmark/?is_place=${isPlace}`, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {                        
                let innerHtml = "";                        
                const bookmarklistPanel = document.querySelector('.bookmarklist-panel ul');                        
                const title = document.querySelector(".bookmarklist-panel h2");
                const addressTitle = document.querySelector(".bookmarklist-panel h3");
                const changeBookmarkTitle = document.getElementById("change-bookmarktitle")
                const panelTitle = document.querySelector("#panel-title");
                bookmarklistPanel.innerHTML = "";

                title.style.display = "block";
                changeBookmarkTitle.style.display = "none";

                if (isPlace) {          
                    //장소 이름을 그대로 제목으로 짓기
                    if (address) {
                        addressTitle.textContent = address;
                    }
                    else if (document.querySelectorAll(".place-section p")[1]) {
                        addressTitle.textContent = document.querySelectorAll(".place-section p")[1].textContent.split(": ")[1];
                    }
                    // else { // 채팅 내역에서 장소를 즐겨찾기 등록하는 케이스
                    // }
                    if (name) {
                        title.textContent = name;
                    }
                    else if (document.querySelector("#panel-title").textContent.trim()) {
                        title.textContent = document.querySelector("#panel-title").textContent.trim();
                    }
                    // else { // 채팅 내역에서 장소를 즐겨찾기 등록하는 케이스
                    // } 
                    title.addEventListener("dblclick", function () {
                        changeBookmarkTitle.value = title.textContent;
                        changeBookmarkTitle.style.display = "block"; // 입력창 표시
                        title.style.display = "none"; // 기존 텍스트 숨김
                        changeBookmarkTitle.focus();
                    });

                    // 2) Enter: 제목 저장, ESC: 취소
                    changeBookmarkTitle.addEventListener("keydown", async function (e) {
                        if (event.key === "Enter") {
                            const newTitle = changeBookmarkTitle.value.trim();
                            
                            if (!newTitle) {
                                switch (countryId) {
                                    case "KR": alert('제목을 입력해주세요.'); break;
                                    case "JP": alert('タイトルを入力してください。'); break;
                                    case "CN": alert('请输入标题。'); break;
                                    case "US": alert('Please enter the title.'); break;
                                }
                                return;
                            }
                            
                            title.textContent = newTitle;
                            title.style.display = "block"; // 기존 텍스트 표시
                            changeBookmarkTitle.style.display = "none"; // 입력창 숨김
                        } 
                        else if (event.key === "Escape") {
                            title.style.display = "block"; // 기존 텍스트 표시
                            changeBookmarkTitle.style.display = "none";  // 입력창 숨김
                        }                    
                    });
                }
                else if (isSchedule) {
                    //일정 이름은 (일정 + 시간)으로 짓기  (예:일정250120102730)
                    // title.textContent = "";
                    title.addEventListener("dblclick", function () {
                        changeBookmarkTitle.value = title.textContent;
                        changeBookmarkTitle.style.display = "block"; // 입력창 표시
                        title.style.display = "none"; // 기존 텍스트 숨김
                        console.log("title:", changeBookmarkTitle);
                        changeBookmarkTitle.focus();
                    });

                    // 2) Enter: 제목 저장, ESC: 취소
                    changeBookmarkTitle.addEventListener("keydown", async function (e) {
                        if (event.key === "Enter") {
                            const newTitle = changeBookmarkTitle.value.trim();
                            
                            if (!newTitle) {
                                switch (countryId) {
                                    case "KR": alert('제목을 입력해주세요.'); break;
                                    case "JP": alert('タイトルを入力してください。'); break;
                                    case "CN": alert('请输入标题。'); break;
                                    case "US": alert('Please enter the title.'); break;
                                }
                                return;
                            }
                            
                            title.textContent = newTitle;
                            title.style.display = "block"; // 기존 텍스트 표시
                            changeBookmarkTitle.style.display = "none"; // 입력창 숨김
                        } 
                        else if (event.key === "Escape") {
                            title.style.display = "block"; // 기존 텍스트 표시
                            changeBookmarkTitle.style.display = "none";  // 입력창 숨김
                        }                    
                    });

                    if (panelTitle.textContent == "") {
                        // 현재 시각 포맷팅
                        const now = new Date();
                        const year = String(now.getFullYear()).slice(2); // 연도 마지막 두 자리
                        const month = String(now.getMonth() + 1).padStart(2, "0"); // 월 (1~12)
                        const day = String(now.getDate()).padStart(2, "0"); // 일
                        const hours = String(now.getHours()).padStart(2, "0"); // 시간 (0~23)
                        const minutes = String(now.getMinutes()).padStart(2, "0"); // 분
                        const seconds = String(now.getSeconds()).padStart(2, "0"); // 초
                        const milliseconds = now.getTime();
                        // const curDate = `${year}.${month}.${day} ${hours}:${minutes}:${seconds}`;
                        const curDate = `${milliseconds.toString(16)}`;
                        title.textContent = "일정 " + curDate;
                    }
                    else {
                        title.textContent = panelTitle.textContent;
                    }
                } 

                //기존 즐겨찾기 항목 버튼들 추가
                data.bookmarks.forEach(bookmark => {
                    const createLi = document.createElement('li');                            
                    const milliseconds = new Date(bookmark['created_at']).getTime();
                    const colorValue = milliseconds % 0xFFFFFF; 
                    const hexColor = `#${colorValue.toString(16).padStart(6, '0')}`;
                    createLi.className = "bookmark_item";
                    createLi.id = bookmark['id'];
                    createLi.style.cursor = "pointer";
                    innerHtml = `
                        <div style="background-color: ${hexColor}">
                            <span style="font-size: 17px; color: white;">★</span>
                        </div>
                        <p>${bookmark['title']}</p>
                        <button>
                            ${bookmarkID === bookmark['id'] 
                                ? '<span style="font-size: 17px; color: #5454ea;">✔</span>' 
                                : '<span style="font-size: 27px; color: white;">+</span>'
                            }
                        </button>
                    `;                            
                    createLi.innerHTML = innerHtml;
                    
                    createLi.addEventListener('click', (event) => {event.stopPropagation(); addToBookmark(createLi, createLi.querySelector('button span'), isPlace, name, address) });
                    createLi.querySelector('div').addEventListener('click', (event) => {event.stopPropagation(); addToBookmark(createLi, createLi.querySelector('button span'), isPlace, name, address) });
                    createLi.querySelector('span').addEventListener('click', (event) => {event.stopPropagation(); addToBookmark(createLi, createLi.querySelector('button span'), isPlace, name, address) });
                    createLi.querySelector('button').addEventListener('click', (event) => {event.stopPropagation(); addToBookmark(createLi, createLi.querySelector('button span'), isPlace, name, address) });
                    createLi.querySelector('p').addEventListener('click', (event)=> {event.stopPropagation(); addToBookmark(createLi, createLi.querySelector('button span'), isPlace, name, address) });
                    bookmarklistPanel.appendChild(createLi);
                });
                
                //새 즐겨찾기 항목 만드는 버튼 추가                        
                const createLi = document.createElement('li');
                createLi.className = "bookmark_item";
                createLi.id = "add_bookmark_list_btn";   
                innerHtml = `
                    <div>
                        <span>+</span>
                    </div>
                    <p>새 즐겨찾기 항목</p>
                `;              

                //10개 미만이면 활성화, 그 이상이면 비활성화 
                if (bookmarklistPanel.childNodes.length < 10) {
                    createLi.addEventListener('click', () => {
                        if (document.querySelectorAll("#new-folder").length == 0) {
                            const add_bookmark_list_btn = document.getElementById("add_bookmark_list_btn");
                            const inputElem = document.createElement("input");
                            inputElem.id = "new-folder";
                            inputElem.type = "text";
                            inputElem.placeholder = "새 폴더 이름 입력 (Enter)";
                            // inputElem.style.width = "200px";
                            // inputElem.style.marginBottom = "20px";

                            inputElem.style.margin = "0px auto 10px";
                            inputElem.style.marginBottom = "20px";
                            inputElem.style.background = "transparent";
                            inputElem.style.color = "white";
                            inputElem.style.outline = "none";
                            inputElem.style.border = "1px solid";
                            inputElem.style.fontSize = "20px";
                            inputElem.style.maxWidth = "330px";
                            inputElem.style.minWidth = "200px";

                            const plusElement = document.querySelector(".bookmarklist-panel ul");
                            plusElement.insertBefore(inputElem, add_bookmark_list_btn);

                            inputElem.focus();

                            // Enter로 확정
                            inputElem.addEventListener("keydown", function (e) {
                                if (e.key === "Enter") {
                                    e.preventDefault();
                                    const textValue = inputElem.value.trim();
                                    const isLightTheme = document.body.getAttribute("data-theme") === "light";

                                    // 입력이 없으면 취소
                                    if (textValue !== "") {
                                        const inputItem = document.querySelector(`.bookmarklist-panel .folder-item`);
                                        const items = document.querySelectorAll('.bookmarklist-panel ul li');                                                                             
                                        inputElem.remove();

                                        // 서버로 AJAX 호출
                                        fetch("/app/partials/favorites/add/", {
                                            method: "POST",
                                            headers: {
                                                "Content-Type": "application/json",
                                                "X-CSRFToken": getCSRFToken()
                                            },
                                            body: JSON.stringify({
                                                title: textValue,
                                                is_place: isPlace,
                                            })
                                        })
                                        .then(response => {
                                            if (!response.ok) {
                                                throw new Error(`HTTP error! status: ${response.status}`);
                                            }
                                            return response.json();
                                        })
                                        .then((data) => {
                                            if (data.success) {
                                                const createLi = document.createElement('li');                            
                                                const milliseconds = Date.now();
                                                const colorValue = milliseconds % 0xFFFFFF; 
                                                const hexColor = `#${colorValue.toString(16).padStart(6, '0')}`;
                                                createLi.className = "bookmark_item";
                                                createLi.id = data['id'];
                                                innerHtml = `
                                                    <div style="background-color: ${hexColor}">
                                                        <span style="font-size: 17px; color: white;">★</span>
                                                    </div>
                                                    <p>${textValue}</p>
                                                    <button>
                                                        ${bookmarkID === data['folderId'] 
                                                            ? '<span style="font-size: 17px; color: #5454ea;">✔</span>' 
                                                            : '<span style="font-size: 27px; color: white;">+</span>'
                                                        }
                                                    </button>
                                                `;                            
                                                createLi.innerHTML = innerHtml;
                                                document.querySelector('.bookmarklist-panel ul').insertBefore(createLi, add_bookmark_list_btn);
                                            } else {
                                                switch (countryId) {
                                                    case "KR": alert('즐겨찾기 아이템 생성 실패'); break;
                                                    case "JP": alert('お気に入りアイテムの作成に失敗'); break;
                                                    case "CN": alert('创建收藏夹失败'); break;
                                                    case "US": alert('Failed to create favorite item'); break;
                                                }
                                            }
                                        })
                                        .catch((err) => {
                                            console.error("서버 통신 오류:", err);
                                        });
                                    }                                    
                                }
                            });
                        }

                        // addFolderEventHandler(
                        //     "plus-place",
                        //     "#placesSection",
                        //     "새 폴더 이름 입력 (Enter)",
                        //     true,
                        //     { light: "/static/images/folder_light.png", dark: "/static/images/folder_dark.png" }
                        // );
                    })
                    createLi.classList.remove("button_inactive");
                    createLi.classList.add("button_active");
                }
                else {
                    createLi.classList.remove("button_active");
                    createLi.classList.add("button_inactive");
                }

                createLi.innerHTML = innerHtml;
                bookmarklistPanel.appendChild(createLi);
                
                toggleAnimation();                       
            } 
        } catch (error) {
            console.error("Error fetching bookmarks:", error);
        }
    }
    else {
        switch (countryId) {
            case "KR": alert('즐겨찾기에 저장할 데이터가 없습니다.'); break;
            case "JP": alert('お気に入りに保存するデータがありません。'); break;
            case "CN": alert('收藏夹中没有要保存的数据 。'); break;
            case "US": alert('There is no data to save in your favorites.'); break;
        }
    }
}

function addClickEvent() {
    
}

async function deleteBookmarklist(row) {
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    try {
        const payload = {
            bookmark_id: row.bookmark, // bookmark_id는 항상 포함
        };
        if (row.id.includes("pc")) {
            payload.bookmarkplace_id = row.id;
            if (row.id == getBookmarkListBtn.getAttribute("bookmarkplace_id")) {
                removeContent();
            }
        }
        if (row.id.includes("sc")) {
            payload.bookmarkschedule_id = row.id;
            if (row.id == getBookmarkListBtn.getAttribute("bookmarkschedule_id")) {
                removeContent();
            }
        }
        const response = await fetch(`/app/partials/favorites/delete_bookmarklist/`, {
            method: "POST", // POST 요청
            headers: {
                "Content-Type": "application/json", // JSON 데이터 전송
            },
            body: JSON.stringify(payload), // payload를 JSON으로 변환하여 본문에 추가
        });
    } catch (error) {
        console.error("Error fetching bookmarks:", error);
    }
}

function addToBookmark(li, span, isPlace, name, address) {
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    const panelTitle= document.getElementById("panel-title");
    const bookmarkId = li.id; 
    let body = null;
    let nameData = name || document.querySelector(".bookmarklist-panel h2").textContent;
    let addressData = address || document.querySelector(".bookmarklist-panel h3").textContent;

    if (isPlace) {
        // getBookmarkListBtn.classList.remove('place');
        body = JSON.stringify({
            is_place: true,
            name: nameData,
            bookmark_id: bookmarkId,
            bookmarkplace_id: getBookmarkListBtn.getAttribute("bookmarkplace_id"),
            bookmarkschedule_id: null,
            category: null,
            longitude: null,
            latitude: null,
            address: addressData,
            overview: getBookmarkListBtn.getAttribute("overview"),
        })
    }
    else {
        body = JSON.stringify({
            is_place: false,
            name: nameData,
            bookmark_id: bookmarkId,
            bookmarkplace_id: null,
            bookmarkschedule_id: getBookmarkListBtn.getAttribute("bookmarkschedule_id"),
            json_data: getBookmarkListBtn.getAttribute("json_data"),
        })
    }

    span.textContent = "✔";
    span.style.fontSize = "17px";
    span.style.color = "#5454ea";

    fetch("/app/partials/favorites/add_bookmarklist/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(), // Django CSRF 토큰 필요
        },
        body: body,
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log("Bookmark list added successfully!");
        } else {
            console.error("Error:", data.error || data.message);
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
}

function editPanelTitle() {
    console.log("editPanelTitle");
    const panelTitle = document.getElementById("panel-title");
    const editTitle = document.getElementById("edit-title");
    const editPanelTitleBtn = document.getElementById("editPanelTitleBtn");
    const editPanelTitleOKBtn = document.getElementById("editPanelTitleOKBtn");
    const editPanelTitleNOBtn = document.getElementById("editPanelTitleNOBtn");
    
    editPanelTitleBtn.style.display = "none";
    editPanelTitleOKBtn.style.display = "contents";      
    editPanelTitleNOBtn.style.display = "contents";      
    panelTitle.style.display = "none";
    editTitle.style.display = "block";
    editTitle.value = panelTitle.textContent;      
}

async function editPanelTitleOK() {
    const panelTitle = document.getElementById("panel-title");
    const editTitle = document.getElementById("edit-title");
    const editPanelTitleBtn = document.getElementById("editPanelTitleBtn");
    const editPanelTitleOKBtn = document.getElementById("editPanelTitleOKBtn");
    const editPanelTitleNOBtn = document.getElementById("editPanelTitleNOBtn");
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    const bookmarkschedule_id = getBookmarkListBtn.getAttribute("bookmarkschedule_id");
    const scheduleItems = document.querySelectorAll(".schedule-item");
    const oldName = panelTitle.textContent;

    editPanelTitleBtn.style.display = "contents";   
    editPanelTitleOKBtn.style.display = "none";      
    editPanelTitleNOBtn.style.display = "none";  
    editTitle.style.display = "none";    
    panelTitle.style.display = "block";
    panelTitle.textContent = editTitle.value;

    try {
        const response = await fetch('/app/partials/favorites/update_bookmark_title/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(), // CSRF 토큰 추가
            },
            body: JSON.stringify({ 
                bookmarkschedule_id: bookmarkschedule_id,
                name: editTitle.value,
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
            console.log("일정 즐겨찾기 항목 제목 업데이트 완료");
            scheduleItems.forEach(item => {
                if (item.querySelector('p').innerText.split("이름:")[1].trim() === oldName.trim()) {
                    item.querySelector('p').innerText = "이름:" + editTitle.value.trim();
                }
            });
        } else {
            console.error("1.Error updating schdule bookmark title:", error);
        }
    } catch (error) {
        console.error("2.Error updating schdule bookmark title:", error);
    }
}

function editPanelTitleNO() {
    const panelTitle = document.getElementById("panel-title");
    const editTitle = document.getElementById("edit-title");
    const editPanelTitleBtn = document.getElementById("editPanelTitleBtn");
    const editPanelTitleOKBtn = document.getElementById("editPanelTitleOKBtn");
    const editPanelTitleNOBtn = document.getElementById("editPanelTitleNOBtn");
    
    editPanelTitleBtn.style.display = "contents";     
    editPanelTitleOKBtn.style.display = "none";      
    editPanelTitleNOBtn.style.display = "none";    
    editTitle.style.display = "none";     
    panelTitle.style.display = "block";
}

function removeContent(nopaneltitle=true) {
    if (window.currentMarkers) {
        window.currentMarkers.forEach(marker => marker.setMap(null));
    }
    window.currentMarkers = []; // 새로운 마커 배열 초기화

    const map_panel_content = document.querySelector(".map-panel-content");
    const getBookmarkListBtn = document.getElementById("getBookmarkListBtn");
    const panelTitle= document.getElementById("panel-title");
    const editPanelTitleBtn = document.getElementById("editPanelTitleBtn");
    const dayButtonContainer = document.getElementById("day-button-container");
    
    if (getBookmarkListBtn && nopaneltitle) {
        getBookmarkListBtn.classList.remove('place');
        getBookmarkListBtn.classList.remove('schedule');
        getBookmarkListBtn.setAttribute("bookmark_id", null);
        getBookmarkListBtn.setAttribute("bookmarkplace_id", null);
        getBookmarkListBtn.setAttribute("bookmarkschedule_id", null);
        getBookmarkListBtn.setAttribute("json_data", null);
        getBookmarkListBtn.textContent = "☆";
    }
    if (panelTitle && nopaneltitle)
        panelTitle.innerHTML = "";
    if (map_panel_content)
        map_panel_content.innerHTML = "";
    if (editPanelTitleBtn && nopaneltitle)
        editPanelTitleBtn.style.display = "none";
    if (dayButtonContainer)
        dayButtonContainer.innerHTML = "";
}

function toggleMapPanel() {
    const minHeight = 45; // 터미널 최소 높이
    const maxHeight = window.innerHeight / 2; // 터미널 최대 높이
    const toggleUIBtn = document.getElementById("toggleUIBtn");
    const mapPanel = document.getElementById("map-panel");
    const buttonContainer = document.getElementById("day-button-container");

    // transition 적용
    mapPanel.style.transition = "height 0.5s ease";

    // 터미널 높이 및 버튼 상태 변경
    if (toggleUIBtn.textContent === "⮝") {
        // 터미널 확장
        mapPanel.style.height = `${maxHeight}px`;
        toggleUIBtn.textContent = "⮟";
    } else {
        // 터미널 축소
        mapPanel.style.height = `${minHeight}px`;
        toggleUIBtn.textContent = "⮝";
    }

    // 버튼 컨테이너 위치 업데이트
    if (buttonContainer) {
        buttonContainer.style.transition = "top 0.5s ease"; // 부드럽게 이동
        const mapPanelHeight = parseInt(mapPanel.style.height, 10);
        const mapPanelTop = window.innerHeight - mapPanelHeight; // mapPanel의 상단 위치 계산
        buttonContainer.style.top = `${mapPanelTop - buttonContainer.offsetHeight - 15}px`; // 터미널 위로 15px
    }

    // transition 제거 (500ms 후)
    setTimeout(() => {
        mapPanel.style.transition = "none";
        if (buttonContainer) {
            buttonContainer.style.transition = "none";
        }
    }, 500); // transition 시간과 동일하게 설정
}

function toggleAnimation() {
    const animatedDiv = document.getElementById('bookmarklist-div');
    if (animatedDiv.classList.contains('active')) {
        // 활성화 상태이면 숨김
        animatedDiv.classList.remove('active');
    } else {
        // 비활성화 상태이면 나타냄
        animatedDiv.classList.add('active');
    }
}

function updateLanguage(selectedCountryId) {
    const label_Settings = document.querySelector("#label_Settings");
    const label_theme = document.querySelector("#label_theme");
    const label_light = document.querySelector("#label_light");
    const label_dark = document.querySelector("#label_dark");
    const label_language = document.querySelector("#label_language");
    const label_contact = document.querySelector("#label_contact");
    const label_deleteBtn = document.querySelector(".delete-btn");

    const label_home = document.querySelector("#label_home");
    const label_planner = document.querySelector("#label_planner");
    const label_chatting = document.querySelector("#label_chatting");
    const label_bookmarks = document.querySelector("#label_bookmarks");
    const label_settings = document.querySelector("#label_settings");
    const label_profile = document.querySelector("#label_profile");

    const dayButtonContainer = document.querySelectorAll("#day-button-container button");

    // 각 country_id에 따른 텍스트 맵핑
    const translations_for_settings_page = [
        {
            US: "Settings",
            KR: "설정",
            JP: "設定",
            CN: "环境",
        },
        {
            US: "Theme",
            KR: "테마",
            JP: "テーマ",
            CN: "主题",
        },
        {
            US: "Light",
            KR: "밝은 모드",
            JP: "明るい",
            CN: "光",
        },
        {
            US: "Dark",
            KR: "어두운 모드",
            JP: "暗い",
            CN: "黑暗的",
        },
        {
            US: "Language",
            KR: "언어",
            JP: "言語",
            CN: "语言",
        },
        {
            US: "Contact Us",
            KR: "연락처",
            JP: "お問い合わせ",
            CN: "接触",
        },
        {
            US: "Delete Account",
            KR: "계정 삭제",
            JP: "アカウントの削除",
            CN: "删除帐户",
        },
    ];

    const translations_for_spa_page = [
        {
            US: "Home",
            KR: "홈",
            JP: "うち",
            CN: "房子",
        },
        {
            US: "Planner",
            KR: "플래너",
            JP: "プランナー",
            CN: "规划师",
        },
        {
            US: "Chatting",
            KR: "채팅",
            JP: "おしゃべり",
            CN: "聊天",
        },
        {
            US: "Bookmarks",
            KR: "즐겨찾기",
            JP: "お気に入り",
            CN: "收藏夹",
        },
        {
            US: "Settings",
            KR: "설정",
            JP: "設定",
            CN: "设置",
        },
        {
            US: "Profile",
            KR: "내 프로필",
            JP: "プロフィール",
            CN: "轮廓",
        },
    ];

    // 새로 선택된 언어에 따른 텍스트로 업데이트
    label_Settings.textContent = translations_for_settings_page[0][selectedCountryId] || "Settings";
    label_theme.textContent = translations_for_settings_page[1][selectedCountryId] || "Theme";
    label_light.textContent = translations_for_settings_page[2][selectedCountryId] || "Light";
    label_dark.textContent = translations_for_settings_page[3][selectedCountryId] || "Dark";
    label_language.textContent = translations_for_settings_page[4][selectedCountryId] || "Language";
    label_contact.textContent = translations_for_settings_page[5][selectedCountryId] || "Contact Us";
    label_deleteBtn.textContent = translations_for_settings_page[6][selectedCountryId] || "Delete Account";

    label_home.textContent = translations_for_spa_page[0][selectedCountryId] || "Home";
    label_planner.textContent = translations_for_spa_page[1][selectedCountryId] || "Planner";
    label_chatting.textContent = translations_for_spa_page[2][selectedCountryId] || "Chatting";
    label_bookmarks.textContent = translations_for_spa_page[3][selectedCountryId] || "Bookmarks";
    label_settings.textContent = translations_for_spa_page[4][selectedCountryId] || "Settings";
    label_profile.textContent = translations_for_spa_page[5][selectedCountryId] || "Profile";

    countryId = selectedCountryId;

    dayButtonContainer.forEach(button => {
        switch (countryId) {            
            case "KR": 
                button.textContent = button.textContent.replace("日目", "").replace("第", "").replace("天", "").replace("Day", "") + "일차"; 
                break;
            case "JP": 
                button.textContent = button.textContent.replace("일차", "").replace("第", "").replace("天", "").replace("Day", "") + "日目"; 
                break;
            case "CN": 
                button.textContent = "第" + button.textContent.replace("일차", "").replace("日目", "").replace("Day", "") + "天"; 
                break;
            case "US": 
                button.textContent = "Day" + button.textContent.replace("일차", "").replace("日目", "").replace("第", "").replace("天", "");
                break;
        }
    });
}