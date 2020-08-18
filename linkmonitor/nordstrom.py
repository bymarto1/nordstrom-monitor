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
 
async def get_cookie(session):
	print('klk')
	url = 'https://www.nordstrom.com/api/looks/stylehaslook/' + str(random.randint(1234, 123456789))
	headers = {
	'authority':  'www.nordstrom.com',
	'method': 'GET',
	'scheme': 'https',
	'accept': ' */*',
	'accept-encoding': ' gzip, deflate, br',
	'accept-language': ' es,ca;q=0.9,en;q=0.8,de;q=0.7',
	'clientid': ' APP02369',
	'identified-bot': ' False',
	'nord-country-code': ' US',
	'nordapiversion': ' 1',
	'sec-fetch-dest': ' empty',
	'sec-fetch-mode': ' cors',
	'sec-fetch-site': ' same-origin',
	'user-agent': ' Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
	'x-y8s6k3db-a': ' _SDIP=NgsKnf-ImH-qGlc7oKaBeqSxuQHXU6lI4GpIXUfuTsnU0xXQlKIOEx=fSNRMphPfUQAqebpbvpb-E_77EJGkJtjI8O=Kw0JpoxEqbghHpp0UtwPObO_nF6knaJ4azG9_nVK5C45o2Awp46Vc=-C8_GSw7Jm92_7X-FoJ4WjjJXNgndEKasQMMY0Er_tYix1WfnU5FIyqe5gCNfBrr1nfvugRaLjvFIDlQCSufwXXg__OvvJOS7FURbl_BgfX4wxNxsbOho_RtVoB0E70znXLgho30=7_uhj01orPbckTcogQfa=MXsuCElm8v=6uKYCW5TyM1mHP-xfArGq-4mzlPH1XGTxGcgXNe=E0xJopkkpPu8dXgAiVqcizVaYFm4w7j5XlU_ogshurbjy9ulQfPozStpCTIMmoYAqgeDQ7Rw9KNidjnlVettA8UwpJIv6U7h2lGd-gzq5ntleK7rWwowsHsHe3bGAot=qfQrJ=EToj-xINwe8Qx5j_pKUwGYXYWBMdKHckEHJCI=bzmeiH8PQWE4n7b7ydbOPRO-usC72uguFMfkrRd0gy8y4CzvYsRLKWW3NySn03L=8HdlsqqzkFpP95Y0j2_bHciE9g2dtGplz2RcRgKFoog6Vx-Odri5Ktqq9X7h9faRRyuUIp7JSCiT6HRtPUPaeQqd515w3Avn4=Q3IPDwnBJvhT4YDi7LCx7O4E8wyF6Tg-rAgyqNz8QeOx0EMOnmGIJj4mYfdwzhKecQz5HKxh3UnLRjDd_xML3kRXvUbW6sx49yQuAPGmVC2FadHXnVJQLdwwnxL5Mb69vyrdk3iOp2-izMpgqd4aT0N_yaG5cf28h3wGk_MIwtRF2ExKt5UgkYK4Tq3_cz2Wu5r9gHSnOAyi5N1cJqxF13jPYfp0tFJ=qkafCcIGKpEtl1oxCcm5ErDHC7BmtUfd13FCAXIo2TQari411z5PHHsWzGjlBoPHo1QlIqNndoSnkc-gDPTdmtRxskCEoHxb1CNjvxckcHaA5UQwba_LsDtzd-0QNURmI_lHUxEDusH1kExbxx=n1lu-o7gOFQ5vHwkbYwXbOSx=UsoR=vUdxrsD8OCvKohEbblVXMu6LLM3H5atrX7yNW1qij_VpM4gUr5TX=JfKXmYabpdrSL2_2etMTTWIffzdG2J-_WaP7_37cOn1a4sr5n9gE8LMkoIC3wVkkgex-9pYd9x1chBR=4vGQ5qYt3BGR6a-OML6PvWRV0YK7s0K4lO04DIbXwx4FoYJ=7-Ez83_J=h8DE2x2ILvw8vXoPxE6dwgRJNLYVBR5SJhGy=QuDTuSd7TanCxsofTCuHj5Y2_G9MXCCVUKchWLt67NA_kutysJl=87Crw04yiPFDwy5Oyi3mWHke6=H4Gf_NdRVgBm5g39kYc9Oj-6OTrC2qubMRHzp7pgTJ5RUae5SDu6sWCI7TuGk8JRBWTe4L9K-UG_00k1vS=rTyIT7onIXOOg78cNF8fDJa1vgY2v=yE52bTeUPd8b8jgbIN_de3cnn5DAw9ksv8Pw4KLINUl2_Di7Ke8c-TszQz6hVnv7VpFigm_ceBbJ0KTX=1RV4Um_yv2h3Kn1-Nr=dqcOKqTnTMWPdA1fXVw9RPQiejKylVE5wBCX0sQGWag0xce2AX6KyvTarMFxV1q3c33fRHw4=3KVEbqIgmLqBqvszwHO8xWGq07G7jj5GXqx1nerlfHlN2KkaTXIGTnSEQYMDFzbpM2fjcrIoTjqansRoONEdVDqqgVyWpjo21iPtnRkn14lIdgUlDn0kqPwUm=qniGKuWYGhpS0g1UqVal2tG97wfmnM9lmFxMdE3oks1esMS1lemjL=UuFdqsI3eH5NTYMPY8R6_-thEow4QPq_yNrDY=u2RPXoThBxQlWryohH1uQAe_gX7IoHPm-CKkWUx=p0q4QHxuA2Dh3x0Bb0R9acdip0Eb0UgehMrc_a46uNuiCQ3bI45Wy8QGVSC6h85QzaL2KjEwUp8gnslDhg7M-uCFqPbijKhbWcif2=Us8IHKReBRGHn4q4l5m-6mBXhP3_=aWxOKmNrTLdzYwzroqXqoKorh6QcEkMGeHwkENhpBrFnNG9HzHvl-U_i2zVsMpEHnBlQefTwnOxyfCMAC6cjhtvPGSLa9lrrepWJkw19iLA9Povbxpt59y3Wu-2LHx-ecTQhMugqM25Hm7TI4mab68YHnm3YB6mT_mx2mE1dpE-i9xhCI_5YnHePPd2=XsngOWUeuYesxL3un7bao-xiKQvYyjSb8-H8gQ8ogRaPosVMskGhQTnEue3PVc8pw4_5-N5GoiKUpJynamH5endlUtoBTbVJt_-pBLf1WIpdap0WOw46Dao7fSTWDfb8VDeCJfJW-MJd03LF_1Jj=4Dl6Rn1JXYJPxnTUDEChu0U2KS-X56bcB_f64bpssVaCIofwMEkIb8tXA2RmsmtXJ=w0PBDOMRLNDnM9qYW3GKU=ogHQfNGKhj4TAyQ-qjk9xQaPS7ik0xO9OrxKaMwWWBeeKfKsq=PlhDnshdcUh6H4kRjdoOwRIDtjWLF=x-PnnX69j5ceudzSRqkVlTWbVBh0tmBKxCcV6t_dUcl1KFbU00pSXt3m5Au98Ln_ftGYa-xhzaigoFO96lM6I99_WfUbH1DDIixLAleijbKjG3_KINrpqC94pCf_4LGP5Iqsc0B1V6MBjs4QCSW_Jd72nosQEQN5QJlwQmw-4yCwOxGN4qb2IdJwBxraGJn9U1vIcQGY5OtFysAWBM_AHT7hhVzeVeox4tf=-rs7GS_D74Y_qUvVH-fY5Aap7HT7k8KvrzUareiv4vfe55xLTSW1d0nxgO4u7OQ_Kx6UdFpzsJhSBe8qd2kxVfwqvAc8ciGMB9smmLdfrmotVGmR8u9fUd6FCb9YJorEaOIWR2yVq2SdqeJLzYxA7gwW-MIu_QSBct4ud-H7=DIRVY9aps7TvlR083p2w7reB31o_kaujCayBwX6FxO7muEDmKRWDXMBI9xxaFkPPm=PMdONXfCmEtfL-mppUbpPntczL0ePq1efaq7Dj0N=ehDHpV58fcFe1bN_f1Q6wYYtut27Gy4hH1fcoyOKJAbl9F0obs5S2mk5UilMy9HhsvwmRF_y8mq_lFi0D4b-7WmAX=DxQdXuPwNbhV19adrtqVHvDgKt-P275ormEi5dz4J_LHOTHJuu6PTgMdLSYjPFO=hIW0468dYeLum2Nb4Fm5CPfHzRa1SGRLS5gIJyJM4WIY6_Oi6Fj4cL2S1H4mhoPNMQIjy_1hdApFPNRWdN1=A=8PaKKTjAMQoJFbCkPVFonclrBf3=_41goFMGdA0JY7Jctf4BvT1h3ydUXO1bbp3BCOdi8hunUgWkSqu-Hq3X_O1Jn0GnxM2wlbt98fWJjWk3tuHFJzfdG6VU0we9U0=UgzjtU9-AB6lNCPV84_P3hk9QbcOXn2PlpXULYY8kiBxj8lHAgpU_HqG19q3zbF6-zcE7Rl-WPMfgG8R1xKkMHDuA9mbb1SxknsC-qFcNQUbjRYfpa3x3mH8OklMLSXhdrcLAfDJKz5qIGBxQStEbckpdb_E0B4i-tJHmNe0LCOU=gPKzCKJ7bVCQ-cf6EzbEwNdGGXSeKgN73QfdrnVLG8eLy85xE_q3mTAARMird2cNz3GFVI48_NhhWqnXcnivod30TYd7c5qyXCjs2UKbiCziJu43WrVAyi4cSmVJ9aLJDGu=Y6UBYORXV4jFVu_Tdbytvs22fSmC5jjMQ5DiKqW=nV-8HWzvTTjWjaNybH8WCFa519B=ngU-NE5GcGduWHLfpuv72Xkp3dXp1bNxKwfXre9HjwMUXioLbGyVWgsW60I5thoT36yXrkcXTvv3hN2jhgp9j5EMjUuk7nKOKjEu=g2TX7w3A0sdNgx69BiKv3Ne0-KghRE39FQK1QojIcJx0Av7TxNjuuFi-40-grjI8hX_HnHYn4NbSN0S_UEl36DBuTBoT_jq3CGx5Xa8CwxhqAIVKY3PzgGW2Ua2nE5ypySDT4SVXu2HtzC8EVGrlsVz=Wi6Rr_zAsxnCyrmUu3cc4VOoSSLC0cuFr9IA=Hc4TIVjxRE9t35kKX9FKpK5s2_h-ein7Si1gUoAnRLOxzag4LIQ7ByfE=BbudhgGshJflwhiJTuDv=LU43Fry8CmMTJWLW_GuaPfExYQnS7LPu1yuMQcAr9gEKyjWE-8csztMWIzpbTrRob9tCFY6FY-R7IIT63=rbwv_DBPqnFK5cyXI_reoDNMLyjegjWwf8mfTUT3feEjHbaTr1pYtpfMKd3=b1LwmvHEWhHcK_DSWh0dHlOQagNvvsHwXCHfSMwwXdHl1azx2q_JnPONGTy1M1aR04F8qYUD7_n-c=6BYpjdSApaq_dXi3-4tytBvHmph3=4QEO33SB61_4HK78F0JP=FScJ-AKh3=NWhORX1g9848BkJmV2DCi_C4s1cDn=QIIlMo36Sm=ozjE7kOUmutxJSx4DjEtsS4QxDHlNgBwX0ejdVOB2Y3HoP5rwI-M8y-54dXbTQzhrUC6RRCoQn1crjy-xjEkJKk=FezbADM-_Q_8ApEzNKtH3ukEiTXoBkJqUEnENiiu71erxWhFQDpTeBK3tYLwNIOTq50mVXzMUQ4QkNh41EoJwyz5T0wcrpGla1nHBshyX3a9=xma2YisTpRIRq4VXLhLWhvgd5V=jciHEv4vs8B8g5r=_thjxmA5vsbjkr4K-T3jQ_oso-y=nzDrAs3ihRrKEKDO_2poY2QDJk1eaa13jMmzB87qz1LB0aX87MDDqaY6jO-lxtnKIJlSwqsdcmjn9vVCmyif7j0m28MwWKYPGS_iB_RVyEV0PvhwGsoSwuOKMB81=0DJQcOG__lIBjNOOzHSPFc88_lqbFJ=fK1UMal5c3RRBmIenK2t5=fa4ft3o7r_pwk_abjdGaRbx3jnSR8KLzlQmhgevynEOh7f_GOe6P_86gagxW1Mx8vni1Rv_jCmuuFSuJu3Piaj6VieI=oKbVTpPW7XALqVwfxo8OK6DgNMPEqqLHrjabTUiIY-MgmQuYqgH1hY4S0ftQAcOuiCvs=m83fwhgSFG04bbwecmuqG41CaSsMTsYCBqaPrHikUfTWim9Ixq62JITvpl0u3hn4eXS0efJRlh8',
	'x-y8s6k3db-b': ' -hj9pel',
	'x-y8s6k3db-c': ' AMBGVQF0AQAA94ZLeV1vDU_P-SC_X1wpB9PI0R6Iqjdq-7Iz5gf0B8AbBoc5',
	'x-y8s6k3db-d': ' AAaihIjBDKGNgUGASZAQhISy1WIH9AfAGwaHOSPT0RQSNP1UAPFw1Z87LHSljbqsAkV-70A',
	'x-y8s6k3db-f': ' AwzuYAF0AQAANDLZjbCd4jfHR8IHCw2VD9x8zmS4gBq1Cgiqp8-aZsOA28ntAVAnJzeucmGVwH8AAEB3AAAAAA==',
	'x-y8s6k3db-z': ' q'
	}
	
	async with session.get(url , headers = headers  ) as response:
		response.text_content = await response.text()

	cookies = response.headers['Set-Cookie']
	print(cookies)
	return cookies











class Monitor:
	def __init__(self, id, *, urlQueue, proxyBuffer, stock_info, session, webhook):
		self.urlQueue = urlQueue
		self.proxyBuffer = proxyBuffer
		self.stock_info = stock_info
		self.session = session
		self.first = True
		self.cookie = ''
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

		if self.cookie!= '':
			headers={
				'set-cookie': self.cookie 
			}
			async with self.session.get(urlts ,headers = headers ) as response:
				response.text_content = await response.text()

		else : 
			async with self.session.get(urlts  ) as response:
				response.text_content = await response.text()
		
		
		#print(response.text_content)
		#print(response.text_content)
		log_based_on_response(self.id, response)
		raise_for_status(response)

		
		if '<title></title>'  in response.text_content:
			print('cookie error')
			self.cookie = await get_cookie(self.session)
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
	'authority': 'www.nordstrom.com',
	'method':'GET',
	'scheme':  'https',
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
	#'cookie': 'Ad34bsY56=AA-BcQF0AQAAMX4YFwZdRFYUJnQ37RPMOeJiaJoyA_Ur5sfKRzItys3d6h8T'
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
