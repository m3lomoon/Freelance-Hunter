"""
多語言介面模組 — 繁體中文 / 简体中文 / English / Español
"""
import streamlit as st

SUPPORTED_LANGUAGES = {
    "繁體中文": "zh-TW",
    "简体中文": "zh-CN",
    "English":   "en",
    "Español":   "es",
}

_T: dict[str, dict[str, str]] = {

    # ── App Meta ───────────────────────────────────────────────────────────
    "app_title": {
        "zh-TW": "🎯 爆款影片獵手",
        "zh-CN": "🎯 爆款视频猎手",
        "en":    "🎯 Viral Video Hunter",
        "es":    "🎯 Cazador de Videos Virales",
    },
    "app_subtitle": {
        "zh-TW": "找到爆款 → 理解為什麼爆 → 做出你的版本",
        "zh-CN": "找到爆款 → 理解为什么爆 → 做出你的版本",
        "en":    "Find viral videos → Understand why → Create your version",
        "es":    "Encuentra virales → Entiende por qué → Crea tu versión",
    },
    "sidebar_caption": {
        "zh-TW": "為內容創作者打造的爆款分析工具",
        "zh-CN": "为内容创作者打造的爆款分析工具",
        "en":    "The viral video analysis tool for content creators",
        "es":    "La herramienta de análisis viral para creadores",
    },

    # ── Theme Toggle ───────────────────────────────────────────────────────
    "dark_mode": {
        "zh-TW": "🌙 深色模式",
        "zh-CN": "🌙 深色模式",
        "en":    "🌙 Dark Mode",
        "es":    "🌙 Modo Oscuro",
    },
    "light_mode": {
        "zh-TW": "☀️ 淺色模式",
        "zh-CN": "☀️ 浅色模式",
        "en":    "☀️ Light Mode",
        "es":    "☀️ Modo Claro",
    },

    # ── Language Selector ──────────────────────────────────────────────────
    "language_label": {
        "zh-TW": "🌍 介面語言",
        "zh-CN": "🌍 界面语言",
        "en":    "🌍 Interface Language",
        "es":    "🌍 Idioma de Interfaz",
    },

    # ── Paywall / Unlock ──────────────────────────────────────────────────
    "unlock_expander": {
        "zh-TW": "🔒 解鎖進階功能",
        "zh-CN": "🔒 解锁高级功能",
        "en":    "🔒 Unlock PRO Features",
        "es":    "🔒 Desbloquear PRO",
    },
    "access_code_placeholder": {
        "zh-TW": "VH-XXXX-XXXX 或 Gumroad 授權碼",
        "zh-CN": "VH-XXXX-XXXX 或 Gumroad 授权码",
        "en":    "VH-XXXX-XXXX or Gumroad License Key",
        "es":    "VH-XXXX-XXXX o Clave de Licencia Gumroad",
    },
    "unlock_btn": {
        "zh-TW": "🔓 解鎖",
        "zh-CN": "🔓 解锁",
        "en":    "🔓 Unlock",
        "es":    "🔓 Desbloquear",
    },
    "buy_pro": {
        "zh-TW": "🛒 購買 PRO 進階版",
        "zh-CN": "🛒 购买 PRO 高级版",
        "en":    "🛒 Buy PRO Version",
        "es":    "🛒 Comprar versión PRO",
    },
    "unlock_success": {
        "zh-TW": "✅ 解鎖成功！",
        "zh-CN": "✅ 解锁成功！",
        "en":    "✅ Unlocked successfully!",
        "es":    "✅ ¡Desbloqueado con éxito!",
    },
    "unlock_error": {
        "zh-TW": "Code 不正確或已達嘗試上限",
        "zh-CN": "Code 不正确或已达尝试上限",
        "en":    "Invalid code or too many attempts",
        "es":    "Código incorrecto o demasiados intentos",
    },
    "pro_unlocked_msg": {
        "zh-TW": "✅ 進階版已解鎖",
        "zh-CN": "✅ 高级版已解锁",
        "en":    "✅ PRO Unlocked",
        "es":    "✅ PRO Desbloqueado",
    },
    "logout_pro": {
        "zh-TW": "登出進階版",
        "zh-CN": "登出高级版",
        "en":    "Sign out of PRO",
        "es":    "Cerrar sesión PRO",
    },
    "free_features_header": {
        "zh-TW": "免費功能",
        "zh-CN": "免费功能",
        "en":    "Free Features",
        "es":    "Funciones Gratuitas",
    },
    "pro_features_header": {
        "zh-TW": "進階功能 🔥",
        "zh-CN": "高级功能 🔥",
        "en":    "PRO Features 🔥",
        "es":    "Funciones PRO 🔥",
    },
    "purchase_hint": {
        "zh-TW": "訂閱後你會收到授權碼，輸入即可解鎖月費版",
        "zh-CN": "订阅后你会收到授权码，输入即可解锁月费版",
        "en":    "After subscribing you'll receive a license key — enter it to unlock",
        "es":    "Tras suscribirte recibirás una clave de licencia para ingresar",
    },
    "buy_pro_monthly": {
        "zh-TW": "🛒 訂閱月費 PRO",
        "zh-CN": "🛒 订阅月费 PRO",
        "en":    "🛒 Subscribe Monthly PRO",
        "es":    "🛒 Suscribirse PRO Mensual",
    },
    "sub_active": {
        "zh-TW": "✅ 月費訂閱中",
        "zh-CN": "✅ 月费订阅中",
        "en":    "✅ Active subscription",
        "es":    "✅ Suscripción activa",
    },
    "sub_cancelled": {
        "zh-TW": "⚠️ 訂閱已取消，當前週期結束前仍可使用",
        "zh-CN": "⚠️ 订阅已取消，当前周期结束前仍可使用",
        "en":    "⚠️ Subscription cancelled — access until end of billing period",
        "es":    "⚠️ Suscripción cancelada — acceso hasta fin del período",
    },
    "sub_payment_failed": {
        "zh-TW": "❌ 付款失敗，請更新付款方式以繼續使用",
        "zh-CN": "❌ 付款失败，请更新付款方式以继续使用",
        "en":    "❌ Payment failed — please update your payment method",
        "es":    "❌ Pago fallido — actualiza tu método de pago",
    },
    "sub_ended": {
        "zh-TW": "❌ 訂閱已到期，請重新訂閱",
        "zh-CN": "❌ 订阅已到期，请重新订阅",
        "en":    "❌ Subscription ended — please resubscribe",
        "es":    "❌ Suscripción vencida — vuelve a suscribirte",
    },
    "manage_sub": {
        "zh-TW": "管理訂閱",
        "zh-CN": "管理订阅",
        "en":    "Manage Subscription",
        "es":    "Gestionar Suscripción",
    },

    # ── Settings ───────────────────────────────────────────────────────────
    "settings_header": {
        "zh-TW": "⚙️ 設定",
        "zh-CN": "⚙️ 设置",
        "en":    "⚙️ Settings",
        "es":    "⚙️ Configuración",
    },
    "ai_enabled": {
        "zh-TW": "✅ AI 功能已啟用",
        "zh-CN": "✅ AI 功能已启用",
        "en":    "✅ AI features enabled",
        "es":    "✅ Funciones IA activadas",
    },
    "api_key_label": {
        "zh-TW": "Anthropic API Key（選填）",
        "zh-CN": "Anthropic API Key（选填）",
        "en":    "Anthropic API Key (optional)",
        "es":    "Anthropic API Key (opcional)",
    },
    "api_key_help": {
        "zh-TW": "有填 Key → Claude 翻譯；沒填 → Google 翻譯（免費）",
        "zh-CN": "有填 Key → Claude 翻译；没填 → Google 翻译（免费）",
        "en":    "With Key → Claude translation; Without → Google Translate (free)",
        "es":    "Con Key → Traducción Claude; Sin Key → Google Translate (gratis)",
    },
    "ig_session_label": {
        "zh-TW": "Instagram Session ID（選填）",
        "zh-CN": "Instagram Session ID（选填）",
        "en":    "Instagram Session ID (optional)",
        "es":    "Instagram Session ID (opcional)",
    },
    "ig_session_help": {
        "zh-TW": "分析 Instagram Reels 需要",
        "zh-CN": "分析 Instagram Reels 需要",
        "en":    "Required for Instagram Reels analysis",
        "es":    "Necesario para analizar Instagram Reels",
    },
    "whisper_model_label": {
        "zh-TW": "🎙 Whisper 模型",
        "zh-CN": "🎙 Whisper 模型",
        "en":    "🎙 Whisper Model",
        "es":    "🎙 Modelo Whisper",
    },
    "whisper_model_help": {
        "zh-TW": "模型越大越準確，但速度較慢",
        "zh-CN": "模型越大越准确，但速度较慢",
        "en":    "Larger model = more accurate but slower",
        "es":    "Modelo mayor = más preciso pero más lento",
    },
    "admin_tools": {
        "zh-TW": "🔧 管理員工具",
        "zh-CN": "🔧 管理员工具",
        "en":    "🔧 Admin Tools",
        "es":    "🔧 Herramientas Admin",
    },
    "admin_password": {
        "zh-TW": "管理員密碼",
        "zh-CN": "管理员密码",
        "en":    "Admin Password",
        "es":    "Contraseña Admin",
    },
    "wrong_password": {
        "zh-TW": "密碼錯誤",
        "zh-CN": "密码错误",
        "en":    "Wrong password",
        "es":    "Contraseña incorrecta",
    },
    "admin_tab_analytics": {
        "zh-TW": "📊 使用分析",
        "zh-CN": "📊 使用分析",
        "en":    "📊 Analytics",
        "es":    "📊 Análisis",
    },
    "admin_tab_survey": {
        "zh-TW": "💬 問卷",
        "zh-CN": "💬 问卷",
        "en":    "💬 Survey",
        "es":    "💬 Encuesta",
    },
    "admin_tab_codes": {
        "zh-TW": "🔑 Access Code",
        "zh-CN": "🔑 Access Code",
        "en":    "🔑 Access Codes",
        "es":    "🔑 Códigos de Acceso",
    },
    "generate_codes_btn": {
        "zh-TW": "產生 Access Code",
        "zh-CN": "生成 Access Code",
        "en":    "Generate Access Codes",
        "es":    "Generar Códigos de Acceso",
    },
    "generate_codes_hint": {
        "zh-TW": "複製後加入 Streamlit Secrets 的 ACCESS_CODES（逗號分隔）",
        "zh-CN": "复制后加入 Streamlit Secrets 的 ACCESS_CODES（逗号分隔）",
        "en":    "Copy and add to Streamlit Secrets under ACCESS_CODES (comma-separated)",
        "es":    "Copia y añade a Streamlit Secrets en ACCESS_CODES (separado por comas)",
    },

    # ── STEP 1 ─────────────────────────────────────────────────────────────
    "step1_title": {
        "zh-TW": "找到你的靈感影片",
        "zh-CN": "找到你的灵感视频",
        "en":    "Find Your Inspiration Video",
        "es":    "Encuentra tu Video de Inspiración",
    },
    "input_link": {
        "zh-TW": "🔗 貼上連結",
        "zh-CN": "🔗 粘贴链接",
        "en":    "🔗 Paste Link",
        "es":    "🔗 Pegar Enlace",
    },
    "input_search": {
        "zh-TW": "🔍 關鍵字搜尋",
        "zh-CN": "🔍 关键词搜索",
        "en":    "🔍 Keyword Search",
        "es":    "🔍 Búsqueda",
    },
    "url_placeholder": {
        "zh-TW": "貼上 YouTube / TikTok / Instagram / 小紅書 / Bilibili 連結…",
        "zh-CN": "粘贴 YouTube / TikTok / Instagram / 小红书 / Bilibili 链接…",
        "en":    "Paste YouTube / TikTok / Instagram / RED / Bilibili link…",
        "es":    "Pega enlace de YouTube / TikTok / Instagram / RED / Bilibili…",
    },
    "analyze_btn": {
        "zh-TW": "分析 →",
        "zh-CN": "分析 →",
        "en":    "Analyze →",
        "es":    "Analizar →",
    },
    "keyword_placeholder": {
        "zh-TW": "例如：AI副業、健身教學…",
        "zh-CN": "例如：AI副业、健身教程…",
        "en":    "e.g. AI side hustle, fitness tutorial…",
        "es":    "ej. emprendimiento IA, tutorial fitness…",
    },
    "search_btn": {
        "zh-TW": "🔍 搜尋",
        "zh-CN": "🔍 搜索",
        "en":    "🔍 Search",
        "es":    "🔍 Buscar",
    },
    "searching": {
        "zh-TW": "搜尋爆款中…",
        "zh-CN": "搜索爆款中…",
        "en":    "Searching for viral videos…",
        "es":    "Buscando videos virales…",
    },
    "no_results": {
        "zh-TW": "沒有找到影片，換個關鍵字試試",
        "zh-CN": "没有找到视频，换个关键词试试",
        "en":    "No videos found. Try a different keyword.",
        "es":    "No se encontraron videos. Prueba otra palabra clave.",
    },
    "select_btn": {
        "zh-TW": "✅ 選這部",
        "zh-CN": "✅ 选这部",
        "en":    "✅ Select",
        "es":    "✅ Seleccionar",
    },
    "watch_btn": {
        "zh-TW": "▶ 看影片",
        "zh-CN": "▶ 看视频",
        "en":    "▶ Watch",
        "es":    "▶ Ver",
    },

    # ── STEP 2 ─────────────────────────────────────────────────────────────
    "step2_title": {
        "zh-TW": "分析影片",
        "zh-CN": "分析视频",
        "en":    "Analyze Video",
        "es":    "Analizar Video",
    },
    "loading_info": {
        "zh-TW": "讀取影片資訊中…",
        "zh-CN": "读取视频信息中…",
        "en":    "Loading video info…",
        "es":    "Cargando información del video…",
    },
    "ig_hint": {
        "zh-TW": "💡 Instagram 需要 Session ID，請在左側欄「設定」中填入",
        "zh-CN": "💡 Instagram 需要 Session ID，请在左侧栏「设置」中填入",
        "en":    "💡 Instagram requires a Session ID. Please enter it in sidebar Settings.",
        "es":    "💡 Instagram requiere un Session ID. Ingrésalo en Configuración.",
    },
    "change_video": {
        "zh-TW": "← 換一部影片",
        "zh-CN": "← 换一部视频",
        "en":    "← Try another video",
        "es":    "← Probar otro video",
    },
    "watch_original": {
        "zh-TW": "▶ 觀看原影片",
        "zh-CN": "▶ 观看原视频",
        "en":    "▶ Watch Original",
        "es":    "▶ Ver Original",
    },
    "subscribers": {
        "zh-TW": "訂閱數",
        "zh-CN": "订阅数",
        "en":    "Subscribers",
        "es":    "Suscriptores",
    },
    "description_expander": {
        "zh-TW": "📝 影片描述",
        "zh-CN": "📝 视频描述",
        "en":    "📝 Video Description",
        "es":    "📝 Descripción del Video",
    },
    "transcript_header": {
        "zh-TW": "#### 📜 逐字稿",
        "zh-CN": "#### 📜 逐字稿",
        "en":    "#### 📜 Transcript",
        "es":    "#### 📜 Transcripción",
    },
    "get_subtitle_btn": {
        "zh-TW": "🗒 取得字幕逐字稿",
        "zh-CN": "🗒 获取字幕逐字稿",
        "en":    "🗒 Get Subtitle Transcript",
        "es":    "🗒 Obtener Transcripción",
    },
    "whisper_btn": {
        "zh-TW": "🎙 Whisper 語音辨識",
        "zh-CN": "🎙 Whisper 语音识别",
        "en":    "🎙 Whisper Transcription",
        "es":    "🎙 Transcripción Whisper",
    },
    "whisper_help": {
        "zh-TW": "需要 ffmpeg",
        "zh-CN": "需要 ffmpeg",
        "en":    "Requires ffmpeg",
        "es":    "Requiere ffmpeg",
    },
    "no_subtitles": {
        "zh-TW": "⚠️ 找不到字幕，試試 Whisper 語音辨識",
        "zh-CN": "⚠️ 找不到字幕，试试 Whisper 语音识别",
        "en":    "⚠️ No subtitles found. Try Whisper transcription.",
        "es":    "⚠️ Sin subtítulos. Prueba la transcripción Whisper.",
    },
    "getting_transcript": {
        "zh-TW": "取得逐字稿中…",
        "zh-CN": "获取逐字稿中…",
        "en":    "Getting transcript…",
        "es":    "Obteniendo transcripción…",
    },
    "downloading_audio": {
        "zh-TW": "下載音頻中…",
        "zh-CN": "下载音频中…",
        "en":    "Downloading audio…",
        "es":    "Descargando audio…",
    },
    "audio_fail": {
        "zh-TW": "❌ 音頻下載失敗：{e}",
        "zh-CN": "❌ 音频下载失败：{e}",
        "en":    "❌ Audio download failed: {e}",
        "es":    "❌ Error al descargar audio: {e}",
    },
    "whisper_fail": {
        "zh-TW": "❌ Whisper 失敗：{e}",
        "zh-CN": "❌ Whisper 失败：{e}",
        "en":    "❌ Whisper failed: {e}",
        "es":    "❌ Whisper falló: {e}",
    },
    "translate_header": {
        "zh-TW": "#### 🌐 翻譯逐字稿",
        "zh-CN": "#### 🌐 翻译逐字稿",
        "en":    "#### 🌐 Translate Transcript",
        "es":    "#### 🌐 Traducir Transcripción",
    },
    "free_translation_notice": {
        "zh-TW": "🆓 免費模式：使用 Google 翻譯 · 輸入 Anthropic API Key 切換 Claude 高品質翻譯",
        "zh-CN": "🆓 免费模式：使用 Google 翻译 · 输入 Anthropic API Key 切换 Claude 高质量翻译",
        "en":    "🆓 Free mode: Google Translate · Enter API Key for Claude high-quality translation",
        "es":    "🆓 Modo gratis: Google Translate · Ingresa API Key para traducción Claude",
    },
    "translate_btn": {
        "zh-TW": "🌐 翻譯為「{lang}」",
        "zh-CN": "🌐 翻译为「{lang}」",
        "en":    "🌐 Translate to {lang}",
        "es":    "🌐 Traducir a {lang}",
    },
    "translating": {
        "zh-TW": "翻譯中…",
        "zh-CN": "翻译中…",
        "en":    "Translating…",
        "es":    "Traduciendo…",
    },
    "translation_fail": {
        "zh-TW": "❌ 翻譯失敗：{e}",
        "zh-CN": "❌ 翻译失败：{e}",
        "en":    "❌ Translation failed: {e}",
        "es":    "❌ Error al traducir: {e}",
    },
    "download_translation": {
        "zh-TW": "⬇ 下載翻譯",
        "zh-CN": "⬇ 下载翻译",
        "en":    "⬇ Download Translation",
        "es":    "⬇ Descargar Traducción",
    },

    # ── STEP 3 / PRO ─────────────────────────────────────────────────────
    "step3_title": {
        "zh-TW": "生成你的版本",
        "zh-CN": "生成你的版本",
        "en":    "Create Your Version",
        "es":    "Crea Tu Versión",
    },
    "tab_analysis": {
        "zh-TW": "🔥 爆款分析 + 模板",
        "zh-CN": "🔥 爆款分析 + 模板",
        "en":    "🔥 Viral Analysis + Templates",
        "es":    "🔥 Análisis Viral + Plantillas",
    },
    "tab_recreation": {
        "zh-TW": "🎥 重現指南",
        "zh-CN": "🎥 重现指南",
        "en":    "🎥 Recreation Guide",
        "es":    "🎥 Guía de Recreación",
    },
    "tab_tools": {
        "zh-TW": "✍️ 內容工具",
        "zh-CN": "✍️ 内容工具",
        "en":    "✍️ Content Tools",
        "es":    "✍️ Herramientas",
    },
    "tab_faceless": {
        "zh-TW": "🤖 無臉頻道工作坊",
        "zh-CN": "🤖 无脸频道工作坊",
        "en":    "🤖 Faceless Channel Studio",
        "es":    "🤖 Estudio Canal Anónimo",
    },
    "tab_favorites": {
        "zh-TW": "⭐ 我的收藏",
        "zh-CN": "⭐ 我的收藏",
        "en":    "⭐ My Favorites",
        "es":    "⭐ Mis Favoritos",
    },
    "tab_history": {
        "zh-TW": "📋 分析歷史",
        "zh-CN": "📋 分析历史",
        "en":    "📋 History",
        "es":    "📋 Historial",
    },
    "need_api_key": {
        "zh-TW": "❌ 此功能需要 Anthropic API Key，請在左側欄填入",
        "zh-CN": "❌ 此功能需要 Anthropic API Key，请在左侧栏填入",
        "en":    "❌ This feature requires an Anthropic API Key. Please enter it in the sidebar.",
        "es":    "❌ Esta función requiere un Anthropic API Key. Ingrésalo en la barra lateral.",
    },
    "generating": {
        "zh-TW": "生成中…",
        "zh-CN": "生成中…",
        "en":    "Generating…",
        "es":    "Generando…",
    },
    "gen_fail": {
        "zh-TW": "❌ 生成失敗：{e}",
        "zh-CN": "❌ 生成失败：{e}",
        "en":    "❌ Generation failed: {e}",
        "es":    "❌ Error al generar: {e}",
    },
    "download_btn": {
        "zh-TW": "⬇ 下載",
        "zh-CN": "⬇ 下载",
        "en":    "⬇ Download",
        "es":    "⬇ Descargar",
    },
    "save_btn": {
        "zh-TW": "⭐ 收藏",
        "zh-CN": "⭐ 收藏",
        "en":    "⭐ Save",
        "es":    "⭐ Guardar",
    },
    "saved_msg": {
        "zh-TW": "✅ 已收藏！",
        "zh-CN": "✅ 已收藏！",
        "en":    "✅ Saved!",
        "es":    "✅ ¡Guardado!",
    },
    "generate_template_btn": {
        "zh-TW": "🚀 生成爆款模板",
        "zh-CN": "🚀 生成爆款模板",
        "en":    "🚀 Generate Viral Template",
        "es":    "🚀 Generar Plantilla Viral",
    },
    "analyzing": {
        "zh-TW": "AI 分析中…約需 20 秒",
        "zh-CN": "AI 分析中…约需 20 秒",
        "en":    "AI analyzing… about 20 seconds",
        "es":    "IA analizando… unos 20 segundos",
    },
    "gen_recreation_btn": {
        "zh-TW": "🎥 生成重現指南",
        "zh-CN": "🎥 生成重现指南",
        "en":    "🎥 Generate Recreation Guide",
        "es":    "🎥 Generar Guía de Recreación",
    },
    "gen_hook_btn": {
        "zh-TW": "✨ 生成鉤子",
        "zh-CN": "✨ 生成钩子",
        "en":    "✨ Generate Hooks",
        "es":    "✨ Generar Anzuelos",
    },
    "your_topic": {
        "zh-TW": "你的創作主題（選填）",
        "zh-CN": "你的创作主题（选填）",
        "en":    "Your content niche (optional)",
        "es":    "Tu nicho de contenido (opcional)",
    },
    "your_gear": {
        "zh-TW": "你有哪些器材？",
        "zh-CN": "你有哪些器材？",
        "en":    "What equipment do you have?",
        "es":    "¿Qué equipo tienes?",
    },
    "gear_placeholder": {
        "zh-TW": "iPhone 15、環形燈、剪映…",
        "zh-CN": "iPhone 15、环形灯、剪映…",
        "en":    "iPhone 15, ring light, CapCut…",
        "es":    "iPhone 15, aro de luz, CapCut…",
    },

    # ── Favorites ──────────────────────────────────────────────────────────
    "no_favorites": {
        "zh-TW": "💡 還沒有收藏，在各工具頁點「⭐ 收藏」即可",
        "zh-CN": "💡 还没有收藏，在各工具页点「⭐ 收藏」即可",
        "en":    "💡 No favorites yet. Click ⭐ on any tool to save.",
        "es":    "💡 Sin favoritos. Haz clic en ⭐ en cualquier herramienta.",
    },
    "clear_favorites": {
        "zh-TW": "🗑 清空所有收藏",
        "zh-CN": "🗑 清空所有收藏",
        "en":    "🗑 Clear All Favorites",
        "es":    "🗑 Borrar Todo",
    },
    "delete_btn": {
        "zh-TW": "🗑 刪除",
        "zh-CN": "🗑 删除",
        "en":    "🗑 Delete",
        "es":    "🗑 Eliminar",
    },
    "fav_count": {
        "zh-TW": "共 {n} 個收藏",
        "zh-CN": "共 {n} 个收藏",
        "en":    "{n} saved items",
        "es":    "{n} elementos guardados",
    },

    # ── History ────────────────────────────────────────────────────────────
    "no_history": {
        "zh-TW": "💡 還沒有分析過任何影片",
        "zh-CN": "💡 还没有分析过任何视频",
        "en":    "💡 No videos analyzed yet",
        "es":    "💡 Aún no hay videos analizados",
    },
    "history_count": {
        "zh-TW": "最近分析了 {n} 部影片（最多保留 50 筆）",
        "zh-CN": "最近分析了 {n} 部视频（最多保留 50 条）",
        "en":    "Analyzed {n} videos recently (up to 50 saved)",
        "es":    "{n} videos analizados recientemente (máx. 50)",
    },
    "reanalyze_btn": {
        "zh-TW": "🔄 重新分析",
        "zh-CN": "🔄 重新分析",
        "en":    "🔄 Re-analyze",
        "es":    "🔄 Re-analizar",
    },
    "clear_history": {
        "zh-TW": "🗑 清空歷史",
        "zh-CN": "🗑 清空历史",
        "en":    "🗑 Clear History",
        "es":    "🗑 Borrar Historial",
    },

    # ── Survey ─────────────────────────────────────────────────────────────
    "survey_expander": {
        "zh-TW": "💬 分享你的使用體驗（只需 1 分鐘）",
        "zh-CN": "💬 分享你的使用体验（只需 1 分钟）",
        "en":    "💬 Share Your Experience (1 minute)",
        "es":    "💬 Comparte tu Experiencia (1 minuto)",
    },

    # ── Content Tools ─────────────────────────────────────────────────────
    "ab_title": {
        "zh-TW": "🔤 A/B 標題",
        "zh-CN": "🔤 A/B 标题",
        "en":    "🔤 A/B Titles",
        "es":    "🔤 Títulos A/B",
    },
    "thumbnail_copy": {
        "zh-TW": "🖼 縮圖文案",
        "zh-CN": "🖼 缩图文案",
        "en":    "🖼 Thumbnail Copy",
        "es":    "🖼 Texto Miniatura",
    },
    "calendar_30": {
        "zh-TW": "📅 30天日曆",
        "zh-CN": "📅 30天日历",
        "en":    "📅 30-Day Calendar",
        "es":    "📅 Calendario 30 días",
    },
    "platform_adapt": {
        "zh-TW": "🔄 平台適配",
        "zh-CN": "🔄 平台适配",
        "en":    "🔄 Platform Adapt",
        "es":    "🔄 Adaptar Plataforma",
    },
    "best_time": {
        "zh-TW": "⏰ 最佳時段",
        "zh-CN": "⏰ 最佳时段",
        "en":    "⏰ Best Time",
        "es":    "⏰ Mejor Hora",
    },

    # ── Faceless ──────────────────────────────────────────────────────────
    "faceless_caption": {
        "zh-TW": "從找利基、寫腳本、SEO 到分鏡，一站式無臉頻道製作流程",
        "zh-CN": "从找利基、写脚本、SEO 到分镜，一站式无脸频道制作流程",
        "en":    "End-to-end faceless channel workflow: niche → script → SEO → storyboard",
        "es":    "Flujo completo de canal anónimo: nicho → guión → SEO → storyboard",
    },
    "niche_finder": {
        "zh-TW": "🔍 利基市場發現器",
        "zh-CN": "🔍 利基市场发现器",
        "en":    "🔍 Niche Finder",
        "es":    "🔍 Buscador de Nichos",
    },
    "script_gen": {
        "zh-TW": "📝 AI 腳本生成",
        "zh-CN": "📝 AI 脚本生成",
        "en":    "📝 AI Script Generator",
        "es":    "📝 Generador de Guiones IA",
    },
    "seo_package": {
        "zh-TW": "🔑 SEO 優化包",
        "zh-CN": "🔑 SEO 优化包",
        "en":    "🔑 SEO Package",
        "es":    "🔑 Paquete SEO",
    },
    "thumbnail_prompt": {
        "zh-TW": "🖼 縮圖 Prompt",
        "zh-CN": "🖼 缩图 Prompt",
        "en":    "🖼 Thumbnail Prompt",
        "es":    "🖼 Prompt Miniatura",
    },
    "storyboard": {
        "zh-TW": "🎬 AI 分鏡腳本",
        "zh-CN": "🎬 AI 分镜脚本",
        "en":    "🎬 AI Storyboard",
        "es":    "🎬 Storyboard IA",
    },

    # ── 留言挖掘 Comment Mining ─────────────────────────────────────────────
    "tab_comments": {
        "zh-TW": "💬 留言挖掘 → 內容點子",
        "zh-CN": "💬 评论挖掘 → 内容点子",
        "en":    "💬 Comment Mining → Ideas",
        "es":    "💬 Minería de Comentarios",
    },
    "comments_caption": {
        "zh-TW": "分析觀眾留言，挖出他們真正想看的內容 → 直接變成你的下一支影片點子",
        "zh-CN": "分析观众评论，挖出他们真正想看的内容 → 直接变成你的下一支视频点子",
        "en":    "Analyze viewer comments to uncover what they really want → turn it into your next video",
        "es":    "Analiza los comentarios para descubrir qué quiere tu audiencia → tu próximo video",
    },
    "fetch_comments_btn": {
        "zh-TW": "💬 抓取並分析留言",
        "zh-CN": "💬 抓取并分析评论",
        "en":    "💬 Fetch & Analyze Comments",
        "es":    "💬 Obtener y Analizar Comentarios",
    },
    "fetching_comments": {
        "zh-TW": "抓取留言中…熱門影片可能需要 20~40 秒",
        "zh-CN": "抓取评论中…热门视频可能需要 20~40 秒",
        "en":    "Fetching comments… popular videos may take 20-40s",
        "es":    "Obteniendo comentarios… puede tardar 20-40s",
    },
    "mining_comments": {
        "zh-TW": "AI 分析觀眾需求中…",
        "zh-CN": "AI 分析观众需求中…",
        "en":    "AI analyzing audience demand…",
        "es":    "IA analizando la demanda…",
    },
    "comments_found": {
        "zh-TW": "✅ 抓到 {n} 則留言，依讚數排序分析中",
        "zh-CN": "✅ 抓到 {n} 条评论，依赞数排序分析中",
        "en":    "✅ Got {n} comments, analyzing top by likes",
        "es":    "✅ {n} comentarios obtenidos, analizando por likes",
    },
    "no_comments": {
        "zh-TW": "⚠️ {e}",
        "zh-CN": "⚠️ {e}",
        "en":    "⚠️ {e}",
        "es":    "⚠️ {e}",
    },
    "max_comments_label": {
        "zh-TW": "分析留言數量",
        "zh-CN": "分析评论数量",
        "en":    "Comments to analyze",
        "es":    "Comentarios a analizar",
    },
    "top_comments_expander": {
        "zh-TW": "📋 查看抓到的熱門留言",
        "zh-CN": "📋 查看抓到的热门评论",
        "en":    "📋 View fetched top comments",
        "es":    "📋 Ver comentarios obtenidos",
    },
}


def get_lang() -> str:
    """回傳目前 UI 語言代碼（如 zh-TW）"""
    lang_name = st.session_state.get("ui_lang", "繁體中文")
    return SUPPORTED_LANGUAGES.get(lang_name, "zh-TW")


def t(key: str, **kwargs) -> str:
    """
    回傳目前語言的翻譯字串。
    支援格式化：t("translate_btn", lang="English")
    找不到 key 或語言時 fallback 到繁體中文，再 fallback 到 key 本身。
    """
    lang = get_lang()
    entry = _T.get(key, {})
    text = entry.get(lang) or entry.get("zh-TW") or key
    return text.format(**kwargs) if kwargs else text
