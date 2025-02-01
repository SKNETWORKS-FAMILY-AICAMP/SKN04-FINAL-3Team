function updateLanguage(selectedCountryId) {
    const label_SignIn = document.querySelector("#label_SignIn");
    const username = document.querySelector("#username");
    const password = document.querySelector("#password");
    const label_password = document.querySelector("#label_password");
    const loginBtn = document.querySelector(".login-button");
    const label_or = document.querySelector("#label_or");
    const label_google = document.querySelector("#label_google");
    const label_account = document.querySelector("#label_account");
    const label_SignUp = document.querySelector("#label_SignUp");

    const translations_for_signin = [
        {
            English: "Sign In",
            한국어: "로그인",
            日本語: "サインイン",
            汉文: "登入",
        },
        {
            English: "Password",
            한국어: "비밀번호",
            日本語: "パスワード",
            汉文: "密码",
        },
        {
            English: "OR",
            한국어: "또는",
            日本語: "または",
            汉文: "或者",
        },
        {
            English: "Sign in with Google",
            한국어: "구글 계정으로 로그인",
            日本語: "Googleでサインイン",
            汉文: "使用 Google 登录",
        },
        {
            English: "Don't have an account?",
            한국어: "계정이 없습니까?",
            日本語: "アカウントがありませんか？",
            汉文: "没有帐户？",
        },
        {
            English: "Sign Up",
            한국어: "회원가입",
            日本語: "会員登録",
            汉文: "加入会员",
        },
        {
            English: "Enter your ID",
            한국어: "아이디를 입력하세요.",
            日本語: "IDを入力してください",
            汉文: "请输入您的ID",
        },
        {
            English: "Enter your Password",
            한국어: "비밀번호를 입력하세요.",
            日本語: "パスワードを入力してください",
            汉文: "请输入您的密码",
        },                
    ];

    label_SignIn.textContent = translations_for_signin[0][selectedCountryId];
    loginBtn.textContent = translations_for_signin[0][selectedCountryId];
    label_password.textContent = translations_for_signin[1][selectedCountryId];
    label_or.textContent = translations_for_signin[2][selectedCountryId];
    label_google.textContent = translations_for_signin[3][selectedCountryId];
    label_account.textContent = translations_for_signin[4][selectedCountryId];
    label_SignUp.textContent = translations_for_signin[5][selectedCountryId];

    username.placeholder = translations_for_signin[6][selectedCountryId];
    password.placeholder = translations_for_signin[7][selectedCountryId];
}