import streamlit as st
import pandas as pd
import numpy as np
import json
import re
import sys
import os
import time
import warnings
import html
from urllib.parse import urlparse, quote, unquote
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
from datetime import datetime, timedelta, timezone
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from pyvi import ViTokenizer
from stopwordsiso import stopwords
import feedparser
import google.generativeai as genai
from dotenv import load_dotenv
import requests
# from streamlit_extras.app_logo import app_logo
# --- CẤU HÌNH TRANG VÀ CSS ---

st.set_page_config(page_title="Tạp chí của bạn", page_icon="📖", layout="wide")

# Load environment variables
load_dotenv()

# Các nguồn RSS để thu thập dữ liệu
RSS_URLS = [
    "https://dantri.com.vn/rss/home.rss",
    "https://dantri.com.vn/rss/xa-hoi.rss",
    "https://dantri.com.vn/rss/gia-vang.rss",
    "https://dantri.com.vn/rss/the-thao.rss",
    "https://dantri.com.vn/rss/giao-duc.rss",
    "https://dantri.com.vn/rss/kinh-doanh.rss",
    "https://dantri.com.vn/rss/giai-tri.rss",
    "https://dantri.com.vn/rss/phap-luat.rss",
    "https://dantri.com.vn/rss/cong-nghe.rss",
    "https://dantri.com.vn/rss/tinh-yeu-gioi-tinh.rss",
    "https://dantri.com.vn/rss/noi-vu.rss",
    "https://dantri.com.vn/rss/tam-diem.rss",
    "https://dantri.com.vn/rss/infographic.rss",
    "https://dantri.com.vn/rss/dnews.rss",
    "https://dantri.com.vn/rss/xo-so.rss",
    "https://dantri.com.vn/rss/tet-2025.rss",
    "https://dantri.com.vn/rss/d-buzz.rss",
    "https://dantri.com.vn/rss/su-kien.rss",
    "https://dantri.com.vn/rss/the-gioi.rss",
    "https://dantri.com.vn/rss/doi-song.rss",
    "https://dantri.com.vn/rss/lao-dong-viec-lam.rss",
    "https://dantri.com.vn/rss/tam-long-nhan-ai.rss",
    "https://dantri.com.vn/rss/bat-dong-san.rss",
    "https://dantri.com.vn/rss/du-lich.rss",
    "https://dantri.com.vn/rss/suc-khoe.rss",
    "https://dantri.com.vn/rss/o-to-xe-may.rss",
    "https://dantri.com.vn/rss/khoa-hoc.rss",
    "https://dantri.com.vn/rss/ban-doc.rss",
    "https://dantri.com.vn/rss/dmagazine.rss",
    "https://dantri.com.vn/rss/photo-news.rss",
    "https://dantri.com.vn/rss/toa-dam-truc-tuyen.rss",
    "https://dantri.com.vn/rss/interactive.rss",
    "https://dantri.com.vn/rss/photo-story.rss",
    "https://vnexpress.net/rss/tin-moi-nhat.rss",      # Trang chủ (thường là tin mới nhất)
    "https://vnexpress.net/rss/the-gioi.rss",
    "https://vnexpress.net/rss/thoi-su.rss",
    "https://vnexpress.net/rss/kinh-doanh.rss",
    "https://vnexpress.net/rss/startup.rss",
    "https://vnexpress.net/rss/giai-tri.rss",
    "https://vnexpress.net/rss/the-thao.rss",
    "https://vnexpress.net/rss/phap-luat.rss",
    "https://vnexpress.net/rss/giao-duc.rss",
    "https://vnexpress.net/rss/tin-noi-bat.rss",
    
    # # Cột bên phải
    "https://vnexpress.net/rss/suc-khoe.rss",
    "https://vnexpress.net/rss/doi-song.rss",
    "https://vnexpress.net/rss/du-lich.rss",
    "https://vnexpress.net/rss/khoa-hoc.rss",         # Khoa học công nghệ
    "https://vnexpress.net/rss/xe.rss",
    "https://vnexpress.net/rss/y-kien.rss",
    "https://vnexpress.net/rss/tam-su.rss",
    "https://vnexpress.net/rss/cuoi.rss",
    "https://vnexpress.net/rss/tin-xem-nhieu.rss",
    "https://thanhnien.vn/rss/home.rss",                   # Trang chủ
    "https://thanhnien.vn/rss/thoi-su.rss",
    "https://thanhnien.vn/rss/chinh-tri.rss",
    "https://thanhnien.vn/rss/chao-ngay-moi.rss",
    "https://thanhnien.vn/rss/the-gioi.rss",
    "https://thanhnien.vn/rss/kinh-te.rss",
    "https://thanhnien.vn/rss/doi-song.rss",
    "https://thanhnien.vn/rss/suc-khoe.rss",
    "https://thanhnien.vn/rss/gioi-tre.rss",
    "https://thanhnien.vn/rss/tieu-dung-thong-minh.rss",
    "https://thanhnien.vn/rss/giao-duc.rss",
    "https://thanhnien.vn/rss/du-lich.rss",
    "https://thanhnien.vn/rss/van-hoa.rss",
    "https://thanhnien.vn/rss/giai-tri.rss",
    "https://thanhnien.vn/rss/the-thao.rss",
    "https://thanhnien.vn/rss/cong-nghe.rss",
    "https://thanhnien.vn/rss/xe.rss",
    "https://thanhnien.vn/rss/thoi-trang-tre.rss",
    "https://thanhnien.vn/rss/ban-doc.rss",
    "https://thanhnien.vn/rss/rao-vat.rss",
    "https://thanhnien.vn/rss/video.rss",
    "https://thanhnien.vn/rss/dien-dan.rss",
    "https://thanhnien.vn/rss/podcast.rss",
    "https://thanhnien.vn/rss/nhat-ky-tet-viet.rss",
    "https://thanhnien.vn/rss/magazine.rss",
    "https://thanhnien.vn/rss/cung-con-di-tiep-cuoc-doi.rss",
    "https://thanhnien.vn/rss/ban-can-biet.rss",
    "https://thanhnien.vn/rss/cai-chinh.rss",
    "https://thanhnien.vn/rss/blog-phong-vien.rss",
    "https://thanhnien.vn/rss/toi-viet.rss",
    "https://thanhnien.vn/rss/viec-lam.rss",
    "https://thanhnien.vn/rss/tno.rss",
    "https://thanhnien.vn/rss/tin-24h.rss",
    "https://thanhnien.vn/rss/thi-truong.rss",
    "https://thanhnien.vn/rss/tin-nhanh-360.tno",
     # Cột bên trái
    "https://tuoitre.vn/rss/tin-moi-nhat.rss",  # Trang chủ
    "https://tuoitre.vn/rss/the-gioi.rss",
    "https://tuoitre.vn/rss/kinh-doanh.rss",
    "https://tuoitre.vn/rss/xe.rss",
    "https://tuoitre.vn/rss/van-hoa.rss",
    "https://tuoitre.vn/rss/the-thao.rss",
    "https://tuoitre.vn/rss/khoa-hoc.rss",
    "https://tuoitre.vn/rss/gia-that.rss",
    "https://tuoitre.vn/rss/ban-doc.rss",
    "https://tuoitre.vn/rss/video.rss",

    # Cột bên phải
    "https://tuoitre.vn/rss/thoi-su.rss",
    "https://tuoitre.vn/rss/phap-luat.rss",
    "https://tuoitre.vn/rss/cong-nghe.rss",
    "https://tuoitre.vn/rss/nhip-song-tre.rss",
    "https://tuoitre.vn/rss/giai-tri.rss",
    "https://tuoitre.vn/rss/giao-duc.rss",
    "https://tuoitre.vn/rss/suc-khoe.rss",
    "https://tuoitre.vn/rss/thu-gian.rss",
    "https://tuoitre.vn/rss/du-lich.rss"
]

# Initialize session state
if 'read_articles' not in st.session_state:
    st.session_state.read_articles = set()
if 'reading_history' not in st.session_state:
    st.session_state.reading_history = []
if 'current_view' not in st.session_state:
    st.session_state.current_view = "main"
if 'current_article_id' not in st.session_state:
    st.session_state.current_article_id = None
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = "Dành cho bạn (Tất cả)"
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = []
if 'update_log' not in st.session_state:
    st.session_state.update_log = ""
if 'update_error' not in st.session_state:
    st.session_state.update_error = ""
if 'update_success' not in st.session_state:
    st.session_state.update_success = False
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'processing_progress' not in st.session_state:
    st.session_state.processing_progress = {
        'step': '',
        'message': '',
        'progress': 0
    }

@st.cache_resource
def get_sbert_model():
    return SentenceTransformer('Cloyne/vietnamese-sbert-v3')

def local_css(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Lỗi: Không tìm thấy file '{file_name}'.")

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---
def get_source_name(link):
    try:
        domain = urlparse(link).netloc
        if domain.startswith('www.'): domain = domain[4:]
        return domain.split('.')[0].capitalize()
    except:
        return "N/A"

def normalize_title(title):
    return html.unescape(title).strip().lower()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_recent_articles(rss_urls, hours=24):
    """Fetch recent articles from RSS feeds."""
    articles = []
    seen_titles = set()
    seen_links = set()
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    for url in rss_urls:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            norm_title = normalize_title(entry.title)
            link = entry.link.strip()
            if norm_title in seen_titles or link in seen_links:
                continue
            published_time = entry.get("published", "")
            summary_raw = entry.get("summary", "")
            image_url = None
            if summary_raw:
                soup = BeautifulSoup(summary_raw, 'html.parser')
                img_tag = soup.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    image_url = img_tag['src']
            source_name = get_source_name(entry.link)
            if published_time:
                try:
                    parsed_time = parse_date(published_time).astimezone(timezone.utc)
                    if parsed_time >= time_threshold:
                        articles.append({
                            "title": entry.title,
                            "link": entry.link,
                            "summary_raw": summary_raw,
                            "published_time": parsed_time.isoformat(),
                            "image_url": image_url,
                            "source": source_name,
                            "source_name": source_name  # Thêm cột source_name
                        })
                        seen_titles.add(norm_title)
                        seen_links.add(link)
                except (ValueError, TypeError):
                    continue
    return pd.DataFrame(articles)

@st.cache_data(ttl=3600)
def clean_text(df):
    """Clean and process text from articles."""
    # Lưu lại các cột quan trọng
    important_columns = ['title', 'link', 'published_time', 'image_url', 'source', 'source_name']
    
    # Xử lý văn bản
    summary = (df['summary_raw']
               .str.lower()
               .str.replace(r'<.*?>', '', regex=True)
               .str.replace(r'[^\w\s]', '', regex=True))
    df['summary_cleaned'] = summary
    df.dropna(subset=['summary_cleaned'], inplace=True)
    df = df[df['summary_cleaned'].str.strip() != '']
    df = df[df['summary_cleaned'].str.split().str.len() >= 10]
    
    vi_stop = stopwords("vi")
    def remove_stop_pyvi(text):
        tokens = ViTokenizer.tokenize(text).split()
        filtered = [t for t in tokens if t not in vi_stop]
        return " ".join(filtered)
    
    df['summary_not_stop_word'] = df['summary_cleaned'].apply(remove_stop_pyvi)
    
    # Đảm bảo các cột quan trọng vẫn còn trong DataFrame
    for col in important_columns:
        if col not in df.columns:
            df[col] = df[col] if col in df.columns else None
            
    return df.reset_index(drop=True)

@st.cache_data(ttl=3600)
def vectorize_text(sentences, _model):
    """Vectorize text using S-BERT."""
    return _model.encode(sentences, show_progress_bar=True)

@st.cache_data(ttl=3600)
def generate_meaningful_topic_name(keywords, sample_titles):
    """Generate topic name using Gemini."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        prompt = f"""Bạn là một trợ lý biên tập báo chí. Dựa vào các thông tin dưới đây, hãy tạo ra chỉ duy nhất một tên chủ đề ngắn gọn (không quá 6 từ, không cần diễn giải) bằng tiếng Việt để tóm tắt nội dung chính.
        Các từ khóa chính của chủ đề: {keywords}
        Một vài tiêu đề bài viết ví dụ:
        - {"\n- ".join(sample_titles)}
        Tên chủ đề gợi ý:"""
        response = model.generate_content(prompt)
        return response.text.strip().replace("*", "")
    except Exception as e:
        return keywords

@st.cache_data(ttl=3600)
def get_topic_labels(df, num_keywords=5):
    """Generate topic labels for clusters."""
    topic_labels = {}
    actual_clusters = df['topic_cluster'].nunique()
    for i in range(actual_clusters):
        cluster_df = df[df['topic_cluster'] == i]
        cluster_texts = cluster_df['summary_cleaned'].tolist()
        if len(cluster_texts) < 3:
            topic_labels[str(i)] = "Chủ đề nhỏ (ít bài viết)"
            continue
        vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        tfidf_matrix = vectorizer.fit_transform(cluster_texts)
        avg_tfidf_scores = tfidf_matrix.mean(axis=0).A1
        top_indices = avg_tfidf_scores.argsort()[-num_keywords:][::-1]
        feature_names = vectorizer.get_feature_names_out()
        keywords = ", ".join([feature_names[j] for j in top_indices])
        sample_titles = cluster_df['title'].head(3).tolist()
        meaningful_name = generate_meaningful_topic_name(keywords, sample_titles)
        topic_labels[str(i)] = meaningful_name
    return topic_labels

@st.cache_data(ttl=3600)
def process_articles():
    """Main function to process articles and return all necessary data."""
    # Fetch and clean articles
    df = fetch_recent_articles(RSS_URLS, hours=24)
    if df.empty:
        return None, None, None, None
    
    df = clean_text(df)
    
    # Get SBERT model and vectorize
    sbert_model = get_sbert_model()
    embeddings = vectorize_text(df['summary_not_stop_word'].tolist(), _model=sbert_model)
    
    # Find optimal number of clusters
    silhouette_scores = []
    possible_k_values = range(2, 20)
    for k in possible_k_values:
        kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans_temp.fit_predict(embeddings)
        score = silhouette_score(embeddings, labels)
        silhouette_scores.append(score)
    
    best_k = possible_k_values[np.argmax(silhouette_scores)]
    
    # Perform final clustering
    kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    df['topic_cluster'] = kmeans.fit_predict(embeddings)
    
    # Generate topic labels
    topic_labels = get_topic_labels(df)
    
    # Calculate similarity matrix
    cosine_sim = cosine_similarity(embeddings)
    
    return df, cosine_sim, topic_labels, embeddings

# --- HÀM HIỂN THỊ (RENDER) ---
def render_main_grid(df, selected_topic_name):
    st.header(f"Bảng tin: {selected_topic_name}")
    st.markdown(f"Tìm thấy **{len(df)}** bài viết liên quan.")
    st.markdown("---")
    num_columns = 3
    cols = st.columns(num_columns)
    if df.empty:
        st.warning("Không có bài viết nào phù hợp với lựa chọn của bạn.")
    else:
        for i, (index, row) in enumerate(df.iterrows()):
            with cols[i % num_columns]:
                # Xử lý hình ảnh với placeholder
                image_html = ''
                if pd.notna(row["image_url"]):
                    image_html = f'<div class="card-image-container"><img src="{row["image_url"]}" onerror="this.onerror=null; this.src=\'no-image-png-2.webp\';"></div>'
                else:
                    image_html = '<div class="card-image-container"><img src="no-image-png-2.webp"></div>'
                
                # Sử dụng cột 'source_name' đã tạo
                source_name = row['source_name']


                card_html = f"""<div class="article-card">
                                {image_html}
                                <div class="article-content">
                                    <div class="article-title">{row['title']}</div>
                                    <div class="article-source">{source_name}</div>
                                </div>
                           </div>"""
                st.markdown(card_html, unsafe_allow_html=True)
                if st.button("Đọc bài viết", key=f"read_{index}"):
                    st.session_state.current_article_id = index
                    st.session_state.current_view = "detail"
                    st.rerun()

                

def calculate_interest_vector(df, cosine_sim, article_ids):
    """Calculate interest vector from reading history."""
    if not article_ids:
        return None
    
    # Get vectors for articles in history
    vectors = []
    for article_id in article_ids:
        if article_id < len(cosine_sim):
            vectors.append(cosine_sim[article_id])
    
    if not vectors:
        return None
    
    # Calculate average vector
    avg_vector = np.mean(vectors, axis=0)
    return avg_vector

def update_interest_vector(df, cosine_sim, article_id):
    """Update interest vector when new article is read."""
    if article_id not in st.session_state.reading_history:
        # Add to reading history (keep last 5)
        st.session_state.reading_history.insert(0, article_id)
        st.session_state.reading_history = st.session_state.reading_history[:5]
        
        # Calculate new interest vector
        st.session_state.interest_vector = calculate_interest_vector(
            df, cosine_sim, st.session_state.reading_history
        )
        
        # Update interest articles if vector exists
        if st.session_state.interest_vector is not None:
            similarity_scores = cosine_similarity([st.session_state.interest_vector], cosine_sim)[0]
            # Create mask to exclude read articles
            mask = ~df.index.isin(st.session_state.reading_history)
            similarity_scores[~mask] = -1  # Set similarity to -1 for read articles
            # Get top similar articles
            top_indices = np.argsort(similarity_scores)[::-1][:10]
            st.session_state.interest_articles = df.iloc[top_indices].copy()
            st.session_state.interest_articles['similarity_score'] = similarity_scores[top_indices]

def get_interest_articles():
    """Get articles based on user's interests."""
    if st.session_state.interest_articles is not None:
        return st.session_state.interest_articles
    return pd.DataFrame()

def calculate_average_vector(article_ids, cosine_sim):
    """Calculate average vector from last 5 articles."""
    if not article_ids:
        return None
    
    vectors = []
    for article_id in article_ids:
        if article_id < len(cosine_sim):
            vectors.append(cosine_sim[article_id])
    
    if not vectors:
        return None
    
    return np.mean(vectors, axis=0)

def get_similar_articles_by_history(df, cosine_sim, history_articles, exclude_articles=None):
    """Get similar articles based on reading history."""
    if not history_articles:
        return pd.DataFrame()
    
    # Chỉ lấy 5 bài viết mới đọc gần nhất
    recent_articles = history_articles[:5]
    
    avg_vector = calculate_average_vector(recent_articles, cosine_sim)
    if avg_vector is None:
        return pd.DataFrame()
    
    # Calculate similarity scores
    similarity_scores = cosine_similarity([avg_vector], cosine_sim)[0]
    
    # Create mask to exclude read articles
    if exclude_articles:
        mask = ~df.index.isin(exclude_articles)
        similarity_scores[~mask] = -1
    
    # Get top similar articles
    top_indices = np.argsort(similarity_scores)[::-1][:10]
    similar_articles = df.iloc[top_indices].copy()
    similar_articles['similarity_score'] = similarity_scores[top_indices]
    
    return similar_articles

def crawl_article_content(url):
    """Crawl nội dung bài viết từ URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # Xử lý lazy load ảnh: chuyển data-src thành src
        for img in soup.find_all('img'):
            if img.has_attr('data-src'):
                img['src'] = img['data-src']
            # Xóa img không có src hoặc src rỗng
            if not img.has_attr('src') or not img['src'].strip():
                img.decompose()

        # Xóa các figure rỗng hoặc chỉ chứa ảnh lỗi
        for fig in soup.find_all('figure'):
            if not fig.text.strip() and not fig.find('img'):
                fig.decompose()

        # VnExpress
        if 'vnexpress.net' in url:
            article = soup.find('article', class_='fck_detail')
            if not article:
                # fallback: lấy article đầu tiên
                article = soup.find('article')
            if article:
                # Xóa các thẻ không cần thiết
                for tag in article.find_all(['script', 'style', 'iframe']):
                    tag.decompose()
                return str(article)

        # Tuổi Trẻ, Thanh Niên
        elif 'tuoitre.vn' in url or 'thanhnien.vn' in url:
            article = soup.find('div', class_='detail-content')
            if not article:
                # fallback: lấy div lớn nhất
                divs = soup.find_all('div')
                article = max(divs, key=lambda d: len(d.text)) if divs else None
            if article:
                for tag in article.find_all(['script', 'style', 'iframe']):
                    tag.decompose()
                return str(article)

        # Dân trí
        elif 'dantri.com.vn' in url:
            article = soup.find('div', class_='dt-news__content')
            if not article:
                # fallback: lấy article đầu tiên
                article = soup.find('article')
            if not article:
                # fallback: lấy div lớn nhất
                divs = soup.find_all('div')
                article = max(divs, key=lambda d: len(d.text)) if divs else None
            if article:
                for tag in article.find_all(['script', 'style', 'iframe']):
                    tag.decompose()
                return str(article)

        return None
    except Exception as e:
        print(f"Lỗi khi crawl bài viết: {str(e)}")
        return None

def render_detail_view(article_id, df, cosine_sim, topic_labels):
    try:
        article = df.loc[article_id]
    except KeyError:
        st.error("Không tìm thấy bài viết.")
        if st.button("⬅️ Quay lại danh sách"):
            st.session_state.current_view = "main"
            st.session_state.current_article_id = None
            st.rerun()
        return
    
    # Add article to read articles set and update reading history
    st.session_state.read_articles.add(article_id)
    if article_id not in st.session_state.reading_history:
        st.session_state.reading_history.insert(0, article_id)
    
    # Ẩn thanh bên và ảnh trong nội dung bài viết
    st.markdown("""
        <style>
            [data-testid="stSidebar"][aria-expanded="true"]{
                display: none;
            }
            /* Cỡ chữ cho toàn bộ nội dung article */
            article {
                font-size: 10px !important;
                line-height: 1.7 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            /* Cỡ chữ cho các class detail */
            .article-content, .fck_detail, .detail-content, .dt-news__content {
                font-size: 15px !important;
                line-height: 1.6 !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            .article-content img,
            .fck_detail img,
            .detail-content img,
            .dt-news__content img {
                max-width: 800px !important;
                height: auto !important;
                display: block;
                margin: 10px auto 10px auto;
                border-radius: 8px;
                box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            }
            .recommendation-image {
                width: 240px !important;
                height: 140px !important;
                object-fit: cover !important;
                border-radius: 6px !important;
                box-shadow: 0 1px 2px rgba(0,0,0,0.08) !important;
                margin-right: 8px !important;
                display: block;
            }
            .block-container .stColumns {
                gap: 0 !important;
            }
            .recommendation-caption {
                font-size: 11px !important;
                color: #888;
                margin-top: 2px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100%;
                display: block;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Nút quay lại
    if st.button("⬅️ Quay lại danh sách"):
        st.session_state.current_view = "main"
        st.session_state.current_article_id = None
        st.rerun()
    
    st.title(article['title'])
    
    # Chuyển đổi thời gian đăng bài
    try:
        published_time = pd.to_datetime(article['published_time'])
        vn_time = published_time.tz_convert('Asia/Ho_Chi_Minh')
        time_str = vn_time.strftime('%d-%m-%Y %H:%M')
    except:
        time_str = article['published_time']
    
    st.caption(f"Nguồn: {article['source_name']} | Xuất bản: {time_str}")
    st.markdown("---")
    
    # Crawl và hiển thị nội dung bài viết
    with st.spinner("Đang tải nội dung bài viết..."):
        article_content = crawl_article_content(article['link'])
        
    if article_content:
        # Hiển thị nội dung bài viết
        st.markdown(article_content, unsafe_allow_html=True)
        
        # Thêm CSS để định dạng nội dung
        st.markdown("""
            <style>
                .article-content p {
                    font-size: 10px;
                    line-height: 1.6;
                    margin: 10px 0;
                }
                .article-content h1, .article-content h2, .article-content h3 {
                    margin: 20px 0 10px 0;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        # Nếu không crawl được, hiển thị tóm tắt
        st.subheader("Tóm tắt")
        summary_raw = article.get('summary_raw', '')
        summary_without_img = re.sub(r'<img[^>]*>', '', summary_raw, flags=re.IGNORECASE)
        st.markdown(summary_without_img, unsafe_allow_html=True)
    
    # Nút đọc bài viết gốc
    st.link_button("Đọc toàn bộ bài viết trên trang gốc", article['link'])
    
    # Phần bài viết liên quan
    st.markdown("---")
    st.subheader("Khám phá thêm")
    rec_type = st.radio("Hiển thị các bài viết:", ("Có nội dung tương tự", "Trong cùng chủ đề"), key=f"rec_type_{article_id}")
    
    if rec_type == "Có nội dung tương tự":
        st.markdown("##### Dựa trên phân tích ngữ nghĩa:")
        sim_scores = sorted(list(enumerate(cosine_sim[article_id])), key=lambda x: x[1], reverse=True)[1:6]
        for i, (article_index, score) in enumerate(sim_scores):
            rec_article = df.iloc[article_index]
            with st.container(border=True):
                rec_col1, rec_col2 = st.columns([0.13, 0.87])  # Ảnh nhỏ hơn, chữ rộng hơn
                with rec_col1:
                    if pd.notna(rec_article['image_url']):
                        st.markdown(f'<img src="{rec_article["image_url"]}" onerror="this.onerror=null; this.src=\'no-image-png-2.webp\';" class="recommendation-image">', unsafe_allow_html=True)
                    else:
                        st.markdown('<img src="no-image-png-2.webp" class="recommendation-image">', unsafe_allow_html=True)
                with rec_col2:
                    if st.button(rec_article['title'], key=f"rec_{article_index}"):
                        st.session_state.current_article_id = article_index
                        st.rerun()
                    st.markdown(f'<div class="recommendation-caption">Nguồn: {rec_article["source_name"]} | Độ tương đồng: {score:.2f}</div>', unsafe_allow_html=True)
    else:
        cluster_id = article['topic_cluster']
        topic_name = topic_labels.get(str(cluster_id), "N/A")
        st.markdown(f"##### Thuộc chủ đề: **{topic_name}**")
        same_cluster_df = df[(df['topic_cluster'] == cluster_id) & (df.index != article_id)].head(5)
        for i, row in same_cluster_df.iterrows():
            with st.container(border=True):
                rec_col1, rec_col2 = st.columns([0.13, 0.87])  # Ảnh nhỏ hơn, chữ rộng hơn
                with rec_col1:
                    if pd.notna(row['image_url']):
                        st.markdown(f'<img src="{row["image_url"]}" onerror="this.onerror=null; this.src=\'no-image-png-2.webp\';" class="recommendation-image">', unsafe_allow_html=True)
                    else:
                        st.markdown('<img src="no-image-png-2.webp" class="recommendation-image">', unsafe_allow_html=True)
                with rec_col2:
                    if st.button(row['title'], key=f"rec_{i}"):
                        st.session_state.current_article_id = i
                        st.rerun()
                    similarity_score = cosine_sim[article_id][i]
                    st.markdown(f'<div class="recommendation-caption">Nguồn: {row["source_name"]} | Độ tương đồng: {similarity_score:.2f}</div>', unsafe_allow_html=True)

def render_search_results(query, df, embeddings, sbert_model):
    """Vector hóa truy vấn và hiển thị kết quả tìm kiếm."""
    st.header(f"Kết quả tìm kiếm cho: \"{query}\"")
    # Vector hóa câu truy vấn
    with st.spinner("Đang phân tích và tìm kiếm..."):
        query_vector = sbert_model.encode([query])
        # Tính toán độ tương đồng
        similarities = cosine_similarity(query_vector, embeddings)[0]
        # Sắp xếp và lấy kết quả
        sim_scores = sorted(list(enumerate(similarities)), key=lambda x: x[1], reverse=True)
        result_indices = [i[0] for i in sim_scores]
        result_df = df.iloc[result_indices].copy()
    render_main_grid(result_df, f"Kết quả cho: \"{query}\"")

# --- LUỒNG CHÍNH CỦA ỨNG DỤNG ---
local_css("style.css")

# --- PHẦN LOGIC MỚI: QUẢN LÝ TRẠNG THÁI ---
if 'update_log' not in st.session_state:
    st.session_state.update_log = ""
if 'update_error' not in st.session_state:
    st.session_state.update_error = ""
if 'update_success' not in st.session_state:
    st.session_state.update_success = False

# Initialize session state for reading history and interest tracking
if 'reading_history' not in st.session_state:
    st.session_state.reading_history = []
if 'interest_vector' not in st.session_state:
    st.session_state.interest_vector = None
if 'interest_articles' not in st.session_state:
    st.session_state.interest_articles = None

def update_processing_progress(step, message, progress):
    """Cập nhật tiến trình xử lý."""
    st.session_state.processing_progress = {
        'step': step,
        'message': message,
        'progress': progress
    }

def append_update_log(message):
    if 'update_log' not in st.session_state:
        st.session_state.update_log = ""
    st.session_state.update_log += f"{message}\n"

def process_in_background():
    """Xử lý dữ liệu trong nền."""
    try:
        # Reset trạng thái
        st.session_state.update_error = ""
        st.session_state.update_success = False
        
        # Bước 1: Tải bài viết mới
        append_update_log("Bắt đầu cập nhật dữ liệu...")
        update_processing_progress('Bắt đầu', 'Đang tải bài viết mới...', 10)
        df = fetch_recent_articles(RSS_URLS, hours=24)
        append_update_log(f"Đã lấy {len(df)} bài viết mới.")

        if df.empty:
            st.session_state.update_error = "Không tìm thấy bài viết mới nào."
            append_update_log("Không tìm thấy bài viết mới nào.")
            return

        update_processing_progress('Làm sạch', 'Đang xử lý văn bản...', 30)
        append_update_log("Bắt đầu làm sạch dữ liệu...")
        df = clean_text(df)
        append_update_log(f"Sau làm sạch còn {len(df)} bài viết.")

        if df.empty:
            st.session_state.update_error = "Không có bài viết nào sau khi làm sạch dữ liệu."
            append_update_log("Không có bài viết nào sau khi làm sạch dữ liệu.")
            return

        update_processing_progress('Vector hóa', 'Đang vector hóa nội dung...', 50)
        append_update_log("Bắt đầu vector hóa nội dung...")
        sbert_model = get_sbert_model()
        embeddings = vectorize_text(df['summary_not_stop_word'].tolist(), _model=sbert_model)
        append_update_log("Đã vector hóa xong.")

        update_processing_progress('Phân cụm', 'Đang phân tích chủ đề...', 70)
        append_update_log("Bắt đầu phân cụm chủ đề...")
        silhouette_scores = []
        possible_k_values = range(2, min(20, len(df) // 2))  # Giới hạn số cụm dựa trên số lượng bài viết
        for k in possible_k_values:
            kmeans_temp = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans_temp.fit_predict(embeddings)
            score = silhouette_score(embeddings, labels)
            silhouette_scores.append(score)
        
        best_k = possible_k_values[np.argmax(silhouette_scores)]
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df['topic_cluster'] = kmeans.fit_predict(embeddings)
        append_update_log(f"Đã phân cụm thành {best_k} chủ đề.")

        update_processing_progress('Gán nhãn', 'Đang tạo nhãn chủ đề...', 85)
        append_update_log("Bắt đầu gán nhãn chủ đề...")
        topic_labels = get_topic_labels(df)
        append_update_log("Đã gán nhãn chủ đề.")

        update_processing_progress('Hoàn tất', 'Đang tính toán ma trận tương đồng...', 95)
        append_update_log("Bắt đầu tính toán ma trận tương đồng...")
        cosine_sim = cosine_similarity(embeddings)
        append_update_log("Đã tính toán xong ma trận tương đồng.")

        st.session_state.processed_data = {
            'df': df,
            'cosine_sim': cosine_sim,
            'topic_labels': topic_labels,
            'embeddings': embeddings
        }
        update_processing_progress('Hoàn tất', 'Đã cập nhật xong!', 100)
        st.session_state.update_success = True
        append_update_log("Cập nhật hoàn tất!")
    except Exception as e:
        st.session_state.update_error = f"Lỗi không xác định: {str(e)}"
        append_update_log(f"Lỗi: {str(e)}")
    finally:
        st.session_state.is_processing = False

# Khởi tạo dữ liệu ban đầu
if 'processed_data' not in st.session_state:
    st.session_state.update_log = ""
    # Lần đầu chạy, xử lý dữ liệu
    df, cosine_sim, topic_labels, embeddings = process_articles()
    if df is not None:
        st.session_state.processed_data = {
            'df': df,
            'cosine_sim': cosine_sim,
            'topic_labels': topic_labels,
            'embeddings': embeddings
        }
        st.write("### Nhật ký xử lý dữ liệu")
        st.code(st.session_state.update_log, language="log")
    else:
        df = pd.DataFrame()
        cosine_sim = None
        topic_labels = {}
        embeddings = None
else:
    # Lấy dữ liệu từ session state
    processed_data = st.session_state.processed_data
    df = processed_data.get('df', pd.DataFrame())
    cosine_sim = processed_data.get('cosine_sim', None)
    topic_labels = processed_data.get('topic_labels', {})
    embeddings = processed_data.get('embeddings', None)

sbert_model = get_sbert_model()

# --- GIAO DIỆN THANH BÊN ---
st.sidebar.title("Tạp chí của bạn")
st.sidebar.markdown("---")

# Cập nhật phần hiển thị tiến trình trong sidebar
if st.sidebar.button("🔄 Cập nhật tin tức mới", use_container_width=True, disabled=st.session_state.is_processing):
    st.session_state.is_processing = True
    st.session_state.update_error = ""
    st.session_state.update_success = False
    process_in_background()

# Hiển thị tiến trình xử lý
if st.session_state.is_processing:
    progress = st.session_state.processing_progress
    st.sidebar.progress(progress['progress'] / 100)
    st.sidebar.info(f"**{progress['step']}**: {progress['message']}")

# Hiển thị kết quả cập nhật
if st.session_state.update_error:
    st.sidebar.error("❌ Cập nhật thất bại!")
    with st.sidebar.expander("Xem chi tiết lỗi"):
        st.code(st.session_state.update_error)
    if st.sidebar.button("Thử lại", use_container_width=True, key="retry_button"):
        st.session_state.update_error = ""
        st.rerun()

if st.session_state.update_success:
    st.sidebar.success("✅ Cập nhật hoàn tất!")
    if st.sidebar.button("Xem tin tức mới", use_container_width=True, key="view_new_button"):
        # Cập nhật dữ liệu chính
        if 'processed_data' in st.session_state:
            processed_data = st.session_state.processed_data
            df = processed_data.get('df', pd.DataFrame())
            cosine_sim = processed_data.get('cosine_sim', None)
            topic_labels = processed_data.get('topic_labels', {})
            embeddings = processed_data.get('embeddings', None)
        st.session_state.update_success = False
        st.rerun()

if st.session_state.is_processing or st.session_state.update_log:
    st.sidebar.markdown("#### Nhật ký cập nhật")
    st.sidebar.code(st.session_state.update_log, language="log")

st.sidebar.markdown("---")

# --- Ô TÌM KIẾM SEMANTIC Ở HEADER ---
search_col1, search_col2 = st.columns([0.85, 0.15])
with search_col1:
    search_input = st.text_input(
        "Tìm kiếm bài viết (theo ngữ nghĩa, nhập từ khóa hoặc câu hỏi):",
        value=st.session_state.get('search_query', ''),
        key="search_input",
        placeholder="Nhập nội dung bạn muốn tìm...",
        label_visibility="collapsed"
    )
with search_col2:
    search_button = st.button("🔍 Tìm kiếm", use_container_width=True, key="search_button")

if search_input and (search_button or search_input != st.session_state.get('search_query', '')):
    st.session_state['search_query'] = search_input
    st.session_state['current_view'] = "search"
    st.rerun()

if st.session_state.get('current_view', 'main') == "search" and st.session_state.get('search_query', ''):
    with st.spinner("Đang phân tích và tìm kiếm..."):
        query_vector = sbert_model.encode([st.session_state['search_query']])
        similarities = cosine_similarity(query_vector, embeddings)[0]
        sim_scores = sorted(list(enumerate(similarities)), key=lambda x: x[1], reverse=True)
        result_indices = [i[0] for i in sim_scores]
        result_df = df.iloc[result_indices].copy()
    st.sidebar.info("Bạn đang ở trang kết quả tìm kiếm. Chọn danh mục khác hoặc bấm 'Quay lại' để trở về.")
    if st.sidebar.button("⬅️ Quay lại trang chủ", use_container_width=True, key="back_to_main"):
        st.session_state['search_query'] = ''
        st.session_state['current_view'] = "main"
        st.rerun()
    render_main_grid(result_df, f"Kết quả cho: \"{st.session_state['search_query']}\"")
    st.stop()
elif st.session_state.current_view == "detail" and st.session_state.current_article_id is not None:
    render_detail_view(st.session_state.current_article_id, df, cosine_sim, topic_labels)
else:
    if df is None:
        st.error("Lỗi: Không thể tải dữ liệu. Vui lòng bấm nút 'Cập nhật tin tức mới' ở thanh bên.")
    else:
        # --- PHẦN LỌC THEO CHỦ ĐỀ ---
        st.sidebar.subheader("Khám phá các chủ đề")
        topic_display_list = ["Dành cho bạn (Tất cả)", "Bài viết đã đọc", "Dựa trên lịch sử đọc"] + [f"{v} ({k})" for k, v in topic_labels.items()]
        
        st.sidebar.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        for topic in topic_display_list:
            is_active = (topic == st.session_state.selected_topic)
            active_class = "active" if is_active else ""
            icon = "📖" if topic != "Bài viết đã đọc" and topic != "Dựa trên lịch sử đọc" else "👁️" if topic == "Bài viết đã đọc" else "🎯"
            if st.sidebar.button(f"{icon} {topic}", key=f"topic_{topic.replace(' ', '_')}", use_container_width=True):
                st.session_state.selected_topic = topic
                st.rerun()
        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        st.sidebar.markdown("---")

        # --- BỔ SUNG: PHẦN LỌC THEO NGUỒN ---
        st.sidebar.subheader("Lọc theo nguồn")
        all_sources = sorted(df['source_name'].unique().tolist())
        selected_sources = st.sidebar.multiselect(
            "Chọn một hoặc nhiều nguồn:",
            options=all_sources,
            default=st.session_state.selected_sources
        )
        
        if selected_sources != st.session_state.selected_sources:
            st.session_state.selected_sources = selected_sources
            st.rerun()

        # --- HIỂN THỊ VIEW TƯƠNG ỨNG ---
        if st.session_state.selected_topic == "Bài viết đã đọc":
            if st.session_state.read_articles:
                # Lấy danh sách bài viết đã đọc theo thứ tự trong reading_history (mới nhất lên đầu)
                ordered_articles = [article_id for article_id in st.session_state.reading_history if article_id in st.session_state.read_articles]
                # Tạo DataFrame với thứ tự đã sắp xếp
                display_df = df[df.index.isin(ordered_articles)].copy()
                # Sắp xếp lại theo thứ tự trong ordered_articles
                display_df = display_df.reindex(ordered_articles)
            else:
                display_df = pd.DataFrame()
                st.info("Bạn chưa đọc bài viết nào.")
        elif st.session_state.selected_topic == "Dựa trên lịch sử đọc":
            if len(st.session_state.reading_history) > 0:
                display_df = get_similar_articles_by_history(
                    df, cosine_sim,
                    st.session_state.reading_history,
                    exclude_articles=st.session_state.read_articles
                )
                if display_df.empty:
                    st.info("Không tìm thấy bài viết tương tự dựa trên lịch sử đọc.")
            else:
                display_df = pd.DataFrame()
                st.info("Bạn chưa có lịch sử đọc bài viết nào.")
        elif st.session_state.selected_topic != "Dành cho bạn (Tất cả)":
            # Tách cluster ID từ tên chủ đề (format: "Tên chủ đề (cluster_id)")
            topic_parts = st.session_state.selected_topic.split(" (")
            if len(topic_parts) > 1:
                try:
                    cluster_id = int(topic_parts[1].rstrip(")"))
                    display_df = df[df['topic_cluster'] == cluster_id].copy()
                except ValueError:
                    # Xử lý các trường hợp đặc biệt như "Bài viết đã đọc" và "Dựa trên lịch sử đọc"
                    if st.session_state.selected_topic == "Bài viết đã đọc":
                        # ... xử lý bài viết đã đọc ...
                        display_df = df[df['topic_cluster'] == cluster_id].copy()
                    elif st.session_state.selected_topic == "Dựa trên lịch sử đọc":
                        # ... xử lý bài viết dựa trên lịch sử ...
                        display_df = pd.DataFrame()
                    else:
                        display_df = pd.DataFrame()
            else:
                display_df = pd.DataFrame()
        else:
            display_df = df.copy()

        # Áp dụng bộ lọc nguồn
        if st.session_state.selected_sources:
            display_df = display_df[display_df['source_name'].isin(st.session_state.selected_sources)]

        # Sắp xếp và hiển thị
        if not display_df.empty:
            # Chỉ sắp xếp theo thời gian đăng nếu không phải là bài viết đã đọc
            if st.session_state.selected_topic != "Bài viết đã đọc":
                display_df = display_df.sort_values(by='published_time', ascending=False)
        render_main_grid(display_df, st.session_state.selected_topic)
