// flatpickr 기본 설정
const birthdayPicker = flatpickr("#birthday", {
    dateFormat: "Y-m-d",
    maxDate: "today",
});

// 언어 매핑
const languageMap = {
    US: "default", // 영어
    KR: "ko",      // 한국어
    JP: "ja",      // 일본어
    CN: "zh",      // 중국어
    ES: "es",      // 스페인어 (예시로 추가)
};

// 언어 변경 이벤트 처리
document.getElementById("language").addEventListener("change", function () {
    const selectedLanguage = this.value; // 선택된 언어 코드
    const locale = languageMap[selectedLanguage] || "default";
    birthdayPicker.set("locale", locale); // flatpickr 언어 설정
});

function submitSignup(event) {
    event.preventDefault();

    const usernameField = document.getElementById("username");
    const passwordField = document.getElementById("password");
    const confirmPasswordField = document.getElementById("confirm-password");
    const birthdayField = document.getElementById("birthday");
    const alertDiv = document.querySelector(".alert");
    const language = document.querySelector("#language");
    const selectedLanguage = language.selectedOptions[0].text;

    // 비밀번호와 비밀번호 확인 검증
    if (passwordField.value !== confirmPasswordField.value) {
        switch (selectedLanguage) {
            case "한국어": alertDiv.textContent = "비밀번호가 일치하지 않습니다!"; break;
            case "日本語": alertDiv.textContent = "パスワードが一致しません！"; break;
            case "简体字": alertDiv.textContent = "密码不匹配!"; break;
            case "English": alertDiv.textContent = "Passwords do not match!"; break;
        }
        confirmPasswordField.focus();
        passwordField.style.border = "2px solid red";
        confirmPasswordField.style.border = "2px solid red";
        return;
    } else {
        alertDiv.textContent = "";
        passwordField.style.border = "";
        confirmPasswordField.style.border = "";
    }

    if (!birthdayField.value.trim()) {
        switch (selectedLanguage) {
            case "한국어": alertDiv.textContent = "생년월일을 입력해 주세요!"; break;
            case "日本語": alertDiv.textContent = "生年月日の入力をお願いします！"; break;
            case "简体字": alertDiv.textContent = "请输入出生年月日！"; break;
            case "English": alertDiv.textContent = "Please enter your date of birth!"; break;
        }        
        return;
    }

    // 라디오 버튼 값 변환 (male -> 1, female -> 2, other -> 0)
    const genderMap = { male: 1, female: 2, other: 0 };
    const genderValue = document.querySelector('input[name="sex"]:checked').value;
    const gender = genderMap[genderValue] ?? 0;
    let countryId = "";

    const formData = {
        username: usernameField.value,
        password: passwordField.value,
        confirm_password: confirmPasswordField.value,
        nationality: document.getElementById("nationality").value,
        birthday: document.getElementById("birthday").value,
        gender: gender,
    };

    fetch("../signup_process/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify(formData),
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                switch (selectedLanguage) {
                    case "한국어": alert('성공적으로 가입되었습니다! 로그인해 주세요.'); break;
                    case "日本語": alert('登録に成功しました！ ログインしてください。'); break;
                    case "简体字": alert('您成功注册了 ！ 请登录。'); break;
                    case "English": alert('You have successfully signed up! Please sign in.'); break;
                }
                window.location.href = "../login/";
            } else {
                switch (selectedLanguage) {
                    case "한국어": alertDiv.textContent = "가입에 실패했습니다!"; break;
                    case "日本語": alertDiv.textContent = "登録に失敗しました！"; break;
                    case "简体字": alertDiv.textContent = "注册失败!"; break;
                    case "English": alertDiv.textContent = "Sign up failed!"; break;
                }
            }
        })
        .catch(error => console.error("Error:", error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateLanguage(selectedCountryId) {
    const username = document.querySelector("#username");
    const password = document.querySelector("#password");
    const confirmPassword = document.querySelector("#confirm-password");

    const label_password = document.querySelector("#label_password");
    const label_confirm_password = document.querySelector("#label_confirm_password");
    const label_birthday = document.querySelector("#label_birthday");
    const label_nationality = document.querySelector("#label_nationality");

    const label_gender = document.querySelector("#label_gender");
    const label_male = document.querySelector("#label_male");
    const label_female = document.querySelector("#label_female");
    const label_other = document.querySelector("#label_other");

    const label_account = document.querySelector("#label_account");
    const label_SignUp = document.querySelector("#label_SignUp");
    const label_signup = document.querySelector("#label_signup");
    const label_login = document.querySelector("#label_login");

    const translations_for_signup = [
        {
            English: "Sign Up",
            한국어: "회원가입",
            日本語: "会員登録",
            汉文: "加入会员",
        },
        {
            English: "Password",
            한국어: "비밀번호",
            日本語: "パスワード",
            汉文: "密码",
        },
        {
            English: "Confirm Password",
            한국어: "또는",
            日本語: "パスワード 確認",
            汉文: "验证密码",
        },
        {
            English: "Birthday",
            한국어: "생년월일",
            日本語: "生年月日",
            汉文: "出生日期",
        },
        {
            English: "Nationality",
            한국어: "국적",
            日本語: "国籍",
            汉文: "国籍",
        },
        {
            English: "Gender",
            한국어: "성별",
            日本語: "性別",
            汉文: "性别",
        },
        {
            English: "Male",
            한국어: "남성",
            日本語: "男",
            汉文: "男性",
        },
        {
            English: "Female",
            한국어: "여성",
            日本語: "女",
            汉文: "女性",
        },  
        {
            English: "Other",
            한국어: "기타",
            日本語: "その他",
            汉文: "等等",
        },
        {
            English: "Already have an account?",
            한국어: "계정이 있습니까?",
            日本語: "すでにアカウントをお持ちですか?",
            汉文: "已经有帐户？",
        },                
        {
            English: "Log In",
            한국어: "로그인",
            日本語: "ログイン",
            汉文: "登录",
        },                
    ];
    const translations_for_placeholder = [
        {
            English: "Enter your ID",
            한국어: "아이디를 입력하세요.",
            日本語: "IDを入力してください",
            汉文: "输入您的身份证件",
        },
        {
            English: "Enter your password",
            한국어: "비밀번호를 입력하세요.",
            日本語: "パスワードを入力してください",
            汉文: "输入您的密码",
        },
        {
            English: "Confirm your password",
            한국어: "비밀번호를 입력하세요.",
            日本語: "パスワードを確認してください",
            汉文: "确认您的密码",
        },                
    ];

    label_SignUp.textContent = translations_for_signup[0][selectedCountryId];
    label_signup.textContent = translations_for_signup[0][selectedCountryId];
    label_password.textContent = translations_for_signup[1][selectedCountryId];
    label_confirm_password.textContent = translations_for_signup[2][selectedCountryId];
    label_birthday.textContent = translations_for_signup[3][selectedCountryId];
    label_nationality.textContent = translations_for_signup[4][selectedCountryId];
    
    label_gender.textContent = translations_for_signup[5][selectedCountryId];
    label_male.textContent = translations_for_signup[6][selectedCountryId];
    label_female.textContent = translations_for_signup[7][selectedCountryId];
    label_other.textContent = translations_for_signup[8][selectedCountryId];

    label_account.textContent = translations_for_signup[9][selectedCountryId];
    label_login.firstChild.nodeValue = translations_for_signup[10][selectedCountryId];

    username.placeholder = translations_for_placeholder[0][selectedCountryId];
    password.placeholder = translations_for_placeholder[1][selectedCountryId];
    confirmPassword.placeholder = translations_for_placeholder[2][selectedCountryId];
    countryId = selectedCountryId;
}