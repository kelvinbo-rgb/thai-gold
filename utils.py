import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import os

class ThaiGoldScraper:
    GTA_URL = "https://www.goldtraders.or.th/"
    BOC_URL = "https://www.boc.cn/th/bocinfo/bi3/201309/t20130910_2462434.html"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    GTA_SELECTORS = {
        "bullion_sell": "#DetailPlace_uc_goldprices1_lblBLSell",
        "bullion_buy": "#DetailPlace_uc_goldprices1_lblBLBuy",
        "ornament_sell": "#DetailPlace_uc_goldprices1_lblOMSell",
        "tax_base": "#DetailPlace_uc_goldprices1_lblOMBuy",
        "update_time": "#DetailPlace_uc_goldprices1_lblAsTime"
    }

    @staticmethod
    def get_latest_prices():
        try:
            response = requests.get(ThaiGoldScraper.GTA_URL, headers=ThaiGoldScraper.HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            data = {}
            for key, selector in ThaiGoldScraper.GTA_SELECTORS.items():
                element = soup.select_one(selector)
                if element:
                    text_val = element.get_text().strip()
                    if key != 'update_time':
                        num_str = re.sub(r'[^\d.]', '', text_val)
                        data[key] = float(num_str) if num_str else 0.0
                    else:
                        data[key] = text_val
                else:
                    data[key] = None
            return data
        except Exception:
            return None

    @staticmethod
    def get_superrich_rates():
        """尝试 SuperRich -> 尝试中国银行(泰国) -> 尝试国际API"""
        # 1. 尝试 SuperRich
        try:
            api_url = "https://www.superrichthailand.com/api/v1/rates"
            response = requests.get(api_url, headers=ThaiGoldScraper.HEADERS, timeout=5)
            if response.status_code == 200:
                rates = response.json().get('data', {}).get('all', [])
                for rate in rates:
                    if rate.get('currency') == 'CNY':
                        for d in rate.get('denominations', []):
                            if d.get('denomination') == '100':
                                return {"buy": float(d.get('buy')), "sell": float(d.get('sell')), "source": "SuperRich"}
        except: pass

        # 2. 尝试 中国银行 (泰国) - 抓取网页表格
        try:
            print("Fetching BOC Thailand...")
            response = requests.get(ThaiGoldScraper.BOC_URL, headers=ThaiGoldScraper.HEADERS, timeout=10)
            response.encoding = 'utf-8' # 确保中文不乱码
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 中行的表格通常在 class 为 'wrapper' 内部的 table
                rows = soup.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        text = cols[0].get_text(strip=True)
                        # 匹配 '人民币' 或 'CNY'
                        if "人民币" in text or "CNY" in text:
                            # 中行表格顺序通常是: 货币, 现汇买入价, 现钞买入价, 卖出价...
                            # 泰国的页面习惯显示 Buying Rate (汇买价)
                            # 我们取第二列或第三列
                            buy_rate = cols[1].get_text(strip=True)
                            sell_rate = cols[3].get_text(strip=True)
                            return {
                                "buy": float(buy_rate) / 100 if float(buy_rate) > 10 else float(buy_rate), 
                                "sell": float(sell_rate) / 100 if float(sell_rate) > 10 else float(sell_rate),
                                "source": "BOC Thailand"
                            }
        except Exception as e:
            print(f"BOC Error: {e}")

        # 3. 终极备用：国际公开 API
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/CNY", timeout=5)
            if response.status_code == 200:
                rate = response.json().get('rates', {}).get('THB')
                return {"buy": rate * 0.98, "sell": rate * 1.02, "source": "Market API"}
        except: pass

        return {"buy": 4.50, "sell": 4.60, "source": "Hardcoded"}

class GoldConverter:
    BAHT_TO_GRAM_BULLION = 15.244
    BAHT_TO_GRAM_ORNAMENT = 15.16
    OZ_TO_GRAM = 31.1034768
    @staticmethod
    def baht_to_gram(weight_baht, is_ornament=False):
        return weight_baht * (GoldConverter.BAHT_TO_GRAM_ORNAMENT if is_ornament else GoldConverter.BAHT_TO_GRAM_BULLION)
    @staticmethod
    def gram_to_baht(weight_gram, is_ornament=False):
        return weight_gram / (GoldConverter.BAHT_TO_GRAM_ORNAMENT if is_ornament else GoldConverter.BAHT_TO_GRAM_BULLION)
    @staticmethod
    def oz_to_gram(weight_oz): return weight_oz * GoldConverter.OZ_TO_GRAM
    @staticmethod
    def gram_to_oz(weight_gram): return weight_gram / GoldConverter.OZ_TO_GRAM

class DataManager:
    HISTORY_FILE = "gold_history.csv"
    @staticmethod
    def save_snapshot(data):
        df = pd.DataFrame([data])
        df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not os.path.exists(DataManager.HISTORY_FILE):
            df.to_csv(DataManager.HISTORY_FILE, index=False)
        else:
            df.to_csv(DataManager.HISTORY_FILE, mode='a', header=False, index=False)
    @staticmethod
    def load_history():
        if not os.path.exists(DataManager.HISTORY_FILE): return pd.DataFrame()
        df = pd.read_csv(DataManager.HISTORY_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    @staticmethod
    def filter_history(df, period):
        if df.empty or 'timestamp' not in df.columns: return df
        from datetime import timedelta
        now = datetime.now()
        if period == "1W": return df[df['timestamp'] > now - timedelta(days=7)]
        elif period == "1M": return df[df['timestamp'] > now - timedelta(days=30)]
        elif period == "1Y": return df[df['timestamp'] > now - timedelta(days=365)]
        return df

class AlertManager:
    @staticmethod
    def check_alerts(current, threshold, condition):
        return current >= threshold if condition == "ABOVE" else current <= threshold
        
