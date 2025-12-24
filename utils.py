import requests
from bs4 import BeautifulSoup
import re

class ThaiGoldScraper:
    BOC_URL = "https://www.boc.cn/th/bocinfo/bi3/201309/t20130910_2462434.html"
    SR_API = "https://www.superrichthailand.com/api/v1/rates"
    GTA_URL = "https://www.goldtraders.or.th/"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    @staticmethod
    def get_latest_prices():
        try:
            resp = requests.get(ThaiGoldScraper.GTA_URL, headers=ThaiGoldScraper.HEADERS, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return {
                "sell": soup.select_one("#DetailPlace_uc_goldprices1_lblBLSell").text,
                "buy": soup.select_one("#DetailPlace_uc_goldprices1_lblBLBuy").text,
                "time": soup.select_one("#DetailPlace_uc_goldprices1_lblAsTime").text
            }
        except:
            return {"sell": "0", "buy": "0", "time": "获取失败"}

    @staticmethod
    def get_realtime_rates():
        # 1. 优先尝试 SuperRich API
        try:
            r = requests.get(ThaiGoldScraper.SR_API, timeout=5)
            if r.status_code == 200:
                data = r.json().get('data', {}).get('all', [])
                for item in data:
                    if item.get('currency') == 'CNY':
                        # 取 100 面值的汇买价
                        rate = float(item['denominations'][0]['buy'])
                        return {"rate": rate, "source": "SuperRich"}
        except: pass

        # 2. 备选尝试 中国银行 (泰国)
        try:
            r = requests.get(ThaiGoldScraper.BOC_URL, headers=ThaiGoldScraper.HEADERS, timeout=5)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            for row in soup.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) > 2 and ("CNY" in cells[0].text or "人民币" in cells[0].text):
                    # 抓取表格中的汇买价
                    val = float(cells[1].text.strip())
                    rate = val / 100 if val > 10 else val
                    return {"rate": rate, "source": "BOC Thailand"}
        except: pass

        # 3. 终极保底
        return {"rate": 4.46, "source": "保底数据"}
