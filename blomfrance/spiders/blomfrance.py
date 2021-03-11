import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from blomfrance.items import Article


class BlomfranceSpider(scrapy.Spider):
    name = 'blomfrance'
    start_urls = ['https://www.blomfrance.com/london/latest-news/brexit-information']

    def parse(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        next_page = response.xpath('//div[@class="nextPreviouArrows"]/a[1]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//h4/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="summary"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
