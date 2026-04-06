import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from llama_index.core import Document

SUPPORTED_EXTENSIONS = {".md", ".txt"}
URL_PATTERN = re.compile(r"https?://[^\s<>\"]+")
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
}


def load_documents_from_urls(data_dir: Path) -> list[Document]:
    url_entries = collect_url_entries(data_dir)
    if not url_entries:
        raise ValueError("没有读取到任何 URL，请检查 data/ 目录下的链接文件内容")

    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    documents = []
    failed_urls = []

    for url, source_file in url_entries:
        print(f"抓取: {url}")
        try:
            document = fetch_url_document(session, url, source_file, data_dir)
        except (requests.RequestException, ValueError) as exc:
            failed_urls.append((url, str(exc)))
            print(f"抓取失败: {url} ({exc})")
            continue

        documents.append(document)

    if not documents:
        failed_summary = "\n".join(f"- {url}: {error}" for url, error in failed_urls)
        raise ValueError(f"所有链接都抓取失败了：\n{failed_summary}")

    if failed_urls:
        print(f"警告: {len(failed_urls)} 个链接抓取失败，已跳过。")

    return documents


def collect_url_entries(data_dir: Path) -> list[tuple[str, Path]]:
    entries = []
    seen = set()

    for path in iter_link_files(data_dir):
        text = path.read_text(encoding="utf-8")
        urls = extract_urls(text)
        if not urls:
            print(f"跳过空链接文件: {path.relative_to(data_dir)}")
            continue

        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            entries.append((url, path))

    return entries


def iter_link_files(data_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in data_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def extract_urls(text: str) -> list[str]:
    urls = []
    seen = set()

    for match in URL_PATTERN.findall(text):
        url = match.rstrip("),.;!?]}>\"'")
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)

    return urls


def fetch_url_document(
    session: requests.Session, url: str, source_file: Path, data_dir: Path
) -> Document:
    response = session.get(url, timeout=(10, 30))
    response.raise_for_status()

    title, text = extract_page_content(response.text)
    if not text:
        raise ValueError(f"网页正文为空: {url}")

    if title and title not in text[:200]:
        content = f"{title}\n\n{text}"
    else:
        content = text

    relative_file = source_file.relative_to(data_dir)
    return Document(
        text=content,
        metadata={
            "file_name": relative_file.name,
            "source_file": str(relative_file),
            "source_url": url,
            "page_title": title or url,
        },
        id_=f"{relative_file}:{url}",
    )


def extract_page_content(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()

    title = extract_title(soup)
    content_root = soup.find("article") or soup.find("main") or soup.body or soup
    text = normalize_text(content_root.get_text("\n", strip=True))

    if len(text) < 200:
        text = normalize_text(soup.get_text("\n", strip=True))

    return title, text


def extract_title(soup: BeautifulSoup) -> str:
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"].strip()

    title_tag = soup.find("title")
    if title_tag and title_tag.text:
        return title_tag.text.strip()

    h1_tag = soup.find("h1")
    if h1_tag and h1_tag.text:
        return h1_tag.text.strip()

    return ""


def normalize_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
