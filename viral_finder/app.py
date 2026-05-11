import os
import sys
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from search import search_videos, format_count, format_duration, format_date, PLATFORMS
from analyzer import get_video_info, get_transcript, download_audio, transcribe_with_whisper
from translator import translate_text, LANGUAGES
from templates import analyze_and_generate_templates, generate_custom_hook
from recreate import generate_recreation_guide


# ── 共用：翻譯區塊 ──────────────────────────────────────────────────────────

def _render_translation(text: str, target_lang: str):
    st.markdown("### 🌐 翻譯")
    if st.button(f"翻譯為「{target_lang}」", type="primary", use_container_width=True):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("請先在左側欄輸入 Anthropic API Key")
        else:
            with st.spinner(f"正在翻譯為 {target_lang}…"):
                try:
                    result = translate_text(text, target_lang)
                    st.text_area(f"翻譯結果（{target_lang}）", result, height=320)
                    fname = f"translation_{target_lang.replace(' ', '_')}.txt"
                    st.download_button(
                        "⬇ 下載翻譯文字",
                        result,
                        file_name=fname,
                        mime="text/plain",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"翻譯失敗：{e}")

# ── 頁面設定 ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="爆款影片獵手",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
/* 卡片 */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px;
}
.tag {
    display: inline-block;
    background: #FF4B4B;
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 20px;
    margin-bottom: 4px;
}
.views-big {
    font-size: 1.3rem;
    font-weight: 800;
    color: #FF4B4B;
}
.transcript-scroll {
    max-height: 380px;
    overflow-y: auto;
    font-size: 0.92rem;
    line-height: 1.75;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 14px 18px;
    background: #0e1117;
    white-space: pre-wrap;
}
</style>
""", unsafe_allow_html=True)

# ── 側邊欄 ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🎯 爆款影片獵手")
    st.caption("搜尋各平台爆款 · 逐字稿 · 翻譯")
    st.divider()

    st.markdown("#### ⚙️ 設定")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        placeholder="sk-ant-...",
        help="翻譯功能需要此 Key，可在 console.anthropic.com 免費申請",
    )
    if api_key:
        os.environ["ANTHROPIC_API_KEY"] = api_key

    st.divider()
    st.markdown("#### 📸 Instagram 設定")
    ig_session = st.text_input(
        "Instagram Session ID",
        type="password",
        placeholder="貼上 sessionid cookie 值",
        help="Instagram 需要登入才能抓取。在瀏覽器開發者工具 → Application → Cookies → sessionid",
        key="ig_session",
    )

    whisper_model = st.selectbox(
        "Whisper 模型大小",
        ["tiny", "base", "small", "medium"],
        index=1,
        help="模型越大越準確，但需要更多時間與記憶體",
    )

    st.divider()
    st.markdown("**📱 支援平台**")
    st.markdown("- YouTube / Shorts")
    st.markdown("- Bilibili")
    st.markdown("- TikTok（分析連結）")
    st.markdown("- Instagram Reels（分析連結）")
    st.markdown("- Twitter / X（分析連結）")

    st.divider()
    st.markdown("**📌 使用流程**")
    st.markdown("1. **搜尋** 關鍵字找爆款")
    st.markdown("2. **分析** 貼連結取逐字稿")
    st.markdown("3. **翻譯** 一鍵多國語言")
    st.markdown("4. **模板** 生成拍攝模板與鉤子")

# ── 主區域 Tab ──────────────────────────────────────────────────────────────

tab_search, tab_analyze, tab_template, tab_recreate = st.tabs([
    "🔍 搜尋爆款影片",
    "📊 分析影片連結",
    "🎬 模板生成器",
    "🎥 重現指南",
])

# ════════════════════════════════════════════════════════════
# TAB 1 · 搜尋爆款影片
# ════════════════════════════════════════════════════════════

with tab_search:
    c1, c2, c3, c4 = st.columns([3, 1.5, 1, 1])

    with c1:
        keyword = st.text_input(
            "關鍵字",
            placeholder="例如：AI 副業、韓國料理、健身教學…",
            label_visibility="collapsed",
        )
    with c2:
        platform = st.selectbox("平台", list(PLATFORMS.keys()), label_visibility="collapsed")
    with c3:
        max_results = st.selectbox("數量", [10, 20, 30], label_visibility="collapsed")
    with c4:
        search_btn = st.button("🔍 搜尋", use_container_width=True, type="primary")

    if search_btn:
        if not keyword.strip():
            st.warning("請輸入搜尋關鍵字")
        else:
            with st.spinner(f"正在搜尋 {platform} 的爆款影片…"):
                videos = search_videos(keyword.strip(), platform, max_results)

            if not videos:
                st.error("沒有找到影片，請換個關鍵字或平台試試")
            else:
                st.success(f"共找到 {len(videos)} 部影片，按觀看數排序 🔥")
                st.divider()

                cols_per_row = 3
                for row_start in range(0, len(videos), cols_per_row):
                    row = videos[row_start: row_start + cols_per_row]
                    cols = st.columns(cols_per_row)

                    for col, video in zip(cols, row):
                        with col:
                            with st.container(border=True):
                                if video["thumbnail"]:
                                    st.image(video["thumbnail"], use_container_width=True)

                                st.markdown(
                                    f"**{video['title'][:55]}{'…' if len(video['title']) > 55 else ''}**"
                                )
                                st.caption(f"📺 {video['channel']}")

                                m1, m2 = st.columns(2)
                                m1.metric("👁 觀看", format_count(video["view_count"]))
                                m2.metric("⏱ 時長", format_duration(video["duration"]))

                                date_str = format_date(video["upload_date"])
                                if date_str:
                                    st.caption(f"📅 {date_str}")

                                b1, b2 = st.columns(2)
                                with b1:
                                    st.link_button("▶ 觀看", video["url"], use_container_width=True)
                                with b2:
                                    if st.button(
                                        "📊 分析",
                                        key=f"go_{row_start}_{video['id']}",
                                        use_container_width=True,
                                    ):
                                        st.session_state["analyze_url"] = video["url"]
                                        st.session_state["auto_analyze"] = True
                                        st.info("請切換到「📊 分析影片連結」頁籤")

# ════════════════════════════════════════════════════════════
# TAB 2 · 分析影片連結
# ════════════════════════════════════════════════════════════

with tab_analyze:
    default_url = st.session_state.get("analyze_url", "")

    url_input = st.text_input(
        "影片連結",
        value=default_url,
        placeholder="貼上 YouTube / TikTok / Instagram / Bilibili / Twitter 連結…",
        label_visibility="collapsed",
    )

    col_btn, col_lang = st.columns([1, 1])
    with col_btn:
        analyze_btn = st.button("📊 分析影片", type="primary", use_container_width=True)
    with col_lang:
        target_lang = st.selectbox(
            "翻譯語言",
            list(LANGUAGES.keys()),
            label_visibility="collapsed",
        )

    if analyze_btn and url_input.strip():
        url = url_input.strip()

        # ── 影片基本資訊 ──
        ig_session = st.session_state.get("ig_session", "")
        with st.spinner("正在讀取影片資訊…"):
            info = get_video_info(url, ig_session)

        if "error" in info:
            st.error(f"無法讀取影片：{info['error']}")
            st.stop()

        st.divider()

        # 縮圖 + 基本數據
        col_img, col_meta = st.columns([1, 2])
        with col_img:
            if info["thumbnail"]:
                st.image(info["thumbnail"], use_container_width=True)
            st.link_button("▶ 觀看原影片", info["webpage_url"], use_container_width=True)

        with col_meta:
            st.markdown(f"## {info['title']}")
            channel_link = f"[{info['channel']}]({info['channel_url']})" if info["channel_url"] else info["channel"]
            st.markdown(f"📺 **頻道**：{channel_link}")

            if info["channel_follower_count"]:
                st.markdown(f"👥 **訂閱數**：{format_count(info['channel_follower_count'])}")

            date_str = format_date(info["upload_date"])
            if date_str:
                st.markdown(f"📅 **上傳日期**：{date_str}")

            st.markdown(f"🎬 **平台**：{info['platform']}")

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("👁 觀看", format_count(info["view_count"]))
            m2.metric("👍 按讚", format_count(info["like_count"]))
            m3.metric("💬 留言", format_count(info["comment_count"]))
            m4.metric("⏱ 時長", format_duration(info["duration"]))

            if info["description"]:
                with st.expander("📝 影片描述"):
                    desc = info["description"]
                    st.text(desc[:1500] + ("…" if len(desc) > 1500 else ""))

        st.divider()

        # ── 逐字稿區塊 ──
        st.markdown("### 📜 逐字稿")

        col_sub, col_whisper, col_audio = st.columns(3)
        with col_sub:
            get_sub_btn = st.button("📜 取得字幕逐字稿", use_container_width=True)
        with col_whisper:
            get_whisper_btn = st.button("🎙 Whisper 語音辨識", use_container_width=True,
                                        help="無字幕時使用，需先下載音頻")
        with col_audio:
            get_audio_btn = st.button("🎵 下載音頻 MP3", use_container_width=True,
                                      help="需要系統安裝 ffmpeg")

        # 字幕逐字稿
        if get_sub_btn:
            with st.spinner("正在取得字幕逐字稿…"):
                entries, lang = get_transcript(url, ig_session=ig_session)

            if not entries:
                st.warning("找不到字幕，可嘗試「Whisper 語音辨識」")
            else:
                full_text = " ".join(e["text"] for e in entries)
                st.success(f"字幕語言：{lang}　共 {len(entries)} 段")

                mode = st.radio("顯示模式", ["純文字", "時間軸"], horizontal=True)

                if mode == "純文字":
                    st.text_area("逐字稿內容", full_text, height=320)
                else:
                    lines = ""
                    for e in entries[:300]:
                        ts = format_duration(int(e["start"]))
                        lines += f"**[{ts}]** {e['text']}\n\n"
                    st.markdown(
                        f'<div class="transcript-scroll">{lines}</div>',
                        unsafe_allow_html=True,
                    )

                st.divider()
                _render_translation(full_text, target_lang)

        # Whisper 語音辨識
        if get_whisper_btn:
            with st.spinner("正在下載音頻（需要 ffmpeg）…"):
                try:
                    tmpdir = tempfile.mkdtemp()
                    audio_path = download_audio(url, tmpdir)
                except Exception as e:
                    st.error(f"音頻下載失敗：{e}\n\n請確認已安裝 ffmpeg：`sudo apt install ffmpeg`")
                    audio_path = None

            if audio_path:
                with st.spinner(f"正在用 Whisper（{whisper_model}）辨識語音…約需 1-3 分鐘"):
                    try:
                        entries, lang = transcribe_with_whisper(audio_path, whisper_model)
                        full_text = " ".join(e["text"] for e in entries)

                        st.success(f"辨識語言：{lang}　共 {len(entries)} 段")
                        st.text_area("Whisper 逐字稿", full_text, height=320)

                        st.divider()
                        _render_translation(full_text, target_lang)
                    except Exception as e:
                        st.error(f"Whisper 辨識失敗：{e}")

        # 音頻下載
        if get_audio_btn:
            with st.spinner("正在下載音頻（需要 ffmpeg）…"):
                try:
                    tmpdir = tempfile.mkdtemp()
                    audio_path = download_audio(url, tmpdir)

                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()

                    st.audio(audio_bytes, format="audio/mp3")
                    fname = (info["title"][:40] or "audio").replace("/", "_") + ".mp3"
                    st.download_button(
                        "⬇ 下載 MP3",
                        audio_bytes,
                        file_name=fname,
                        mime="audio/mp3",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"音頻下載失敗：{e}\n\n請確認已安裝 ffmpeg：`sudo apt install ffmpeg`")

    elif analyze_btn:
        st.warning("請輸入影片連結")

# ════════════════════════════════════════════════════════════
# TAB 3 · 模板生成器
# ════════════════════════════════════════════════════════════

with tab_template:
    st.markdown("### 🎬 從爆款影片生成拍攝模板")
    st.caption("貼上任何爆款連結，AI 幫你分析爆款原因並生成可複製的鉤子與拍攝模板")

    col_url, col_platform = st.columns([3, 1])
    with col_url:
        tmpl_url = st.text_input(
            "爆款影片連結",
            placeholder="貼上 YouTube / TikTok / Instagram / Bilibili 連結…",
            label_visibility="collapsed",
            key="tmpl_url",
        )
    with col_platform:
        tmpl_platform = st.selectbox(
            "平台",
            ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "Bilibili"],
            label_visibility="collapsed",
            key="tmpl_platform",
        )

    tmpl_niche = st.text_input(
        "你的創作主題（選填）",
        placeholder="例如：科技開箱、健身教學、個人理財… 填了會生成更貼近你的模板",
        key="tmpl_niche",
    )

    tmpl_btn = st.button("🚀 生成模板", type="primary", use_container_width=True)

    if tmpl_btn:
        if not tmpl_url.strip():
            st.warning("請輸入影片連結")
        elif not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("請先在左側欄輸入 Anthropic API Key")
        else:
            with st.spinner("正在讀取影片資訊…"):
                info = get_video_info(tmpl_url.strip())

            if "error" in info:
                st.error(f"無法讀取影片：{info['error']}")
            else:
                with st.spinner("正在取得逐字稿…"):
                    entries, _ = get_transcript(tmpl_url.strip())
                    transcript_text = " ".join(e["text"] for e in entries) if entries else ""

                if not transcript_text:
                    st.info("找不到字幕，將只根據標題和元數據分析")

                with st.spinner("AI 正在分析爆款原因並生成模板…約需 15-30 秒"):
                    try:
                        result = analyze_and_generate_templates(
                            title=info["title"],
                            transcript=transcript_text,
                            view_count=info["view_count"],
                            like_count=info["like_count"],
                            channel=info["channel"],
                            platform=tmpl_platform,
                            user_niche=tmpl_niche.strip(),
                        )

                        st.success(f"分析完成！影片：{info['title'][:50]}…")
                        st.caption(f"👁 {format_count(info['view_count'])} 觀看 · 👍 {format_count(info['like_count'])} 按讚")
                        st.divider()

                        tab_r1, tab_r2, tab_r3, tab_r4, tab_r5, tab_r6 = st.tabs([
                            "🔥 爆款原因",
                            "🪝 鉤子模板",
                            "🎬 拍攝模板",
                            "✂️ 剪輯建議",
                            "📐 標題公式",
                            "💡 主題靈感",
                        ])

                        with tab_r1:
                            st.markdown(result["virality_reasons"] or result["raw"])
                        with tab_r2:
                            st.markdown(result["hooks"])
                        with tab_r3:
                            st.markdown(result["shooting_template"])
                        with tab_r4:
                            st.markdown(result["editing_tips"])
                        with tab_r5:
                            st.markdown(result["title_formulas"])
                        with tab_r6:
                            st.markdown(result["topic_ideas"])

                        st.divider()
                        full_report = result["raw"]
                        st.download_button(
                            "⬇ 下載完整模板報告",
                            full_report,
                            file_name="viral_template.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                    except Exception as e:
                        st.error(f"生成失敗：{e}")

    st.divider()

    # ── 自訂鉤子生成器 ──
    st.markdown("### 🪝 自訂鉤子生成器")
    st.caption("不需要影片連結，直接輸入主題就能生成開場鉤子")

    hk_col1, hk_col2, hk_col3 = st.columns([3, 1, 1])
    with hk_col1:
        hk_topic = st.text_input(
            "影片主題",
            placeholder="例如：我用 AI 一個月賺了 10 萬",
            label_visibility="collapsed",
            key="hk_topic",
        )
    with hk_col2:
        hk_platform = st.selectbox(
            "平台",
            ["TikTok", "YouTube Shorts", "Instagram Reels", "YouTube"],
            label_visibility="collapsed",
            key="hk_platform",
        )
    with hk_col3:
        hk_style = st.selectbox(
            "風格",
            ["好奇心", "震驚開場", "痛點共鳴", "反直覺", "數字衝擊"],
            label_visibility="collapsed",
            key="hk_style",
        )

    hk_btn = st.button("🪝 生成鉤子", use_container_width=True)

    if hk_btn:
        if not hk_topic.strip():
            st.warning("請輸入影片主題")
        elif not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("請先在左側欄輸入 Anthropic API Key")
        else:
            with st.spinner("正在生成鉤子…"):
                try:
                    hooks = generate_custom_hook(hk_topic.strip(), hk_platform, hk_style)
                    st.markdown(hooks)
                except Exception as e:
                    st.error(f"生成失敗：{e}")

# ════════════════════════════════════════════════════════════
# TAB 4 · 重現指南
# ════════════════════════════════════════════════════════════

with tab_recreate:
    st.markdown("### 🎥 影片重現指南")
    st.caption("貼上任何影片連結，AI 告訴你怎麼拍出一樣效果 + 生成 AI 影片工具 Prompt")

    rc_col1, rc_col2 = st.columns([3, 1])
    with rc_col1:
        rc_url = st.text_input(
            "影片連結",
            placeholder="YouTube / TikTok / Instagram Reels / Bilibili…",
            label_visibility="collapsed",
            key="rc_url",
        )
    with rc_col2:
        rc_platform = st.selectbox(
            "平台",
            ["YouTube", "YouTube Shorts", "TikTok", "Instagram Reels", "Bilibili"],
            label_visibility="collapsed",
            key="rc_platform",
        )

    rc_tools = st.text_input(
        "你有哪些器材？（選填）",
        placeholder="例如：iPhone 15、環形燈、DJI Osmo、剪映… 不填也沒關係",
        key="rc_tools",
    )

    rc_btn = st.button("🎥 生成重現指南", type="primary", use_container_width=True)

    if rc_btn:
        if not rc_url.strip():
            st.warning("請輸入影片連結")
        elif not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("請先在左側欄輸入 Anthropic API Key")
        else:
            _ig = st.session_state.get("ig_session", "")
            with st.spinner("正在讀取影片資訊…"):
                rc_info = get_video_info(rc_url.strip(), _ig)

            if "error" in rc_info:
                st.error(f"無法讀取影片：{rc_info['error']}")
                if "instagram" in rc_url.lower() or "instagram" in rc_info.get("error","").lower():
                    st.info("Instagram 影片需要登入 Cookie。請在左側欄「Instagram 設定」貼上你的 Session ID。\n\n取得方法：瀏覽器登入 Instagram → 開發者工具（F12）→ Application → Cookies → 找 `sessionid` 複製值")
            else:
                with st.spinner("正在取得逐字稿…"):
                    rc_entries, _ = get_transcript(rc_url.strip(), ig_session=_ig)
                    rc_transcript = " ".join(e["text"] for e in rc_entries) if rc_entries else ""

                with st.spinner("AI 正在生成完整重現指南…約需 20-30 秒"):
                    try:
                        rc_result = generate_recreation_guide(
                            title=rc_info["title"],
                            transcript=rc_transcript,
                            description=rc_info.get("description", ""),
                            view_count=rc_info["view_count"],
                            platform=rc_platform,
                            thumbnail_url=rc_info.get("thumbnail", ""),
                            user_tools=rc_tools.strip(),
                        )

                        st.success(f"指南生成完成：{rc_info['title'][:50]}…")

                        if rc_info.get("thumbnail"):
                            st.image(rc_info["thumbnail"], width=300)

                        st.divider()

                        t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
                            "📱 拍攝設置",
                            "💡 燈光場景",
                            "📝 腳本結構",
                            "✂️ 剪輯",
                            "🎵 音樂",
                            "📦 器材",
                            "🤖 AI Prompt",
                            "🪜 重現步驟",
                        ])

                        with t1:
                            st.markdown(rc_result["filming_setup"])
                        with t2:
                            st.markdown(rc_result["lighting_scene"])
                        with t3:
                            st.markdown(rc_result["script_breakdown"])
                        with t4:
                            st.markdown(rc_result["editing"])
                        with t5:
                            st.markdown(rc_result["music"])
                        with t6:
                            st.markdown(rc_result["equipment"])
                        with t7:
                            st.markdown(rc_result["ai_prompts"])
                        with t8:
                            st.markdown(rc_result["steps"])

                        st.divider()
                        st.download_button(
                            "⬇ 下載完整重現指南",
                            rc_result["raw"],
                            file_name="recreation_guide.md",
                            mime="text/markdown",
                            use_container_width=True,
                        )

                    except Exception as e:
                        st.error(f"生成失敗：{e}")
