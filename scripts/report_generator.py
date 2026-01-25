from jinja2 import Template
from datetime import datetime
from pathlib import Path
import json
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """HTML report generator"""
    
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Template]:
        """Load HTML templates"""
        templates = {}
        
        # Main report template
        templates['main'] = Template(self._get_main_template())
        
        return templates
    
    def _get_main_template(self) -> str:
        """Get the main HTML template"""
        return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report_date }} - AI资讯哨兵</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }
        
        .header .date {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-card .label {
            color: #666;
            margin-top: 5px;
        }
        
        .content {
            padding: 30px;
        }
        
        .category-section {
            margin-bottom: 40px;
        }
        
        .category-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .category-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .badge-重大新闻 { background: #dc2626; color: white; }
        .badge-行业动态 { background: #ea580c; color: white; }
        .badge-产品发布 { background: #16a34a; color: white; }
        .badge-技术干货 { background: #2563eb; color: white; }
        .badge-观点评论 { background: #9333ea; color: white; }
        
        .article {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #667eea;
        }
        
        .article:hover {
            transform: translateY(-3px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
        }
        
        .article-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
            gap: 15px;
        }
        
        .article-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #1a1a1a;
            flex: 1;
        }
        
        .article-title a {
            color: inherit;
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .article-title a:hover {
            color: #667eea;
        }
        
        .hot-score {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            white-space: nowrap;
        }
        
        .article-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #666;
        }
        
        .article-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .article-summary {
            color: #444;
            margin-bottom: 15px;
            line-height: 1.7;
        }
        
        .article-keywords {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .keyword {
            background: #e0e7ff;
            color: #4338ca;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.85em;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }
        
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        
        .archive-link {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            text-decoration: none;
            transition: background 0.2s;
        }
        
        .archive-link:hover {
            background: #5568d3;
        }
        
        @media (max-width: 768px) {
            .stats {
                grid-template-columns: 1fr;
            }
            
            .article-header {
                flex-direction: column;
            }
            
            .article-meta {
                flex-direction: column;
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 AI资讯哨兵</h1>
            <div class="date">{{ report_date }}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{{ total_articles }}</div>
                <div class="label">总文章数</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ "%.1f"|format(avg_hot_score) }}</div>
                <div class="label">平均热度</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ total_sources }}</div>
                <div class="label">资讯来源</div>
            </div>
            <div class="stat-card">
                <div class="number">{{ total_categories }}</div>
                <div class="label">新闻分类</div>
            </div>
        </div>
        
        <div class="content">
            {% for category_name, category_articles in categories.items() %}
            {% if category_articles %}
            <div class="category-section">
                <div class="category-title">
                    <span class="category-badge badge-{{ category_name }}">{{ category_name }}</span>
                    <span>{{ category_articles|length }} 篇文章</span>
                </div>
                
                {% for article in category_articles %}
                <div class="article">
                    <div class="article-header">
                        <div class="article-title">
                            <a href="{{ article.link }}" target="_blank">{{ article.title }}</a>
                        </div>
                        <div class="hot-score">热度: {{ article.hot_score }}</div>
                    </div>
                    
                    <div class="article-meta">
                        <span>📅 {{ article.published.strftime('%Y-%m-%d %H:%M') }}</span>
                        <span>📌 {{ article.source }}</span>
                        {% if article.reasoning %}
                        <span>💡 {{ article.reasoning }}</span>
                        {% endif %}
                    </div>
                    
                    <div class="article-summary">
                        {{ article.summary }}
                    </div>
                    
                    {% if article.keywords %}
                    <div class="article-keywords">
                        {% for keyword in article.keywords[:5] %}
                        <span class="keyword">{{ keyword }}</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
            {% endif %}
            {% endfor %}
        </div>
        
        <div class="footer">
            <p>由 AI资讯哨兵 自动生成 | Powered by <a href="https://www.deepseek.com" target="_blank">DeepSeek</a></p>
            <p>生成时间: {{ generation_time }}</p>
            <a href="archive/" class="archive-link">📚 查看历史存档</a>
        </div>
    </div>
</body>
</html>'''
    
    def generate_report(self, articles: List[Dict], output_path: str = "docs/index.html"):
        """Generate HTML report from articles"""
        # Group articles by category
        categories = {}
        category_order = ['重大新闻', '行业动态', '产品发布', '技术干货', '观点评论']
        
        for cat in category_order:
            categories[cat] = []
        
        for article in articles:
            cat = article.get('category', '行业动态')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(article)
        
        # Sort articles in each category by hot_score
        for cat in categories:
            categories[cat].sort(key=lambda x: x.get('hot_score', 0), reverse=True)
        
        # Calculate statistics
        total_articles = len(articles)
        avg_hot_score = sum(a.get('hot_score', 0) for a in articles) / total_articles if articles else 0
        total_sources = len(set(a.get('source', '') for a in articles))
        total_categories = len([c for c in categories.values() if c])
        
        # Generate report
        report_date = datetime.now().strftime('%Y年%m月%d日')
        generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = self.templates['main'].render(
            report_date=report_date,
            generation_time=generation_time,
            total_articles=total_articles,
            avg_hot_score=avg_hot_score,
            total_sources=total_sources,
            total_categories=total_categories,
            categories=categories
        )
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"✓ Report generated: {output_path}")
        
        return output_path
    
    def create_archive_entry(self, articles: List[Dict], archive_dir: str = "docs/archive"):
        """Create archive entry for current report"""
        archive_path = Path(archive_dir)
        archive_path.mkdir(parents=True, exist_ok=True)
        
        # Archive filename with date
        date_str = datetime.now().strftime('%Y-%m-%d')
        archive_file = archive_path / f"report_{date_str}.html"
        
        # Generate report
        self.generate_report(articles, str(archive_file))
        
        logger.info(f"✓ Archive created: {archive_file}")
        
        return archive_file


def main():
    """Test the report generator"""
    from datetime import datetime, timezone
    
    # Test articles
    test_articles = [
        {
            'title': '测试文章1',
            'link': 'https://example.com/1',
            'summary': '这是一篇测试文章的摘要内容',
            'category': '重大新闻',
            'hot_score': 85,
            'source': 'Test Source',
            'published': datetime.now(timezone.utc),
            'keywords': ['测试', '文章', 'AI'],
            'reasoning': '测试原因'
        }
    ]
    
    generator = ReportGenerator()
    generator.generate_report(test_articles, 'test_report.html')
    print("Report generated: test_report.html")


if __name__ == "__main__":
    main()
