#!/usr/bin/env python3
"""
Complex Problem 3: Web Scraping Simulation and Data Processing
"""

import asyncio
import sys
sys.path.append('/home/krawin/exp.code/jarvis')

from core.execution.docker_executor import DockerCodeExecutor, ExecutionConfig

async def problem_3_web_simulation():
    """Problem 3: Web Scraping Simulation and Data Processing"""
    print("🌐 PROBLEM 3: Web Scraping Simulation & Data Processing")
    print("=" * 60)
    print("Task: Simulate web scraping, parse HTML-like data, and extract insights")
    
    code = """
# Complex Web Scraping Simulation Problem
import re
import json
from collections import Counter, defaultdict
from urllib.parse import urlparse

# Simulate HTML content from multiple web pages
html_pages = [
    '''
    <html>
    <head><title>Tech News - AI Revolution</title></head>
    <body>
        <article>
            <h1>Artificial Intelligence Transforms Healthcare</h1>
            <p class="author">By John Smith</p>
            <p class="date">2024-01-15</p>
            <p>AI is revolutionizing healthcare with machine learning algorithms...</p>
            <div class="tags">AI, Healthcare, Technology, Innovation</div>
        </article>
    </body>
    </html>
    ''',
    '''
    <html>
    <head><title>Business Weekly - Market Analysis</title></head>
    <body>
        <article>
            <h1>Stock Market Reaches New Heights</h1>
            <p class="author">By Sarah Johnson</p>
            <p class="date">2024-01-16</p>
            <p>The stock market continues its upward trend with technology stocks leading...</p>
            <div class="tags">Finance, Stocks, Technology, Investment</div>
        </article>
    </body>
    </html>
    ''',
    '''
    <html>
    <head><title>Science Daily - Climate Research</title></head>
    <body>
        <article>
            <h1>Breakthrough in Renewable Energy Storage</h1>
            <p class="author">By Dr. Michael Chen</p>
            <p class="date">2024-01-17</p>
            <p>Scientists develop new battery technology for renewable energy storage...</p>
            <div class="tags">Science, Energy, Environment, Innovation</div>
        </article>
    </body>
    </html>
    '''
]

class WebScraper:
    def __init__(self):
        self.articles = []
    
    def extract_text_between_tags(self, html, tag):
        pattern = f'<{tag}[^>]*>(.*?)</{tag}>'
        matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)
        return [match.strip() for match in matches]
    
    def extract_attribute(self, html, tag, attribute):
        pattern = f'<{tag}[^>]*{attribute}="([^"]*)"[^>]*>'
        matches = re.findall(pattern, html, re.IGNORECASE)
        return matches
    
    def parse_article(self, html):
        article = {}
        
        # Extract title
        titles = self.extract_text_between_tags(html, 'title')
        article['page_title'] = titles[0] if titles else 'Unknown'
        
        # Extract article headline
        headlines = self.extract_text_between_tags(html, 'h1')
        article['headline'] = headlines[0] if headlines else 'No headline'
        
        # Extract author
        authors = self.extract_attribute(html, 'p', 'class')
        author_text = self.extract_text_between_tags(html, 'p')
        for i, cls in enumerate(authors):
            if 'author' in cls and i < len(author_text):
                article['author'] = author_text[i].replace('By ', '')
                break
        else:
            article['author'] = 'Unknown'
        
        # Extract date
        for i, cls in enumerate(authors):
            if 'date' in cls and i < len(author_text):
                article['date'] = author_text[i]
                break
        else:
            article['date'] = 'Unknown'
        
        # Extract tags
        tags = self.extract_text_between_tags(html, 'div')
        for tag_text in tags:
            if ',' in tag_text:
                article['tags'] = [tag.strip() for tag in tag_text.split(',')]
                break
        else:
            article['tags'] = []
        
        # Extract content
        paragraphs = self.extract_text_between_tags(html, 'p')
        content_paragraphs = [p for p in paragraphs if not p.startswith('By ') and '2024-' not in p]
        article['content'] = ' '.join(content_paragraphs)
        
        return article
    
    def scrape_pages(self, html_pages):
        for html in html_pages:
            article = self.parse_article(html)
            self.articles.append(article)
        return self.articles
    
    def analyze_data(self):
        print("=== WEB SCRAPING ANALYSIS ===")
        print(f"Total articles scraped: {len(self.articles)}")
        
        # Author analysis
        authors = [article['author'] for article in self.articles]
        author_counts = Counter(authors)
        print(f"\\nAuthors found: {len(author_counts)}")
        for author, count in author_counts.most_common():
            print(f"  {author}: {count} article(s)")
        
        # Tag analysis
        all_tags = []
        for article in self.articles:
            all_tags.extend(article['tags'])
        
        tag_counts = Counter(all_tags)
        print(f"\\nMost common tags:")
        for tag, count in tag_counts.most_common(5):
            print(f"  {tag}: {count} mentions")
        
        # Content analysis
        total_words = 0
        for article in self.articles:
            words = len(article['content'].split())
            total_words += words
            print(f"\\nArticle: {article['headline'][:50]}...")
            print(f"  Author: {article['author']}")
            print(f"  Date: {article['date']}")
            print(f"  Word count: {words}")
            print(f"  Tags: {', '.join(article['tags'])}")
        
        avg_words = total_words / len(self.articles) if self.articles else 0
        print(f"\\nAverage words per article: {avg_words:.1f}")
        
        # Trend analysis
        dates = [article['date'] for article in self.articles if article['date'] != 'Unknown']
        print(f"\\nDate range: {min(dates)} to {max(dates)}")
        
        return {
            'total_articles': len(self.articles),
            'authors': len(author_counts),
            'unique_tags': len(tag_counts),
            'avg_words': avg_words
        }

# Execute web scraping simulation
scraper = WebScraper()
articles = scraper.scrape_pages(html_pages)
analysis_results = scraper.analyze_data()

print("\\n=== SCRAPING SUMMARY ===")
print(f"Successfully processed {analysis_results['total_articles']} articles")
print(f"Found {analysis_results['authors']} unique authors")
print(f"Identified {analysis_results['unique_tags']} unique tags")
print(f"Average article length: {analysis_results['avg_words']:.1f} words")

print("\\n=== WEB SCRAPING SIMULATION COMPLETE ===")
"""
    
    executor = DockerCodeExecutor()
    executor.docker_available = False
    
    config = ExecutionConfig(language="python", timeout=20)
    result = await executor.execute_code(code, config)
    
    print(f"✅ Success: {result.success}")
    print(f"Output:\n{result.output}")
    print(f"Execution time: {result.execution_time:.3f}s")
    
    return result.success

if __name__ == "__main__":
    result = asyncio.run(problem_3_web_simulation())
    print(f"\n🎯 Problem 3 Result: {'PASSED' if result else 'FAILED'}")
