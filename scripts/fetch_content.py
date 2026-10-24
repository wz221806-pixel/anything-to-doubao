# -*- coding: utf-8 -*-
"""
anything-to-doubao / fetch_content.py
统一内容获取器：微信公众号文章 / 本地文件（PDF EPUB Word PPT Excel md txt 图片 音频 ZIP）→ TXT

用法:
  python fetch_content.py <输入> <输出TXT>
    输入: mp.weixin.qq.com 链接 或 本地文件绝对路径
依赖: httpx, beautifulsoup4, markitdown[all]
"""
import sys, os, re, zipfile, tempfile
import httpx
from bs4 import BeautifulSoup

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Referer": "https://weixin.qq.com/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def _proxies():
    """检测系统代理（红岸加速器等本地代理），返回可用代理 dict 或 None"""
    for port in (7892, 7890, 10809, 1080):
        sock = None
        try:
            import socket
            sock = socket.create_connection(("127.0.0.1", port), timeout=0.5)
            return {"http://": f"http://127.0.0.1:{port}", "https://": f"http://127.0.0.1:{port}"}
        except Exception:
            if sock:
                sock.close()
            continue
    return None

def is_url(s):
    return s.startswith("http://") or s.startswith("https://")

# ---------- 微信公众号 ----------
def fetch_weixin(url):
    # 1) 直连（国内站首选）
    r = httpx.get(url, headers=HEADERS, timeout=25, follow_redirects=True, trust_env=False)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.select_one("h1#activity-name") or soup.select_one("h1.rich_media_title")
        if title:
            title = title.get_text(strip=True)
            author = soup.select_one("a#js_name") or soup.select_one("span#js_name")
            author = author.get_text(strip=True) if author else ""
            content = soup.select_one("div#js_content") or soup.select_one("div.rich_media_content")
            if content:
                for tag in content.select("script, style"):
                    tag.decompose()
                text = content.get_text("\n", strip=True)
                text = re.sub(r"\n{3,}", "\n\n", text)
                if len(text.strip()) > 100:
                    return text, {"title": title, "author": author, "url": url}
    # 2) r.jina.ai 回退（需代理）
    proxies = _proxies()
    try:
        rr = httpx.get("https://r.jina.ai/" + url, headers=HEADERS, timeout=30,
                       follow_redirects=True, trust_env=False, proxy=proxies if proxies else None)
        if rr.status_code == 200 and len(rr.text) > 500:
            return rr.text, {"title": os.path.basename(url), "author": "", "url": url}
    except Exception:
        pass
    return None

# ---------- 本地文件 ----------
def fetch_local(path):
    if MarkItDown is None:
        raise RuntimeError("markitdown 未安装: pip install 'markitdown[all]'")
    md = MarkItDown()
    ext = os.path.splitext(path)[1].lower()
    if ext == ".zip":
        parts = []
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(path) as z:
                z.extractall(tmp)
            for root, _, files in os.walk(tmp):
                for fn in sorted(files):
                    fp = os.path.join(root, fn)
                    try:
                        txt = md.convert(fp).text_content
                        if txt and len(txt.strip()) > 20:
                            parts.append(f"## 文件: {fn}\n\n{txt}")
                    except Exception as e:
                        parts.append(f"## 文件: {fn}\n\n[转换失败: {e}]")
        text = "\n\n".join(parts)
    else:
        try:
            text = md.convert(path).text_content
        except Exception as e:
            raise RuntimeError(f"文件转换失败: {e}")
    meta = {"title": os.path.basename(path), "author": "", "url": path}
    return (text, meta)

def main():
    if len(sys.argv) < 3:
        print("用法: python fetch_content.py <输入> <输出TXT>")
        sys.exit(1)
    src, out = sys.argv[1], sys.argv[2]

    if is_url(src) and "mp.weixin.qq.com" in src:
        res = fetch_weixin(src)
        if res is None:
            print("ERROR: 微信文章抓取失败（可能被反爬或链接失效）")
            sys.exit(1)
        text, meta = res
    elif os.path.exists(src):
        text, meta = fetch_local(src)
    else:
        print("ERROR: 输入既不是可访问 URL 也不是存在的文件路径")
        sys.exit(1)

    if not text or len(text.strip()) < 100:
        print("ERROR: 提取内容为空或过短")
        sys.exit(1)

    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {meta['title']}\n\n")
        if meta.get("author"):
            f.write(f"作者: {meta['author']}\n")
        f.write(f"来源: {meta['url']}\n\n")
        f.write(text)

    print(f"✅ 获取成功: {meta['title']}")
    print(f"   正文长度: {len(text)} 字符")
    print(f"   已保存: {out}")

if __name__ == "__main__":
    main()
