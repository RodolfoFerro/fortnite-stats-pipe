import scrapy


class FortniteStatsSpider(scrapy.Spider):
    name = "fortnite-stats"

    def start_requests(self):
        urls = [
            'https://fortnitestats.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        table = response.xpath('//*[@class="table"]')
        col_names = table.xpath('//thead//tr//th//text()').extract()
        rows = table.xpath('//tbody//tr')



        with open(self.filename, 'w+') as f:
            f.write(','.join(col_names))

            for row in rows:
                data = row.xpath('td//text()').extract()
                data = [data[3]] + data[5:]
                f.write('\n' + ','.join(data))

        self.log(f'Saved file {self.filename}.')