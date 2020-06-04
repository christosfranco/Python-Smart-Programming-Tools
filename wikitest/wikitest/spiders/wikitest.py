import scrapy
import re
# Import the CrawlerProcess: for running the spider
#from scrapy.crawler import CrawlerProcess
class testSpider(scrapy.Spider):
    name = "wikitest"
    def start_requests(self):
        start_urls = [
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=D",
            '''"https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=E",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=F",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=G",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=H",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=I",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=J",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=K",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=L",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=M",
            "https://en.wikinews.org/w/index.php?title=Category:Politics_and_conflicts&from=N",'''
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
        forbiddenNP =  r"https:\/\/en\.wikinews\.org\/w\/index\.php\?title=Category:Politics_and_conflicts&pagefrom=O"
        #This has to be get() instead of extract so that forbiddenNP in nextpageurl can be compared as strings
        nextpageurl1 = response.xpath("//*[@id='mw-pages']/a[contains(.,'next page')]/@href").get()
        nextpageurl = response.urljoin(nextpageurl1)

        #Obama signs $787 billion stimulus package #Last on the N page
        #Obama signs healthcare bill for 9/11 emergency workers #first on the O page
        if nextpageurl and (re.match(forbiddenNP , nextpageurl ) == None):
            # If we've found a pattern which matches
            #print("Found url: {}".format(nextpageurl)) # Write a debug statement
            yield scrapy.Request(nextpageurl, callback=self.parse) # Return a call to the function "parse"

    #Will run over all individual articles and extract appropriate data
    def parse2(self, response):
        #return individual article 
        #title
        title = response.xpath('/html/body/div[3]/h1/text()').get()
        #source(s)
        source = response.xpath('/html/body/div[3]/div[3]/div[4]/div/ul/li/span/descendant-or-self::text()').extract()
        #date
        date = response.xpath('/html/body/div[3]/div[3]/div[4]/div/p[1]/strong/text()').get()
        #text
        text = response.xpath("""/html/body/div[3]/div[3]/div[4]/div/p/descendant-or-self::text()[not( parent::strong | ancestor::i)]""").extract()

        finaltext = ''.join(text)

        finalsource = ''.join(source)

        yield {
            'title'  : title,
            'source' : finalsource,
            'date'   : date,
            'text'   : finaltext,
        }

        #put date text and source in right side of equal sign
        #title as key
        #test_dict[title] = [finalsource , date , finaltext]

#dictionary to store data
#test_dict = dict()

#run spider
#process = CrawlerProcess()
#process.crawl(testSpider)
#process.start()

# Print a preview of dict
#var = test_dict.keys()
#print(var)