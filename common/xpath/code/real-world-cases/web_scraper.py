# 简单的网页爬虫示例，使用XPath提取数据
import requests
from lxml import etree
import csv
import time

class WebScraper:
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
    
    def extract_links(self, html_content, base_url):
        """从HTML中提取所有链接"""
        tree = etree.HTML(html_content)
        
        # 使用XPath提取所有链接
        links = tree.xpath("//a/@href")
        
        # 处理相对链接
        full_links = []
        for link in links:
            if link and not link.startswith('#'):
                if link.startswith('http'):
                    full_links.append(link)
                elif link.startswith('/'):
                    full_links.append(base_url + link)
                else:
                    full_links.append(base_url + '/' + link)
        
        return full_links
    
    def extract_images(self, html_content, base_url):
        """从HTML中提取所有图片"""
        tree = etree.HTML(html_content)
        
        # 使用XPath提取所有图片
        images = tree.xpath("//img/@src")
        
        # 处理相对路径
        full_images = []
        for img in images:
            if img:
                if img.startswith('http'):
                    full_images.append(img)
                elif img.startswith('/'):
                    full_images.append(base_url + img)
                else:
                    full_images.append(base_url + '/' + img)
        
        return full_images
    
    def extract_text_content(self, html_content):
        """从HTML中提取文本内容"""
        tree = etree.HTML(html_content)
        
        # 提取标题
        title_nodes = tree.xpath("//title/text()")
        title = title_nodes[0].strip() if title_nodes else "无标题"
        
        # 提取所有段落文本
        paragraph_nodes = tree.xpath("//p//text()")
        paragraphs = [p.strip() for p in paragraph_nodes if p.strip()]
        
        # 提取所有标题文本
        heading_nodes = tree.xpath("//h1//text() | //h2//text() | //h3//text() | //h4//text() | //h5//text() | //h6//text()")
        headings = [h.strip() for h in heading_nodes if h.strip()]
        
        return {
            'title': title,
            'headings': headings,
            'paragraphs': paragraphs
        }
    
    def extract_meta_info(self, html_content):
        """从HTML中提取元信息"""
        tree = etree.HTML(html_content)
        
        meta_info = {}
        
        # 提取meta标签信息
        description = tree.xpath("//meta[@name='description']/@content")
        if description:
            meta_info['description'] = description[0]
        
        keywords = tree.xpath("//meta[@name='keywords']/@content")
        if keywords:
            meta_info['keywords'] = keywords[0]
        
        author = tree.xpath("//meta[@name='author']/@content")
        if author:
            meta_info['author'] = author[0]
        
        # 提取Open Graph信息
        og_title = tree.xpath("//meta[@property='og:title']/@content")
        if og_title:
            meta_info['og_title'] = og_title[0]
        
        og_description = tree.xpath("//meta[@property='og:description']/@content")
        if og_description:
            meta_info['og_description'] = og_description[0]
        
        og_image = tree.xpath("//meta[@property='og:image']/@content")
        if og_image:
            meta_info['og_image'] = og_image[0]
        
        return meta_info
    
    def extract_tables(self, html_content):
        """从HTML中提取表格数据"""
        tree = etree.HTML(html_content)
        
        tables = []
        
        # 获取所有表格
        table_nodes = tree.xpath("//table")
        
        for i, table in enumerate(table_nodes):
            table_data = {
                'index': i,
                'headers': [],
                'rows': []
            }
            
            # 提取表头
            header_cells = table.xpath(".//thead//th//text() | .//tr[1]//th//text() | .//tr[1]//td//text()")
            table_data['headers'] = [h.strip() for h in header_cells if h.strip()]
            
            # 提取数据行
            row_nodes = table.xpath(".//tbody//tr | .//tr[position()>1]")
            
            for row in row_nodes:
                row_data = []
                cell_nodes = row.xpath("./td//text() | ./th//text()")
                
                for cell in cell_nodes:
                    cell_text = cell.strip()
                    if cell_text:
                        row_data.append(cell_text)
                
                if row_data:
                    table_data['rows'].append(row_data)
            
            tables.append(table_data)
        
        return tables
    
    def extract_form_data(self, html_content):
        """从HTML中提取表单信息"""
        tree = etree.HTML(html_content)
        
        forms = []
        
        # 获取所有表单
        form_nodes = tree.xpath("//form")
        
        for form in form_nodes:
            form_data = {
                'action': form.xpath("./@action")[0] if form.xpath("./@action") else "",
                'method': form.xpath("./@method")[0] if form.xpath("./@method") else "GET",
                'fields': []
            }
            
            # 提取表单字段
            input_nodes = form.xpath(".//input | .//select | .//textarea")
            
            for field in input_nodes:
                field_data = {
                    'type': field.xpath("./@type")[0] if field.xpath("./@type") else "text",
                    'name': field.xpath("./@name")[0] if field.xpath("./@name") else "",
                    'id': field.xpath("./@id")[0] if field.xpath("./@id") else "",
                    'value': field.xpath("./@value")[0] if field.xpath("./@value") else "",
                    'placeholder': field.xpath("./@placeholder")[0] if field.xpath("./@placeholder") else "",
                    'required': field.xpath("./@required")[0] == "required" if field.xpath("./@required") else False
                }
                
                # 处理select字段
                if field.tag == "select":
                    options = field.xpath("./option/text()")
                    field_data['options'] = [opt.strip() for opt in options if opt.strip()]
                
                # 处理textarea字段
                if field.tag == "textarea":
                    field_data['text'] = field.xpath("./text()")[0].strip() if field.xpath("./text()") else ""
                
                form_data['fields'].append(field_data)
            
            forms.append(form_data)
        
        return forms
    
    def scrape_page(self, url):
        """抓取单个页面并提取所有有用信息"""
        print(f"正在抓取页面: {url}")
        
        html_content = self.fetch_page(url)
        if not html_content:
            return None
        
        # 解析URL获取基础URL
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # 提取各种信息
        page_data = {
            'url': url,
            'title': "",
            'meta': {},
            'text_content': {},
            'links': [],
            'images': [],
            'tables': [],
            'forms': []
        }
        
        # 提取标题和文本内容
        text_content = self.extract_text_content(html_content)
        page_data['title'] = text_content['title']
        page_data['text_content'] = text_content
        
        # 提取元信息
        page_data['meta'] = self.extract_meta_info(html_content)
        
        # 提取链接和图片
        page_data['links'] = self.extract_links(html_content, base_url)
        page_data['images'] = self.extract_images(html_content, base_url)
        
        # 提取表格和表单
        page_data['tables'] = self.extract_tables(html_content)
        page_data['forms'] = self.extract_form_data(html_content)
        
        return page_data
    
    def save_to_csv(self, page_data, filename="web_content.csv"):
        """将抓取的数据保存到CSV文件"""
        if not page_data:
            print("没有数据可保存")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'title', 'description', 'keywords', 'links_count', 'images_count', 'tables_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            row = {
                'url': page_data['url'],
                'title': page_data['title'],
                'description': page_data['meta'].get('description', ''),
                'keywords': page_data['meta'].get('keywords', ''),
                'links_count': len(page_data['links']),
                'images_count': len(page_data['images']),
                'tables_count': len(page_data['tables'])
            }
            writer.writerow(row)
        
        print(f"数据已保存到 {filename}")
    
    def save_tables_to_csv(self, page_data, directory="tables"):
        """将表格数据保存到单独的CSV文件"""
        import os
        
        if not page_data or not page_data['tables']:
            print("没有表格数据可保存")
            return
        
        # 创建目录（如果不存在）
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        for i, table in enumerate(page_data['tables']):
            filename = os.path.join(directory, f"table_{i+1}.csv")
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 写入表头
                if table['headers']:
                    writer.writerow(table['headers'])
                
                # 写入数据行
                for row in table['rows']:
                    writer.writerow(row)
            
            print(f"表格 {i+1} 已保存到 {filename}")

# 使用示例
def main():
    # 创建爬虫实例
    scraper = WebScraper()
    
    # 要抓取的URL（这里使用示例URL）
    url = "https://example.com"  # 替换为您想抓取的URL
    
    # 抓取页面
    page_data = scraper.scrape_page(url)
    
    if page_data:
        # 显示摘要信息
        print("\n页面抓取摘要:")
        print(f"URL: {page_data['url']}")
        print(f"标题: {page_data['title']}")
        print(f"链接数: {len(page_data['links'])}")
        print(f"图片数: {len(page_data['images'])}")
        print(f"表格数: {len(page_data['tables'])}")
        print(f"表单数: {len(page_data['forms'])}")
        
        # 显示元信息
        if page_data['meta']:
            print("\n元信息:")
            for key, value in page_data['meta'].items():
                print(f"  {key}: {value}")
        
        # 显示前几个标题
        if page_data['text_content']['headings']:
            print("\n页面标题:")
            for i, heading in enumerate(page_data['text_content']['headings'][:5]):
                print(f"  {i+1}. {heading}")
        
        # 显示前几个链接
        if page_data['links']:
            print("\n前5个链接:")
            for i, link in enumerate(page_data['links'][:5]):
                print(f"  {i+1}. {link}")
        
        # 显示表格信息
        if page_data['tables']:
            print("\n表格信息:")
            for i, table in enumerate(page_data['tables']):
                print(f"  表格 {i+1}: {len(table['headers'])} 个列, {len(table['rows'])} 行")
        
        # 保存数据
        scraper.save_to_csv(page_data)
        scraper.save_tables_to_csv(page_data)
        
        # 如果有表单，显示表单信息
        if page_data['forms']:
            print("\n表单信息:")
            for i, form in enumerate(page_data['forms']):
                print(f"  表单 {i+1}: 方法={form['method']}, 操作={form['action']}, 字段数={len(form['fields'])}")
                for j, field in enumerate(form['fields'][:3]):
                    print(f"    字段 {j+1}: 名称={field['name']}, 类型={field['type']}")

if __name__ == "__main__":
    main()