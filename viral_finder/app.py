import os
import sys
import tempfile

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from search import search_videos, format_count, format_duration, format_date, PLATFORMS
from analyzer import get_video_info, get_transcript, download_audio, transcribe_with_whisper
from translator import translate_text, LANGUAGES


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

# ── 主區域 Tab ──────────────────────────────────────────────────────────────

tab_search, tab_analyze = st.tabs(["🔍 搜尋爆款影片", "📊 分析影片連結"])

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
        with st.spinner("正在讀取影片資訊…"):
            info = get_video_info(url)

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
                entries, lang = get_transcript(url)

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
