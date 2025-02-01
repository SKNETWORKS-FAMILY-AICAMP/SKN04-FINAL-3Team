document.addEventListener('DOMContentLoaded', function() {
    const inputBox = document.querySelector(".input-box");
    const popup = document.getElementById('profilePopup');
    const navicon = document.getElementById('nav-icon');
    const profileLink = document.getElementById('profileLink');
    updateLanguage(countryId);

    if (inputBox) {
        switch (countryId) {
            case "KR": inputBox.placeholder = "일정을 만들거나 장소를 검색해 보세요"; break;
            case "JP": inputBox.placeholder = "スケジュールを作成するか、場所を検索してください"; break;
            case "CN": inputBox.placeholder = "创建日程或搜索地点"; break;
            case "US": inputBox.placeholder = "Search for a place or create a schedule"; break;
        }
    }
    if (navicon) {
        navicon.addEventListener('click', function(e) {
            if (isLoggedIn) {
                // 로그인이 되어 있다면 팝업창 열기
                e.stopPropagation(); // 이벤트 버블링 방지
                popup.classList.toggle('hidden');                        
                // window.location.href = "/app/profile/";
            } else {
                // 안 되어 있다면 로그인 페이지로 이동
                window.location.href = "/login/";
            }
        });
    }
    if (profileLink) {
        profileLink.addEventListener('click', function(e) {
            if (isLoggedIn) {
                // 로그인이 되어 있다면 팝업창 열기
                e.stopPropagation(); // 이벤트 버블링 방지
                popup.classList.toggle('hidden');                        
                // window.location.href = "/app/profile/";
            } else {
                // 안 되어 있다면 로그인 페이지로 이동
                window.location.href = "/login/";
            }
        });

        // 팝업 외부 클릭 시 닫기
        document.addEventListener('click', function (e) {
            if (popup) {
                if (!popup.classList.contains('hidden')) {
                    popup.classList.add('hidden');
                }
            }                    
        });

        if (popup) {
            // 팝업 내부 클릭 시 닫히지 않음
            popup.addEventListener('click', function (e) {
                e.stopPropagation();
            });
        }                
    }
});

async function goToEnterPage() {
    const inputBox = document.querySelector('.input-box');
    const userInput = inputBox.value.trim();

    if (userInput === "") {
        switch (countryId) {
            case "KR": alert('내용을 입력해주세요.'); break;
            case "JP": alert('内容を入力してください。'); break;
            case "CN": alert('请输入内容。'); break;
            case "US": alert('Please enter the contents.'); break;
        }
        return;
    }

    localStorage.setItem("chatMessage", userInput);

    if (isLoggedIn) {
        // 로그인한 사용자일 경우 chat_id 가져오기
        try {
            const response = await fetch("/app/partials/planner/get_or_create_chat_id/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success && data.chat_id) {
                // chat_id를 URL에 포함하여 이동
                window.location.href = `/app/planner/?chat_id=${encodeURIComponent(data.chat_id)}`;
            } else {
                console.error("Failed to get chat_id:", data.error || "Unknown error");
                window.location.href = `/app/planner/`;
            }
        } catch (error) {
            console.error("Error fetching chat_id:", error);
        }
    } else {
        // 비로그인 사용자일 경우
        window.location.href = `/app/planner/?chatMessage=${encodeURIComponent(userInput)}`;
    }
}

// 입력창 자동 높이 조정 및 버튼 위치 유지
document.querySelector('.input-box').addEventListener('input', function () {
    this.style.height = "auto";
    const scrollHeight = this.scrollHeight;
    const maxHeight = 300; // 6줄 높이 제한
    this.style.height = `${Math.min(scrollHeight, maxHeight)}px`;

    if (scrollHeight > maxHeight) {
        this.style.overflowY = "scroll";
    } else {
        this.style.overflowY = "hidden";
    }
});

// Enter 및 Shift+Enter 처리
document.querySelector('.input-box').addEventListener('keydown', function (e) {
    if (e.key === "Enter" && e.shiftKey) {
        e.preventDefault();
        const cursorPosition = this.selectionStart;
        this.value = this.value.slice(0, cursorPosition) + "\n" + this.value.slice(cursorPosition);
    } else if (e.key === "Enter") {
        e.preventDefault();
        document.querySelector('.send-button').click();
    }
});

function getCSRFToken() {
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    return csrfToken;
}

function updateLanguage(selectedCountryId) {
    const profilePopups = document.querySelectorAll("#profilePopup li a");
    const profileLink = document.querySelector("#profileLink");
    const researchHelper = document.querySelector(".research-helper");
    const inputBox = document.querySelector(".input-box");

    const translations_for_sign_in = {
        US: "Sign In",
        KR: "로그인",
        JP: "サインイン",
        CN: "登入",
    }

    const translations_for_popups = [
        {
            US: "Chattings",
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

    const translations_for_search_helper = {
        US: "Search example: Can you make a schedule for 2 nights and 3 days in Yongsan-gu, \n Jung-gu, Jongno-gu, and Gangnam-gu?",
        KR: "검색 예제: 용산구/중구/종로구/강남구의 2박 3일동안 일정을 만들어줘.",
        JP: "検索例: 龍山区/中区/鍾路区/江南区の2泊3日の日程を作ってくれる？",
        CN: "搜索示例: 龙山区/中区/钟路区/江南区能帮我安排3天2夜的日程吗？",
    }

    const translations_for_placeholder = {
        US: "Search for a place or create a schedule",
        KR: "일정을 만들거나 장소를 검색해 보세요",
        JP: "スケジュールを作成するか、場所を検索してください",
        CN: "创建日程或搜索地点",
    }

    // 새로 선택된 언어에 따른 텍스트로 업데이트
    if (name) {
        profileLink.textContent = name;
    }
    else {
        profileLink.textContent = translations_for_sign_in[selectedCountryId];
    }
    profilePopups.forEach((popup, index) => {
        popup.textContent = translations_for_popups[index][selectedCountryId];
    });

    researchHelper.textContent = translations_for_search_helper[selectedCountryId];
    researchHelper.style.marginTop = "20px";
                
    inputBox.placeholder = translations_for_placeholder[selectedCountryId];
}