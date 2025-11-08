# 第8章：XPath实战案例

## 8.1 Web数据抓取实战

### 8.1.1 电商网站商品信息提取

本案例演示如何使用XPath从电商网站提取商品信息。

```python
# code/real-world-cases/ecommerce_scraper.py
import requests
from lxml import etree
import csv
import time

class ECommerceScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_page(self, url):
        """获取页面内容"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None
    
    def extract_product_list(self, html_content):
        """从HTML中提取商品列表"""
        tree = etree.HTML(html_content)
        
        products = []
        
        # 使用XPath提取商品信息
        product_elements = tree.xpath("//div[contains(@class, 'product-item')]")
        
        for product in product_elements:
            # 提取商品名称
            name = product.xpath(".//h3[contains(@class, 'product-name')]/text()")
            name = name[0].strip() if name else "未知商品"
            
            # 提取商品价格
            price = product.xpath(".//span[contains(@class, 'price')]/text()")
            if price:
                # 移除货币符号和空格，转换为数字
                price_text = price[0].strip().replace('$', '').replace(',', '')
                try:
                    price_value = float(price_text)
                except ValueError:
                    price_value = 0.0
            else:
                price_value = 0.0
            
            # 提取商品评分
            rating = product.xpath(".//div[contains(@class, 'rating')]//@data-rating")
            rating_value = float(rating[0]) if rating else 0.0
            
            # 提取商品链接
            link = product.xpath(".//a[contains(@class, 'product-link')]/@href")
            link_url = link[0] if link else ""
            if link_url and not link_url.startswith('http'):
                link_url = self.base_url + link_url
            
            # 提取商品图片
            image = product.xpath(".//img[contains(@class, 'product-image')]/@src")
            image_url = image[0] if image else ""
            if image_url and not image_url.startswith('http'):
                image_url = self.base_url + image_url
            
            # 提取折扣信息
            discount = product.xpath(".//span[contains(@class, 'discount')]/text()")
            discount_text = discount[0].strip() if discount else ""
            
            # 提取商品ID
            product_id = product.xpath("./@data-product-id")
            id_value = product_id[0] if product_id else ""
            
            product_info = {
                'id': id_value,
                'name': name,
                'price': price_value,
                'rating': rating_value,
                'link': link_url,
                'image': image_url,
                'discount': discount_text
            }
            
            products.append(product_info)
        
        return products
    
    def extract_product_details(self, html_content):
        """提取商品详情页信息"""
        tree = etree.HTML(html_content)
        
        # 提取商品标题
        title = tree.xpath("//h1[contains(@class, 'product-title')]/text()")
        title = title[0].strip() if title else ""
        
        # 提取商品描述
        description = tree.xpath("//div[contains(@class, 'product-description')]//text()")
        description = " ".join([d.strip() for d in description if d.strip()])
        
        # 提取规格参数
        specs = {}
        spec_rows = tree.xpath("//table[contains(@class, 'product-specs')]//tr")
        
        for row in spec_rows:
            cells = row.xpath(".//td/text()")
            if len(cells) >= 2:
                key = cells[0].strip()
                value = cells[1].strip()
                specs[key] = value
        
        # 提取商品图片列表
        images = tree.xpath("//div[contains(@class, 'product-gallery')]//img/@src")
        
        # 提取评论数量
        reviews_count = tree.xpath("//span[contains(@class, 'reviews-count')]/text()")
        reviews_count = int(reviews_count[0].strip().split()[0]) if reviews_count else 0
        
        # 提取库存状态
        stock_status = tree.xpath("//div[contains(@class, 'stock-status')]/text()")
        stock_status = stock_status[0].strip() if stock_status else ""
        
        # 提取卖家信息
        seller = tree.xpath("//div[contains(@class, 'seller-info')]//text()")
        seller = " ".join([s.strip() for s in seller if s.strip()])
        
        return {
            'title': title,
            'description': description,
            'specifications': specs,
            'images': images,
            'reviews_count': reviews_count,
            'stock_status': stock_status,
            'seller': seller
        }
    
    def get_pagination_links(self, html_content):
        """获取分页链接"""
        tree = etree.HTML(html_content)
        
        # 获取当前页码
        current_page = tree.xpath("//ul[contains(@class, 'pagination')]//li[contains(@class, 'active')]/text()")
        current_page = int(current_page[0]) if current_page else 1
        
        # 获取总页数
        total_pages = tree.xpath("//ul[contains(@class, 'pagination')]//li[last()-1]/a/text()")
        total_pages = int(total_pages[0]) if total_pages else current_page
        
        # 获取下一页链接
        next_page = tree.xpath("//ul[contains(@class, 'pagination')]//li[contains(@class, 'next')]/a/@href")
        next_link = next_page[0] if next_page else None
        
        return {
            'current_page': current_page,
            'total_pages': total_pages,
            'next_page': next_link
        }
    
    def scrape_category(self, category_url, max_pages=None):
        """抓取整个分类的商品"""
        all_products = []
        current_url = category_url
        page_count = 0
        
        while current_url and (max_pages is None or page_count < max_pages):
            print(f"抓取页面 {page_count + 1}: {current_url}")
            
            html_content = self.fetch_page(current_url)
            if not html_content:
                break
            
            # 提取商品列表
            products = self.extract_product_list(html_content)
            all_products.extend(products)
            print(f"  找到 {len(products)} 件商品")
            
            # 获取分页信息
            pagination = self.get_pagination_links(html_content)
            print(f"  当前页: {pagination['current_page']}/{pagination['total_pages']}")
            
            # 获取下一页链接
            if pagination['next_page']:
                if not pagination['next_page'].startswith('http'):
                    current_url = self.base_url + pagination['next_page']
                else:
                    current_url = pagination['next_page']
            else:
                current_url = None
            
            page_count += 1
            
            # 礼貌性延迟
            time.sleep(1)
        
        return all_products
    
    def save_to_csv(self, products, filename="products.csv"):
        """将商品信息保存到CSV文件"""
        if not products:
            print("没有商品数据可保存")
            return
        
        fieldnames = ['id', 'name', 'price', 'rating', 'link', 'image', 'discount']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for product in products:
                writer.writerow(product)
        
        print(f"已保存 {len(products)} 件商品到 {filename}")

# 使用示例
def main():
    # 初始化爬虫
    scraper = ECommerceScraper("https://example-ecommerce.com")
    
    # 抓取特定分类的商品
    category_url = "https://example-ecommerce.com/electronics"
    products = scraper.scrape_category(category_url, max_pages=3)  # 限制页数以演示
    
    # 保存结果
    scraper.save_to_csv(products, "electronics_products.csv")
    
    # 如果需要抓取商品详情，可以进一步处理
    if products:
        first_product_url = products[0]['link']
        if first_product_url:
            html_content = scraper.fetch_page(first_product_url)
            if html_content:
                details = scraper.extract_product_details(html_content)
                print("\n商品详情:")
                print(f"标题: {details['title']}")
                print(f"描述: {details['description'][:100]}...")
                print(f"规格参数: {len(details['specifications'])} 项")
                print(f"图片数量: {len(details['images'])}")
                print(f"评论数: {details['reviews_count']}")
                print(f"库存状态: {details['stock_status']}")

if __name__ == "__main__":
    main()
```

### 8.1.2 新闻网站内容提取

```python
# code/real-world-cases/news_extractor.py
import requests
from lxml import etree
import json
import datetime

class NewsExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_page(self, url):
        """获取页面内容"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取页面失败: {e}")
            return None
    
    def extract_article_list(self, html_content, source_name):
        """提取文章列表"""
        tree = etree.HTML(html_content)
        articles = []
        
        # 根据不同新闻站点使用不同的XPath
        if source_name == "news_site_a":
            article_elements = tree.xpath("//div[contains(@class, 'article-card')]")
            title_xpath = ".//h3[contains(@class, 'title')]/a/text()"
            link_xpath = ".//h3[contains(@class, 'title')]/a/@href"
            summary_xpath = ".//p[contains(@class, 'summary')]/text()"
            date_xpath = ".//time[contains(@class, 'date')]/@datetime"
            author_xpath = ".//span[contains(@class, 'author')]/text()"
            image_xpath = ".//img[contains(@class, 'thumbnail')]/@src"
        elif source_name == "news_site_b":
            article_elements = tree.xpath("//article[contains(@class, 'news-item')]")
            title_xpath = ".//h2[contains(@class, 'headline')]/a/text()"
            link_xpath = ".//h2[contains(@class, 'headline')]/a/@href"
            summary_xpath = ".//div[contains(@class, 'excerpt')]/text()"
            date_xpath = ".//span[contains(@class, 'publish-date')]/text()"
            author_xpath = ".//span[contains(@class, 'byline')]/text()"
            image_xpath = ".//figure[contains(@class, 'media')]/img/@src"
        else:
            # 默认XPath
            article_elements = tree.xpath("//div[contains(@class, 'article') or contains(@class, 'post')]")
            title_xpath = ".//h1//a/text() | .//h2//a/text() | .//h3//a/text()"
            link_xpath = ".//h1//a/@href | .//h2//a/@href | .//h3//a/@href"
            summary_xpath = ".//p[contains(@class, 'summary') or contains(@class, 'excerpt')]/text()"
            date_xpath = ".//time/@datetime | .//span[contains(@class, 'date')]/text() | .//div[contains(@class, 'date')]/text()"
            author_xpath = ".//span[contains(@class, 'author') or contains(@class, 'by')]/text()"
            image_xpath = ".//img/@src"
        
        for article in article_elements:
            # 提取标题
            title_nodes = article.xpath(title_xpath)
            title = title_nodes[0].strip() if title_nodes else ""
            
            # 提取链接
            link_nodes = article.xpath(link_xpath)
            link = link_nodes[0] if link_nodes else ""
            
            # 提取摘要
            summary_nodes = article.xpath(summary_xpath)
            summary = summary_nodes[0].strip() if summary_nodes else ""
            
            # 提取日期
            date_nodes = article.xpath(date_xpath)
            date_str = date_nodes[0].strip() if date_nodes else ""
            date = self.parse_date(date_str)
            
            # 提取作者
            author_nodes = article.xpath(author_xpath)
            author = author_nodes[0].strip() if author_nodes else ""
            
            # 提取图片
            image_nodes = article.xpath(image_xpath)
            image = image_nodes[0] if image_nodes else ""
            
            articles.append({
                'title': title,
                'link': link,
                'summary': summary,
                'date': date,
                'author': author,
                'image': image,
                'source': source_name
            })
        
        return articles
    
    def parse_date(self, date_str):
        """解析日期字符串"""
        if not date_str:
            return None
        
        # 尝试解析常见日期格式
        formats = [
            '%Y-%m-%dT%H:%M:%S%z',  # ISO 8601 with timezone
            '%Y-%m-%dT%H:%M:%SZ',   # ISO 8601 UTC
            '%Y-%m-%d %H:%M:%S',    # 常用格式
            '%Y-%m-%d',            # 仅日期
            '%b %d, %Y',           # 英文月份缩写
            '%d %b %Y',            # 日 月 年
        ]
        
        for fmt in formats:
            try:
                return datetime.datetime.strptime(date_str, fmt).isoformat()
            except ValueError:
                continue
        
        return date_str  # 返回原始字符串
    
    def extract_article_content(self, html_content):
        """提取文章完整内容"""
        tree = etree.HTML(html_content)
        
        # 提取标题
        title_nodes = tree.xpath("//h1[contains(@class, 'title') or contains(@class, 'headline')]/text()")
        title = title_nodes[0].strip() if title_nodes else ""
        
        # 提取正文内容
        content_selectors = [
            "//div[contains(@class, 'content') or contains(@class, 'article-body') or contains(@class, 'post-content')]//p/text()",
            "//article//p/text()",
            "//main//p/text()"
        ]
        
        content = ""
        for selector in content_selectors:
            content_nodes = tree.xpath(selector)
            if content_nodes:
                content = "\n".join([node.strip() for node in content_nodes if node.strip()])
                break
        
        # 提取发布日期
        date_nodes = tree.xpath("//time/@datetime | //meta[@property='article:published_time']/@content")
        date_str = date_nodes[0] if date_nodes else ""
        date = self.parse_date(date_str)
        
        # 提取作者
        author_nodes = tree.xpath("//span[contains(@class, 'author') or contains(@class, 'byline')]/text() | //meta[@property='article:author']/@content")
        author = author_nodes[0].strip() if author_nodes else ""
        
        # 提取标签
        tags_nodes = tree.xpath("//div[contains(@class, 'tags')]//a/text()")
        tags = [tag.strip() for tag in tags_nodes if tag.strip()]
        
        # 提取主图
        image_nodes = tree.xpath("//meta[@property='og:image']/@content | //figure//img/@src")
        image = image_nodes[0] if image_nodes else ""
        
        return {
            'title': title,
            'content': content,
            'date': date,
            'author': author,
            'tags': tags,
            'image': image
        }
    
    def extract_news_from_multiple_sources(self, sources):
        """从多个新闻源提取新闻"""
        all_articles = []
        
        for name, url in sources.items():
            print(f"正在从 {name} 提取新闻: {url}")
            
            html_content = self.fetch_page(url)
            if html_content:
                articles = self.extract_article_list(html_content, name)
                all_articles.extend(articles)
                print(f"  找到 {len(articles)} 篇文章")
        
        return all_articles
    
    def save_to_json(self, articles, filename="news.json"):
        """将新闻保存为JSON文件"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {len(articles)} 篇文章到 {filename}")
    
    def filter_by_keywords(self, articles, keywords):
        """根据关键词筛选文章"""
        filtered_articles = []
        
        for article in articles:
            title = article.get('title', '').lower()
            summary = article.get('summary', '').lower()
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                if keyword_lower in title or keyword_lower in summary:
                    filtered_articles.append(article)
                    break
        
        return filtered_articles
    
    def sort_by_date(self, articles):
        """按日期排序文章"""
        def get_date(article):
            date_str = article.get('date', '')
            if not date_str:
                return datetime.datetime.min.isoformat()
            
            try:
                return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                return datetime.datetime.min.isoformat()
        
        return sorted(articles, key=get_date, reverse=True)

# 使用示例
def main():
    extractor = NewsExtractor()
    
    # 定义新闻源
    sources = {
        "tech_news": "https://example-tech-news.com",
        "world_news": "https://example-world-news.com",
        "business_news": "https://example-business-news.com"
    }
    
    # 提取新闻
    all_articles = extractor.extract_news_from_multiple_sources(sources)
    print(f"总共提取了 {len(all_articles)} 篇文章")
    
    # 筛选特定主题的新闻
    keywords = ["technology", "AI", "artificial intelligence", "machine learning"]
    tech_articles = extractor.filter_by_keywords(all_articles, keywords)
    print(f"筛选出 {len(tech_articles)} 篇技术相关文章")
    
    # 按日期排序
    sorted_articles = extractor.sort_by_date(tech_articles)
    
    # 保存结果
    extractor.save_to_json(sorted_articles, "tech_news.json")
    
    # 获取第一篇文章的详细内容
    if sorted_articles:
        article_url = sorted_articles[0].get('link')
        if article_url:
            print(f"\n获取文章详情: {article_url}")
            html_content = extractor.fetch_page(article_url)
            if html_content:
                article_content = extractor.extract_article_content(html_content)
                print(f"标题: {article_content['title']}")
                print(f"作者: {article_content['author']}")
                print(f"发布时间: {article_content['date']}")
                print(f"标签: {', '.join(article_content['tags'])}")
                print(f"内容摘要: {article_content['content'][:200]}...")

if __name__ == "__main__":
    main()
```

## 8.2 XML数据处理实战

### 8.2.1 图书馆管理系统数据处理

```python
# code/real-world-cases/library_system.py
from lxml import etree
import csv
import json
import datetime

class LibrarySystem:
    def __init__(self, xml_file):
        self.xml_file = xml_file
        self.tree = etree.parse(xml_file)
        self.root = self.tree.getroot()
    
    def get_all_books(self):
        """获取所有书籍"""
        return self.root.xpath("//book")
    
    def get_books_by_category(self, category):
        """获取特定类别的书籍"""
        return self.root.xpath(f"//book[@category='{category}']")
    
    def get_book_by_id(self, book_id):
        """根据ID获取书籍"""
        return self.root.xpath(f"//book[@id='{book_id}']")
    
    def search_books(self, query):
        """搜索书籍"""
        # 标题、作者、描述中包含查询词的书籍
        books = self.root.xpath(f"//book[contains(title, '{query}') or contains(author, '{query}') or contains(description, '{query}')]")
        return books
    
    def get_overdue_books(self):
        """获取逾期书籍"""
        today = datetime.date.today().isoformat()
        # 假设借阅记录中有due_date属性
        overdue_loans = self.root.xpath(f"//loan[due_date < '{today}' and returned='false']")
        
        overdue_books = []
        for loan in overdue_loans:
            book_id = loan.get("book_id")
            book = self.get_book_by_id(book_id)
            if book:
                book_info = {
                    'book_id': book_id,
                    'title': book.xpath("title/text()")[0],
                    'author': book.xpath("author/text()")[0],
                    'borrower': loan.get("borrower_id"),
                    'due_date': loan.get("due_date"),
                    'days_overdue': (datetime.date.today() - datetime.date.fromisoformat(loan.get("due_date"))).days
                }
                overdue_books.append(book_info)
        
        return overdue_books
    
    def get_popular_books(self, limit=10):
        """获取热门书籍（按借阅次数排序）"""
        # 获取所有书籍及其借阅次数
        books = self.get_all_books()
        book_stats = []
        
        for book in books:
            book_id = book.get("id")
            title = book.xpath("title/text()")[0]
            
            # 计算借阅次数
            loan_count = len(self.root.xpath(f"//loan[@book_id='{book_id}']"))
            
            # 计算当前借阅次数
            active_loans = len(self.root.xpath(f"//loan[@book_id='{book_id}' and returned='false']"))
            
            book_stats.append({
                'book_id': book_id,
                'title': title,
                'total_loans': loan_count,
                'active_loans': active_loans
            })
        
        # 按借阅次数排序
        book_stats.sort(key=lambda x: x['total_loans'], reverse=True)
        
        return book_stats[:limit]
    
    def get_user_activity(self, user_id):
        """获取用户活动记录"""
        # 获取用户的所有借阅记录
        loans = self.root.xpath(f"//loan[@borrower_id='{user_id}']")
        
        activity = {
            'user_id': user_id,
            'total_loans': len(loans),
            'active_loans': 0,
            'overdue_loans': 0,
            'loan_history': []
        }
        
        today = datetime.date.today().isoformat()
        
        for loan in loans:
            book_id = loan.get("book_id")
            book = self.get_book_by_id(book_id)
            
            if book:
                title = book.xpath("title/text()")[0]
                
                loan_info = {
                    'book_id': book_id,
                    'title': title,
                    'loan_date': loan.get("loan_date"),
                    'due_date': loan.get("due_date"),
                    'return_date': loan.get("return_date"),
                    'returned': loan.get("returned") == "true"
                }
                
                if loan.get("returned") == "false":
                    activity['active_loans'] += 1
                    
                    if loan.get("due_date") < today:
                        activity['overdue_loans'] += 1
                
                activity['loan_history'].append(loan_info)
        
        return activity
    
    def generate_inventory_report(self, category=None):
        """生成库存报告"""
        books = self.get_books_by_category(category) if category else self.get_all_books()
        
        report = {
            'report_date': datetime.date.today().isoformat(),
            'category': category,
            'total_books': len(books),
            'total_value': 0.0,
            'books_by_year': {},
            'books_by_status': {
                'available': 0,
                'loaned': 0,
                'reserved': 0
            },
            'books': []
        }
        
        for book in books:
            book_id = book.get("id")
            title = book.xpath("title/text()")[0]
            author = book.xpath("author/text()")[0]
            year = book.xpath("year/text()")[0] if book.xpath("year/text()") else "未知"
            price = float(book.xpath("price/text()")[0]) if book.xpath("price/text()") else 0.0
            
            # 更新总价值
            report['total_value'] += price
            
            # 按年份统计
            if year not in report['books_by_year']:
                report['books_by_year'][year] = 0
            report['books_by_year'][year] += 1
            
            # 统计状态
            active_loans = len(self.root.xpath(f"//loan[@book_id='{book_id}' and returned='false']"))
            
            if active_loans > 0:
                report['books_by_status']['loaned'] += 1
                status = "借出中"
            else:
                # 检查是否有预约
                reservations = len(self.root.xpath(f"//reservation[@book_id='{book_id}' and fulfilled='false']"))
                if reservations > 0:
                    report['books_by_status']['reserved'] += 1
                    status = "已预约"
                else:
                    report['books_by_status']['available'] += 1
                    status = "可借阅"
            
            book_info = {
                'book_id': book_id,
                'title': title,
                'author': author,
                'year': year,
                'price': price,
                'status': status
            }
            
            report['books'].append(book_info)
        
        return report
    
    def export_to_csv(self, output_file):
        """导出数据到CSV"""
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'title', 'author', 'category', 'year', 'price']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            books = self.get_all_books()
            for book in books:
                book_id = book.get("id")
                title = book.xpath("title/text()")[0] if book.xpath("title/text()") else ""
                author = book.xpath("author/text()")[0] if book.xpath("author/text()") else ""
                category = book.get("category", "")
                year = book.xpath("year/text()")[0] if book.xpath("year/text()") else ""
                price = book.xpath("price/text()")[0] if book.xpath("price/text()") else ""
                
                writer.writerow({
                    'id': book_id,
                    'title': title,
                    'author': author,
                    'category': category,
                    'year': year,
                    'price': price
                })
    
    def import_from_csv(self, csv_file):
        """从CSV导入数据"""
        with open(csv_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                # 创建书籍元素
                book = etree.SubElement(self.root, "book")
                book.set("id", row['id'])
                book.set("category", row['category'])
                
                title = etree.SubElement(book, "title")
                title.text = row['title']
                
                author = etree.SubElement(book, "author")
                author.text = row['author']
                
                year = etree.SubElement(book, "year")
                year.text = row['year']
                
                price = etree.SubElement(book, "price")
                price.text = row['price']
        
        # 保存更改
        self.tree.write(self.xml_file, encoding='utf-8', xml_declaration=True)

# 使用示例
def main():
    # 创建示例XML文件（如果不存在）
    import os
    if not os.path.exists("library.xml"):
        create_sample_xml("library.xml")
    
    # 初始化图书馆系统
    library = LibrarySystem("library.xml")
    
    # 1. 获取所有书籍
    all_books = library.get_all_books()
    print(f"图书馆共有 {len(all_books)} 本书")
    
    # 2. 获取特定类别的书籍
    programming_books = library.get_books_by_category("programming")
    print(f"编程类书籍有 {len(programming_books)} 本")
    
    # 3. 搜索书籍
    search_results = library.search_books("Python")
    print(f"搜索'Python'找到 {len(search_results)} 本书籍")
    
    # 4. 获取逾期书籍
    overdue_books = library.get_overdue_books()
    print(f"当前有 {len(overdue_books)} 本逾期书籍")
    
    # 5. 获取热门书籍
    popular_books = library.get_popular_books(5)
    print("热门书籍:")
    for book in popular_books:
        print(f"  {book['title']}: 借阅 {book['total_loans']} 次")
    
    # 6. 生成库存报告
    inventory_report = library.generate_inventory_report()
    print(f"\n库存报告 (截至 {inventory_report['report_date']}):")
    print(f"总书籍数: {inventory_report['total_books']}")
    print(f"总价值: ${inventory_report['total_value']:.2f}")
    print(f"按年份分布: {inventory_report['books_by_year']}")
    print(f"按状态分布: {inventory_report['books_by_status']}")
    
    # 7. 导出CSV
    library.export_to_csv("library_export.csv")
    print("\n已导出数据到 library_export.csv")

def create_sample_xml(filename):
    """创建示例XML文件"""
    root = etree.Element("library")
    
    # 添加一些示例书籍
    books_data = [
        {"id": "bk001", "category": "programming", "title": "Python编程", "author": "John Smith", "year": "2020", "price": "39.99"},
        {"id": "bk002", "category": "programming", "title": "Java编程", "author": "Alice Johnson", "year": "2019", "price": "45.99"},
        {"id": "bk003", "category": "database", "title": "SQL基础", "author": "Bob Davis", "year": "2018", "price": "32.99"},
        {"id": "bk004", "category": "web", "title": "HTML与CSS", "author": "Eve Wilson", "year": "2021", "price": "29.99"},
        {"id": "bk005", "category": "programming", "title": "数据结构", "author": "Frank Miller", "year": "2017", "price": "42.99"}
    ]
    
    for book_data in books_data:
        book = etree.SubElement(root, "book")
        book.set("id", book_data["id"])
        book.set("category", book_data["category"])
        
        title = etree.SubElement(book, "title")
        title.text = book_data["title"]
        
        author = etree.SubElement(book, "author")
        author.text = book_data["author"]
        
        year = etree.SubElement(book, "year")
        year.text = book_data["year"]
        
        price = etree.SubElement(book, "price")
        price.text = book_data["price"]
    
    # 添加借阅记录
    loans_data = [
        {"book_id": "bk001", "borrower_id": "user001", "loan_date": "2023-01-15", "due_date": "2023-02-15", "return_date": "2023-02-10", "returned": "true"},
        {"book_id": "bk003", "borrower_id": "user002", "loan_date": "2023-03-01", "due_date": "2023-04-01", "return_date": "", "returned": "false"},
        {"book_id": "bk005", "borrower_id": "user001", "loan_date": "2023-02-20", "due_date": "2023-03-20", "return_date": "", "returned": "false"},
    ]
    
    for loan_data in loans_data:
        loan = etree.SubElement(root, "loan")
        for key, value in loan_data.items():
            loan.set(key, value)
    
    # 保存XML文件
    tree = etree.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True, pretty_print=True)

if __name__ == "__main__":
    main()
```

### 8.2.2 产品配置管理系统

```java
// code/real-world-cases/ConfigurationManager.java
package com.example.config;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import javax.xml.xpath.*;
import org.w3c.dom.*;
import java.io.File;
import java.util.*;

public class ConfigurationManager {
    private Document document;
    private XPath xpath;
    private String configFilePath;
    
    public ConfigurationManager(String configFilePath) throws Exception {
        this.configFilePath = configFilePath;
        File configFile = new File(configFilePath);
        
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        factory.setNamespaceAware(true);
        DocumentBuilder builder = factory.newDocumentBuilder();
        
        if (configFile.exists()) {
            document = builder.parse(configFile);
        } else {
            document = builder.newDocument();
            Element root = document.createElement("configuration");
            document.appendChild(root);
        }
        
        XPathFactory xPathFactory = XPathFactory.newInstance();
        xpath = xPathFactory.newXPath();
    }
    
    public String getValue(String xpathExpression) throws XPathExpressionException {
        XPathExpression expr = xpath.compile(xpathExpression + "/text()");
        Node node = (Node) expr.evaluate(document, XPathConstants.NODE);
        return node != null ? node.getNodeValue() : null;
    }
    
    public void setValue(String xpathExpression, String value) throws Exception {
        // 确保路径存在
        ensurePathExists(xpathExpression);
        
        // 查找或创建节点
        XPathExpression expr = xpath.compile(xpathExpression);
        Node node = (Node) expr.evaluate(document, XPathConstants.NODE);
        
        if (node == null) {
            // 创建新节点
            String[] parts = xpathExpression.split("/");
            Element parent = (Element) xpath.compile("/" + String.join("/", Arrays.copyOf(parts, parts.length - 1)))
                    .evaluate(document, XPathConstants.NODE);
            
            Element newElement = document.createElement(parts[parts.length - 1]);
            newElement.setTextContent(value);
            parent.appendChild(newElement);
        } else {
            // 更新现有节点
            node.setTextContent(value);
        }
    }
    
    public Map<String, String> getSection(String sectionPath) throws XPathExpressionException {
        Map<String, String> section = new HashMap<>();
        
        XPathExpression expr = xpath.compile(sectionPath + "/*");
        NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
        
        for (int i = 0; i < nodes.getLength(); i++) {
            Node node = nodes.item(i);
            section.put(node.getNodeName(), node.getTextContent());
        }
        
        return section;
    }
    
    public List<String> getSectionNames() throws XPathExpressionException {
        List<String> sections = new ArrayList<>();
        
        XPathExpression expr = xpath.compile("/*/name()");
        NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
        
        for (int i = 0; i < nodes.getLength(); i++) {
            sections.add(nodes.item(i).getNodeValue());
        }
        
        return sections;
    }
    
    public void addSection(String sectionName) throws Exception {
        Element root = document.getDocumentElement();
        Element section = document.createElement(sectionName);
        root.appendChild(section);
    }
    
    public void removeSection(String sectionName) throws Exception {
        Element section = (Element) xpath.compile("/" + sectionName)
                .evaluate(document, XPathConstants.NODE);
        
        if (section != null) {
            section.getParentNode().removeChild(section);
        }
    }
    
    public boolean hasPath(String xpathExpression) throws XPathExpressionException {
        XPathExpression expr = xpath.compile("boolean(" + xpathExpression + ")");
        return (Boolean) expr.evaluate(document, XPathConstants.BOOLEAN);
    }
    
    public List<String> searchByValue(String searchTerm) throws XPathExpressionException {
        List<String> paths = new ArrayList<>();
        
        // 搜索所有包含搜索词的节点
        XPathExpression expr = xpath.compile("//*[contains(text(), '" + searchTerm + "')]");
        NodeList nodes = (NodeList) expr.evaluate(document, XPathConstants.NODESET);
        
        for (int i = 0; i < nodes.getLength(); i++) {
            paths.add(getNodePath(nodes.item(i)));
        }
        
        return paths;
    }
    
    public void save() throws Exception {
        TransformerFactory transformerFactory = TransformerFactory.newInstance();
        Transformer transformer = transformerFactory.newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        transformer.setOutputProperty("{http://xml.apache.org/xslt}indent-amount", "2");
        
        DOMSource source = new DOMSource(document);
        StreamResult result = new StreamResult(new File(configFilePath));
        
        transformer.transform(source, result);
    }
    
    private void ensurePathExists(String path) throws Exception {
        String[] parts = path.split("/");
        Element current = document.getDocumentElement();
        
        if (current == null) {
            current = document.createElement(parts[0]);
            document.appendChild(current);
        }
        
        for (int i = 1; i < parts.length; i++) {
            String part = parts[i];
            Node child = xpath.getChildNode(current, part);
            
            if (child == null) {
                Element newElement = document.createElement(part);
                current.appendChild(newElement);
                current = newElement;
            } else {
                current = (Element) child;
            }
        }
    }
    
    private String getNodePath(Node node) {
        List<String> path = new ArrayList<>();
        Node current = node;
        
        while (current != null && current.getNodeType() != Node.DOCUMENT_NODE) {
            path.add(0, current.getNodeName());
            current = current.getParentNode();
        }
        
        return "/" + String.join("/", path);
    }
    
    // 高级配置管理功能
    public void backupConfiguration(String backupPath) throws Exception {
        TransformerFactory transformerFactory = TransformerFactory.newInstance();
        Transformer transformer = transformerFactory.newTransformer();
        transformer.setOutputProperty(OutputKeys.INDENT, "yes");
        
        DOMSource source = new DOMSource(document);
        StreamResult result = new StreamResult(new File(backupPath));
        
        transformer.transform(source, result);
    }
    
    public void restoreFromBackup(String backupPath) throws Exception {
        File backupFile = new File(backupPath);
        if (backupFile.exists()) {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document backupDoc = builder.parse(backupFile);
            
            // 导入备份文档的根元素
            Node importedRoot = document.importNode(backupDoc.getDocumentElement(), true);
            
            // 清除当前配置
            document.removeChild(document.getDocumentElement());
            
            // 添加备份的配置
            document.appendChild(importedRoot);
        }
    }
    
    public void mergeConfiguration(String otherConfigPath) throws Exception {
        File otherFile = new File(otherConfigPath);
        if (otherFile.exists()) {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document otherDoc = builder.parse(otherFile);
            
            // 合并其他配置文档的节点
            NodeList children = otherDoc.getDocumentElement().getChildNodes();
            for (int i = 0; i < children.getLength(); i++) {
                Node child = children.item(i);
                if (child.getNodeType() == Node.ELEMENT_NODE) {
                    Node imported = document.importNode(child, true);
                    document.getDocumentElement().appendChild(imported);
                }
            }
        }
    }
    
    public Map<String, Object> validateConfiguration() throws Exception {
        Map<String, Object> validationResults = new HashMap<>();
        List<String> errors = new ArrayList<>();
        List<String> warnings = new ArrayList<>();
        
        // 检查必需的配置节
        List<String> requiredSections = Arrays.asList("database", "server", "security");
        List<String> actualSections = getSectionNames();
        
        for (String requiredSection : requiredSections) {
            if (!actualSections.contains(requiredSection)) {
                errors.add("缺少必需的配置节: " + requiredSection);
            }
        }
        
        // 检查数据库配置
        if (hasPath("/database")) {
            Map<String, String> dbConfig = getSection("/database");
            
            if (!dbConfig.containsKey("host") || dbConfig.get("host").isEmpty()) {
                errors.add("数据库配置缺少host设置");
            }
            
            if (!dbConfig.containsKey("port") || dbConfig.get("port").isEmpty()) {
                warnings.add("数据库配置缺少port设置，将使用默认值");
            }
            
            if (dbConfig.containsKey("username") && dbConfig.get("username").isEmpty()) {
                errors.add("数据库配置的username不能为空");
            }
        }
        
        // 检查服务器配置
        if (hasPath("/server")) {
            Map<String, String> serverConfig = getSection("/server");
            
            if (serverConfig.containsKey("port")) {
                try {
                    int port = Integer.parseInt(serverConfig.get("port"));
                    if (port < 1 || port > 65535) {
                        errors.add("服务器端口号必须在1-65535范围内");
                    }
                } catch (NumberFormatException e) {
                    errors.add("服务器端口号必须是有效数字");
                }
            }
        }
        
        validationResults.put("errors", errors);
        validationResults.put("warnings", warnings);
        validationResults.put("isValid", errors.isEmpty());
        
        return validationResults;
    }
    
    public static void main(String[] args) {
        try {
            // 创建配置管理器
            ConfigurationManager config = new ConfigurationManager("app_config.xml");
            
            // 设置配置值
            config.setValue("/database/host", "localhost");
            config.setValue("/database/port", "3306");
            config.setValue("/database/username", "admin");
            config.setValue("/database/password", "secret");
            
            config.setValue("/server/port", "8080");
            config.setValue("/server/context", "/myapp");
            
            config.setValue("/security/encryption", "AES");
            config.setValue("/security/key", "mySecretKey123");
            
            // 保存配置
            config.save();
            
            // 读取配置值
            String dbHost = config.getValue("/database/host");
            System.out.println("数据库主机: " + dbHost);
            
            // 获取整个配置节
            Map<String, String> dbConfig = config.getSection("/database");
            System.out.println("数据库配置: " + dbConfig);
            
            // 验证配置
            Map<String, Object> validationResults = config.validateConfiguration();
            System.out.println("配置验证结果: " + validationResults);
            
            // 备份配置
            config.backupConfiguration("app_config_backup.xml");
            System.out.println("配置已备份");
            
            // 搜索配置值
            List<String> searchResults = config.searchByValue("8080");
            System.out.println("搜索'8080'的结果: " + searchResults);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## 8.3 实验验证

让我们创建一个综合实验，展示XPath在实际项目中的应用：

```python
# code/real-world-cases/xpath_project_demo.py
import json
from lxml import etree

class XPathProjectDemo:
    def __init__(self):
        self.sample_xml = self.create_sample_xml()
    
    def create_sample_xml(self):
        """创建示例XML文档"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<company>
    <employees>
        <employee id="emp001" department="engineering" status="active">
            <personal>
                <name>张三</name>
                <age>32</age>
                <email>zhangsan@example.com</email>
                <phone>13800138001</phone>
                <address>
                    <street>科技路123号</street>
                    <city>北京</city>
                    <zip>100000</zip>
                </address>
            </personal>
            <professional>
                <position>高级工程师</position>
                <skills>
                    <skill level="expert">Python</skill>
                    <skill level="advanced">Java</skill>
                    <skill level="intermediate">JavaScript</skill>
                </skills>
                <projects>
                    <project id="proj001" role="lead" completed="true">电商系统重构</project>
                    <project id="proj002" role="member" completed="false">数据分析平台</project>
                </projects>
                <salary currency="CNY">15000</salary>
                <hire_date>2018-05-15</hire_date>
            </professional>
        </employee>
        
        <employee id="emp002" department="marketing" status="active">
            <personal>
                <name>李四</name>
                <age>28</age>
                <email>lisi@example.com</email>
                <phone>13800138002</phone>
                <address>
                    <street>商业街456号</street>
                    <city>上海</city>
                    <zip>200000</zip>
                </address>
            </personal>
            <professional>
                <position>市场经理</position>
                <skills>
                    <skill level="expert">市场分析</skill>
                    <skill level="advanced">团队管理</skill>
                    <skill level="intermediate">设计</skill>
                </skills>
                <projects>
                    <project id="proj003" role="lead" completed="true">品牌推广活动</project>
                    <project id="proj004" role="member" completed="true">产品发布会</project>
                </projects>
                <salary currency="CNY">12000</salary>
                <hire_date>2019-03-20</hire_date>
            </professional>
        </employee>
        
        <employee id="emp003" department="engineering" status="inactive">
            <personal>
                <name>王五</name>
                <age>35</age>
                <email>wangwu@example.com</email>
                <phone>13800138003</phone>
                <address>
                    <street>创新大道789号</street>
                    <city>深圳</city>
                    <zip>518000</zip>
                </address>
            </personal>
            <professional>
                <position>系统架构师</position>
                <skills>
                    <skill level="expert">系统设计</skill>
                    <skill level="expert">云架构</skill>
                    <skill level="advanced">Go语言</skill>
                </skills>
                <projects>
                    <project id="proj005" role="lead" completed="true">微服务架构</project>
                </projects>
                <salary currency="CNY">18000</salary>
                <hire_date>2017-08-10</hire_date>
            </professional>
        </employee>
    </employees>
    
    <departments>
        <department id="engineering" name="工程部">
            <budget currency="CNY">500000</budget>
            <location>北京总部</location>
            <head>emp001</head>
        </department>
        
        <department id="marketing" name="市场部">
            <budget currency="CNY">300000</budget>
            <location>上海分部</location>
            <head>emp002</head>
        </department>
    </departments>
    
    <projects>
        <project id="proj001" name="电商系统重构" status="completed" priority="high">
            <start_date>2021-01-15</start_date>
            <end_date>2021-06-30</end_date>
            <budget currency="CNY">200000</budget>
        </project>
        
        <project id="proj002" name="数据分析平台" status="ongoing" priority="medium">
            <start_date>2021-07-01</start_date>
            <end_date></end_date>
            <budget currency="CNY">150000</budget>
        </project>
        
        <project id="proj003" name="品牌推广活动" status="completed" priority="high">
            <start_date>2021-02-01</start_date>
            <end_date>2021-04-30</end_date>
            <budget currency="CNY">80000</budget>
        </project>
    </projects>
</company>"""
        return xml_content
    
    def demo_employee_queries(self):
        """演示员工信息查询"""
        print("=" * 50)
        print("员工信息查询演示")
        print("=" * 50)
        
        root = etree.fromstring(self.sample_xml)
        
        queries = [
            ("所有员工姓名", "/company/employees/employee/personal/name/text()"),
            ("工程部员工", "/company/employees/employee[@department='engineering']/personal/name/text()"),
            ("年龄超过30的员工", "/company/employees/employee[personal/age > 30]/personal/name/text()"),
            ("薪水超过14000的员工", "/company/employees/employee[professional/salary > 14000]/personal/name/text()"),
            ("拥有'expert'级别技能的员工", "/company/employees/employee[professional/skills/skill[@level='expert']]/personal/name/text()"),
            ("担任项目负责人的员工", "/company/employees/employee[professional/projects/project[@role='lead']]/personal/name/text()"),
            ("在北京的员工", "/company/employees/employee[personal/address/city='北京']/personal/name/text()"),
            ("非在职员工", "/company/employees/employee[@status='inactive']/personal/name/text()"),
            ("拥有'Python'技能的员工", "/company/employees/employee[professional/skills/skill[text()='Python']]/personal/name/text()"),
            ("2018年入职的员工", "/company/employees/employee[starts-with(professional/hire_date, '2018')]/personal/name/text()")
        ]
        
        for description, xpath_expr in queries:
            results = root.xpath(xpath_expr)
            print(f"\n{description}:")
            print(f"XPath: {xpath_expr}")
            print(f"结果: {results}")
    
    def demo_department_queries(self):
        """演示部门信息查询"""
        print("\n" + "=" * 50)
        print("部门信息查询演示")
        print("=" * 50)
        
        root = etree.fromstring(self.sample_xml)
        
        queries = [
            ("所有部门名称", "/company/departments/department/name/text()"),
            ("预算超过40万的部门", "/company/departments/department[number(budget) > 400000]/name/text()"),
            ("北京的部门", "/company/departments/department[location='北京']/name/text()"),
            ("预算最高的部门", "/company/departments/department[number(budget) = max(/company/departments/department/budget)]/name/text()"),
            ("每个部门的负责人", "/company/departments/department/concat(name, ': ', /company/employees/employee[@id=current()/head]/personal/name)")
        ]
        
        for description, xpath_expr in queries:
            results = root.xpath(xpath_expr)
            print(f"\n{description}:")
            print(f"XPath: {xpath_expr}")
            print(f"结果: {results}")
    
    def demo_project_queries(self):
        """演示项目信息查询"""
        print("\n" + "=" * 50)
        print("项目信息查询演示")
        print("=" * 50)
        
        root = etree.fromstring(self.sample_xml)
        
        queries = [
            ("所有项目名称", "/company/projects/project/name/text()"),
            ("高优先级项目", "/company/projects/project[@priority='high']/name/text()"),
            ("已完成项目", "/company/projects/project[@status='completed']/name/text()"),
            ("2021年7月后开始的项目", "/company/projects/project[start_date > '2021-07-01']/name/text()"),
            ("预算超过10万的项目", "/company/projects/project[number(budget) > 100000]/name/text()"),
            ("正在进行的项目", "/company/projects/project[@status='ongoing']/name/text()"),
            ("有结束日期的项目", "/company/projects/project[end_date != '']/name/text()"),
            ("按预算降序排列的项目", "/company/projects/project"),
            ("项目时间跨度（已完成的）", "/company/projects/project[@status='completed']/concat(name, ': ', days-from-date(start_date), ' 到 ', days-from-date(end_date))")
        ]
        
        for description, xpath_expr in queries:
            try:
                results = root.xpath(xpath_expr)
                print(f"\n{description}:")
                print(f"XPath: {xpath_expr}")
                print(f"结果: {results}")
            except Exception as e:
                print(f"\n{description}:")
                print(f"XPath: {xpath_expr}")
                print(f"错误: {str(e)}")
    
    def demo_complex_queries(self):
        """演示复杂查询"""
        print("\n" + "=" * 50)
        print("复杂查询演示")
        print("=" * 50)
        
        root = etree.fromstring(self.sample_xml)
        
        queries = [
            ("工程部员工的平均薪水", "sum(/company/employees/employee[@department='engineering']/professional/salary) div count(/company/employees/employee[@department='engineering'])"),
            ("每个部门员工数量", "count(/company/employees/employee[@department='engineering'])"),
            ("每个部门预算总和", "/company/departments/department[name='工程部']/budget"),
            ("参与高优先级项目的员工", "/company/employees/employee[professional/projects/project/@id = /company/projects/project[@priority='high']/@id]/personal/name/text()"),
            ("拥有3个以上技能的员工", "/company/employees/employee[count(professional/skills/skill) > 2]/personal/name/text()"),
            ("同城市的员工数量", "count(/company/employees/employee[personal/address/city = '北京'])"),
            ("部门预算与员工平均薪水的比较", "/company/departments/department/budget - sum(/company/employees/employee[@department=current()/id]/professional/salary) div count(/company/employees/employee[@department=current()/id])")
        ]
        
        for description, xpath_expr in queries:
            try:
                result = root.xpath(xpath_expr)
                print(f"\n{description}:")
                print(f"XPath: {xpath_expr}")
                print(f"结果: {result}")
            except Exception as e:
                print(f"\n{description}:")
                print(f"XPath: {xpath_expr}")
                print(f"错误: {str(e)}")
    
    def demo_data_transformation(self):
        """演示数据转换"""
        print("\n" + "=" * 50)
        print("数据转换演示")
        print("=" * 50)
        
        root = etree.fromstring(self.sample_xml)
        
        # 创建员工报告
        print("\n员工报告:")
        employees = root.xpath("/company/employees/employee")
        
        for employee in employees:
            emp_id = employee.get("id")
            name = employee.xpath("personal/name/text()")[0]
            department = employee.get("department")
            position = employee.xpath("professional/position/text()")[0]
            salary = employee.xpath("professional/salary/text()")[0]
            
            # 计算技能数量
            skills = employee.xpath("professional/skills/skill")
            skill_count = len(skills)
            
            # 计算项目数量
            projects = employee.xpath("professional/projects/project")
            completed_projects = employee.xpath("professional/projects/project[@completed='true']")
            project_count = len(projects)
            completed_count = len(completed_projects)
            
            print(f"\n员工: {name} ({emp_id})")
            print(f"  部门: {department}")
            print(f"  职位: {position}")
            print(f"  薪水: {salary}")
            print(f"  技能数: {skill_count}")
            print(f"  项目数: {project_count} (已完成: {completed_count})")
        
        # 创建部门统计
        print("\n部门统计:")
        departments = root.xpath("/company/departments/department")
        
        for dept in departments:
            dept_id = dept.get("id")
            dept_name = dept.xpath("name/text()")[0]
            budget = dept.xpath("budget/text()")[0]
            head_id = dept.xpath("head/text()")[0]
            
            # 获取部门负责人姓名
            head_name = root.xpath(f"/company/employees/employee[@id='{head_id}']/personal/name/text()")[0]
            
            # 计算部门员工数量
            employee_count = len(root.xpath(f"/company/employees/employee[@department='{dept_id}']"))
            
            # 计算部门总薪水
            total_salary = sum(
                float(salary) 
                for salary in root.xpath(f"/company/employees/employee[@department='{dept_id}']/professional/salary/text()")
            )
            
            print(f"\n部门: {dept_name} ({dept_id})")
            print(f"  预算: {budget}")
            print(f"  负责人: {head_name}")
            print(f"  员工数: {employee_count}")
            print(f"  总薪水: {total_salary}")
    
    def export_to_json(self):
        """将XML数据导出为JSON"""
        root = etree.fromstring(self.sample_xml)
        
        company_data = {
            "employees": [],
            "departments": [],
            "projects": []
        }
        
        # 提取员工数据
        employees = root.xpath("/company/employees/employee")
        for employee in employees:
            emp_data = {
                "id": employee.get("id"),
                "department": employee.get("department"),
                "status": employee.get("status"),
                "name": employee.xpath("personal/name/text()")[0],
                "age": int(employee.xpath("personal/age/text()")[0]),
                "email": employee.xpath("personal/email/text()")[0],
                "phone": employee.xpath("personal/phone/text()")[0],
                "address": {
                    "street": employee.xpath("personal/address/street/text()")[0],
                    "city": employee.xpath("personal/address/city/text()")[0],
                    "zip": employee.xpath("personal/address/zip/text()")[0]
                },
                "position": employee.xpath("professional/position/text()")[0],
                "skills": [
                    {
                        "name": skill.text,
                        "level": skill.get("level")
                    } for skill in employee.xpath("professional/skills/skill")
                ],
                "projects": [
                    {
                        "id": project.get("id"),
                        "name": project.text,
                        "role": project.get("role"),
                        "completed": project.get("completed") == "true"
                    } for project in employee.xpath("professional/projects/project")
                ],
                "salary": float(employee.xpath("professional/salary/text()")[0]),
                "hire_date": employee.xpath("professional/hire_date/text()")[0]
            }
            company_data["employees"].append(emp_data)
        
        # 提取部门数据
        departments = root.xpath("/company/departments/department")
        for dept in departments:
            dept_data = {
                "id": dept.get("id"),
                "name": dept.xpath("name/text()")[0],
                "budget": float(dept.xpath("budget/text()")[0]),
                "location": dept.xpath("location/text()")[0],
                "head": dept.xpath("head/text()")[0]
            }
            company_data["departments"].append(dept_data)
        
        # 提取项目数据
        projects = root.xpath("/company/projects/project")
        for project in projects:
            project_data = {
                "id": project.get("id"),
                "name": project.xpath("name/text()")[0],
                "status": project.get("status"),
                "priority": project.get("priority"),
                "start_date": project.xpath("start_date/text()")[0],
                "end_date": project.xpath("end_date/text()")[0] if project.xpath("end_date/text()") else None,
                "budget": float(project.xpath("budget/text()")[0])
            }
            company_data["projects"].append(project_data)
        
        # 保存到JSON文件
        with open("company_data.json", "w", encoding="utf-8") as f:
            json.dump(company_data, f, ensure_ascii=False, indent=2)
        
        print("\n数据已导出到 company_data.json")

def main():
    demo = XPathProjectDemo()
    
    # 运行各种演示
    demo.demo_employee_queries()
    demo.demo_department_queries()
    demo.demo_project_queries()
    demo.demo_complex_queries()
    demo.demo_data_transformation()
    demo.export_to_json()

if __name__ == "__main__":
    main()
```

## 8.4 本章小结

本章通过多个实战案例展示了XPath在实际项目中的应用，包括：

- **Web数据抓取**：电商网站商品信息提取、新闻网站内容提取
- **XML数据处理**：图书馆管理系统、产品配置管理系统
- **复杂查询**：多条件筛选、数据统计分析、跨文档关联查询
- **数据转换**：XML到JSON的转换、数据重组和格式化

通过这些案例，您应该能够：

1. 在实际项目中灵活应用XPath技术
2. 解决复杂的数据查询和处理问题
3. 设计高效的XPath表达式
4. 实现跨平台的数据交换和转换
5. 构建基于XML的企业级应用

## 8.5 练习

1. 扩展电商网站爬虫，添加价格变动追踪功能
2. 为图书馆系统添加推荐系统，根据用户借阅历史推荐书籍
3. 实现配置管理系统的版本控制和回滚功能
4. 创建一个XML数据验证工具，可以检查文档结构的完整性和一致性
5. 设计一个基于XPath的报表系统，可以从多个XML源中提取数据并生成报表

尝试运行本章中的示例代码，并根据您的实际需求进行修改和扩展。这些案例可以作为您实际项目的起点，帮助您快速应用XPath技术解决实际问题。