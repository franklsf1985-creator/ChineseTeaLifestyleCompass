# -*- coding: utf-8 -*-
"""
中国茶生活风格罗盘 / Chinese Tea Lifestyle Compass / 중국 차로 알아보는 나의 티 라이프 스타일

单文件 Streamlit 应用，代码分区：
  1) 页面配置与全局常量
  2) 视觉样式（低饱和配色 + 内联 SVG 茶文化线稿）
  3) 三语界面文案 TEXT
  4) 10 道选择轴题目数据 QUESTIONS
  5) 六种风格三语结果内容 STYLES
  6) 组合建议模板
  7) 数据校验与计分逻辑（标准化、同分处理）
  8) 页面渲染（登录 / 介绍 / 问卷 / 结果）
  9) 主流程路由
"""

import streamlit as st

# ============================================================
# 1) 页面配置与全局常量
# ============================================================
st.set_page_config(
    page_title="中国茶生活风格罗盘 · Chinese Tea Lifestyle Compass",
    page_icon="🍵",
    layout="centered",
)

ACCESS_CODE = "pnumis"  # 固定访问码（轻量门槛，非生产级安全认证）
CORE_QUESTION_IDS = ("q5", "q10")  # 核心情境题：同分时优先比较这两题的实际得分

# 固定的风格顺序：标准化得分与核心题得分都相同时，按此顺序稳定处理
STYLE_ORDER = [
    "pure_taste",
    "origin_explorer",
    "easy_daily",
    "social_host",
    "creative_mixer",
    "ritual_aesthete",
]

LANG_OPTIONS = ["zh", "ko", "en"]
LANG_NAMES = {"zh": "简体中文", "ko": "한국어", "en": "English"}

# 会话状态初始化：语言（默认韩语）、登录状态、是否开始测试、测试结果
st.session_state.setdefault("lang", "ko")
st.session_state.setdefault("authed", False)
st.session_state.setdefault("started", False)
st.session_state.setdefault("result", None)


# ============================================================
# 2) 视觉样式：低饱和配色 + 少量内联 SVG 线稿
#    背景装饰透明度约 4%–8%，pointer-events 关闭，手机端自动隐藏
# ============================================================
st.markdown(
    """
<style>
.stApp { background-color: #FAF9F5; }
html, body, [data-testid="stAppViewContainer"] { color: #343832; }
h1, h2, h3, h4 { color: #343832; font-weight: 600; }

.tea-card {
    background: #FFFEFB;
    border: 1px solid #E7EAE0;
    border-radius: 16px;
    padding: 22px 24px;
    margin: 6px 0 18px 0;
    box-shadow: 0 1px 3px rgba(52,56,50,0.05);
}
.tea-band {
    height: 6px; border-radius: 3px;
    background: linear-gradient(90deg, #788774, #D8C8B4);
    margin-bottom: 14px;
}
.tea-band-secondary {
    height: 6px; border-radius: 3px;
    background: linear-gradient(90deg, #D8C8B4, #E4E9E0);
    margin-bottom: 14px;
}
.tagline { color: #788774; font-size: 1.0rem; margin-top: -6px; }
.muted { color: #6b6f66; font-size: 0.92rem; }

.stButton > button {
    background: #788774; color: #FFFEFB; border: none;
    border-radius: 10px; padding: 0.45rem 1.4rem;
}
.stButton > button:hover { background: #687663; color: #FFFEFB; }
div[data-testid="stFormSubmitButton"] > button {
    background: #788774; color: #FFFEFB; border: none;
    border-radius: 10px; padding: 0.55rem 1.6rem; font-size: 1.02rem;
}
div[data-testid="stFormSubmitButton"] > button:hover { background: #687663; }

/* 角落茶叶线稿与底部远山：仅装饰，不拦截点击 */
.corner-leaf {
    position: fixed; top: 10px; right: 18px;
    width: 120px; opacity: 0.06; pointer-events: none; z-index: 0;
}
.footer-art {
    width: 100%; opacity: 0.07; pointer-events: none; margin-top: 30px;
}
/* 手机端隐藏边角装饰，优先展示题目与结果 */
@media (max-width: 640px) {
    .corner-leaf, .footer-art { display: none; }
    .tea-card { padding: 16px 16px; }
}
</style>
""",
    unsafe_allow_html=True,
)

# 盖碗线稿（登录页与介绍页页首使用）
GAIWAN_SVG = """
<svg viewBox="0 0 140 100" width="96" xmlns="http://www.w3.org/2000/svg"
     fill="none" stroke="#788774" stroke-width="2" stroke-linecap="round">
  <ellipse cx="70" cy="88" rx="46" ry="6"/>
  <path d="M36 44 C36 74, 50 84, 70 84 C90 84, 104 74, 104 44"/>
  <path d="M32 44 C32 40, 108 40, 108 44" stroke-linecap="round"/>
  <path d="M40 34 C50 24, 90 24, 100 34"/>
  <circle cx="70" cy="22" r="4"/>
  <path d="M56 12 C54 8, 58 6, 56 2" opacity="0.6"/>
  <path d="M72 12 C70 8, 74 6, 72 2" opacity="0.6"/>
</svg>
"""

# 右上角茶叶小枝线稿（页面角落装饰，透明度已由 CSS 控制）
LEAF_SPRIG_SVG = """
<svg viewBox="0 0 120 120" class="corner-leaf" xmlns="http://www.w3.org/2000/svg"
     fill="none" stroke="#788774" stroke-width="2.5" stroke-linecap="round">
  <path d="M60 110 C58 70, 62 40, 74 12"/>
  <path d="M64 84 C48 78, 38 64, 40 48 C56 54, 64 66, 64 84 Z"/>
  <path d="M66 56 C80 50, 88 38, 86 24 C72 30, 66 42, 66 56 Z"/>
</svg>
"""

# 底部远山轮廓线稿（结果页与介绍页底部，透明度由 CSS 控制）
MOUNTAINS_SVG = """
<svg viewBox="0 0 800 90" class="footer-art" xmlns="http://www.w3.org/2000/svg"
     fill="none" stroke="#788774" stroke-width="2" stroke-linecap="round">
  <path d="M0 80 C80 40, 140 20, 220 62 C300 96, 360 30, 460 58 C540 80, 620 26, 700 56 C750 74, 780 66, 800 60"/>
  <path d="M60 84 C160 60, 260 48, 380 74 C500 96, 640 54, 800 78" opacity="0.5"/>
</svg>
"""

# 六种风格的简洁线性小图标（仅帮助识别，不代表等级）
STYLE_ICONS = {
    "pure_taste": """<svg viewBox="0 0 48 48" width="34" fill="none" stroke="#788774" stroke-width="2.4" stroke-linecap="round"><path d="M10 38 C10 20, 22 10, 38 8 C38 26, 28 38, 10 38 Z"/><path d="M14 34 C20 26, 26 20, 34 14"/></svg>""",
    "origin_explorer": """<svg viewBox="0 0 48 48" width="34" fill="none" stroke="#788774" stroke-width="2.4" stroke-linecap="round"><path d="M6 38 L18 16 L26 28 L32 18 L42 38 Z"/><circle cx="36" cy="10" r="3.5"/></svg>""",
    "easy_daily": """<svg viewBox="0 0 48 48" width="34" fill="none" stroke="#788774" stroke-width="2.4" stroke-linecap="round"><path d="M12 14 H32 V36 C32 39, 30 41, 27 41 H17 C14 41, 12 39, 12 36 Z"/><path d="M32 18 C39 18, 39 28, 32 28"/></svg>""",
    "social_host": """<svg viewBox="0 0 48 48" width="34" fill="none" stroke="#788774" stroke-width="2.4" stroke-linecap="round"><path d="M12 22 C12 15, 30 15, 30 22 C30 29, 26 33, 21 33 C16 33, 12 29, 12 22 Z"/><path d="M30 21 C36 19, 40 22, 37 27"/><path d="M12 21 C8 19, 6 22, 8 25"/><path d="M18 12 C17 10, 19 9, 18 7"/></svg>""",
    "creative_mixer": """<svg viewBox="0 0 48 48" width="34" fill="none" stroke="#788774" stroke-width="2.4" stroke-linecap="round"><path d="M20 8 H28 V14 C33 16, 36 20, 36 27 V38 C36 40, 34 42, 32 42 H16 C14 42, 12 40, 12 38 V27 C12 20, 15 16, 20 14 Z"/><path d="M12 28 C18 24, 24 32, 30 28 C33 26, 35 27, 36 28"/></svg>""",
    "ritual_aesthete": """<svg viewBox="0 0 48 48" width="34" fill="none" stroke="#788774" stroke-width="2.4" stroke-linecap="round"><ellipse cx="24" cy="40" rx="18" ry="3"/><path d="M14 20 C14 32, 18 36, 24 36 C30 36, 34 32, 34 20"/><path d="M12 20 C12 18, 36 18, 36 20"/><path d="M17 14 C20 11, 28 11, 31 14"/><circle cx="24" cy="9" r="1.8"/></svg>""",
}


# ============================================================
# 3) 三语界面文案（zh / ko / en）
# ============================================================
TEXT = {
    "app_title": {
        "zh": "中国茶生活风格罗盘",
        "ko": "중국 차로 알아보는 나의 티 라이프 스타일",
        "en": "Chinese Tea Lifestyle Compass",
    },
    "app_subtitle": {
        "zh": "10 道情境选择题，找到属于你的饮茶方式",
        "ko": "10개의 상황 질문으로 찾는 나만의 차 마시는 방식",
        "en": "Ten situational questions to find your own way of enjoying tea",
    },
    "tagline": {
        "zh": "一盏清茶，留白片刻",
        "ko": "한 잔의 맑은 차, 잠시의 여백",
        "en": "A cup of clear tea, a moment of calm",
    },
    "lang_label": {"zh": "语言 / Language", "ko": "언어 / Language", "en": "Language / 语言"},
    "login_intro": {
        "zh": "这是一方安静的小茶室。输入访问码，即可开始一段关于茶与生活方式的小探索。",
        "ko": "조용한 작은 찻자리에 오신 것을 환영합니다. 접속 코드를 입력하면 차와 라이프스타일에 관한 작은 탐색을 시작할 수 있습니다.",
        "en": "Welcome to this quiet little tea room. Enter the access code to begin a small exploration of tea and lifestyle.",
    },
    "access_code_label": {"zh": "访问码", "ko": "접속 코드", "en": "Access code"},
    "access_code_placeholder": {"zh": "请输入访问码", "ko": "접속 코드를 입력하세요", "en": "Enter the access code"},
    "login_button": {"zh": "进入茶室", "ko": "입장하기", "en": "Enter the tea room"},
    "err_empty": {
        "zh": "访问码不能为空，请输入后再试。",
        "ko": "접속 코드가 비어 있습니다. 입력 후 다시 시도해 주세요.",
        "en": "The access code is empty. Please enter it and try again.",
    },
    "err_wrong": {
        "zh": "访问码不正确，请核对后重试。",
        "ko": "접속 코드가 올바르지 않습니다. 확인 후 다시 입력해 주세요.",
        "en": "The access code is incorrect. Please check it and try again.",
    },
    "logout": {"zh": "退出登录", "ko": "로그아웃", "en": "Log out"},
    # ---- 介绍页 ----
    "intro_title": {"zh": "测试介绍", "ko": "테스트 소개", "en": "About this quiz"},
    "intro_body": {
        "zh": "这不是心理测评，而是一张以中国茶文化为底色的生活灵感地图。通过 10 道日常情境选择题，我们会把你在选择轴上的位置，对应到六种茶生活风格：从茶汤本味到风土探索，从松弛日常到茶桌分享，从新趣创意到仪式美学。",
        "ko": "이 테스트는 심리 검사가 아니라, 중국 차 문화를 바탕으로 한 라이프스타일 영감 지도입니다. 일상적인 상황을 담은 10개의 질문에 답하면, 선택 축 위의 위치를 여섯 가지 티 라이프 스타일과 연결해 드립니다. 차 본연의 맛부터 산지 탐험, 편안한 일상, 함께 나누는 찻자리, 새로운 시도, 의식적 미학까지.",
        "en": "This is not a psychological assessment — it is a lifestyle inspiration map drawn from Chinese tea culture. Through ten everyday situational questions, we match your positions on the selection axes to six tea lifestyle styles: from pure taste to origin exploration, easy daily rituals to shared tea tables, creative mixing to quiet aesthetics.",
    },
    "intro_format_title": {"zh": "测试形式", "ko": "테스트 방식", "en": "How it works"},
    "intro_format": {
        "zh": "每道题提供一组并列的选项，代表两种自然状态或偏好之间的不同位置，点选最贴近你的一项即可。中间位置的选项同样是有效回答，代表“偶尔”“部分符合”或“两者皆可”。",
        "ko": "각 문항에는 두 가지 자연스러운 상태나 선호 사이의 서로 다른 위치를 나타내는 선택지가 나란히 제시됩니다. 자신에게 가장 가까운 하나를 눌러 주세요. 가운데 위치의 선택지도 '가끔', '부분적으로 그렇다', '둘 다 좋다'를 뜻하는 유효한 답변입니다.",
        "en": "Each question offers a row of options representing positions between two natural states or preferences — just tap the one closest to you. Middle options are valid answers too, meaning “occasionally”, “partly true”, or “both are fine”.",
    },
    "intro_meta": {
        "zh": "共 10 题 · 约 2 分钟完成 · 不收集任何个人信息",
        "ko": "총 10문항 · 약 2분 소요 · 개인정보를 수집하지 않습니다",
        "en": "10 questions · about 2 minutes · no personal information collected",
    },
    "intro_note_title": {"zh": "温和提醒", "ko": "참고 안내", "en": "A gentle note"},
    "intro_note": {
        "zh": "本测试仅用于茶文化体验、生活灵感与娱乐，不属于专业心理测评。六种风格没有高低优劣，也没有“最懂茶”的默认排名。",
        "ko": "이 테스트는 차 문화 체험과 일상의 영감, 재미를 위한 것으로 전문 심리 검사가 아닙니다. 여섯 가지 스타일에는 우열이 없으며, '가장 차를 잘 아는' 기본 순위도 없습니다.",
        "en": "This quiz is for tea culture, lifestyle inspiration, and fun — it is not a professional psychological assessment. The six styles are equal; there is no default ranking of who “knows tea best”.",
    },
    "intro_scoring_title": {"zh": "计分与同分处理（公开说明）", "ko": "점수 계산 및 동점 처리 (공개 안내)", "en": "Scoring and tie-breaking (explained)"},
    "intro_scoring": {
        "zh": "每道题的回答会同时为一种主要关联风格和一种辅助关联风格加分；各风格对应的题目数量与理论最高分可能不同，因此先计算“实际得分 ÷ 该风格理论最高分”进行标准化，再据此排序。若出现同分，优先比较第 5 题与第 10 题两道核心情境题中的实际得分；仍然相同时，按固定的风格顺序决定。标准化结果仅用于本次测试内部排序，不是任何专业测量指标。",
        "ko": "각 문항의 답변은 하나의 주요 연관 스타일과 하나의 보조 연관 스타일에 함께 점수를 더합니다. 스타일별 문항 수와 이론상 최고점이 다를 수 있으므로, 먼저 '실제 점수 ÷ 해당 스타일의 이론상 최고점'으로 표준화한 뒤 순위를 매깁니다. 동점이면 5번과 10번 두 핵심 상황 문항의 실제 점수를 비교하고, 그래도 같으면 고정된 스타일 순서를 따릅니다. 표준화 결과는 이번 테스트 내부 정렬에만 사용되며 전문적인 측정 지표가 아닙니다.",
        "en": "Each answer adds points to one primary and one secondary associated style. Because styles may have different numbers of questions and theoretical maximums, we first normalize (actual score ÷ that style's maximum) before ranking. Ties are broken by comparing actual scores on the two core situational questions (Q5 and Q10); if still tied, a fixed style order applies. Normalized results are only used for ranking within this quiz and are not any professional measurement.",
    },
    "style_preview_title": {"zh": "六种风格预览", "ko": "여섯 가지 스타일 미리보기", "en": "The six styles at a glance"},
    "start_button": {"zh": "开始测试", "ko": "테스트 시작", "en": "Start the quiz"},
    # ---- 问卷页 ----
    "quiz_title": {"zh": "10 道情境题", "ko": "10개의 상황 질문", "en": "Ten situational questions"},
    "quiz_total": {"zh": "共 10 题，点选最贴近你的选项", "ko": "총 10문항, 가장 가까운 답을 눌러 주세요", "en": "10 questions — tap the option closest to you"},
    "quiz_hint": {
        "zh": "请逐题点选最贴近你的选项，所有题目作答后即可提交。",
        "ko": "각 문항에서 가장 가까운 답을 눌러 주세요. 모든 문항에 답하면 제출할 수 있습니다.",
        "en": "Tap the option closest to you for each question — you can submit once all are answered.",
    },
    "quiz_unanswered": {
        "zh": "还有 {n} 道题未作答（第 {nums} 题），请全部完成后再提交。",
        "ko": "아직 답하지 않은 문항이 {n}개 있습니다({nums}번). 모두 답한 뒤 제출해 주세요.",
        "en": "{n} question(s) still unanswered (No. {nums}) — please answer all before submitting.",
    },
    "quiz_progress_label": {"zh": "第 {n} 题 / 共 10 题", "ko": "{n}번 / 총 10문항", "en": "Question {n} of 10"},
    "submit_button": {"zh": "提交，查看我的茶生活风格", "ko": "제출하고 나의 티 라이프 스타일 보기", "en": "Submit and see my tea lifestyle"},
    "mid_note_even": {
        "zh": "中间位置同样有效，表示介于两端之间。",
        "ko": "가운데 위치도 양쪽 사이를 뜻하는 유효한 답변입니다.",
        "en": "In-between positions are valid answers, meaning something between the two ends.",
    },
    # ---- 结果页 ----
    "result_title": {"zh": "你的茶生活风格结果", "ko": "당신의 티 라이프 스타일 결과", "en": "Your tea lifestyle result"},
    "primary_label": {"zh": "主要风格", "ko": "주요 스타일", "en": "Primary style"},
    "secondary_label": {"zh": "辅助风格", "ko": "보조 스타일", "en": "Secondary style"},
    "dist_title": {"zh": "六种风格的相对得分分布", "ko": "여섯 가지 스타일의 상대 점수 분포", "en": "Relative score distribution across the six styles"},
    "dist_note": {
        "zh": "得分只反映本次作答与六种风格的对应关系，不是专业心理测量分数。",
        "ko": "점수는 이번 답변과 여섯 가지 스타일의 대응 관계만을 보여줄 뿐, 전문적인 심리 측정 점수가 아닙니다.",
        "en": "Scores only reflect how this set of answers corresponds to the six styles — they are not professional psychological measurements.",
    },
    "scenes_title": {"zh": "你可能喜欢的饮茶场景", "ko": "어울릴 만한 티타임 장면", "en": "Tea moments you may enjoy"},
    "teas_title": {"zh": "推荐尝试的中国茶与喝法", "ko": "추천하는 중국차와 마시는 방법", "en": "Chinese teas and ways of drinking to try"},
    "tips_title": {"zh": "冲泡与品饮小建议", "ko": "우리고 마시는 작은 팁", "en": "Brewing and tasting tips"},
    "teaware_title": {"zh": "推荐茶具", "ko": "추천 다구", "en": "Recommended teaware"},
    "space_title": {"zh": "茶桌与空间小建议", "ko": "찻자리와 공간 팁", "en": "Tea table and space idea"},
    "try_title": {"zh": "也可以适度尝试", "ko": "가볍게 시도해 보면 좋은 스타일", "en": "Also worth a gentle try"},
    "combo_title": {"zh": "主风格 × 辅助风格的组合建议", "ko": "주요 스타일 × 보조 스타일 조합 조언", "en": "Your primary × secondary style combination"},
    "secondary_intro": {
        "zh": "作为补充，你的回答中也带有明显的「{name}」特质。它不会覆盖主要风格，而是为你的茶生活添上一层底色。",
        "ko": "보충으로, 당신의 답변에는 뚜렷한 '{name}' 성향도 함께 담겨 있습니다. 주요 스타일을 덮기보다는, 당신의 차 생활에 은은한 바탕을 더해 줍니다.",
        "en": "As a complement, your answers also show a clear touch of “{name}”. It does not replace your primary style — it adds a quiet undertone to your tea life.",
    },
    "retake_button": {"zh": "重新测试", "ko": "다시 테스트하기", "en": "Retake the quiz"},
    "edit_answers_button": {"zh": "返回修改答案", "ko": "답변 수정하기", "en": "Back to edit answers"},
    "result_restart_hint": {
        "zh": "重新测试会清除所有答案与本次结果，回到未作答状态；语言与登录状态会保留。",
        "ko": "다시 테스트하면 모든 답변과 이번 결과가 지워지고 처음 상태로 돌아갑니다. 언어와 로그인 상태는 유지됩니다.",
        "en": "Retaking clears all answers and this result, returning to an unanswered state; your language and login stay unchanged.",
    },
    "footer_disclaimer": {
        "zh": "本测试仅用于茶文化体验、生活灵感与娱乐，不构成专业心理评估或健康建议。",
        "ko": "이 테스트는 차 문화 체험, 일상의 영감과 재미를 위한 것이며, 전문적인 심리 평가나 건강 조언을 구성하지 않습니다.",
        "en": "This quiz is for tea culture, lifestyle inspiration, and entertainment only. It does not constitute professional psychological assessment or health advice.",
    },
}


def t(key):
    """按当前语言取出界面文案。"""
    return TEXT[key][st.session_state.lang]


# ============================================================
# 4) 10 道情境题数据
#    - axis: frequency(2) / willingness(2) / agreement(2) / preference(4)，自然交错
#    - levels: 选项数量（5 个为主，q6 为 4 个、q10 为 6 个，由题干自然决定）
#    - 答案保存为 0 起的整数索引：0 = 最左端，最大索引 = 最右端；未作答前不预选任何项
#    - reverse: 反向计分标记（最高分在最左端），约三分之一题目采用，避免高分总在右侧
#    - primary / secondary: 主要、辅助关联风格，二者必须不同
#    - w_primary / w_secondary: 每个选项对应的主要、辅助风格加分权重，长度必须等于 levels
# ============================================================
QUESTIONS = [
    {
        "id": "q1",
        "axis": "preference",
        "levels": 5,
        "reverse": False,
        "stem": {
            "zh": "周末午后，你想为自己泡一杯茶。此刻你更希望——",
            "ko": "주말 오후, 나를 위해 차 한 잔을 준비합니다. 지금 더 끌리는 쪽은——",
            "en": "It's a quiet weekend afternoon and you're making yourself some tea. Right now you'd prefer—",
        },
        "left": {"zh": "越简单方便越好", "ko": "최대한 간편하게", "en": "As simple and easy as possible"},
        "right": {"zh": "愿意慢慢准备和冲泡", "ko": "천천히 준비하고 우리고 싶다", "en": "Happy to prepare and brew slowly"},
        "mid": {"zh": "看情况，两者都可以", "ko": "상황에 따라 둘 다 괜찮다", "en": "Depends — both are fine"},
        "labels": {
            "zh": ["越简单越好", "偏简单", "两者都可以", "愿意慢慢泡", "享受完整过程"],
            "ko": ["최대한 간편하게", "조금 간편하게", "둘 다 괜찮아요", "천천히 우리는 편", "과정까지 즐기기"],
            "en": ["As simple as possible", "Fairly simple", "Either way", "Brew with some care", "Enjoy the full process"],
        },
        "primary": "ritual_aesthete",
        "secondary": "easy_daily",
        # 双端偏好：右端提高仪式美学，左端提高松弛日常，中点给双方相等基础分
        "w_primary": [0, 1, 2, 3, 4],
        "w_secondary": [4, 3, 2, 1, 0],
    },
    {
        "id": "q2",
        "axis": "frequency",
        "levels": 5,
        "reverse": False,
        "stem": {
            "zh": "喝茶时，你会留意并回想一款茶的香气、滋味等细节吗？",
            "ko": "차를 마실 때, 그 차의 향이나 맛 같은 디테일을 눈여겨보고 떠올리는 편인가요?",
            "en": "When you drink tea, how often do you notice and reflect on details like its aroma and taste?",
        },
        "left": {"zh": "从不", "ko": "전혀 그렇지 않다", "en": "Never"},
        "right": {"zh": "几乎每次都会", "ko": "거의 매번 그렇다", "en": "Almost every time"},
        "mid": {"zh": "偶尔", "ko": "가끔", "en": "Occasionally"},
        "labels": {
            "zh": ["从不", "很少", "偶尔", "经常", "几乎每次"],
            "ko": ["전혀", "거의 안", "가끔", "자주", "거의 매번"],
            "en": ["Never", "Rarely", "Occasionally", "Often", "Almost every time"],
        },
        "primary": "origin_explorer",
        "secondary": "pure_taste",
        # 频率越高，探索与品味细节越多；本味派仅在高频端轻度加分
        "w_primary": [0, 1, 2, 3, 4],
        "w_secondary": [0, 0, 1, 1, 2],
    },
    {
        "id": "q3",
        "axis": "willingness",
        "levels": 5,
        "reverse": False,
        "stem": {
            "zh": "如果看到冷泡茶、水果茶等新式喝法，你愿意亲自尝试吗？",
            "ko": "냉침차나 과일차 같은 새로운 방식의 차를 본다면, 직접 시도해 볼 의향이 있나요?",
            "en": "If you come across new-style tea drinks like cold-brew or fruit tea, how willing are you to try making them yourself?",
        },
        "left": {"zh": "完全不想尝试", "ko": "전혀 시도하고 싶지 않다", "en": "Not willing at all"},
        "right": {"zh": "非常愿意尝试", "ko": "꼭 한번 시도해 보고 싶다", "en": "Very willing to try"},
        "mid": {"zh": "可以试试看", "ko": "한 번쯤 해 볼 수 있다", "en": "Could give it a try"},
        "labels": {
            "zh": ["完全不想", "不太想", "可以试试看", "比较愿意", "非常愿意"],
            "ko": ["전혀", "별로", "해 볼 수 있어요", "꽤 하고 싶어요", "꼭 해 보고 싶어요"],
            "en": ["Not at all", "Not really", "Could try", "Quite willing", "Very willing"],
        },
        "primary": "creative_mixer",
        "secondary": "easy_daily",
        # 意愿越高，新趣创意得分越高；冷泡等方式也给松弛日常轻度加分
        "w_primary": [0, 1, 2, 3, 4],
        "w_secondary": [0, 0, 1, 1, 2],
    },
    {
        "id": "q4",
        "axis": "agreement",
        "levels": 5,
        "reverse": False,
        "stem": {
            "zh": "家人或朋友来访时，我会很自然地想泡一壶茶招待大家。",
            "ko": "가족이나 친구가 찾아오면 자연스럽게 차를 우려 대접하고 싶어진다.",
            "en": "When family or friends visit, I naturally feel like brewing a pot of tea for everyone.",
        },
        "left": {"zh": "完全不符合", "ko": "전혀 그렇지 않다", "en": "Not like me at all"},
        "right": {"zh": "非常符合", "ko": "매우 그렇다", "en": "Very much like me"},
        "mid": {"zh": "部分符合", "ko": "부분적으로 그렇다", "en": "Partly true"},
        "labels": {
            "zh": ["完全不符合", "不太符合", "部分符合", "比较符合", "非常符合"],
            "ko": ["전혀 아니다", "별로 아니다", "부분적으로 그렇다", "꽤 그렇다", "매우 그렇다"],
            "en": ["Not at all", "Not really", "Partly true", "Mostly true", "Very much me"],
        },
        "primary": "social_host",
        "secondary": "creative_mixer",
        # 待客意愿越高，茶桌分享得分越高；茶点搭配给新趣创意轻度加分
        "w_primary": [0, 1, 2, 3, 4],
        "w_secondary": [0, 0, 1, 1, 2],
    },
    {
        "id": "q5",  # 核心情境题（同分时优先比较）
        "axis": "preference",
        "levels": 5,
        "reverse": True,  # 反向计分：最高分在最左端
        "stem": {
            "zh": "理想的喝茶时刻，更接近哪一种？",
            "ko": "이상적인 티타임에 더 가까운 쪽은?",
            "en": "Which comes closer to your ideal tea moment?",
        },
        "left": {"zh": "和喜欢的人围坐在一起分享", "ko": "좋아하는 사람들과 둘러앉아 나누기", "en": "Sharing the moment with people I like"},
        "right": {"zh": "一个人安安静静地享用", "ko": "혼자 조용히 즐기기", "en": "Enjoying it quietly on my own"},
        "mid": {"zh": "看心情，两种都好", "ko": "기분에 따라 둘 다 좋다", "en": "Depends on my mood — both are good"},
        "labels": {
            "zh": ["一起分享", "偏分享", "两种都好", "偏独处", "安静独享"],
            "ko": ["함께 나누기", "나누는 편", "둘 다 좋아요", "혼자인 편", "조용히 혼자"],
            "en": ["Share together", "Lean to sharing", "Both are good", "Lean to solo", "Quiet and solo"],
        },
        "primary": "social_host",
        "secondary": "ritual_aesthete",
        # 双端偏好（反向）：左端分享提高茶桌分享，右端独处提高仪式美学，中点双方相等
        "w_primary": [4, 3, 2, 1, 0],
        "w_secondary": [0, 1, 2, 3, 4],
    },
    {
        "id": "q6",
        "axis": "willingness",
        "levels": 4,  # 偶数级：此题不适合设置中间立场，采用 4 级
        "reverse": False,
        "stem": {
            "zh": "你愿不愿意用几句话简单记录喝过的茶，比如它的香气和口感？",
            "ko": "마신 차의 향이나 맛을 몇 줄로 간단히 기록해 볼 의향이 있나요?",
            "en": "Would you be willing to jot down a few notes about the teas you drink — their aroma, taste, and so on?",
        },
        "left": {"zh": "完全不感兴趣", "ko": "전혀 관심 없다", "en": "Not interested at all"},
        "right": {"zh": "很愿意坚持记录", "ko": "꾸준히 기록하고 싶다", "en": "Happy to keep notes"},
        "mid": {"zh": "中间位置表示兴趣一般，同样是有效回答", "ko": "가운데 위치도 유효한 답변입니다", "en": "In-between positions are valid answers too"},
        "labels": {
            "zh": ["完全不感兴趣", "兴趣不大", "可以偶尔记一记", "很愿意坚持记录"],
            "ko": ["전혀 관심 없다", "별로 끌리지 않는다", "가끔 기록해 볼 수 있다", "꾸준히 기록하고 싶다"],
            "en": ["Not interested at all", "Not very interested", "Could note occasionally", "Happy to keep notes"],
        },
        "primary": "origin_explorer",
        "secondary": "pure_taste",
        "w_primary": [0, 1, 2, 3],
        "w_secondary": [0, 1, 1, 2],
    },
    {
        "id": "q7",
        "axis": "preference",
        "levels": 5,
        "reverse": True,  # 反向计分：探索意愿放在左端，最高分在最左端
        "stem": {
            "zh": "面对没喝过的茶，你通常——",
            "ko": "마셔 보지 않은 차를 앞에 두면 보통——",
            "en": "When you see a tea you've never tried, you usually—",
        },
        "left": {"zh": "愿意尝试陌生的茶，越新鲜越好", "ko": "새로운 차라면 기꺼이 시도한다", "en": "Happy to try unfamiliar teas — the newer the better"},
        "right": {"zh": "还是选熟悉顺口的茶更安心", "ko": "익숙하고 편안한 차가 더 좋다", "en": "Prefer familiar, reliable teas I already like"},
        "mid": {"zh": "看情况，熟悉的和新鲜的都可以", "ko": "상황에 따라 둘 다 괜찮다", "en": "Depends — both familiar and new are fine"},
        "labels": {
            "zh": ["越新鲜越好", "偏新鲜感", "两者都可以", "偏熟悉安心", "只选熟悉的茶"],
            "ko": ["새로운 게 좋아요", "새로운 편", "둘 다 괜찮아요", "익숙한 편", "익숙한 차만"],
            "en": ["The newer the better", "Lean to new", "Either way", "Lean to familiar", "Only familiar teas"],
        },
        "primary": "origin_explorer",
        "secondary": "easy_daily",
        # 双端偏好（反向）：左端尝试新茶提高风土探索，右端熟悉安心提高松弛日常
        "w_primary": [4, 3, 2, 1, 0],
        "w_secondary": [0, 1, 2, 3, 4],
    },
    {
        "id": "q8",
        "axis": "agreement",
        "levels": 5,
        "reverse": False,
        "stem": {
            "zh": "喝第一口茶时，我会先留意它本身的香气和滋味。",
            "ko": "차를 처음 한 모금 마실 때, 그 차 자체의 향과 맛에 먼저 주의가 간다.",
            "en": "With the first sip of a tea, my attention goes first to its own aroma and taste.",
        },
        "left": {"zh": "完全不符合", "ko": "전혀 그렇지 않다", "en": "Not like me at all"},
        "right": {"zh": "非常符合", "ko": "매우 그렇다", "en": "Very much like me"},
        "mid": {"zh": "部分符合", "ko": "부분적으로 그렇다", "en": "Partly true"},
        "labels": {
            "zh": ["完全不符合", "不太符合", "部分符合", "比较符合", "非常符合"],
            "ko": ["전혀 아니다", "별로 아니다", "부분적으로 그렇다", "꽤 그렇다", "매우 그렇다"],
            "en": ["Not at all", "Not really", "Partly true", "Mostly true", "Very much me"],
        },
        "primary": "pure_taste",
        "secondary": "origin_explorer",
        "w_primary": [0, 1, 2, 3, 4],
        "w_secondary": [0, 0, 1, 1, 2],
    },
    {
        "id": "q9",
        "axis": "frequency",
        "levels": 5,
        "reverse": True,  # 反向计分：左端“从不添加”给本味派最高分
        "stem": {
            "zh": "平时喝茶时，你会往茶里加牛奶、水果或其他风味吗？",
            "ko": "평소 차를 마실 때 우유나 과일 등 다른 풍미를 더하는 편인가요?",
            "en": "When you drink tea, how often do you add milk, fruit, or other flavors to it?",
        },
        "left": {"zh": "从不", "ko": "전혀", "en": "Never"},
        "right": {"zh": "经常这样", "ko": "자주 그런다", "en": "Quite often"},
        "mid": {"zh": "偶尔", "ko": "가끔", "en": "Occasionally"},
        "labels": {
            "zh": ["从不", "很少", "偶尔", "有时", "经常这样"],
            "ko": ["전혀", "거의 안", "가끔", "때때로", "자주"],
            "en": ["Never", "Rarely", "Occasionally", "Sometimes", "Quite often"],
        },
        "primary": "pure_taste",
        "secondary": "creative_mixer",
        # 反向：越常添加风味，新趣创意越高；从不添加则本味派最高，中点双方有基础分
        "w_primary": [4, 3, 2, 1, 0],
        "w_secondary": [0, 1, 2, 3, 4],
    },
    {
        "id": "q10",  # 核心情境题（同分时优先比较）
        "axis": "preference",
        "levels": 6,  # 偶数级：冲泡投入是连续谱，采用 6 级更自然
        "reverse": False,
        "stem": {
            "zh": "如果有一套顺手的茶具摆在面前，你更倾向于——",
            "ko": "손에 익은 다구가 눈앞에 있다면, 당신은——",
            "en": "If a comfortable tea set were placed in front of you, you would lean toward—",
        },
        "left": {"zh": "用顺手的杯子随意泡，怎么方便怎么来", "ko": "편한 컵으로 자유롭게, 편한 대로 우린다", "en": "Brewing casually in a handy cup, whatever is easiest"},
        "right": {"zh": "愿意按温杯、投茶、注水的步骤完整冲泡", "ko": "잔 데우기, 찻잎 넣기, 물 붓기까지 순서대로 우린다", "en": "Following the full steps — warming the cup, adding leaves, pouring water"},
        "mid": {"zh": "中间位置表示介于两者之间，同样是有效回答", "ko": "가운데 위치도 둘 사이를 뜻하는 유효한 답변입니다", "en": "In-between positions are valid answers, meaning something between the two"},
        "labels": {
            "zh": ["怎么方便怎么来", "基本随意", "略微随意", "略微讲究", "比较讲究", "按步骤完整冲泡"],
            "ko": ["편한 대로", "대체로 자유롭게", "약간 자유롭게", "약간 정성 들이기", "꽤 정성 들이기", "순서대로 정성껏"],
            "en": ["Whatever is easiest", "Mostly casual", "Slightly casual", "Slightly careful", "Fairly careful", "Full step-by-step brewing"],
        },
        "primary": "ritual_aesthete",
        "secondary": "easy_daily",
        # 双端偏好：右端完整冲泡提高仪式美学，左端随意泡提高松弛日常，中间双方接近相等
        "w_primary": [0, 1, 2, 3, 4, 5],
        "w_secondary": [5, 4, 3, 2, 1, 0],
    },
]


# ============================================================
# 5) 六种茶生活风格：完整三语结果内容
#    每种风格、每种语言包含：名称 / 标签句 / 完整描述 / 3 个场景 /
#    3-5 项推荐茶与喝法 / 3 条冲泡建议 / 推荐茶具 / 空间建议 /
#    可适度尝试的其他风格 / 组合建议用短句
# ============================================================
STYLES = {
    # ------------------------------------------------ 清香本味派
    "pure_taste": {
        "name": {"zh": "清香本味派", "ko": "맑은 본맛파", "en": "Pure Taste"},
        "tagline": {
            "zh": "少一点添加，多一分真味。",
            "ko": "덜 더할수록 선명해지는, 차의 본래 맛.",
            "en": "Less added, more revealed — the true taste of tea.",
        },
        "desc": {
            "zh": "你欣赏茶叶最本真的样子：一缕清香、一口回甘，就足以让人满足。比起复杂的流程和热闹的场面，你更在意茶汤入口时那份干净与清爽。你不排斥新器物和新方法，但希望它们服务于茶本身，而不是盖过茶的味道。对你来说，喝茶是一种安静的专注：看叶片在水中舒展，闻香气的细微变化，感受一杯茶从浓到淡的完整过程。简单不是没有要求，而是把注意力留给最重要的地方。",
            "ko": "당신은 차의 가장 본래의 모습을 소중히 여깁니다. 은은한 향 하나, 깔끔하게 이어지는 뒷맛 하나면 충분합니다. 복잡한 과정이나 화려한 분위기보다, 찻잎이 우러난 맑고 산뜻한 맛 자체에 더 마음이 갑니다. 새로운 도구나 방식을 배척하지는 않지만, 그것이 차의 맛을 돋우는 역할이기를 바랍니다. 찻잎이 물속에서 펼쳐지는 모습을 보고, 향의 미세한 변화를 느끼며, 한 잔의 차가 진해졌다 옅어지는 전 과정을 조용히 음미하는 시간을 즐깁니다. 단순함은 기준이 없다는 뜻이 아니라, 가장 중요한 곳에 마음을 두는 방식입니다.",
            "en": "You appreciate tea in its most honest form: a clear aroma and a clean, lingering finish are enough. Complicated routines and busy settings matter less to you than the freshness in the cup. You don't reject new tools or methods, but you want them to serve the leaf, not cover it. For you, drinking tea is a quiet kind of attention — watching the leaves open in the water, noticing how the aroma shifts, and following one cup from strong to gentle. Simplicity here is not a lack of standards; it is a way of keeping your attention on what matters most.",
        },
        "scenes": {
            "zh": ["清晨醒来，独自冲一杯清爽的绿茶", "雨后的窗边，慢慢喝一盏白茶", "专注工作或阅读前，先给自己一杯清茶"],
            "ko": ["아침에 일어나 혼자 산뜻한 녹차를 우리는 시간", "비 갠 뒤 창가에서 천천히 마시는 백차 한 잔", "집중해서 일하거나 읽기 전에 곁에 두는 맑은 차"],
            "en": ["A fresh green tea alone on an early morning", "A slow cup of white tea by the window after rain", "A clear cup of tea before focused work or reading"],
        },
        "teas": [
            {
                "name": {"zh": "龙井（绿茶）", "ko": "룽징(녹차)", "en": "Longjing (green tea)"},
                "note": {
                    "zh": "豆香清爽，滋味鲜醇，适合体会绿茶的干净口感。",
                    "ko": "은은한 콩향과 산뜻한 맛이 나는 대표 녹차로, 깔끔한 질감을 느끼기에 좋습니다.",
                    "en": "A classic green tea with a gentle chestnut-like aroma and a fresh, clean taste.",
                },
            },
            {
                "name": {"zh": "白毫银针（白茶）", "ko": "바이하오인전(백차)", "en": "Silver Needle (white tea)"},
                "note": {
                    "zh": "满披白毫的芽头，汤感清淡甘甜，最能感受「少即是多」。",
                    "ko": "흰 솜털을 두른 어린 싹으로 만든 차로, 맑고 은은한 단맛이 '적을수록 깊어지는' 매력을 보여 줍니다.",
                    "en": "Downy young buds with a pale, gently sweet liquor — minimal processing, maximum subtlety.",
                },
            },
            {
                "name": {"zh": "清香型铁观音（乌龙茶）", "ko": "청향형 철관음(우롱차)", "en": "Qingxiang Tieguanyin (light oolong)"},
                "note": {
                    "zh": "兰花香清雅，口感清爽，适合喜欢香而不浓的人。",
                    "ko": "맑은 난초 향과 산뜻한 맛으로, 향기롭지만 무겁지 않은 차를 좋아하는 분께 잘 어울립니다.",
                    "en": "A lightly oxidized oolong with an elegant orchid aroma — fragrant yet refreshing.",
                },
            },
            {
                "name": {"zh": "安吉白茶（绿茶）", "ko": "안지백차(녹차)", "en": "Anji Baicha (green tea)"},
                "note": {
                    "zh": "虽名为白茶，实为绿茶，鲜爽柔和，几乎不苦。",
                    "ko": "이름은 백차지만 녹차의 일종으로, 부드럽고 감칠맛이 좋으며 쓴맛이 거의 없습니다.",
                    "en": "Despite its name, it's a green tea — soft, savory-sweet, and almost never bitter.",
                },
            },
        ],
        "tips": {
            "zh": [
                "泡绿茶用约 80℃ 的水，能减少苦涩，让鲜爽感更突出。",
                "先闻香，再小口慢饮，留意香气从热到凉的变化。",
                "同一款茶试着连泡 2–3 次，感受每一泡浓淡与香气的差别。",
            ],
            "ko": [
                "녹차는 약 80℃의 물로 우리면 쓴맛이 줄고 산뜻함이 살아납니다.",
                "먼저 향을 맡고 천천히 음미하며, 식어 갈 때 향이 어떻게 달라지는지 느껴 보세요.",
                "같은 차를 2~3번 우려 보며, 우릴 때마다 달라지는 농도와 향을 비교해 보세요.",
            ],
            "en": [
                "Brew green teas at around 80°C to reduce bitterness and keep the freshness.",
                "Smell first, then sip slowly — notice how the aroma changes as the cup cools.",
                "Re-steep the same leaves 2–3 times and compare how each infusion shifts.",
            ],
        },
        "teaware": {
            "name": {"zh": "透明玻璃杯或白瓷盖碗", "ko": "투명 유리컵 또는 백자 개완", "en": "A clear glass or a white porcelain gaiwan"},
            "note": {
                "zh": "能看清汤色与叶底，不吸味、不抢味，最衬本味。",
                "ko": "찻물의 색과 찻잎을 그대로 볼 수 있고, 향을 머금지 않아 차 본연의 맛에 잘 어울립니다.",
                "en": "They let you see the liquor and the leaves, and don't hold on to flavors — ideal for pure taste.",
            },
        },
        "space": {
            "zh": "一张干净的桌面、一只喜欢的杯子就足够。对本味派来说，留白就是最好的布置。",
            "ko": "깨끗한 책상 위 좋아하는 컵 하나면 충분합니다. 본맛파에게 여백은 가장 좋은 장식입니다.",
            "en": "A clean table and a cup you love are enough. For pure taste, empty space is the best decoration.",
        },
        "try_other": {
            "id": "origin_explorer",
            "sentence": {
                "zh": "偶尔把两款不同产地的绿茶并排冲一次，只比较香气和口感——你会对自己喜欢的「本味」有更具体的认识。",
                "ko": "가끔은 서로 다른 산지의 녹차 두 가지를 나란히 우려 향과 맛만 비교해 보세요. 좋아하는 '본래의 맛'이 더 구체적으로 보일 거예요.",
                "en": "Once in a while, brew two green teas from different regions side by side and compare only aroma and taste — you'll understand your own idea of “pure taste” much better.",
            },
        },
        "combo_main": {
            "zh": "让茶的香气和滋味始终站在舞台中央，越简单越能见真章",
            "ko": "차의 향과 맛이 언제나 주인공이 되도록, 단순할수록 깊어지는 방식으로",
            "en": "keeping the tea's own aroma and taste at center stage, where simplicity reveals the most",
        },
        "combo_tip": {
            "zh": "在简单之中继续打磨对细节的敏感，比如水温与出汤时间",
            "ko": "물의 온도나 우리는 시간처럼, 단순함 속에서 디테일에 대한 감각을 갈고닦아 보세요",
            "en": "keep sharpening your sense for small details like water temperature and steeping time",
        },
    },
    # ------------------------------------------------ 风土探索派
    "origin_explorer": {
        "name": {"zh": "风土探索派", "ko": "산지 탐험파", "en": "Origin Explorer"},
        "tagline": {
            "zh": "每一片叶子，都藏着一座山的故事。",
            "ko": "찻잎 한 잎마다 어느 산의 이야기가 담겨 있습니다.",
            "en": "Every leaf carries the story of a mountain.",
        },
        "desc": {
            "zh": "你对一杯茶背后的来处充满好奇：它长在什么样的山上，什么季节采摘，又经过了怎样的工艺。你喜欢把两款茶放在一起对比，也愿意用简单的词语记下自己的感受——日积月累，这些小小的记录会变成一张属于你自己的风味地图。对你来说，喝茶是一场不必远行的旅行，每一款陌生的茶都是一个新的目的地；熟悉的老朋友，也常常在新的冲泡方式里露出另一副面孔。",
            "ko": "당신은 한 잔의 차 뒤에 있는 배경이 궁금합니다. 어떤 산에서 자랐는지, 어느 계절에 땄는지, 어떤 공정을 거쳤는지까지. 두 가지 차를 나란히 놓고 비교하는 것을 좋아하고, 느낀 점을 짧은 단어로 기록해 두기도 합니다. 그 작은 기록들이 쌓이면 당신만의 풍미 지도가 됩니다. 당신에게 차 마시기는 멀리 떠나지 않아도 되는 여행입니다. 낯선 차는 새로운 목적지이고, 익숙한 차도 새로운 우리는 방법에서 또 다른 얼굴을 보여 줍니다.",
            "en": "You are curious about where a cup of tea comes from: what kind of mountain it grew on, in which season it was picked, and what craft shaped it. You enjoy brewing two teas side by side, and you like writing down your impressions in simple words — over time, these small notes become your own flavor map. For you, drinking tea is travel without leaving home: every unfamiliar tea is a new destination, and old favorites often reveal a different face under a new brewing method.",
        },
        "scenes": {
            "zh": ["周末下午，把两款不同产区的乌龙茶并排对比", "旅行时拐进当地的小茶馆，喝一杯产地限定", "安静夜晚，给最近喝过的茶写几行风味笔记"],
            "ko": ["주말 오후, 서로 다른 산지의 우롱차 두 가지를 나란히 비교하기", "여행지의 작은 찻집에 들러 그 지역의 차 마셔 보기", "고요한 밤, 최근에 마신 차의 풍미 노트를 몇 줄 적기"],
            "en": ["A weekend afternoon comparing two oolongs from different regions", "Stopping by a small local teahouse while traveling", "A quiet evening writing a few lines of tasting notes"],
        },
        "teas": [
            {
                "name": {"zh": "武夷岩茶（乌龙茶）", "ko": "무이암차(우롱차)", "en": "Wuyi rock tea (oolong)"},
                "note": {
                    "zh": "产自武夷山丹霞岩壁之间，焙火层次丰富，常被称为「岩骨花香」。",
                    "ko": "무이산의 바위 틈에서 자란 차로, 로스팅의 깊은 결이 살아 있어 '바위의 골격과 꽃향기'라 불립니다.",
                    "en": "Grown among the cliffs of Wuyi, known for layered roasting notes often called “rock character with floral aroma”.",
                },
            },
            {
                "name": {"zh": "凤凰单丛（乌龙茶）", "ko": "펑황단총(우롱차)", "en": "Fenghuang Dancong (oolong)"},
                "note": {
                    "zh": "广东凤凰山的单株采制茶，一丛一香，香型从蜜兰到鸭屎香变化多端。",
                    "ko": "광둥 펑황산에서 나무 한 그루씩 따서 만드는 차로, 나무마다 꿀·난초 등 향이 달라 비교하는 재미가 큽니다.",
                    "en": "Single-bush oolongs from Fenghuang Mountain — each bush has its own aroma, from honey-orchid to almond, perfect for comparison.",
                },
            },
            {
                "name": {"zh": "祁门红茶（红茶）", "ko": "치먼 홍차", "en": "Keemun (black tea)"},
                "note": {
                    "zh": "似花似果似蜜的经典红茶，是认识中国红茶的好起点。",
                    "ko": "꽃과 과일, 꿀을 닮은 향의 고전적인 홍차로, 중국 홍차를 시작하기에 좋은 기준점입니다.",
                    "en": "A classic black tea with floral, fruity, honeyed notes — a great benchmark for exploring Chinese black teas.",
                },
            },
            {
                "name": {"zh": "普洱生茶（黑茶类）", "ko": "푸얼 생차", "en": "Raw Pu'er"},
                "note": {
                    "zh": "云南大叶种晒青茶，随年份缓慢转化，适合长期观察与记录。",
                    "ko": "윈난의 큰잎 차를 말려 만든 차로, 시간이 지나며 맛이 서서히 변해 오래 관찰하고 기록하는 재미가 있습니다.",
                    "en": "Sun-dried Yunnan large-leaf tea that slowly transforms with age — ideal for long-term observation and notes.",
                },
            },
        ],
        "tips": {
            "zh": [
                "对比两款茶时用同样的水温和投茶量，差异会更清楚。",
                "笔记不用专业词汇，写「像炒栗子」「像雨后的草」就很好。",
                "买茶时留意产地与采摘季节，同一产区春茶和秋茶性格也不同。",
            ],
            "ko": [
                "두 차를 비교할 때는 물 온도와 찻잎 양을 같게 맞추면 차이가 더 또렷해집니다.",
                "전문 용어가 아니어도 괜찮습니다. '군밤 같다', '비 온 뒤 풀냄새 같다'처럼 내 언어로 적어 보세요.",
                "차를 고를 때 산지와 따는 계절을 확인해 보세요. 같은 산지라도 봄차와 가을차의 성격은 다릅니다.",
            ],
            "en": [
                "When comparing two teas, keep water temperature and leaf amount the same so differences stand out.",
                "Your notes don't need jargon — “like roasted chestnuts” or “like grass after rain” is perfect.",
                "Check the origin and picking season when buying; even spring and autumn picks from one region differ.",
            ],
        },
        "teaware": {
            "name": {"zh": "白瓷小盖碗或审评杯", "ko": "백자 개완 또는 테이스팅 컵", "en": "A small white porcelain gaiwan or tasting cups"},
            "note": {
                "zh": "白色衬底方便对比汤色，小容量适合多款茶连着试。",
                "ko": "흰 바탕 덕분에 찻물 색을 비교하기 쉽고, 작은 용량이라 여러 차를 이어서 시음하기 좋습니다.",
                "en": "The white surface makes liquor colors easy to compare, and the small size suits back-to-back tastings.",
            },
        },
        "space": {
            "zh": "在架子或抽屉留一个「茶样角」，给每款茶贴上产地与日期标签，慢慢攒出你的风味地图。",
            "ko": "선반이나 서랍에 '차 샘플 코너'를 만들어 산지와 날짜를 붙여 두세요. 조금씩 당신만의 풍미 지도가 쌓입니다.",
            "en": "Keep a small “sample corner” on a shelf, with origin and date labels on each tea — your flavor map will grow over time.",
        },
        "try_other": {
            "id": "social_host",
            "sentence": {
                "zh": "下次对比茶时邀一位朋友一起喝——同两款茶，两个人的描述往往不一样，这是探索的另一种乐趣。",
                "ko": "다음 비교 시음에는 친구 한 명을 초대해 보세요. 같은 두 차도 사람마다 표현이 달라서, 탐험이 또 다른 즐거움이 됩니다.",
                "en": "Next time you compare teas, invite a friend — the same two teas often get very different descriptions, which is another kind of discovery.",
            },
        },
        "combo_main": {
            "zh": "把每一杯茶都当作一次小旅行，让好奇心带路",
            "ko": "매 잔의 차를 작은 여행처럼, 호기심이 길을 안내하도록",
            "en": "treating every cup as a small journey, letting curiosity lead the way",
        },
        "combo_tip": {
            "zh": "继续用简单记录积累你的风味地图，偶尔也允许自己「只是好喝」地喝一杯",
            "ko": "간단한 기록으로 풍미 지도를 쌓아 가되, 가끔은 그냥 '맛있네' 하고 즐기는 한 잔도 허락해 보세요",
            "en": "keep building your flavor map with simple notes, while allowing yourself an occasional cup that's “just tasty”",
        },
    },
    # ------------------------------------------------ 松弛日常派
    "easy_daily": {
        "name": {"zh": "松弛日常派", "ko": "편안한 일상파", "en": "Easy Daily"},
        "tagline": {
            "zh": "茶不必隆重，好喝自在就好。",
            "ko": "차는 거창하지 않아도 됩니다. 편하게 맛있으면 그만입니다.",
            "en": "Tea doesn't have to be formal — easy and enjoyable is enough.",
        },
        "desc": {
            "zh": "你希望喝茶像喝水一样自然：不需要专门的茶具，也不用记住复杂的步骤。工作时手边的一杯、通勤路上的一瓶冷泡、睡前的一口温润，都是刚刚好的陪伴。你重视的是轻松、自在和可持续——能天天喝的茶，才是真正属于你的茶。简单并不意味着将就，你同样在意茶好不好喝，只是不愿让形式成为负担。忙碌日子里，那一杯不费力的热茶，就是你给自己的小留白。",
            "ko": "당신은 차 마시기가 물 마시기만큼 자연스럽기를 바랍니다. 전용 다구도, 복잡한 순서도 필요 없습니다. 일하는 동안 곁에 둔 한 잔, 통근길의 냉침 한 병, 잠들기 전의 부드러운 한 모금이면 충분합니다. 당신이 중요하게 여기는 것은 편안함과 지속 가능함입니다. 매일 마실 수 있는 차야말로 진짜 내 차입니다. 단순하다고 대충이라는 뜻은 아닙니다. 맛은 분명히 따지되, 형식이 부담이 되길 원하지 않을 뿐입니다. 바쁜 하루 속 힘들이지 않고 마시는 따뜻한 차 한 잔이, 당신이 스스로에게 주는 작은 여백입니다.",
            "en": "You want tea to feel as natural as drinking water: no special teaware required, no complicated steps to memorize. A cup beside you while you work, a bottle of cold brew on the commute, a mellow sip before bed — each is just right. What you value is ease, comfort, and sustainability: a tea you can drink every day is the tea that truly belongs to you. Simple doesn't mean settling — you still care whether it tastes good; you just don't want formality to become a burden. On busy days, that effortless cup of hot tea is the small breathing room you give yourself.",
        },
        "scenes": {
            "zh": ["办公桌上，马克杯里泡着一天的陪伴", "通勤路上，前一晚冷泡好的一瓶茶", "睡前一小时，一杯温润不刺激的熟茶"],
            "ko": ["책상 위 머그컵에 우려 둔 하루의 동반자", "통근길에 챙긴, 전날 밤 우려 둔 냉침 한 병", "잠들기 한 시간 전, 자극 없이 부드러운 숙차 한 잔"],
            "en": ["A mug of tea keeping you company at your desk", "A bottle of cold brew made the night before, for the commute", "A mellow, gentle cup an hour before bed"],
        },
        "teas": [
            {
                "name": {"zh": "茉莉花茶（再加工茶）", "ko": "재스민차", "en": "Jasmine tea"},
                "note": {
                    "zh": "绿茶吸足茉莉花香，大杯冲泡也明亮好喝，几乎不会失败。",
                    "ko": "녹차에 재스민 향을 입힌 차로, 큰 컵에 우려도 향이 산뜻하고 실패할 일이 거의 없습니다.",
                    "en": "Green tea scented with jasmine blossoms — bright and forgiving even in a big mug.",
                },
            },
            {
                "name": {"zh": "熟普洱（黑茶类）", "ko": "푸얼 숙차", "en": "Ripe Pu'er"},
                "note": {
                    "zh": "醇厚温润、耐泡不苦，马克杯泡一整天也顺口。",
                    "ko": "깊고 부드러운 맛에 여러 번 우려도 쓰지 않아, 머그컵으로 종일 마시기 좋습니다.",
                    "en": "Mellow, smooth, and hard to over-steep — a mug-friendly tea that lasts all day.",
                },
            },
            {
                "name": {"zh": "滇红（红茶）", "ko": "뎬홍(홍차)", "en": "Dianhong (black tea)"},
                "note": {
                    "zh": "云南红茶的甜润顺口，热泡温润，放凉或加冰也好喝。",
                    "ko": "윈난 홍차 특유의 달콤하고 부드러운 맛으로, 뜨겁게도 차갑게도 잘 어울립니다.",
                    "en": "A sweet, smooth Yunnan black tea — good hot, and just as pleasant cooled or over ice.",
                },
            },
            {
                "name": {"zh": "冷泡乌龙", "ko": "냉침 우롱차", "en": "Cold-brew oolong"},
                "note": {
                    "zh": "睡前把茶叶和常温水放进瓶子，早上就能带走，清甜少苦涩。",
                    "ko": "자기 전 찻잎과 상온의 물을 병에 넣어 두면 아침에 바로 챙길 수 있고, 쓴맛 없이 달콤합니다.",
                    "en": "Leaves plus room-temperature water in a bottle overnight — grab it in the morning; sweet, with barely any bitterness.",
                },
            },
        ],
        "tips": {
            "zh": [
                "大杯泡茶时投茶量宁少勿多，泡久了也不容易苦涩。",
                "冷泡最简单：常温水加茶叶，冰箱冷藏约 4 小时即可。",
                "选耐泡的茶（如熟普、寿眉），一杯能喝很久，省去频繁换茶。",
            ],
            "ko": [
                "큰 컵에 우릴 때는 찻잎을 조금 적게 넣으세요. 오래 두어도 쓰지 않습니다.",
                "냉침은 가장 간단합니다. 상온의 물에 찻잎을 넣고 냉장고에 약 4시간 두면 끝.",
                "숙차나 쇼우메이처럼 여러 번 우려지는 차를 고르면 자주 갈 필요가 없습니다.",
            ],
            "en": [
                "When brewing in a big mug, use slightly fewer leaves — it stays smooth even after sitting.",
                "Cold brew is the easiest: leaves in room-temperature water, about 4 hours in the fridge.",
                "Pick re-steepable teas (like ripe Pu'er or Shoumei) so one serving lasts much longer.",
            ],
        },
        "teaware": {
            "name": {"zh": "带滤网的马克杯或飘逸杯", "ko": "거름망 있는 머그컵 또는 인퓨저 컵", "en": "A mug with an infuser, or a one-touch brewing cup"},
            "note": {
                "zh": "投茶、加水、提起滤网，三步搞定，清洗也简单。",
                "ko": "찻잎을 넣고 물을 부은 뒤 거름망만 들어 올리면 끝. 설거지도 간단합니다.",
                "en": "Add leaves, add water, lift the infuser — done in three steps, and easy to clean.",
            },
        },
        "space": {
            "zh": "在书桌或厨房固定一个顺手的「茶角」：茶叶、杯子、热水各就各位，伸手即得就是最好动线。",
            "ko": "책상이나 주방에 손 닿기 좋은 '차 코너'를 정해 두세요. 차, 컵, 물이 제자리에 있으면 그것이 최고의 동선입니다.",
            "en": "Set up a fixed “tea corner” on your desk or in the kitchen: leaves, cup, and hot water within reach is the best layout.",
        },
        "try_other": {
            "id": "creative_mixer",
            "sentence": {
                "zh": "既然已经习惯冷泡，不妨偶尔加一小片柠檬或几颗莓果——只需要一点点，就能给熟悉的味道开一扇窗。",
                "ko": "냉침에 이미 익숙하다면, 가끔 레몬 한 조각이나 베리 몇 알을 넣어 보세요. 아주 조금만 더해도 익숙한 맛에 새로운 창이 열립니다.",
                "en": "Since you already enjoy cold brew, try adding a slice of lemon or a few berries sometime — just a touch opens a new window on a familiar taste.",
            },
        },
        "combo_main": {
            "zh": "让茶以最不费力的方式融入每天的生活",
            "ko": "차가 힘들이지 않고 매일의 일상에 스며들도록",
            "en": "letting tea slip into everyday life with the least possible effort",
        },
        "combo_tip": {
            "zh": "保持这份自在，偶尔给自己一个小小的「升级」，比如一只更好握的杯子",
            "ko": "이 편안함을 유지하되, 가끔은 손에 잘 잡히는 컵 하나처럼 작은 '업그레이드'를 선물해 보세요",
            "en": "keep the ease, and occasionally treat yourself to a small upgrade — like a cup that fits your hand better",
        },
    },
    # ------------------------------------------------ 茶桌分享派
    "social_host": {
        "name": {"zh": "茶桌分享派", "ko": "함께 나누는 찻자리파", "en": "Social Host"},
        "tagline": {
            "zh": "好茶要和喜欢的人一起喝。",
            "ko": "좋은 차는 좋아하는 사람들과 함께 마실 때 완성됩니다.",
            "en": "Good tea is best shared with people you like.",
        },
        "desc": {
            "zh": "对你来说，茶桌是拉近人与人之间距离的地方。家人围坐、朋友来访，你很自然地想烧一壶水、泡一壶茶。你在意的不是茶有多名贵，而是每个人手里都有一杯热茶，话题在茶香里慢慢展开。你享受准备的过程：摆杯子、配茶点、留意谁喜欢浓一点、谁偏爱淡一点。一杯茶递出去，心意就已经传达到了。茶冷了可以再续，人坐得久了，话也就深了。",
            "ko": "당신에게 찻자리는 사람과 사람 사이의 거리를 좁히는 곳입니다. 가족이 둘러앉거나 친구가 찾아오면, 자연스럽게 물을 끓이고 차를 우리게 됩니다. 중요한 건 차가 얼마나 귀한지가 아니라, 모두의 손에 따뜻한 잔이 쥐어져 있고 차 향기 속에서 이야기가 천천히 펼쳐지는 것입니다. 잔을 놓고, 다식을 곁들이고, 누구는 진하게 누구는 연하게 좋아하는지 챙기는 준비 과정 자체를 즐깁니다. 차 한 잔을 건네는 순간, 마음은 이미 전해집니다. 차는 식으면 다시 따르면 되고, 오래 앉아 있을수록 이야기는 깊어집니다.",
            "en": "For you, the tea table is where people grow closer. When family gathers or friends drop by, you naturally reach for the kettle. What matters isn't how rare the tea is, but that everyone holds a warm cup while conversation unfolds in the aroma. You enjoy the preparation: setting out cups, pairing snacks, remembering who likes it stronger and who prefers it light. The moment you hand someone a cup, your care has already been delivered. Tea gone cold can always be refilled — and the longer people linger, the deeper the talk becomes.",
        },
        "scenes": {
            "zh": ["周末家宴之后，为大家泡上一壶解腻的茶", "朋友小聚，茶配点心，聊到天黑", "节日里的家庭茶桌，长辈小辈都有一杯"],
            "ko": ["주말 가족 식사 후, 모두를 위한 깔끔한 차 한 주전자", "친구들과의 모임, 차와 다식으로 어둑해질 때까지 수다", "명절의 가족 찻자리, 어른부터 아이까지 모두의 잔"],
            "en": ["Brewing a pot for everyone after a weekend family meal", "Friends over, tea and snacks, talking until dark", "A holiday family tea table, with a cup for every generation"],
        },
        "teas": [
            {
                "name": {"zh": "铁观音（乌龙茶）", "ko": "철관음(우롱차)", "en": "Tieguanyin (oolong)"},
                "note": {
                    "zh": "香气高扬、回甘明显，大壶冲泡也能让整桌人都闻到香。",
                    "ko": "향이 화사하고 뒷맛이 달아, 큰 주전자로 우려도 온 테이블에 향이 퍼집니다.",
                    "en": "High aroma and a sweet finish — even a big pot fills the whole table with fragrance.",
                },
            },
            {
                "name": {"zh": "滇红（红茶）", "ko": "뎬홍(홍차)", "en": "Dianhong (black tea)"},
                "note": {
                    "zh": "甜润温和、接受度高，是不太喝茶的客人也容易喜欢的一款。",
                    "ko": "달콤하고 순해서 차를 잘 마시지 않는 손님도 편하게 즐길 수 있는 홍차입니다.",
                    "en": "Sweet and gentle with broad appeal — an easy favorite even for guests who rarely drink tea.",
                },
            },
            {
                "name": {"zh": "陈皮普洱", "ko": "진피 푸얼차", "en": "Tangerine-peel Pu'er"},
                "note": {
                    "zh": "熟普的醇厚加上陈皮的清香，饭后解腻，温润好入口。",
                    "ko": "숙차의 깊은 맛에 귤껍질의 상쾌한 향이 더해져, 식후에 깔끔하고 부드럽게 즐기기 좋습니다.",
                    "en": "Mellow ripe Pu'er brightened by dried tangerine peel — smooth and refreshing after a meal.",
                },
            },
            {
                "name": {"zh": "大壶寿眉（白茶）", "ko": "큰 주전자로 우리는 쇼우메이(백차)", "en": "Shoumei (white tea), brewed in a big pot"},
                "note": {
                    "zh": "叶片粗老耐煮耐泡，一大壶能陪整场聚会，越泡越甜。",
                    "ko": "잎이 크고 여러 번 우려도 맛이 좋아, 한 주전자로 모임 내내 함께할 수 있습니다. 우릴수록 달아집니다.",
                    "en": "Sturdy leaves that hold up to many steeps — one big pot lasts the whole gathering and grows sweeter.",
                },
            },
        ],
        "tips": {
            "zh": [
                "人多时用大壶或公道杯分茶，保证每杯浓淡均匀、温度合适。",
                "茶点选清淡不腻的：坚果、淡甜糕点，别抢茶的味。",
                "先问一句客人的偏好——浓一点还是淡一点，是最贴心的开场白。",
            ],
            "ko": [
                "사람이 많을 때는 큰 주전자나 공도배로 나눠 따르면 잔마다 농도와 온도가 고릅니다.",
                "다식은 견과류나 담백한 과자처럼 깔끔한 것으로 고르세요. 차 맛을 가리지 않게.",
                "손님에게 진하게 드릴지 연하게 드릴지 먼저 물어보세요. 가장 다정한 첫인사입니다.",
            ],
            "en": [
                "For groups, use a big pot or a fairness pitcher so every cup is even in strength and temperature.",
                "Pick light snacks — nuts, mildly sweet pastries — that don't overpower the tea.",
                "Ask guests first whether they like it strong or light; it's the warmest opening line.",
            ],
        },
        "teaware": {
            "name": {"zh": "大容量茶壶＋公道杯", "ko": "넉넉한 주전자와 공도배(숙우)", "en": "A generous teapot plus a fairness pitcher"},
            "note": {
                "zh": "先出汤到公道杯再分杯，每个人的茶都一样匀。",
                "ko": "공도배에 먼저 따른 뒤 잔에 나누면, 모든 잔의 맛이 고르게 맞춰집니다.",
                "en": "Pour into the pitcher first, then serve — everyone gets the same even cup.",
            },
        },
        "space": {
            "zh": "围坐的桌面中央留出一小块茶席位置，杯子成组摆好；茶在当中，话就围过来了。",
            "ko": "둘러앉는 테이블 가운데 작은 찻자리를 마련하고 잔을 모아 두세요. 차가 중심에 서면 이야기가 모여듭니다.",
            "en": "Keep a small tea spot at the center of the table with cups grouped together — when tea is at the center, conversation gathers around it.",
        },
        "try_other": {
            "id": "ritual_aesthete",
            "sentence": {
                "zh": "下次招待前，提前十分钟温杯、理好桌面——一点点仪式感，会让客人觉得被认真对待。",
                "ko": "다음 대접 전에는 10분 일찍 잔을 데우고 테이블을 정돈해 보세요. 작은 정성 하나가 손님에게 '소중히 대접받는 느낌'을 줍니다.",
                "en": "Next time, warm the cups and tidy the table ten minutes before guests arrive — a touch of ritual makes people feel truly looked after.",
            },
        },
        "combo_main": {
            "zh": "让茶桌成为人与人之间最舒服的连接",
            "ko": "찻자리가 사람과 사람을 잇는 가장 편안한 연결고리가 되도록",
            "en": "making the tea table the most comfortable connection between people",
        },
        "combo_tip": {
            "zh": "照顾大家之余，也给自己留一杯不用张罗、只管享用的茶",
            "ko": "모두를 챙기는 사이, 아무것도 준비하지 않고 그저 즐기기만 하는 나만의 한 잔도 남겨 두세요",
            "en": "while looking after everyone, keep one cup for yourself that you simply enjoy without hosting",
        },
    },
    # ------------------------------------------------ 新趣创意派
    "creative_mixer": {
        "name": {"zh": "新趣创意派", "ko": "새로운 시도파", "en": "Creative Mixer"},
        "tagline": {
            "zh": "传统茶的下一杯，由你来定义。",
            "ko": "전통차의 다음 한 잔은 당신이 정의합니다.",
            "en": "The next cup of traditional tea is yours to define.",
        },
        "desc": {
            "zh": "你对茶的好奇心不止于传统泡法：冷泡、调味、新式茶饮，你都愿意试一试。在你眼里，传统不是必须原样遵守的规矩，而是可以继续生长的起点。你会留意哪种茶适合冷泡、哪种香气和水果合拍，也会把成功的搭配记下来。你尊重茶本身的味道——创意是为了发现茶的更多可能，而不是用糖和噱头把它淹没。失败的一杯也不可惜，它只是通往好配方的必经之路。",
            "ko": "당신의 호기심은 전통적인 우리는 방법에 머물지 않습니다. 냉침, 블렌딩, 새로운 스타일의 티 음료까지 기꺼이 시도합니다. 당신에게 전통은 그대로 지켜야 할 규칙이라기보다, 계속 자라날 수 있는 출발점입니다. 어떤 차가 냉침에 맞는지, 어떤 향이 과일과 어울리는지 살피고, 성공한 조합은 기록해 둡니다. 차 자체의 맛을 존중하기에, 당신의 창의력은 설탕이나 눈속임으로 차를 덮는 쪽이 아니라 차의 새로운 가능성을 찾는 쪽을 향합니다. 실패한 한 잔도 아깝지 않습니다. 좋은 레시피로 가는 길 위의 한 걸음이니까요.",
            "en": "Your curiosity about tea goes well beyond traditional brewing: cold brews, flavor pairings, new-style tea drinks — you're willing to try them all. In your eyes, tradition is not a rule to follow exactly, but a starting point that keeps growing. You notice which teas suit cold brewing and which aromas pair well with fruit, and you write down the combinations that work. You respect the taste of the leaf itself — creativity, for you, is about discovering tea's possibilities, not drowning it in sugar and gimmicks. Even a failed cup isn't wasted; it's one step on the way to a good recipe.",
        },
        "scenes": {
            "zh": ["夏天的厨房里，做一轮冷泡茶小实验", "周末自制水果乌龙，调出自己的比例", "探访新式茶饮店，研究菜单背后的茶底"],
            "ko": ["여름 주방에서 벌이는 냉침 실험", "주말에 직접 만드는 과일 우롱차, 나만의 비율 찾기", "새로운 티 카페에 가서 메뉴 속 베이스 차를 분석해 보기"],
            "en": ["A round of cold-brew experiments in a summer kitchen", "Mixing your own fruit oolong on the weekend, finding your ratio", "Visiting a new-style tea shop and decoding the tea bases on the menu"],
        },
        "teas": [
            {
                "name": {"zh": "冷泡白牡丹（白茶）", "ko": "냉침 백모란(백차)", "en": "Cold-brew White Peony (white tea)"},
                "note": {
                    "zh": "冷泡后清甜少苦涩，是入门冷泡最稳妥的选择。",
                    "ko": "냉침하면 쓴맛 없이 달콤해져, 냉침 입문에 가장 안전한 선택입니다.",
                    "en": "Sweet and smooth when cold-brewed, with almost no bitterness — the safest first cold brew.",
                },
            },
            {
                "name": {"zh": "桂花红茶", "ko": "계화 홍차", "en": "Osmanthus black tea"},
                "note": {
                    "zh": "桂花香与红茶的甜润自然融合，热泡冷泡两相宜。",
                    "ko": "은은한 계수나무꽃 향과 홍차의 단맛이 자연스럽게 어울려, 뜨겁게도 차갑게도 좋습니다.",
                    "en": "Osmanthus blossoms melt naturally into the black tea's sweetness — lovely hot or cold.",
                },
            },
            {
                "name": {"zh": "蜜桃风味乌龙", "ko": "복숭아향 우롱차", "en": "Peach oolong"},
                "note": {
                    "zh": "果香与焙火香的轻盈搭配，自制时桃片一点点就够。",
                    "ko": "과일 향과 로스팅 향의 가벼운 만남. 직접 만들 때는 복숭아 조각을 조금만 넣어도 충분합니다.",
                    "en": "A light pairing of fruit and roasted notes — when making your own, a few peach slices are plenty.",
                },
            },
            {
                "name": {"zh": "气泡冷萃乌龙", "ko": "스파클링 콜드브루 우롱", "en": "Sparkling cold-brew oolong"},
                "note": {
                    "zh": "冷泡乌龙兑入无糖气泡水，清爽有层次，在家就能做。",
                    "ko": "냉침 우롱에 무가당 탄산수를 섞으면 집에서도 청량하고 입체적인 음료가 완성됩니다.",
                    "en": "Cold-brew oolong topped with unsweetened sparkling water — refreshing and layered, easy to make at home.",
                },
            },
        ],
        "tips": {
            "zh": [
                "冷泡选发酵轻、苦涩低的茶（白茶、清香乌龙），成功率最高。",
                "水果和香料只做点缀，少量即可，别盖过茶本身的味道。",
                "给成功的配方记一行小抄：茶、比例、时间——下次复刻不翻车。",
            ],
            "ko": [
                "냉침에는 백차나 청향 우롱처럼 가볍게 발효돼 쓴맛이 적은 차가 성공률이 높습니다.",
                "과일과 향신료는 포인트만. 조금만 넣어 차 자체의 맛을 가리지 않게 하세요.",
                "성공한 레시피는 차, 비율, 시간을 한 줄로 메모해 두세요. 다음에 그대로 재현할 수 있습니다.",
            ],
            "en": [
                "For cold brew, pick lightly oxidized, low-bitterness teas (white teas, light oolongs) — highest success rate.",
                "Fruit and spices are accents only; use a light hand so they never cover the tea itself.",
                "Jot down winning recipes — tea, ratio, time — so you can repeat them without guesswork.",
            ],
        },
        "teaware": {
            "name": {"zh": "冷泡瓶或透明冷萃壶", "ko": "냉침 보틀 또는 투명 콜드브루 용기", "en": "A cold-brew bottle or a clear cold-brew pitcher"},
            "note": {
                "zh": "透明的瓶身能看见茶叶慢慢舒展，本身就是一道风景。",
                "ko": "투명한 병 안에서 찻잎이 서서히 펼쳐지는 모습이 그 자체로 하나의 풍경입니다.",
                "en": "Watching the leaves slowly open through the clear bottle is part of the pleasure.",
            },
        },
        "space": {
            "zh": "留一块小小的「实验角」：几只瓶罐、不同茶样、一本配方笔记，创意需要随手可得的材料。",
            "ko": "작은 '실험 코너'를 마련해 보세요. 병 몇 개, 다양한 차 샘플, 레시피 노트 — 창의력은 손에 잡히는 재료에서 자랍니다.",
            "en": "Keep a small “lab corner”: a few bottles, different tea samples, and a recipe notebook — creativity grows when materials are within reach.",
        },
        "try_other": {
            "id": "pure_taste",
            "sentence": {
                "zh": "实验间隙，用清水泡一杯什么都不加的好茶——重新校准味觉，会让你的创意更有分寸。",
                "ko": "실험 사이사이, 아무것도 넣지 않은 좋은 차를 한 잔 우려 보세요. 미각을 다시 맞추면 창의력에도 절제가 생깁니다.",
                "en": "Between experiments, brew a cup of good tea with nothing added — recalibrating your palate gives your creativity better judgment.",
            },
        },
        "combo_main": {
            "zh": "把传统茶当作可以不断再创作的素材",
            "ko": "전통차를 계속 다시 창작할 수 있는 재료로 바라보는 시선",
            "en": "treating traditional tea as material that can be endlessly reimagined",
        },
        "combo_tip": {
            "zh": "大胆尝试，但让茶味始终是主角，糖与配料只做配角",
            "ko": "과감하게 시도하되, 차의 맛이 언제나 주연이고 당분과 재료는 조연으로 두세요",
            "en": "experiment boldly, but keep the tea as the star — sugar and extras stay in supporting roles",
        },
    },
    # ------------------------------------------------ 仪式美学派
    "ritual_aesthete": {
        "name": {"zh": "仪式美学派", "ko": "의식 미학파", "en": "Ritual Aesthete"},
        "tagline": {
            "zh": "慢一点，茶会告诉你答案。",
            "ko": "조금 천천히, 차가 답을 알려 줄 것입니다.",
            "en": "Slow down — the tea will tell you the answer.",
        },
        "desc": {
            "zh": "你享受泡茶的一整套节奏：温杯、投茶、注水、出汤，每一步都不慌张。器物的手感、茶汤的颜色、桌面的布置、窗外的季节，都是你喝茶体验的一部分。这种仪式感并非为了繁复而繁复，而是让自己慢下来的一种方式——当动作慢下来，心也就静下来了。你也不需要昂贵的茶具，一件顺手的器物、一方干净的桌面、一枝应季的植物，就足以安放一个下午。美不在价格里，在专注里。",
            "ko": "당신은 차를 우리는 일련의 리듬을 즐깁니다. 잔을 데우고, 찻잎을 넣고, 물을 붓고, 따라 내는 모든 걸음에 서두름이 없습니다. 다구의 손맛, 찻물의 색, 테이블의 정돈, 창밖의 계절까지 모두 당신의 티타임을 구성하는 요소입니다. 이런 의식감은 복잡함을 위한 복잡함이 아니라, 스스로 느려지는 방법입니다. 손끝이 느려지면 마음도 고요해집니다. 비싼 다구는 필요 없습니다. 손에 익은 그릇 하나, 깨끗한 탁자, 계절을 담은 식물 한 가지면 오후 하나를 온전히 품을 수 있습니다. 아름다움은 가격이 아니라 집중에 있습니다.",
            "en": "You enjoy the whole rhythm of making tea: warming the cup, adding the leaves, pouring the water, decanting — no step is rushed. The feel of the teaware, the color of the liquor, the arrangement of the table, the season outside the window — all of it is part of your tea experience. This sense of ritual is not complexity for its own sake; it is a way of slowing yourself down. When the hands slow, the mind settles. You don't need expensive teaware either: one comfortable vessel, a clean table, and a sprig of something seasonal are enough to hold an entire afternoon. Beauty lies not in price, but in attention.",
        },
        "scenes": {
            "zh": ["周末午后，为自己设一席完整的茶", "换季时，重新调整茶具与桌面布置", "雨天独酌，一泡岩茶喝到尾水"],
            "ko": ["주말 오후, 나를 위해 완성된 찻자리를 마련하는 시간", "계절이 바뀔 때마다 다구와 테이블을 새로이 정돈하기", "비 오는 날 홀로, 암차 한 잔을 마지막 물까지 음미하기"],
            "en": ["A full personal tea session on a weekend afternoon", "Rearranging teaware and table settings as the seasons change", "A rainy-day solo session, sipping a rock tea down to its last steep"],
        },
        "teas": [
            {
                "name": {"zh": "武夷岩茶（乌龙茶）", "ko": "무이암차(우롱차)", "en": "Wuyi rock tea (oolong)"},
                "note": {
                    "zh": "多泡之间层次递进，火香与花香交替出现，最耐细品。",
                    "ko": "우릴수록 결이 달라지며 로스팅 향과 꽃향이 번갈아 나타나, 음미하기에 가장 좋은 차 중 하나입니다.",
                    "en": "Layers unfold across many steeps, roasted and floral notes taking turns — a tea that rewards slow attention.",
                },
            },
            {
                "name": {"zh": "普洱生茶", "ko": "푸얼 생차", "en": "Raw Pu'er"},
                "note": {
                    "zh": "每一泡都有变化，从清冽到醇厚，一场茶能喝出一段旅程。",
                    "ko": "우릴 때마다 맑고 날카로운 맛에서 깊은 맛으로 변해, 한 번의 찻자리가 하나의 여정처럼 느껴집니다.",
                    "en": "Every steep changes, from bright and brisk to deep and mellow — one session feels like a journey.",
                },
            },
            {
                "name": {"zh": "白毫银针（白茶）", "ko": "바이하오인전(백차)", "en": "Silver Needle (white tea)"},
                "note": {
                    "zh": "芽形优美，立于水中如林，可观可品，视觉也是茶席的一部分。",
                    "ko": "가늘고 고운 싹이 물속에 숲처럼 서 있어 눈으로도 즐길 수 있습니다. 보는 즐거움도 찻자리의 일부입니다.",
                    "en": "Slender buds stand in the water like a tiny forest — a pleasure for the eyes as much as the palate.",
                },
            },
            {
                "name": {"zh": "炭焙乌龙", "ko": "숯 로스팅 우롱차", "en": "Charcoal-roasted oolong"},
                "note": {
                    "zh": "焙火香沉稳，余韵悠长，适合节奏缓慢的一席茶。",
                    "ko": "차분한 로스팅 향과 긴 여운이 있어, 느린 리듬의 찻자리에 잘 어울립니다.",
                    "en": "Deep roasted aroma with a long finish — ideal for an unhurried tea session.",
                },
            },
        ],
        "tips": {
            "zh": [
                "温杯之后再投茶，趁热闻干茶香，是一席茶最好的开场。",
                "每一泡出汤后看一眼汤色、闻一下杯底香，变化都藏在细节里。",
                "注水放慢一点，感受水流的节奏——手稳了，心就静了。",
            ],
            "ko": [
                "잔을 데운 뒤 찻잎을 넣고, 남은 열기로 마른잎의 향을 맡아 보세요. 찻자리의 가장 좋은 시작입니다.",
                "우려 낼 때마다 찻물 색을 보고 잔바닥 향을 맡아 보세요. 변화는 디테일에 숨어 있습니다.",
                "물을 부을 때 조금 천천히, 물줄기의 리듬을 느껴 보세요. 손이 안정되면 마음도 고요해집니다.",
            ],
            "en": [
                "After warming the cup, add the leaves and smell their dry aroma in the rising heat — the best opening of a session.",
                "After each steep, glance at the liquor and smell the empty cup — the changes hide in the details.",
                "Pour a little slower and feel the rhythm of the water — steady hands quiet the mind.",
            ],
        },
        "teaware": {
            "name": {"zh": "一套顺手的盖碗或小品茗杯", "ko": "손에 익은 개완 또는 작은 찻잔 세트", "en": "A comfortable gaiwan or a set of small tasting cups"},
            "note": {
                "zh": "不必名贵，趁手最重要——器物越顺手，动作越从容。",
                "ko": "비쌀 필요는 없습니다. 손에 익는 것이 가장 중요합니다. 그릇이 편해야 동작도 여유로워집니다.",
                "en": "It doesn't need to be precious — comfort in hand matters most. The easier the vessel, the calmer the movements.",
            },
        },
        "space": {
            "zh": "随季节更换一块桌布、添一枝应季植物；茶席不必大，一方角落就能装下四季。",
            "ko": "계절에 따라 테이블보를 바꾸고 제철 식물 한 가지를 곁들여 보세요. 찻자리는 크지 않아도, 작은 코너 하나에 사계절이 담깁니다.",
            "en": "Change a table cloth with the seasons and add one seasonal sprig — a tea setting doesn't need to be large; a small corner can hold all four seasons.",
        },
        "try_other": {
            "id": "easy_daily",
            "sentence": {
                "zh": "忙的日子里，允许自己用马克杯随便泡一杯——仪式感是滋养，不是任务；松弛也是茶席的一部分。",
                "ko": "바쁜 날에는 머그컵에 대충 우린 한 잔도 허락해 보세요. 의식감은 과제가 아니라 자양분이며, 느슨함도 찻자리의 일부입니다.",
                "en": "On busy days, allow yourself a carelessly brewed mug — ritual is nourishment, not homework; looseness is part of the tea table too.",
            },
        },
        "combo_main": {
            "zh": "在温杯注水之间，把日常泡成值得慢下来的时刻",
            "ko": "잔을 데우고 물을 붓는 사이, 일상을 느려질 가치가 있는 순간으로 만드는 방식",
            "en": "turning everyday moments into ones worth slowing down for, between warming the cup and pouring the water",
        },
        "combo_tip": {
            "zh": "保持你的节奏感，也记得仪式是为自己服务，而不是反过来",
            "ko": "당신만의 리듬을 지키되, 의식이 당신을 위해 존재하는 것이지 그 반대가 아님을 기억하세요",
            "en": "keep your sense of rhythm, and remember the ritual serves you — never the other way around",
        },
    },
}


# ============================================================
# 6) 组合建议模板：主风格 × 辅助风格
#    从预编写的三语模板与风格短句生成，不做生硬拼接
# ============================================================
COMBO_TEMPLATES = {
    "zh": "你的茶生活可以以「{p_name}」为主线——{p_main}；再借一点「{s_name}」的灵感——{s_tip}。两种风格没有高下之分，也不构成固定标签，完全可以随心情和场景自由切换。",
    "ko": "당신의 차 생활은 '{p_name}' 스타일을 큰 줄기로 삼아 보세요. {p_main}. 여기에 '{s_name}' 스타일의 영감을 살짝 더하면 좋습니다. {s_tip}. 두 스타일에는 우열이 없고 고정된 이름표도 아니니, 기분과 상황에 따라 자유롭게 오가면 됩니다.",
    "en": "Let “{p_name}” be the main thread of your tea life — {p_main}. Then borrow a little inspiration from “{s_name}” — {s_tip}. Neither style ranks above the other, and neither is a fixed label; feel free to move between them with your mood and the occasion.",
}


# ============================================================
# 7) 数据校验与计分逻辑
# ============================================================
def validate_data():
    """启动时校验题目与风格数据的完整性，避免静默出错。"""
    assert len(QUESTIONS) == 10, "题目数量必须为 10"
    ids = [q["id"] for q in QUESTIONS]
    assert len(set(ids)) == len(ids), "题目 ID 必须唯一"

    axis_count = {"frequency": 0, "willingness": 0, "agreement": 0, "preference": 0}
    related_styles = set()
    for q in QUESTIONS:
        axis_count[q["axis"]] += 1
        n = q["levels"]
        # 权重数组长度必须与实际刻度数量一致
        assert len(q["w_primary"]) == n and len(q["w_secondary"]) == n, f"{q['id']} 权重长度与刻度数量不一致"
        assert len(q["labels"]["zh"]) == n and len(q["labels"]["ko"]) == n and len(q["labels"]["en"]) == n
        # 同一道题的主要与辅助关联风格必须不同
        assert q["primary"] != q["secondary"], f"{q['id']} 主要与辅助风格相同"
        assert q["primary"] in STYLES and q["secondary"] in STYLES
        related_styles.add(q["primary"])
        related_styles.add(q["secondary"])
    # 四种题型数量符合设计：频率 2 / 意愿 2 / 符合 2 / 双端偏好 4
    assert axis_count == {"frequency": 2, "willingness": 2, "agreement": 2, "preference": 4}
    # 六种风格都至少与一道题相关
    for s in STYLE_ORDER:
        assert s in related_styles, f"风格 {s} 未与任何题目关联"
        assert STYLES[s]["try_other"]["id"] in STYLES


validate_data()


def compute_result(answers):
    """
    根据 10 道题的答案索引（0 起）计分。
    返回：raw 原始分、max 理论最高分、norm 标准化分、primary/secondary 风格 ID。

    规则：
    1) 每题按权重数组同时给主要、辅助关联风格加分（两者不同，不会重复计入同一风格）；
    2) 各风格理论最高分不同，先标准化（实际分 ÷ 理论最高分）再排序；
       若某风格理论最高分为 0，标准化分记为 0，避免除零错误；
    3) 同分时先比较第 5、10 题两道核心情境题中的实际得分，
       仍相同则按固定风格顺序 STYLE_ORDER 稳定处理。
    """
    raw = {s: 0 for s in STYLE_ORDER}
    core = {s: 0 for s in STYLE_ORDER}  # 核心情境题（q5、q10）上的实际得分，用于同分比较
    for q, ans in zip(QUESTIONS, answers):
        raw[q["primary"]] += q["w_primary"][ans]
        raw[q["secondary"]] += q["w_secondary"][ans]
        if q["id"] in CORE_QUESTION_IDS:
            core[q["primary"]] += q["w_primary"][ans]
            core[q["secondary"]] += q["w_secondary"][ans]

    # 由权重数据动态推导各风格理论最高分，保证与题目数据始终一致
    maxscore = {s: 0 for s in STYLE_ORDER}
    for q in QUESTIONS:
        maxscore[q["primary"]] += max(q["w_primary"])
        maxscore[q["secondary"]] += max(q["w_secondary"])

    norm = {s: (raw[s] / maxscore[s] if maxscore[s] > 0 else 0.0) for s in STYLE_ORDER}

    ranked = sorted(
        STYLE_ORDER,
        key=lambda s: (-norm[s], -core[s], STYLE_ORDER.index(s)),
    )
    return {
        "raw": raw,
        "max": maxscore,
        "norm": norm,
        "primary": ranked[0],
        "secondary": ranked[1],
    }


# ============================================================
# 8) 页面渲染
# ============================================================
def lang_selector():
    """语言选择器：切换只改变显示文案，不影响登录、答案与结果。"""
    st.selectbox(
        t("lang_label"),
        options=LANG_OPTIONS,
        format_func=lambda x: LANG_NAMES[x],
        key="lang",
    )


def do_logout():
    """退出登录：清除登录状态、开始标记、全部选择轴答案与测试结果，返回登录页。"""
    for key in ["authed", "started", "result", "saved_answers"]:
        st.session_state.pop(key, None)
    for q in QUESTIONS:
        st.session_state.pop(f"ans_{q['id']}", None)
    st.session_state.authed = False
    st.session_state.started = False
    st.session_state.result = None
    # 语言保留，不强制用户重新选择


def page_login():
    """登录页：居中窄卡片 + 盖碗线稿 + 语言选择 + 访问码输入。"""
    st.markdown(LEAF_SPRIG_SVG, unsafe_allow_html=True)
    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            f"<div class='tea-card' style='text-align:center'>"
            f"<div class='tea-band'></div>"
            f"<div style='display:flex;justify-content:center'>{GAIWAN_SVG}</div>"
            f"<h2 style='margin-bottom:2px'>{t('app_title')}</h2>"
            f"<p class='tagline'>{t('app_subtitle')}</p>"
            f"<p class='muted'>{t('tagline')}</p>"
            f"<p style='text-align:left'>{t('login_intro')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )
        lang_selector()
        with st.form("login_form"):
            code = st.text_input(
                t("access_code_label"),
                type="password",  # 密码输入框，输入内容默认不可见
                placeholder=t("access_code_placeholder"),
                key="access_input",
            )
            submitted = st.form_submit_button(t("login_button"), use_container_width=True)
        if submitted:
            cleaned = code.strip()  # 去除首尾空格后精确匹配
            if not cleaned:
                st.warning(t("err_empty"))
            elif cleaned != ACCESS_CODE:
                st.error(t("err_wrong"))
            else:
                # 验证成功：登录状态写入 session_state，进入测试介绍页
                st.session_state.authed = True
                st.rerun()
    render_footer()


def page_intro():
    """测试介绍页：页首装饰带 + 形式说明 + 风格预览 + 计分说明 + 开始按钮。"""
    st.markdown(LEAF_SPRIG_SVG, unsafe_allow_html=True)
    col_art, col_title = st.columns([1, 4])
    with col_art:
        st.markdown(GAIWAN_SVG, unsafe_allow_html=True)
    with col_title:
        st.title(t("app_title"))
        st.markdown(f"<p class='tagline'>{t('tagline')}</p>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='tea-card'><div class='tea-band'></div>"
        f"<h3>{t('intro_title')}</h3><p>{t('intro_body')}</p>"
        f"<p class='muted'>{t('intro_meta')}</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='tea-card'><h3>{t('intro_format_title')}</h3><p>{t('intro_format')}</p></div>",
        unsafe_allow_html=True,
    )

    # 六种风格简短预览（仅名称与标签句，不代表排名）
    st.markdown(f"### {t('style_preview_title')}")
    for i in range(0, len(STYLE_ORDER), 2):
        cols = st.columns(2)
        for col, sid in zip(cols, STYLE_ORDER[i : i + 2]):
            s = STYLES[sid]
            col.markdown(
                f"<div class='tea-card' style='margin-bottom:10px'>"
                f"<div style='display:flex;align-items:center;gap:10px'>"
                f"{STYLE_ICONS[sid]}<b>{s['name'][st.session_state.lang]}</b></div>"
                f"<p class='tagline' style='margin-top:8px'>{s['tagline'][st.session_state.lang]}</p>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown(
        f"<div class='tea-card'><h3>{t('intro_scoring_title')}</h3><p>{t('intro_scoring')}</p></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='tea-card'><h3>{t('intro_note_title')}</h3><p>{t('intro_note')}</p></div>",
        unsafe_allow_html=True,
    )

    if st.button(t("start_button"), type="primary", use_container_width=True):
        st.session_state.started = True
        st.rerun()
    st.markdown(MOUNTAINS_SVG, unsafe_allow_html=True)
    render_footer()


def _save_answer(qid):
    """选项变更回调：把本次点选（0 起整数索引）立即持久化到 saved_answers。"""
    st.session_state.saved_answers[qid] = st.session_state[f"ans_{qid}"]


def page_quiz():
    """问卷页：每道题一组并列选项（segmented_control），未作答前不预选任何项。

    设计说明：
    - 不再使用 st.form。每次点选都通过 on_change 立即写入 saved_answers（0 起整数索引），
      因此切换语言、重新运行或从结果页返回时，选中项始终从已提交的状态恢复；
    - 实测：该控件在选项文字随语言变化时，已提交的选中项仍能正确恢复；
    - 答案索引与语言无关，切换语言只改变显示文案。
    """
    lang = st.session_state.lang
    st.session_state.setdefault("saved_answers", {})
    saved = st.session_state.saved_answers
    # 若控件状态丢失（如从结果页返回时控件未渲染），按已保存的答案预置
    for q in QUESTIONS:
        key = f"ans_{q['id']}"
        if q["id"] in saved and key not in st.session_state:
            st.session_state[key] = saved[q["id"]]
    st.title(t("quiz_title"))
    st.markdown(f"<p class='muted'>{t('quiz_total')}</p>", unsafe_allow_html=True)
    st.info(t("quiz_hint"))

    for idx, q in enumerate(QUESTIONS):
        st.markdown(
            f"**{t('quiz_progress_label').format(n=idx + 1)} · {q['stem'][lang]}**"
        )
        # 左右端点完整展示；手机端每题仅堆放左右两个短标签
        c_left, c_right = st.columns(2)
        with c_left:
            st.caption("← " + q["left"][lang])
        with c_right:
            st.markdown(
                f"<div style='text-align:right' class='muted'>{q['right'][lang]} →</div>",
                unsafe_allow_html=True,
            )
        # 并列选项：值为 0 起的整数索引；default=None 表示未作答前不预选任何项
        st.segmented_control(
            label=q["stem"][lang],
            options=list(range(q["levels"])),
            format_func=lambda i, q=q: q["labels"][lang][i],
            key=f"ans_{q['id']}",
            default=None,
            on_change=_save_answer,
            args=(q["id"],),
            label_visibility="collapsed",
        )
        st.caption(q["mid"][lang])
        st.divider()

    if st.button(t("submit_button"), type="primary", use_container_width=True):
        # 提交前检查是否全部作答，未完成的题目给出明确提示
        missing = [i + 1 for i, q in enumerate(QUESTIONS) if saved.get(q["id"]) is None]
        if missing:
            nums = "、".join(str(n) for n in missing) if lang == "zh" else ", ".join(str(n) for n in missing)
            st.warning(t("quiz_unanswered").format(n=len(missing), nums=nums))
        else:
            answers = [saved[q["id"]] for q in QUESTIONS]
            st.session_state.result = compute_result(answers)
            st.rerun()
    render_footer()


def render_style_card(sid, band_class, label):
    """结果页风格卡片：顶部色带 + 线性图标 + 完整介绍内容。"""
    lang = st.session_state.lang
    s = STYLES[sid]
    st.markdown(
        f"<div class='tea-card'><div class='{band_class}'></div>"
        f"<div style='display:flex;align-items:center;gap:12px'>"
        f"{STYLE_ICONS[sid]}"
        f"<div><span class='muted'>{label}</span>"
        f"<h3 style='margin:0'>{s['name'][lang]}</h3></div></div>"
        f"<p class='tagline' style='margin-top:10px'>{s['tagline'][lang]}</p>"
        f"<p>{s['desc'][lang]}</p></div>",
        unsafe_allow_html=True,
    )


def render_style_details(sid):
    """场景 / 茶品 / 冲泡建议 / 茶具 / 空间 / 可尝试风格的展示。"""
    lang = st.session_state.lang
    s = STYLES[sid]

    st.markdown(f"#### {t('scenes_title')}")
    for scene in s["scenes"][lang]:
        st.markdown(f"- {scene}")

    st.markdown(f"#### {t('teas_title')}")
    cols = st.columns(2)
    for i, tea in enumerate(s["teas"]):
        with cols[i % 2]:
            st.markdown(
                f"<div class='tea-card' style='padding:14px 16px;margin-bottom:10px'>"
                f"<b>{tea['name'][lang]}</b>"
                f"<p class='muted' style='margin:4px 0 0 0'>{tea['note'][lang]}</p></div>",
                unsafe_allow_html=True,
            )

    st.markdown(f"#### {t('tips_title')}")
    for tip in s["tips"][lang]:
        st.markdown(f"- {tip}")

    st.markdown(f"#### {t('teaware_title')}")
    st.markdown(f"**{s['teaware']['name'][lang]}** — {s['teaware']['note'][lang]}")

    st.markdown(f"#### {t('space_title')}")
    st.markdown(s["space"][lang])

    st.markdown(f"#### {t('try_title')}")
    other = STYLES[s["try_other"]["id"]]
    st.markdown(f"**{other['name'][lang]}** — {s['try_other']['sentence'][lang]}")


def page_result():
    """结果页：主风格 → 辅助风格 → 六维分布 → 完整介绍 → 组合建议。"""
    lang = st.session_state.lang
    result = st.session_state.result
    p_id, s_id = result["primary"], result["secondary"]

    st.title(t("result_title"))

    # 主要风格（浅茶绿顶部色带）
    render_style_card(p_id, "tea-band", t("primary_label"))
    # 辅助风格（淡茶色顶部色带）+ 补充说明
    render_style_card(s_id, "tea-band-secondary", t("secondary_label"))
    st.info(t("secondary_intro").format(name=STYLES[s_id]["name"][lang]))

    # 六维相对得分分布：进度条展示标准化结果，并附非专业测量说明
    st.markdown(f"### {t('dist_title')}")
    for sid in STYLE_ORDER:
        cols = st.columns([2, 5])
        with cols[0]:
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:8px'>"
                f"{STYLE_ICONS[sid]}<span>{STYLES[sid]['name'][lang]}</span></div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            st.progress(min(max(result["norm"][sid], 0.0), 1.0))
    st.caption(t("dist_note"))

    st.divider()

    # 主要风格完整介绍
    render_style_details(p_id)

    st.divider()

    # 辅助风格带来的补充特点（不覆盖主风格完整内容）
    st.markdown(f"### {t('secondary_label')} · {STYLES[s_id]['name'][lang]}")
    s = STYLES[s_id]
    st.markdown(f"*{s['tagline'][lang]}*")
    st.markdown(f"#### {t('tips_title')}")
    for tip in s["tips"][lang][:2]:
        st.markdown(f"- {tip}")
    st.markdown(f"**{t('teaware_title')}** — {s['teaware']['name'][lang]}")

    # 主风格 × 辅助风格组合建议（预编写模板生成）
    st.markdown(f"### {t('combo_title')}")
    st.markdown(
        f"<div class='tea-card'><div class='tea-band'></div><p>"
        + COMBO_TEMPLATES[lang].format(
            p_name=STYLES[p_id]["name"][lang],
            p_main=STYLES[p_id]["combo_main"][lang],
            s_name=STYLES[s_id]["name"][lang],
            s_tip=STYLES[s_id]["combo_tip"][lang],
        )
        + "</p></div>",
        unsafe_allow_html=True,
    )

    st.divider()
    # 返回修改答案：保留轴位置，仅清除结果
    if st.button(t("edit_answers_button")):
        st.session_state.result = None
        st.rerun()
    # 重新测试：清除所有答案（回到未作答状态）与结果，保留语言与登录
    if st.button(t("retake_button"), type="primary"):
        for q in QUESTIONS:
            st.session_state.pop(f"ans_{q['id']}", None)
        st.session_state.saved_answers = {}
        st.session_state.result = None
        st.session_state.started = True
        st.rerun()
    st.caption(t("result_restart_hint"))

    st.markdown(MOUNTAINS_SVG, unsafe_allow_html=True)
    render_footer()


def render_footer():
    """页脚免责声明：按当前语言显示。"""
    st.markdown(
        f"<hr style='border:none;border-top:1px solid #E4E9E0;margin-top:36px'>"
        f"<p class='muted' style='text-align:center;font-size:0.85rem'>"
        f"{t('footer_disclaimer')}</p>",
        unsafe_allow_html=True,
    )


# ============================================================
# 9) 主流程路由：登录 → 介绍 → 问卷 → 结果
# ============================================================
if not st.session_state.authed:
    # 未通过验证前，无法查看测试介绍、问卷及结果
    page_login()
else:
    with st.sidebar:
        lang_selector()
        st.divider()
        st.button(t("logout"), on_click=do_logout, use_container_width=True)
    if st.session_state.result is not None:
        page_result()
    elif st.session_state.started:
        page_quiz()
    else:
        page_intro()
