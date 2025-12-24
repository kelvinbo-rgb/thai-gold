import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import os

class ThaiGoldScraper:
    GTA_URL = "https://www.goldtraders.or.th/"
    # SuperRich 官方 API 接口
    SUPERRICH_API = "https://www.superrichthailand.com/api/v1/rates"
    BOC_URL = "https://www.boc.cn/th/bocinfo/bi3/201309/t20130910_2462434.html"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    @staticmethod
    def get_latest_prices():
        try:
            response = requests.get(ThaiGoldScraper.GTA_URL, headers=ThaiGoldScraper.HEADERS, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            data = {
                "bullion_sell": float(re.sub(r'[^\d.]', '', soup.select_one("#DetailPlace_uc_goldprices1_lblBLSell").text)),
                "bullion_buy": float(re.sub(r'[^\d.]', '', soup.select_one("#DetailPlace_uc_goldprices1_lblBLBuy").text)),
                "ornament_sell": float(re.sub(r'[^\d.]', '', soup.select_one("#DetailPlace_uc_goldprices1_lblOMSell").text)),
                "tax_base": float(re.sub(r'[^\d.]', '', soup.select_one("#DetailPlace_uc_goldprices1_lblOMBuy").text)),
                "update_time": soup.select_one("#DetailPlace_uc_goldprices1_lblAsTime").text
            }
            return data
        except: return None

    @staticmethod
    def get_realtime_rates():
        # --- 方案 1: SuperRich API ---
        try:
            resp = requests.get(ThaiGoldScraper.SUPERRICH_API, headers=ThaiGoldScraper.HEADERS, timeout=5)
            if resp.status_code == 200:
                data = resp.json().get('data', {}).get('all', [])
                for item in data:
                    if item.get('currency') == 'CNY':
                        # 提取 100 面值的汇率
                        for d in item.get('denominations', []):
                            if d.get('denomination') == '100':
                                return {
                                    "buy": float(d.get('buy')), 
                                    "sell": float(d.get('sell')), 
                                    "source": "SuperRich API"
                                }
        except: pass

        # --- 方案 2: 中国银行 (泰国) 网页抓取 ---
        try:
            resp = requests.get(ThaiGoldScraper.BOC_URL, headers=ThaiGoldScraper.HEADERS, timeout=8)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, 'html.parser')
            for row in soup.find_all('tr'):
                cols = row.find_all('td')
                if len(cols) >= 3 and ("人民币" in cols[0].text or "CNY" in cols[0].text):
                    # 抓取中行的汇买价
                    buy = float(cols[1].text.strip())
                    sell = float(cols[3].text.strip())
                    # 中行可能以100为单位，也可能以1为单位
                    rate_buy = buy / 100 if buy > 10 else buy
                    rate_sell = sell / 100 if sell > 10 else sell
                    return {"buy": rate_buy, "sell": rate_sell, "source": "BOC Thailand"}
        except: pass

        # --- 方案 3: 国际 API 保底 ---
        try:
            resp = requests.get("https://api.exchangerate-api.com/v4/latest/CNY", timeout=5)
            rate = resp.json().get('rates', {}).get('THB')
            return {"buy": rate - 0.05, "sell": rate + 0.02, "source": "Market API"}
        except: pass

        return {"buy": 4.50, "sell": 4.55, "source": "Internal Fallback"}

class GoldConverter:
    @staticmethod
    def baht_to_gram(weight_baht, is_ornament=False):
        return weight_baht * (15.16 if is_ornament else 15.244)
