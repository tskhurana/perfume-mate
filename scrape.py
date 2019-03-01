import requests
from scrapy.http import TextResponse
import json
import re
import sys, os, datetime

user_agent = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/58: .0.3029.110 Chrome/58.0.3029.110 Safari/537.36'}
url = "https://www.fragrantica.com"
adv_url = "https://www.fragrantica.com/noses/"	
log_file_path = "C:\\Users\\Tejveer\\Downloads\\MS in CS\\Python\\PerfumeMate\\scrape\\log\\Log.txt"
data = []

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def write_data_to_file(data, file_name):	
	output_path = "C:\\Users\\Tejveer\\Downloads\\MS in CS\\Python\\PerfumeMate\\scrape\\" + file_name
	output_file = open(output_path,"a+")

	for i in data:
		output_file.write(json.dumps(i))
		output_file.write("\r\n")
		
	output_file.close()

def get_url():
	try:
		r = requests.get(adv_url, headers=user_agent)
		response = TextResponse(r.url, body=r.text, encoding='utf-8')

		# Navigate the perfume list
		new_url = response.xpath('//div[@id="main-content"]//a/@href').extract()

		new_url = [x for x in new_url if x is not None]
		new_url = [x for x in new_url if '#app' not in x]
		new_url = [x for x in new_url if 'html' in x]
		new_url = [x for x in new_url if 'news' not in x]	
		new_url = [x for x in new_url if 'privacy-policy' not in x]
		new_url = [x for x in new_url if 'Terms-of-Service' not in x]
		new_url = [x for x in new_url if 'about-us' not in x]
		new_url = [x.replace(url,'') for x in new_url]				
		new_url = [(url + x) for x in new_url]
	except Exception as e:
		log_file = open(log_file_path, "a+")
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))

	return new_url
	
def get_data(new_url):
	try:
		# for u in new_url:
		# try:
		
		n_r = requests.get(new_url, headers=user_agent)
		response = TextResponse(n_r.url, body=n_r.text, encoding='utf-8')
		
		for row in response.xpath('//div[@class="horizontal-perfume-card"]'):
			perfume = {}
			try:
				perfume['name'] = row.xpath('//a/h4/text()').extract()[0]
				perfume['designer'] = row.xpath('//a/p/text()').extract()[0]
				perfume['year'] = row.xpath('//div/div/span/text()').extract()[1]
				perfume['gender'] = row.xpath('//div/div/span/text()').extract()[0]
				perfume['img'] = row.xpath('//div[@class="card-image"]/img//@src').extract()[0]
				perfume['url'] = url + row.xpath('//div[@class="card"]/div[@class="card-section"]/a/@href').extract()[0]
				
				p_r = requests.get(perfume['url'], headers=user_agent)
				response = TextResponse(p_r.url, body=p_r.text, encoding='utf-8')
				
				try:
					name = response.xpath('//div//span[@itemprop="name"]/text()').extract()
					
					perfume['full_name'] = name
					perfume['main_accords'] = response.xpath('//div//span[@style="position: relative; font-weight: bold; z-index: 60;"]/text()').extract()
					perfume['ratingValue'] = response.xpath('//div//span[@itemprop="ratingValue"]/text()').extract_first()
					perfume['bestRating'] = response.xpath('//div//span[@itemprop="bestRating"]/text()').extract_first()
					perfume['ratingCount'] = response.xpath('//div//span[@itemprop="ratingCount"]/text()').extract_first()
					
					try:
						diagram = {}
						diagramresult = response.xpath('//div[@id="diagramresult"]/@title').extract()
						diagramresult = diagramresult[0].split(':')
						for i in range(0, len(diagramresult) - 1,2):
							key, value = diagramresult[i],diagramresult[i+1]
							key = key.replace('cls','')
							diagram[key] = value
							
						perfume['diagramresult'] = diagram
						
					except Exception as e:
						print("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
					
					try:
						notes = {}
						
						for nr in response.xpath('//div[@style="width: 230px; float: left; text-align: center; clear: left;"]/p'):
							sub_cat = []
							sub_note_cat = nr.xpath('b[1]/text()').extract_first()
							if sub_note_cat is None:
								sub_note_cat = "Base Notes"
							for note_span in nr.xpath('span[@class="rtgNote"]'):
								sp = note_span.xpath('img[1]/@alt').extract_first()
								sub_cat.append(sp)
							notes[sub_note_cat] = sub_cat
						perfume['notes'] = notes
					except Exception as e:
						print("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))						
					
					try:
						votes = {}
						Longevity_Votes = {}	
						for vr in response.xpath('//table[@class="voteLS long"]//tr'):		
							key = vr.xpath('td[1]//text()').extract_first()
							value = vr.xpath('td[2]//text()').extract_first()
							if value is not None:
								Longevity_Votes[key] = value	
						votes['longevity'] = Longevity_Votes
						
						Sillage_Votes = {}	
						for vr in response.xpath('//table[@class="voteLS"]//tr'):		
							key = vr.xpath('td[1]//text()').extract_first()
							value = vr.xpath('td[2]//text()').extract_first()
							if value is not None:
								Sillage_Votes[key] = value	
						votes['sillage'] = Sillage_Votes
						
						perfume['votes'] = votes
					except Exception as e:
						print("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
					
					try:
						description = remove_html_tags(str(response.xpath('//div[@id="container"]//div[@itemprop="description"]').extract()))
						perfume['description'] = description.replace('\\n','').replace('\\t','').replace("['","").replace("']","")
					except Exception as e:
						print("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
					
					data.append(perfume)
				except Exception as e:
					log_file = open(log_file_path, "a+")
					exc_type, exc_obj, exc_tb = sys.exc_info()
					fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
			except Exception as e:
				log_file = open(log_file_path, "a+")
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
		# except (RuntimeError, TypeError, NameError, IndexError, AttributeError):
		# 	pass
	except Exception as e:
		log_file = open(log_file_path, "a+")
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
		
	return data

def main():
	try:
		i = 0
		with open("C:\\Users\\Tejveer\\Downloads\\MS in CS\\Python\\PerfumeMate\\scrape\\url_list.txt") as url_file:
			for url in url_file:
				i = i+1				
				url = url.strip()
				if url is not None:
					if url != "":
						try:
							#if i > 3 and i <7:
							print("Getting data for url : ", url)
							_data = get_data(url.strip('"'))
							#print("Data for i : ", _data)
							write_data_to_file(_data, "output.txt")
						except Exception as e:
							print("Error at url : ", i)
							log_file = open(log_file_path, "a+")
							exc_type, exc_obj, exc_tb = sys.exc_info()
							fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
							log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
						
		#url_list = get_url()
		#write_data_to_file(url_list, "url_list.txt")
		# for i in range(len(url_list)):
			# if i < 1:
				# try:					
					# _data = get_data(url_list[i*2:(i+1)*2])
					# write_data_to_file(_data, "output.txt")
				# except Exception as e:
					# log_file = open(log_file_path, "a+")
					# exc_type, exc_obj, exc_tb = sys.exc_info()
					# fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
					# log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))
	except Exception as e:
		log_file = open(log_file_path, "a+")
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		log_file.write("{0} \n{1} {2} \n{3} {4} \n{5} {6}\n\n".format(str(datetime.datetime.today()), 'Exception Type :', str(exc_type).split(' ')[1].replace('>','').strip('\''), 'File Name :', fname, 'Line Number :', exc_tb.tb_lineno))

main()