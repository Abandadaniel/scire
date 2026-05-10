from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from newspaper import Article
from lingua import LanguageDetectorBuilder
import json
from deep_translator import GoogleTranslator
from pydantic import PrivateAttr
from typing import Any

class MultilingualSearchTool(BaseTool):
    name: str = "Scire"
    description: str = """Search the internet for information in multiple languages.
    Input should be a JSON string with 'query' and 'language' (optional, default 'en').
    Returns search results with titles, links, and snippets."""

    _search: DuckDuckGoSearchRun = PrivateAttr()
    _translator: GoogleTranslator = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._search = DuckDuckGoSearchRun()
        self._translator = GoogleTranslator()
    
    def _run(self, query: str) -> str:
        try:
            input_data = json.loads(query)
            search_query = input_data.get('query', query)
            target_lang = input_data.get('language', 'en')
            
            if target_lang != 'en':
                search_query = GoogleTranslator(source='auto', target='en').translate(search_query)
            
            results = self._search.results(search_query, num_results=5)
            search_query = self._translator.translate(search_query)
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('snippet', ''),
                    'source': result.get('source', 'DuckDuckGo')
                })
            
            return json.dumps(formatted_results, ensure_ascii=False)
        
        except Exception as e:
            return f"Search error: {str(e)}"
    
    async def _arun(self, query: str) -> str:
        return self._run(query)


class WebContentExtractorTool(BaseTool):
    name: str = "extract_web_content"
    description: str = """Extract and parse main content from a webpage URL.
    Input should be a URL string. Returns the article title and main text content."""
    
    def _run(self, url: str) -> str:
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            content = {
                'title': article.title,
                'text': article.text[:5000],
                'authors': article.authors,
                'publish_date': str(article.publish_date) if article.publish_date else None
            }
            
            return json.dumps(content, ensure_ascii=False)
        
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    async def _arun(self, url: str) -> str:
        return self._run(url)


class MultilingualSummarizerTool(BaseTool):
    name: str = "summarize_text"
    description: str = """Summarize text content in a specified language.
    Input should be JSON with 'text' and 'language' fields."""

    _llm: Any = PrivateAttr()
    _translator: GoogleTranslator = PrivateAttr()
    
    def __init__(self, llm):
        super().__init__()
        self._llm = llm
        self._translator = GoogleTranslator()
    
    def _run(self, input_data: str) -> str:
        try:
            data = json.loads(input_data)
            text = data.get('text', '')
            target_lang = data.get('language', 'en')
            
            from langchain_core.prompts import PromptTemplate

            prompt = PromptTemplate(
                input_variables=["text", "language"],
                template="""Summarize the following text in {language} language. 
                Keep the summary concise (3-5 sentences) and capture the key points.
                
                Text: {text}
                
                Summary:"""
            )

            chain = prompt | self._llm
            summary = chain.invoke({"text": text[:3000], "language": target_lang})
            
            return summary
        
        except Exception as e:
            return f"Summarization error: {str(e)}"
    
    async def _arun(self, input_data: str) -> str:
        return self._run(input_data)


class LanguageDetectorTool(BaseTool):
    name: str = "detect_language"
    description: str = """Detect the language of input text.
    Input should be a text string. Returns language code and name."""

    _detector: Any = PrivateAttr()
    
    def __init__(self):
        super().__init__()
        self._detector = LanguageDetectorBuilder.from_all_languages().build()
    
    def _run(self, text: str) -> str:
        try:
            language = self._detector.detect_language_of(text)
            if language:
                result = {
                    'language_code': language.iso_code_639_1.name.lower(),
                    'language_name': language.name
                }
                return json.dumps(result)
            return json.dumps({'language_code': 'en', 'language_name': 'English'})
        except Exception as e:
            return f"Language detection error: {str(e)}"