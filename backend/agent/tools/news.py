from backend.agent.tools.tools_base import ToolsRegistry

import feedparser


def _get_news(topic: str = "technology", limit: int = 3) -> str:
    """获取新闻头条，topic: technology（科技）/ business（商业）/ science（科学）"""
    feeds = {
        "technology": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "business": "https://feeds.bloomberg.com/markets/news.rss",
        "science": "https://www.sciencedaily.com/rss/all.xml",
    }

    feed_url = feeds.get(topic, feeds["technology"])

    try:
        feed = feedparser.parse(feed_url)
        news_list = []
        for entry in feed.entries[:limit]:
            news_list.append(f"• {entry.title}")

        if not news_list:
            return f"can't find {topic} news"

        return f"【{topic}】news：\n" + "\n".join(news_list)
    except Exception as e:
        return f"get news error：{e}"


ToolsRegistry.register(
    name="news",
    description="获取新闻头条，topic: technology（科技）/ business（商业）/ science（科学）",
    func=_get_news
)