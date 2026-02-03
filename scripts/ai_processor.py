import os
import json
import logging
from typing import List, Dict, Optional
import requests
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIProcessor:
    """AI processor for analyzing articles using DeepSeek API"""
    
    # Category system
    CATEGORIES = {
        "重大新闻": "重大行业事件、突破性技术、巨头重大决策",
        "行业动态": "行业重要动态、市场变化",
        "产品发布": "重要产品发布、更新",
        "技术干货": "技术分享、教程、深度文章",
        "观点评论": "行业观点、分析评论"
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = "deepseek-ai/DeepSeek-V3"):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            logger.warning("No API key provided, AI processing will be skipped")
        
        self.model = model
        self.api_url = "https://api.siliconflow.cn/v1/chat/completions"
        self.batch_size = 5
    
    def _create_analysis_prompt(self, article: Dict) -> str:
        """Create prompt for AI analysis"""
        categories_str = "\n".join([f"- {k}: {v}" for k, v in self.CATEGORIES.items()])
        
        prompt = f"""请分析以下文章并返回JSON格式的结果：

文章标题：{article['title']}
文章来源：{article['source']}
文章内容：{article['content'][:2000]}

请返回以下信息的JSON格式：
{{
  "category": "从以下分类中选择最合适的一个：\n{categories_str}",
  "summary": "用50-100字总结文章核心内容",
  "hot_score": "给出热度分数（0-100），综合考虑新闻重要性、时效性、影响力等因素",
  "keywords": ["提取3-5个关键词"],
  "reasoning": "简要说明分类和评分理由（20字以内）"
}}

只返回JSON，不要其他内容。
"""
        return prompt
    
    def _analyze_article(self, article: Dict) -> Optional[Dict]:
        """Analyze a single article using AI"""
        if not self.api_key:
            logger.warning("AI client not initialized, skipping analysis")
            return self._get_default_analysis(article)
        
        try:
            prompt = self._create_analysis_prompt(article)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是一个专业的新闻内容分析师，擅长分类、摘要和热度评分。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            result_text = result['choices'][0]['message']['content'].strip()
            
            # Parse JSON response
            try:
                # Clean markdown code blocks if present
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]
                result_text = result_text.strip()
                
                result = json.loads(result_text)
                
                # Validate and clean result
                analysis = {
                    'category': result.get('category', '行业动态'),
                    'summary': result.get('summary', article['summary'][:100]),
                    'hot_score': min(100, max(0, int(result.get('hot_score', 50)))),
                    'keywords': result.get('keywords', [])[:5],
                    'reasoning': result.get('reasoning', '')
                }
                
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response: {e}")
                logger.debug(f"Response text: {result_text}")
                return self._get_default_analysis(article)
            
        except Exception as e:
            logger.error(f"Error analyzing article: {e}")
            return self._get_default_analysis(article)
    
    def _get_default_analysis(self, article: Dict) -> Dict:
        """Get default analysis when AI is not available"""
        return {
            'category': '行业动态',
            'summary': article['summary'],
            'hot_score': 50,
            'keywords': article.get('tags', [])[:3] if article.get('tags') else [],
            'reasoning': 'AI不可用'
        }
    
    def process_batch(self, articles: List[Dict]) -> List[Dict]:
        """Process a batch of articles"""
        processed = []
        
        for i, article in enumerate(articles):
            logger.info(f"Analyzing article {i+1}/{len(articles)}: {article['title'][:50]}...")
            
            analysis = self._analyze_article(article)
            article.update(analysis)
            processed.append(article)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        return processed
    
    def process_all(self, articles: List[Dict]) -> List[Dict]:
        """Process all articles in batches"""
        if not self.api_key:
            logger.warning("No API key configured, processing with default values")
            for article in articles:
                article.update(self._get_default_analysis(article))
            return articles
        
        logger.info(f"Starting AI analysis for {len(articles)} articles...")
        
        all_processed = []
        for i in range(0, len(articles), self.batch_size):
            batch = articles[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(articles)-1)//self.batch_size + 1}")
            
            processed = self.process_batch(batch)
            all_processed.extend(processed)
        
        logger.info("✓ AI analysis completed")
        return all_processed
    
    def filter_by_hot_score(self, articles: List[Dict], threshold: int = 60) -> List[Dict]:
        """Filter articles by hot score threshold"""
        filtered = [a for a in articles if a.get('hot_score', 0) >= threshold]
        logger.info(f"✓ Filtered {len(filtered)} articles with hot_score >= {threshold}")
        return filtered
    
    def sort_by_hot_score(self, articles: List[Dict], reverse: bool = True) -> List[Dict]:
        """Sort articles by hot score"""
        return sorted(articles, key=lambda x: x.get('hot_score', 0), reverse=reverse)


def main():
    """Test the AI processor"""
    import os
    
    # Test articles
    test_articles = [
        {
            'title': 'OpenAI发布GPT-5模型',
            'source': 'TechNews',
            'content': 'OpenAI今天正式发布了备受期待的GPT-5模型，该模型在多项基准测试中表现出色，性能提升显著。新模型支持更长的上下文窗口，推理能力更强，安全性也有所提升。',
            'summary': 'OpenAI发布GPT-5模型',
            'tags': ['AI', 'OpenAI', 'GPT']
        }
    ]
    
    processor = AIProcessor()
    
    if os.getenv('DEEPSEEK_API_KEY'):
        processed = processor.process_all(test_articles)
        print("\nProcessed article:")
        print(json.dumps(processed[0], indent=2, ensure_ascii=False))
    else:
        print("Set DEEPSEEK_API_KEY environment variable to test AI processing")


if __name__ == "__main__":
    main()
