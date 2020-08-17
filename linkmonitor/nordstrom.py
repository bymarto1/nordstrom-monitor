import util
import aiohttp
import asyncio
import discord
import re
import logging
import traceback
import time
import re
import random
import json
from urllib.parse import urljoin
from contextlib import asynccontextmanager
import random
from datetime import datetime



screen_logger = logging.getLogger('screen_logger')
screen_logger.setLevel(logging.INFO)

streamFormatter = logging.StreamHandler()

streamFormatter.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

fileFormatter = logging.FileHandler("nordstrom.logs")

fileFormatter.setFormatter(logging.Formatter('%(asctime)s %(message)s'))

screen_logger.addHandler(streamFormatter)
screen_logger.addHandler(fileFormatter)


class invalid_status_code(Exception):
	"""exception if status code is not 200 or 404"""









def raise_for_status(response, skip = ()):
	if not (response.status == 200 or response.status == 404 or response.status in skip):
		raise invalid_status_code('{} -> {}'.format(response.url, response.status))
	
def log_based_on_response(id, response):
	screen_logger.info("{} > {} -> {} " .format(id, str(response.url), response.status))
	#print(response.headers['server-timing'])

def log_exception(id, ex, *, traceback = True):
	if traceback:
		screen_logger.debug("{} > {}".format(id, traceback.print_tb(ex.__traceback__)))
	screen_logger.info("{} > {}". format(id, str(ex)))



def get_title(sc):
    return re.search('property="og:title" content="(.+?)"',sc).group(1).strip()
    

def get_image(sc):
    return re.search('srcSet="(.+?) 1x,',sc).group(1).strip()

def get_price(sc):
	return re.search('originalPriceString":"(.+?)"',sc).group(1).strip()
 
class Monitor:
	def __init__(self, id, *, urlQueue, proxyBuffer, stock_info, session, webhook):
		self.urlQueue = urlQueue
		self.proxyBuffer = proxyBuffer
		self.stock_info = stock_info
		self.session = session
		self.first = True
		self.instock = False
		self.id = id
		self.embed_sender = discord.embedSender(webhook)
	
	@asynccontextmanager
	async def load_url(self, *, wait):
		url = await self.urlQueue.get()
		try:
			yield url
		finally:
			self.urlQueue.put_nowait(url)
			await asyncio.sleep(wait)
	
	
	async def process_url(self, url, proxy):
		restocked = True
		instock= True
		urlts = url +"?ts="+ str(time.time()) 
		#print (urlts)
		current_stock_info = {}

		delay = random.randint(0, 1)
		#print(delay)
		time.sleep(delay)
	
		async with self.session.get(urlts  ) as response:
			response.text_content = await response.text()
		
		
		#print(response.text_content)
		#print(response.text_content)
		log_based_on_response(self.id, response)
		raise_for_status(response)

		
		if '<title></title>'  in response.text_content:
			print('cookie error')
		elif '<title>Nordstrom</title>' in response.text_content:
			instock = False
		else:
			if self.first:
				self.stock_info['title'] = get_title(response.text_content)
				print(self.stock_info['title'])
				self.stock_info['url'] = url
				self.stock_info['imgUrl'] = get_image(response.text_content)
				print(self.stock_info['imgUrl'])
				self.stock_info['price'] =get_price(response.text_content)
				print(self.stock_info['price'])
				if instock:
					self.instock = True
				
			if(not self.first):
				if instock != self.instock:
					restocked= True

			sizes=[]
			if instock == True:
				sizechart = re.search(r'"size":{"allIds":\["(.+?)"\],"byId"',response.text_content, re.S).group(1).strip()
				print(sizechart)
				sizes = list(sizechart.split('","'))

			print(sizes)
			current_stock_info['sizes'] = sizes
		
			if(not self.first):
					print(len(self.stock_info.get('sizes')))
					if self.stock_info.get('sizes') != current_stock_info.get('sizes') and len(self.stock_info.get('sizes'))<=len(current_stock_info.get('sizes')):
							restocked = True

			if restocked:
				self.stock_info['sizes']= current_stock_info['sizes']
				screen_logger.info("{} > {} Restocked Sizes".format(self.id, url))
				
				#for size_info in restocked:
				
			#		screen_logger.info("{} > {}-{}".format(self.id, size_info['size_code'], size_info['color_name']))
				
				embed = discord.make_embed(self.stock_info)
				
				if await self.embed_sender.send(embed):
					screen_logger.info("{} > **Discord Notification Sent for {}**".format(self.id, url))
				else:
					screen_logger.info("{} > **Discord Notification Failed for {}**".format(self.id, url))

			self.first = False
			self.stock_info['sizes'] = current_stock_info['sizes']	

	
	async def start(self, wait):
		proxy = await self.proxyBuffer.get_and_inc()
		
		screen_logger.info('{} > Using Proxy {}'.format(self.id, proxy))
		
		while True:
			async with self.load_url(wait = wait) as url:
				#screen_logger.info(f"{self.id} > Checking {url}")
				for i in range(2):
					try:
						await self.process_url(url, proxy)
						break
					except Exception as e:
						log_exception(self.id, e, traceback = False)
						
						if i == 1:
							proxy = await self.proxyBuffer.get_and_inc()
							screen_logger.info('{} > Changing Proxy to {}'.format(self.id, proxy))






async def main(urls, proxies, workers, wait_time):
	#queries = [{'url': link, 'previousStockedSizes': []} for link in queries]
	
	proxyBuffer = util.readOnlyAsyncCircularBuffer(proxies)
	
	urlQueue = asyncio.Queue()
	
	for url in urls:
		urlQueue.put_nowait(url)
	
	webhook = util.nonblank_lines('webhook.txt')

	headers = {
	'': 'authority: www.nordstrom.com',
	'': 'method: GET',
	'': 'scheme: https',
	'accept': ' text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	'accept-encoding': ' gzip, deflate, br',
	'accept-language': ' es,ca;q=0.9,en;q=0.8,de;q=0.7',
	'cache-control': ' max-age=0',
	'sec-fetch-dest': ' document',
	'sec-fetch-mode': ' navigate',
	'sec-fetch-site': ' same-origin',
	'sec-fetch-user': ' ?1',
	'upgrade-insecure-requests': ' 1',
	'user-agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.3',
	'cookie': '  Bd34bsY56=AHYfQfxzAQAAzijv2pZreyBjxtIEz5TQ2hG75jMh-8IraFtigu0Mp7JXjaFb;'
	}

	timeout = aiohttp.ClientTimeout(total = 8)
	
	stock_info = {}

	session = aiohttp.ClientSession(headers = headers, timeout = timeout, cookie_jar = aiohttp.CookieJar() )
	
	monitors = [Monitor(f'worker-{i}', stock_info = stock_info, session = session, urlQueue = urlQueue, proxyBuffer = proxyBuffer, webhook = webhook[0]) for i in range(workers)]
	
	coros = [monitor.start(wait = wait_time) for monitor in monitors]
	
	await asyncio.gather(*coros)
	
	await     session.close()
		
if __name__ == "__main__":
	
	url_file = 'urls.txt'
	proxy_file = 'proxies.txt'
	
	urls = util.nonblank_lines(url_file)
	
	proxies = util.load_proxies_from_file(proxy_file, shuffle = True)

	workers = len(urls)
	
	wait_time = 2


	policy = asyncio.WindowsSelectorEventLoopPolicy()
	asyncio.set_event_loop_policy(policy)

	asyncio.run(main(urls, proxies, workers, wait_time))
