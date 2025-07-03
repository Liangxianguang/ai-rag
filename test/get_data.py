import re
import requests
from bs4 import BeautifulSoup
import json
URL = r'http://www.npc.gov.cn/npc/c2/c30834/201905/t20190521_296651.html'
response = requests.get(URL)
response.encoding = 'utf-8'
html = BeautifulSoup(response.text, 'html.parser')
list = html.find_all('p')
datas = []
for item in list:
  datas.append(item.get_text().strip())
data_str = '\n'.join(datas)
pattern = re.compile(r'第([一二三四五六七八九十零百]+)条.*?(?=\n第|$)', re.DOTALL)
dicts = {}
for item in pattern.finditer(data_str):
  key = f'第{item.group(1)}条'
  content = item.group(0).replace(key, '').strip()
  dicts[f'中华人民共和国劳动法 {key}'] = content
json_str = json.dumps(dicts, ensure_ascii=False, indent=4)
with open(r'D:\llama index\test\data\劳动法.json', 'w', encoding='utf-8') as f:
  f.write(json_str)

