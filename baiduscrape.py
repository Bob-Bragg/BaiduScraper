import re
import json
import requests
import urllib.parse
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def resolve_baidu_redirect(url):
    """Follow Baidu's redirect URL and return the final destination."""
    try:
        r = requests.head(url, allow_redirects=True, timeout=5, headers=HEADERS)
        return r.url
    except requests.RequestException:
        return url  # fallback to original if resolution fails

def search_baidu(query, max_pages=3):
    """Search Baidu for a given query and return list of result dicts."""
    results = []
    for page in range(max_pages):
        pn = page * 10  # Baidu pagination: 10 results per page
        url = f"https://www.baidu.com/s?pn={pn}&wd={urllib.parse.quote(query)}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                print(f"[!] Error fetching page {page+1} (status {resp.status_code})")
                continue
        except requests.RequestException as e:
            print(f"[!] Network error on page {page+1}: {e}")
            continue

        # Extract titles and links
        title_regex = re.compile(r'<h3 class="t.*?"><a.*?href="(.*?)".*?>(.*?)</a>', re.S)
        matches = title_regex.findall(resp.text)

        for href, title in matches:
            clean_title = re.sub(r'<.*?>', '', title).strip()
            final_url = resolve_baidu_redirect(href)
            results.append({"title": clean_title, "url": final_url})

    return results

def save_to_json(results, filename="baidu_cyber_news.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved {len(results)} results to {filename}")

if __name__ == "__main__":
    query = "网络安全 新闻"  # "cybersecurity news"
    print(f"[*] Searching Baidu for: {query}")
    baidu_results = search_baidu(query, max_pages=3)
    for r in baidu_results:
        print(f"[+] {r['title']}\n    {r['url']}\n")

    save_to_json(baidu_results)
