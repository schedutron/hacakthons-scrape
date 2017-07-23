import scrapy

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for quote in response.css("div.quote"):
            yield {
                "text": quote.css("span.text::text").extract_first(),
                "author": quote.css("small.author::text").extract_first(),
                "tags": quote.css("div.tags a.tag::text").extract_first(),
            }
        next_page = response.css("li.next a::attr(href)").extract_first()
        if next_page is not None:
            # response.follow works with relative links as well.
            yield response.follow(next_page, callback=self.parse)
