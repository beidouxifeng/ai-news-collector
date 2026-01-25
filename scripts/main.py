#!/usr/bin/env python3
"""
AI资讯哨兵 - 主程序
全自动资讯抓取、AI分析与报告生成系统
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.fetch_rss import RSSFetcher
from scripts.ai_processor import AIProcessor
from scripts.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('news_sentinel.log')
    ]
)
logger = logging.getLogger(__name__)


def save_raw_data(articles: list, output_path: str = "data/articles.json"):
    """Save raw article data to JSON file"""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert datetime objects to string for JSON serialization
    serializable_articles = []
    for article in articles:
        article_copy = article.copy()
        if 'published' in article_copy:
            article_copy['published'] = article_copy['published'].isoformat()
        serializable_articles.append(article_copy)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(serializable_articles, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✓ Raw data saved to {output_path}")


def main():
    """Main execution flow"""
    logger.info("="*60)
    logger.info("🚀 AI资讯哨兵启动")
    logger.info("="*60)
    
    try:
        # Step 1: Fetch RSS feeds
        logger.info("\n📡 Step 1: 抓取RSS源...")
        fetcher = RSSFetcher()
        articles = fetcher.fetch_all()
        
        if not articles:
            logger.warning("没有抓取到任何文章，程序退出")
            return
        
        # Deduplicate articles
        articles = fetcher.deduplicate(articles)
        logger.info(f"✓ 获取到 {len(articles)} 篇唯一文章")
        
        # Step 2: AI Analysis
        logger.info("\n🤖 Step 2: AI智能分析...")
        api_key = os.getenv('DEEPSEEK_API_KEY', '')
        
        if not api_key:
            logger.warning("⚠️  未配置DEEPSEEK_API_KEY，将使用默认值")
            logger.warning("   如需AI分析，请在GitHub Secrets中配置DEEPSEEK_API_KEY")
        
        processor = AIProcessor(api_key=api_key)
        articles = processor.process_all(articles)
        
        # Sort by hot score
        articles = processor.sort_by_hot_score(articles)
        logger.info(f"✓ AI分析完成")
        
        # Step 3: Generate Report
        logger.info("\n📊 Step 3: 生成HTML报告...")
        generator = ReportGenerator()
        
        # Generate main report
        report_path = generator.generate_report(articles, "docs/index.html")
        
        # Create archive entry
        archive_path = generator.create_archive_entry(articles, "docs/archive")
        
        logger.info(f"✓ 报告生成完成")
        logger.info(f"  - 最新报告: {report_path}")
        logger.info(f"  - 历史存档: {archive_path}")
        
        # Step 4: Save raw data
        logger.info("\n💾 Step 4: 保存原始数据...")
        date_str = datetime.now().strftime('%Y-%m-%d')
        save_raw_data(articles, f"data/articles_{date_str}.json")
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 运行摘要")
        logger.info("="*60)
        logger.info(f"总文章数: {len(articles)}")
        
        # Category breakdown
        categories = {}
        for article in articles:
            cat = article.get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        logger.info("分类分布:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  - {cat}: {count}")
        
        # Average hot score
        avg_score = sum(a.get('hot_score', 0) for a in articles) / len(articles) if articles else 0
        logger.info(f"平均热度分数: {avg_score:.1f}")
        
        # Source breakdown (top 10)
        sources = {}
        for article in articles:
            source = article.get('source', 'Unknown')
            sources[source] = sources.get(source, 0) + 1
        
        logger.info("\nTop 10 资讯来源:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  - {source}: {count}")
        
        logger.info("="*60)
        logger.info("✅ 所有任务完成！")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
