"""
用戶體驗問卷模組
"""
import json
import os
from datetime import datetime
import streamlit as st


QUESTIONS = [
    {
        "key": "overall",
        "label": "整體使用體驗",
        "type": "stars",
    },
    {
        "key": "most_useful",
        "label": "你覺得最有用的功能是？",
        "type": "multiselect",
        "options": [
            "搜尋爆款影片",
            "逐字稿取得",
            "翻譯功能",
            "爆款原因分析",
            "鉤子模板生成",
            "影片重現指南",
            "無臉頻道工作坊",
            "30天內容日曆",
            "A/B 標題測試",
        ],
    },
    {
        "key": "missing",
        "label": "你最希望加入什麼功能？",
        "type": "text",
        "placeholder": "例如：自動發布、競爭對手追蹤…",
    },
    {
        "key": "recommend",
        "label": "你會推薦給其他創作者嗎？",
        "type": "radio",
        "options": ["一定會 🔥", "可能會", "不確定", "不會"],
    },
    {
        "key": "comment",
        "label": "其他意見或建議",
        "type": "text",
        "placeholder": "任何想說的都可以留在這裡",
    },
]


def render_survey():
    """顯示問卷，回傳填寫完的回應 dict 或 None"""

    if st.session_state.get("survey_submitted"):
        st.success("🙏 謝謝你的回饋！你的意見會讓這個工具變得更好。")
        if st.button("再填一次", key="survey_refill"):
            st.session_state["survey_submitted"] = False
            st.rerun()
        return None

    with st.form("user_survey", clear_on_submit=True):
        st.markdown("### 💬 使用體驗問卷")
        st.caption("只需要 1 分鐘，幫助我們把工具做得更好")

        responses = {}

        for q in QUESTIONS:
            st.markdown(f"**{q['label']}**")

            if q["type"] == "stars":
                val = st.select_slider(
                    q["label"],
                    options=["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
                    value="⭐⭐⭐⭐",
                    label_visibility="collapsed",
                    key=f"survey_{q['key']}",
                )
                responses[q["key"]] = len(val)  # 星星數量

            elif q["type"] == "multiselect":
                val = st.multiselect(
                    q["label"],
                    options=q["options"],
                    label_visibility="collapsed",
                    key=f"survey_{q['key']}",
                )
                responses[q["key"]] = val

            elif q["type"] == "radio":
                val = st.radio(
                    q["label"],
                    options=q["options"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key=f"survey_{q['key']}",
                )
                responses[q["key"]] = val

            elif q["type"] == "text":
                val = st.text_area(
                    q["label"],
                    placeholder=q.get("placeholder", ""),
                    height=80,
                    label_visibility="collapsed",
                    key=f"survey_{q['key']}",
                )
                responses[q["key"]] = val

            st.markdown("")

        submitted = st.form_submit_button("📤 送出回饋", type="primary", use_container_width=True)

        if submitted:
            responses["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            _save_response(responses)
            st.session_state["survey_submitted"] = True
            st.rerun()

    return None


def _save_response(response: dict):
    """存入 session state 的回應列表"""
    if "survey_responses" not in st.session_state:
        st.session_state["survey_responses"] = []
    st.session_state["survey_responses"].append(response)


def get_all_responses() -> list[dict]:
    return st.session_state.get("survey_responses", [])


def render_admin_dashboard():
    """管理員查看問卷結果（側邊欄或隱藏頁面）"""
    responses = get_all_responses()
    if not responses:
        st.info("還沒有問卷回應")
        return

    st.markdown(f"### 📊 問卷結果（共 {len(responses)} 份）")

    # 平均評分
    stars = [r.get("overall", 0) for r in responses if r.get("overall")]
    if stars:
        avg = sum(stars) / len(stars)
        st.metric("⭐ 平均評分", f"{avg:.1f} / 5")

    # 推薦意願
    from collections import Counter
    rec = Counter(r.get("recommend", "") for r in responses)
    st.markdown("**推薦意願分佈：**")
    for k, v in rec.most_common():
        if k:
            st.markdown(f"- {k}：{v} 人")

    # 最受歡迎功能
    all_features = []
    for r in responses:
        all_features.extend(r.get("most_useful", []))
    if all_features:
        feat_count = Counter(all_features)
        st.markdown("**最受歡迎功能：**")
        for feat, count in feat_count.most_common(5):
            st.markdown(f"- {feat}：{count} 票")

    # 下載完整資料
    json_data = json.dumps(responses, ensure_ascii=False, indent=2)
    st.download_button(
        "⬇ 下載完整問卷資料（JSON）",
        json_data,
        file_name=f"survey_results_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        use_container_width=True,
    )
