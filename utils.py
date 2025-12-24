import requests
from bs4 import BeautifulSoup
import re

class ThaiGoldScraper:
    @staticmethod
    def get_latest_prices():
        try:
            url = "https://www.goldtraders.or.th/"
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            return {
                "bullion_sell": soup.select_one("#DetailPlace_uc_goldprices1_lblBLSell").text,
                "bullion_buy": soup.select_one("#DetailPlace_uc_goldprices1_lblBLBuy").text,
                "update_time": soup.select_one("#DetailPlace_uc_goldprices1_lblAsTime").text
            }
        except: return None

    @staticmethod
    def get_realtime_rates():
        # 优先 SuperRich API
        try:
            api_url = "https://www.superrichthailand.com/api/v1/rates"
            resp = requests.get(api_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json().get('data', {}).get('all', [])
                for item in data:
                    if item.get('currency') == 'CNY':
                        for d in item.get('denominations', []):
                            if d.get('denomination') == '100':
                                return {"buy": float(d.get('buy')), "source": "SuperRich API"}
        except: pass
        
        # 保底 API (确保网页不坏)
        try:
            resp = requests.get("https://api.exchangerate-api.com/v4/latest/CNY", timeout=5)
            rate = resp.json().get('rates', {}).get('THB')
            return {"buy": rate - 0.08, "source": "Market API"}
        except:
            return {"buy": 4.45, "source": "Fixed Fallback"}
