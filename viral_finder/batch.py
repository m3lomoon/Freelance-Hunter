import io
import time

import pandas as pd

from analyzer import get_video_info
from search import format_count, format_duration, format_date


def batch_analyze(urls: list[str], ig_session: str = "", progress_cb=None) -> list[dict]:
    results = []
    for i, url in enumerate(urls):
        url = url.strip()
        if not url:
            continue
        if progress_cb:
            progress_cb(i, len(urls), url)
        try:
            info = get_video_info(url, ig_session)
            if "error" in info:
                results.append({"url": url, "error": info["error"]})
            else:
                results.append({
                    "url": url,
                    "title": info.get("title", ""),
                    "channel": info.get("channel", ""),
                    "platform": info.get("platform", ""),
                    "view_count": info.get("view_count", 0),
                    "like_count": info.get("like_count", 0),
                    "comment_count": info.get("comment_count", 0),
                    "duration_sec": info.get("duration", 0),
                    "upload_date": format_date(info.get("upload_date", "")),
                    "channel_followers": info.get("channel_follower_count", 0),
                    "thumbnail": info.get("thumbnail", ""),
                    "error": "",
                })
        except Exception as e:
            results.append({"url": url, "error": str(e)})
        time.sleep(0.5)
    return results


def results_to_dataframe(results: list[dict]) -> pd.DataFrame:
    rows = []
    for r in results:
        if r.get("error"):
            rows.append({
                "連結": r["url"],
                "標題": "❌ " + r["error"][:60],
                "頻道": "",
                "平台": "",
                "觀看數": 0,
                "按讚數": 0,
                "留言數": 0,
                "時長": "",
                "上傳日期": "",
                "訂閱數": 0,
            })
        else:
            rows.append({
                "連結": r["url"],
                "標題": r.get("title", ""),
                "頻道": r.get("channel", ""),
                "平台": r.get("platform", ""),
                "觀看數": r.get("view_count", 0),
                "按讚數": r.get("like_count", 0),
                "留言數": r.get("comment_count", 0),
                "時長": format_duration(r.get("duration_sec", 0)),
                "上傳日期": r.get("upload_date", ""),
                "訂閱數": r.get("channel_followers", 0),
            })

    df = pd.DataFrame(rows)
    if not df.empty and "觀看數" in df.columns:
        df = df.sort_values("觀看數", ascending=False).reset_index(drop=True)
    return df


def dataframe_to_excel(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="爆款分析")
        ws = writer.sheets["爆款分析"]

        # 欄位寬度
        col_widths = {
            "A": 40, "B": 50, "C": 20, "D": 12,
            "E": 12, "F": 12, "G": 12, "H": 10,
            "I": 14, "J": 14,
        }
        for col, width in col_widths.items():
            ws.column_dimensions[col].width = width

    return buf.getvalue()
