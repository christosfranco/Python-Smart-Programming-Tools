import scrapy
import re
import datetime 

scraped_at = datetime.datetime.now()
domain = "en.wikinews.org"
typ = "reliable"
article_id = 0

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

        for link in links:
            if link and (re.match(WantedArticles , link ) != None):
                yield response.follow(url = link, callback = self.parse2)

        #Change the last in the string to the last letter
        forbiddenNextPage =  r"https:\/\/en\.wikinews\.org\/w\/index\.php\?title=Category:Politics_and_conflicts&pagefrom=O"
        #This has to be get() instead of extract so that forbiddenNextPage in nextpageurl can be compared as strings
        nextpageurl = response.xpath("//*[@id='mw-pages']/a[contains(.,'next page')]/@href").get()
        nextpageurl = response.urljoin(nextpageurl)

        if nextpageurl and (re.match(forbiddenNextPage , nextpageurl ) == None):
            # If we've found a pattern which matches
            #print("Found url: {}".format(nextpageurl)) # Write a debug statement
            yield scrapy.Request(nextpageurl, callback=self.parse) # Return a call to the function "parse"


    #Will run over all individual articles and extract appropriate data
    def parse2(self, response): #return individual article
        
        title = response.xpath('/html/body/div[3]/h1/text()').get()
        

        content = response.xpath("""/html/body/div[3]/div[3]/div[4]/div/p/descendant-or-self::text()[not( parent::strong | ancestor::i)]""").extract()
        content = ''.join(content)

        url = response.url

        # Keywords and date
        keywords = response.xpath("""//div[contains(@class, 'mw-normal-catlinks')]/ul/descendant-or-self::text()""").extract()
        finalkeywords = '[\"'
        written_at = ""
        date_index = 0
        dateRegexPattern = r"(?:january|february|march|april|may|june|july|august|september|october|november|december)(?: )(?:[\d]{1}|[\d]{2})(?:, )(?:1\d{3}|2\d{3})"
        for i in range(len(keywords)):
            keyword = keywords[i].lower()
            if(re.fullmatch(dateRegexPattern, keyword) != None):
                date_index = i
            else:  
                finalkeywords += (keyword + '\", \"')   
        written_at = keywords[date_index]        
        keywords.pop(date_index)
        if len(finalkeywords) < 3:
            finalkeywords = ''
        else:     
            finalkeywords = finalkeywords[:-3] + ']'

        # Sources
        sources = []
        sourcesFromTemplate = response.xpath("""//a[contains(@class, 'external text')]/@href""")
        for li in sourcesFromTemplate:
            temp = li.get().lower()
            sources.append(temp)
            
        finalsources = '[\"'
        
        for i in range(len(sources)):
            source = sources[i].lower()
            finalsources += (source + '\", \"')
        
        if len(finalsources) < 3:
            finalsources = ''
        else:
            finalsources = finalsources[:-3] + ']'            


        global article_id 

        yield {
            'article_id'   : article_id,
            'title'        : title,
            'sources'      : finalsources,
            'scraped_at'   : scraped_at,
            'content'      : content,
            'keywords'     : finalkeywords,
            'written_at'   : written_at,
            'domain'       : domain,
            'url'          : url,
            'type'         : typ,
        }

        article_id += 1
