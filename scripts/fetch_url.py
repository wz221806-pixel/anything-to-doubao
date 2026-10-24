# -*- coding: utf-8 -*-
"""
anything-to-doubao / fetch_url.py
普通网页抓取（含付费墙常见绕过策略），Windows 兼容（纯 Python + httpx）。
策略级联: 直连(浏览器UA) → r.jina.ai → archive.today；境外通道自动走本地代理。

用法:
  python fetch_url.py <URL> [输出TXT]
依赖: httpx, beautifulsoup4
"""
import sys, re, socket
import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
BOT_UA = ("Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)")

def _proxies():
    for port in (7892, 7890, 10809, 1080):
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=0.5)
            s.close()
            return {"http://": f"http://127.0.0.1:{port}", "https://": f"http://127.0.0.1:{port}"}
        except Exception:
            continue
    return None

def has_content(t):
    return t and len(t.strip()) > 500 and not any(k in t.lower() for k in
        ["access denied", "404 not found", "403 forbidden", "don't miss what's happening"])

def html_to_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.select("script, style, nav, footer, header"):
        tag.decompose()
    title = soup.title.get_text(strip=True) if soup.title else "网页"
    text = soup.get_text("\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return title, text

def try_direct(url):
    for ua in (HEADERS["User-Agent"], BOT_UA):
        try:
            h = dict(HEADERS)
            h["User-Agent"] = ua
            r = httpx.get(url, headers=h, timeout=15, follow_redirects=True, trust_env=False)
            if r.status_code == 200 and has_content(r.text):
                title, text = html_to_text(r.text)
                return f"# {title}\n\n来源: {url}\n\n{text}", "markdown"
        except Exception:
            continue
    return None, None

def try_jina(url):
    proxies = _proxies()
    try:
        # r.jina.ai 在国内通常需代理；有代理时走代理，无代理时试直连
        r = httpx.get("https://r.jina.ai/" + url, headers=HEADERS, timeout=30,
                      follow_redirects=True, trust_env=False, proxy=proxies if proxies else None)
        if r.status_code == 200 and has_content(r.text):
            return r.text, "markdown"
    except Exception:
        pass
    return None, None

def try_archive(url):
    proxies = _proxies()
    try:
        r = httpx.get("https://archive.today/newest/" + url, headers=HEADERS, timeout=20,
                      follow_redirects=True, trust_env=False, proxy=proxies if proxies else None)
        if r.status_code == 200:
            title, text = html_to_text(r.text)
            if has_content(text) and "captcha" not in text.lower():
                return f"# {title}\n\n来源(存档): {url}\n\n{text}", "markdown"
    except Exception:
        pass
    return None, None

def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_url.py <URL> [输出TXT]")
        sys.exit(1)
    url = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    for name, fn in (("直连", try_direct), ("r.jina.ai", try_jina), ("archive.today", try_archive)):
        text, fmt = fn(url)
        if text:
            print(f"✅ 抓取成功（通道: {name}）")
            if out:
                with open(out, "w", encoding="utf-8") as f:
                    f.write(text)
                print(f"   已保存: {out}")
            else:
                sys.stdout.write(text)
            sys.exit(0)
        print(f"   通道 {name} 失败")

    print("ERROR: 所有抓取通道均失败")
    sys.exit(1)

if __name__ == "__main__":
    main()
