import scrapy
import re
import datetime 

scrapped_at = datetime.datetime.now()

class testSpider(scrapy.Spider):
    name = "wiki"

    def start_requests(self):
        start_urls = [
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=D",
        ]


        #yield all the article links from the start urls
        for url in start_urls:
            yield scrapy.Request( url = url, callback = self.parse )
        
        
    #We want to follow the next page from the start urls until  we are finished entirely (at letter O)
    #Will find all links in the start url that correspond to category
    #Might also find some categories that should not be processed --- Fixed no longer applicable
    def parse(self, response):    
        links = response.xpath('/html/body/div[3]/div[3]/div[4]/div[2]/div[2]/div/div/div/ul/li/a/@href').extract()
        WantedArticles = r"/wiki/[D-N]"
        #links = response.css('div.mw-category-group ul li').xpath('a/@href').extract()
        for link in links:
            if link and (re.match(WantedArticles , link ) != None):
                yield response.follow(url = link, callback = self.parse2)

        #Change the last in the string to the last letter
        forbiddenNextPage =  r"https:\/\/en\.wikinews\.org\/w\/index\.php\?title=Category:Politics_and_conflicts&pagefrom=O"
        #This has to be get() instead of extract so that forbiddenNextPage in nextpageurl can be compared as strings
        nextpageurl1 = response.xpath("//*[@id='mw-pages']/a[contains(.,'next page')]/@href").get()
        nextpageurl = response.urljoin(nextpageurl1)

        if nextpageurl and (re.match(forbiddenNextPage , nextpageurl ) == None):
            # If we've found a pattern which matches
            #print("Found url: {}".format(nextpageurl)) # Write a debug statement
            yield scrapy.Request(nextpageurl, callback=self.parse) # Return a call to the function "parse"

    #Will run over all individual articles and extract appropriate data
    def parse2(self, response): #return individual article
        
        title = response.xpath('/html/body/div[3]/h1/text()').get()
        
        source = response.xpath('/html/body/div[3]/div[3]/div[4]/div/ul/li/span/descendant-or-self::text()').extract()
        
        text = response.xpath("""/html/body/div[3]/div[3]/div[4]/div/p/descendant-or-self::text()[not( parent::strong | ancestor::i)]""").extract()

        keywords = response.xpath("""//div[contains(@class, 'mw-normal-catlinks')]/ul/descendant-or-self::text()""").extract()

        article_date = keywords[0] #The date at which the article was updated last

        keywords.pop(0)

        finaltext = ''.join(text)

        finalsource = ''.join(source)

        yield {
            'title'        : title,
            'source'       : finalsource,
            'scrapped_at'  : scrapped_at,
            'text'         : finaltext,
            'keywords'     : keywords,
            'article_date' : article_date,
        }
