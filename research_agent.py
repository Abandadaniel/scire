from langchain_ollama import ChatOllama
from langchain_community.tools import DuckDuckGoSearchRun
from typing import Dict, Any
import time
from profanity_filter import ProfanityFilter

from newspaper import Article
from langdetect import detect
from deep_translator import GoogleTranslator
import feedparser
try:
    from newsapi import NewsApiClient
    NEWSAPI_AVAILABLE = True
except ImportError:
    NewsApiClient = None
    NEWSAPI_AVAILABLE = False
import os

class FastResearchAgent:
    def __init__(self):
        self.llm = ChatOllama(
            model="llama3.2:3b",
            temperature=0.5,
            base_url="http://localhost:11434",
            num_predict=512,
        )
        
        self.search_tool = DuckDuckGoSearchRun()
        self.translator = GoogleTranslator()
        self.profanity_filter = ProfanityFilter()
        
        
        newsapi_key = os.getenv('NEWSAPI_KEY')
        self.newsapi = NewsApiClient(api_key=newsapi_key) if newsapi_key and NEWSAPI_AVAILABLE else None
        
        self._cache = {}
        self.history = []
        self.news_sources = [
            "Al Jazeera Africa",
            "BBC Africa",
            "Africanews",
            "Reuters Africa",
            "Voice of America Africa",
            "RFI Afrique",
            "Jeune Afrique",
            "Sahara Reporters",
            "The Africa Report",
            "Premium Times",
            "Khaama Press"
        ]
        self.rss_feeds = [
            'http://feeds.bbci.co.uk/news/africa/rss.xml',
            'https://www.aljazeera.com/xml/rss/all.xml',
            'https://www.reuters.com/rssFeed/africaNews/',
            'https://www.voanews.com/api/zq$ome$',
            'https://www.africanews.com/rss.xml'
        ]
    
    def _build_history_context(self) -> str:
        if not self.history:
            return ""
        parts = ["Conversation history:"]
        for message in self.history[-8:]:
            parts.append(f"{message['role'].capitalize()}: {message['content']}")
        return "\n".join(parts) + "\n\n"
    
    def _fetch_rss_news(self, query: str) -> str:
        """Fetch news from RSS feeds"""
        results = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:  
                    title = entry.title
                    summary = getattr(entry, 'summary', '')
                    link = entry.link
                    if query.lower() in (title + summary).lower():
                        results.append(f"{title} - {link} - {summary[:200]}")
            except:
                pass
        return "\n".join(results[:10])  
    
    def _fetch_newsapi_news(self, query: str) -> str:
        """Fetch news from NewsAPI"""
        if not self.newsapi:
            return ""
        try:
            articles = self.newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=5)
            results = []
            for article in articles['articles']:
                title = article['title']
                description = article.get('description', '')
                url = article['url']
                results.append(f"{title} - {url} - {description}")
            return "\n".join(results)
        except:
            return ""
    
    def _scrape_news_sites(self, query: str) -> str:
        """Scrape specific news sites for Africa/Sahel"""
        results = []
        sites = ['https://www.aljazeera.com/africa/', 'https://www.bbc.com/news/world-africa']
        for site in sites:
            try:
                article = Article(site)
                article.download()
                article.parse()
                if query.lower() in article.text.lower():
                    results.append(f"{article.title} - {site} - {article.text[:300]}")
            except:
                pass
        return "\n".join(results[:5])
    
    def _search_wrapper(self, query: str) -> str:
        """Wrapper for search tool with multiple sources"""
        try:
            try:
                detected_lang = detect(query)
                if detected_lang != 'en':
                    query = self.translator.translate(query, target='en')
            except:
                pass
            
            
            results = []
            
            try:
                ddg_results = self.search_tool.run(query)
                results.append(f"DuckDuckGo: {ddg_results[:1000]}")
            except:
                pass
            
            rss_results = self._fetch_rss_news(query)
            if rss_results:
                results.append(f"RSS Feeds: {rss_results}")
            
            newsapi_results = self._fetch_newsapi_news(query)
            if newsapi_results:
                results.append(f"NewsAPI: {newsapi_results}")
            
            scrape_results = self._scrape_news_sites(query)
            if scrape_results:
                results.append(f"Web Scraping: {scrape_results}")
            
            return "\n\n".join(results)[:2000]  
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def _extract_wrapper(self, url: str) -> str:
        """Extract content from URL"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            return article.text[:1000]
        except Exception as e:
            return f"Extraction error: {str(e)}"
    
    def research_fast(self, query: str) -> Dict[str, Any]:
        """Fast research with caching and conversational context."""
        start_time = time.time()
        
        recent_history = tuple((m['role'], m['content']) for m in self.history[-8:])
        time_sensitive_keywords = ['current', 'today', 'now', 'recent', 'latest', 'breaking', 'live', 'status', 'situation', 'update']
        is_time_sensitive = any(keyword in query.lower() for keyword in time_sensitive_keywords)
        
        if is_time_sensitive:
            cache_key = None
        else:
            cache_key = (query.lower().strip(), recent_history)
        
        if cache_key and cache_key in self._cache:
            cache_time, cached_result = self._cache[cache_key]
            if time.time() - cache_time < 300:
                return cached_result
        
        try:
            self.history.append({'role': 'user', 'content': query})
            history_context = self._build_history_context()
            news_sources_text = ", ".join(self.news_sources)
            
            research_keywords = ['latest', 'news', 'what is', 'how to', 'explain', 'research', 'find', 'search', 'update', 'developments', 'current', 'today', 'now', 'recent', 'breaking', 'live', 'status', 'situation']
            time_sensitive_keywords = ['current', 'today', 'now', 'recent', 'latest', 'breaking', 'live', 'status', 'situation', 'update']
            is_research = any(keyword in query.lower() for keyword in research_keywords)
            is_time_sensitive = any(keyword in query.lower() for keyword in time_sensitive_keywords)
            
            if is_research or is_time_sensitive:
                search_query = query
                try:
                    detected_lang = detect(query)
                    if detected_lang != 'en':
                        search_query = self.translator.translate(query, target='en')
                except:
                    pass
                
                search_results = self._search_wrapper(search_query)
                
                prompt = f"""You are Scire, a fast multilingual research assistant.

                RULES:
                1. Give CONCISE answers (max 3-4 sentences)
                2. Be DIRECT - no fluff
                3. Automatically censor any profanity
                4. Respond in the user's language

                IMPORTANT: Use ONLY the provided search results for current and factual information. Do not rely on pre-trained knowledge. Always prioritize the most recent data from the search results.

                News focus: Prefer coverage from Africa and the Sahel region where possible. Use sources such as {news_sources_text}.

                {history_context}
                User query: {query}

                Search results: {search_results}

                Provide a concise answer based ONLY on the search results and the conversation history."""
                
                response_text = self.llm.invoke(prompt).content
            else:
                prompt = f"""You are Scire, a fast multilingual research assistant.

                RULES:
                1. Give CONCISE answers (max 3-4 sentences)
                2. Be DIRECT - no fluff
                3. Automatically censor any profanity
                4. Respond in the user's language

                {history_context}
                Answer the following question using the previous conversation context if needed:
                {query}"""
                
                response_text = self.llm.invoke(prompt).content
            
            filtered_response = self.profanity_filter.censor_text(
                response_text,
                sensitive_mode='news'
            )
            
            response_time = time.time() - start_time
            
            result_dict = {
                'success': True,
                'response': filtered_response,
                'response_time': response_time,
                'profanity_filtered': filtered_response != response_text
            }
            
            if cache_key:
                self._cache[cache_key] = (time.time(), result_dict)
            self.history.append({'role': 'assistant', 'content': filtered_response})
            
            return result_dict
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': f"Error: {str(e)[:100]}",
                'response_time': time.time() - start_time
            }

    def clear_memory(self):
        self.history.clear()
        self._cache.clear()