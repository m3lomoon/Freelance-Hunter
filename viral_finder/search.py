import yt_dlp

PLATFORMS = {
    "YouTube": "ytsearch{n}:{q}",
    "YouTube Shorts": "ytsearch{n}:{q} #shorts",
    "Bilibili": "bilisearch{n}:{q}",
    "TikTok": "ytsearch{n}:{q} site:tiktok.com",
}


def search_videos(keyword: str, platform: str = "YouTube", max_results: int = 10) -> list[dict]:
    template = PLATFORMS.get(platform, "ytsearch{n}:{q}")
    query = template.format(n=max_results, q=keyword)

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "ignoreerrors": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(query, download=False)
            entries = result.get("entries", []) if result else []
    except Exception:
        return []

    videos = []
    for entry in entries:
        if not entry:
            continue

        video_id = entry.get("id", "")
        url = entry.get("webpage_url") or entry.get("url", "")
        if not url and video_id:
            if "Bilibili" in platform:
                url = f"https://www.bilibili.com/video/{video_id}"
            else:
                url = f"https://www.youtube.com/watch?v={video_id}"

        videos.append({
            "id": video_id,
            "title": entry.get("title") or "未知標題",
            "url": url,
            "thumbnail": entry.get("thumbnail", ""),
            "view_count": entry.get("view_count") or 0,
            "like_count": entry.get("like_count") or 0,
            "duration": entry.get("duration") or 0,
            "channel": entry.get("channel") or entry.get("uploader") or "未知頻道",
            "channel_url": entry.get("channel_url") or entry.get("uploader_url", ""),
            "upload_date": entry.get("upload_date", ""),
            "platform": platform,
        })

    videos.sort(key=lambda x: x["view_count"], reverse=True)
    return videos


def format_count(n: int) -> str:
    if not n:
        return "N/A"
    if n >= 100_000_000:
        return f"{n/100_000_000:.1f}億"
    if n >= 10_000:
        return f"{n/10_000:.1f}萬"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def format_duration(seconds) -> str:
    if not seconds:
        return "--:--"
    seconds = int(seconds)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_date(date_str: str) -> str:
    if not date_str or len(date_str) != 8:
        return ""
    return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
