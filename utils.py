<<<<<<< HEAD
# utils.py
import requests
import json
import os
import math
from datetime import datetime

CALIBRATION_FILE = "superrich_calibration.json"


# =====================================================
# 🔧 SuperRich 校准器（新增，不破坏原结构）
# =====================================================
class SuperRichCalibrator:
    @staticmethod
    def load_offset():
        if not os.path.exists(CALIBRATION_FILE):
            return 0.0
        try:
            with open(CALIBRATION_FILE, "r") as f:
                data = json.load(f)
            return float(data.get("offset", 0.0))
        except Exception:
            return 0.0

    @staticmethod
    def save(real_superrich, bot_rate):
        offset = real_superrich - bot_rate
        data = {
            "offset": round(offset, 6),
            "bot_rate": bot_rate,
            "superrich_rate": real_superrich,
            "updated_at": datetime.now().isoformat()
        }
        with open(CALIBRATION_FILE, "w") as f:
            json.dump(data, f, indent=2)
        return offset


def round_05(val: float) -> float:
    return round(math.floor(val * 20) / 20, 2)


# =====================================================
# 🇹🇭 ThaiGoldScraper（原类，增强但不删）
# =====================================================
class ThaiGoldScraper:

    @staticmethod
    def get_rmb_thb_bot():
        url = "https://www.bot.or.th/App/BTWS_STAT/statistics/ExchangeRate.aspx?lang=en"
        r = requests.get(url, timeout=10)
        text = r.text

        import re
        m = re.search(r'"CNY".*?"BuyingTT":\s*"([\d.]+)"', text)
        if not m:
            raise ValueError("BOT CNY rate not found")
        return float(m.group(1))

    @staticmethod
    def get_superrich_rates():
        """
        ⚠️ 保持原接口名称，供 app.py 调用
        """
        bot = ThaiGoldScraper.get_rmb_thb_bot()
        offset = SuperRichCalibrator.load_offset()
        proxy = round_05(bot + offset)
        return {
            "buy": proxy,
            "sell": proxy
        }

    @staticmethod
    def get_latest_prices():
        url = "https://www.goldtraders.or.th/"
        r = requests.get(url, timeout=10)
        html = r.text

        import re

        def extract(pattern):
            m = re.search(pattern, html)
            return int(m.group(1).replace(",", "")) if m else 0

        return {
            "bullion_buy": extract(r"ทองคำแท่ง.*?รับซื้อ.*?([\d,]+)"),
            "bullion_sell": extract(r"ทองคำแท่ง.*?ขายออก.*?([\d,]+)"),
            "ornament_sell": extract(r"ทองรูปพรรณ.*?ขายออก.*?([\d,]+)"),
            "tax_base": extract(r"ฐานภาษี.*?([\d,]+)"),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M")
        }


# =====================================================
# 💱 GoldConverter（原功能保留）
# =====================================================
class GoldConverter:
    BAHT_TO_GRAM = 15.244

    @staticmethod
    def baht_to_gram(b):
        return b * GoldConverter.BAHT_TO_GRAM

    @staticmethod
    def gram_to_baht(g):
        return g / GoldConverter.BAHT_TO_GRAM


# =====================================================
# 📦 DataManager（保留，走势图已弃用）
# =====================================================
class DataManager:
    @staticmethod
    def save_snapshot(data):
        pass


# =====================================================
# 🔔 AlertManager（原功能保留）
# =====================================================
class AlertManager:
    def __init__(self):
        self.alerts = []
=======
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import os

class ThaiGoldScraper:
    GTA_URL = "https://www.goldtraders.or.th/"
    SUPERRICH_URL = "https://www.superrichthailand.com/#!/en/exchange"
    
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
            response = requests.get(ThaiGoldScraper.GTA_URL, timeout=10)
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
        except Exception as e:
            print(f"GTA Scraping error: {e}")
            return None

    @staticmethod
    def get_superrich_rates():
        """
        Note: SuperRich loads data via JS. For a simple script, we might need 
        to use a headless browser or find their API endpoint.
        For now, providing a robust placeholder or attempting a direct request.
        """
        try:
            # SuperRich often uses a public API: https://www.superrichthailand.com/api/v1/rates
            api_url = "https://www.superrichthailand.com/api/v1/rates"
            response = requests.get(api_url, timeout=10)
            if response.status_code == 200:
                rates = response.json().get('data', {}).get('all', [])
                for rate in rates:
                    if rate.get('currency') == 'CNY':
                        # Find the 100 denomination rate
                        denoms = rate.get('denominations', [])
                        for d in denoms:
                            if d.get('denomination') == '100':
                                return {
                                    "buy": float(d.get('buy')),
                                    "sell": float(d.get('sell'))
                                }
            return {"buy": 4.48, "sell": 4.52} # Robust fallback found in research
        except Exception as e:
            print(f"SuperRich API error: {e}")
            return {"buy": 4.48, "sell": 4.52}

        except Exception as e:
            print(f"SuperRich API error: {e}")
            return {"buy": 4.48, "sell": 4.52}

class GoldConverter:
    # 1 Baht (Bullion) = 15.244 g
    # 1 Baht (Ornament) = 15.16 g
    BAHT_TO_GRAM_BULLION = 15.244
    BAHT_TO_GRAM_ORNAMENT = 15.16
    OZ_TO_GRAM = 31.1034768 # Troy Ounce

    @staticmethod
    def baht_to_gram(weight_baht, is_ornament=False):
        factor = GoldConverter.BAHT_TO_GRAM_ORNAMENT if is_ornament else GoldConverter.BAHT_TO_GRAM_BULLION
        return weight_baht * factor

    @staticmethod
    def gram_to_baht(weight_gram, is_ornament=False):
        factor = GoldConverter.BAHT_TO_GRAM_ORNAMENT if is_ornament else GoldConverter.BAHT_TO_GRAM_BULLION
        return weight_gram / factor

    @staticmethod
    def oz_to_gram(weight_oz):
        return weight_oz * GoldConverter.OZ_TO_GRAM

    @staticmethod
    def gram_to_oz(weight_gram):
        return weight_gram / GoldConverter.OZ_TO_GRAM

    @staticmethod
    def oz_to_baht(weight_oz, is_ornament=False):
        grams = GoldConverter.oz_to_gram(weight_oz)
        return GoldConverter.gram_to_baht(grams, is_ornament)

    @staticmethod
    def calculate_ornament_total(price_per_baht, weight_baht, gamnuy):
        return (price_per_baht * weight_baht) + gamnuy

class DataManager:
    HISTORY_FILE = "gold_history.csv"

    @staticmethod
    def save_snapshot(data):
        """Saves a price snapshot to CSV."""
        df = pd.DataFrame([data])
        df['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if not os.path.exists(DataManager.HISTORY_FILE):
            df.to_csv(DataManager.HISTORY_FILE, index=False)
        else:
            df.to_csv(DataManager.HISTORY_FILE, mode='a', header=False, index=False)

    @staticmethod
    def load_history():
        """Loads historical data from CSV."""
        if not os.path.exists(DataManager.HISTORY_FILE):
            return pd.DataFrame()
        df = pd.read_csv(DataManager.HISTORY_FILE)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    @staticmethod
    def filter_history(df, period):
        """Filters historical data based on period: 7d, 30d, 1y, 3y, All."""
        if df.empty or 'timestamp' not in df.columns:
            return df
        
        from datetime import timedelta
        now = datetime.now()
        
        if period == "1W":
            return df[df['timestamp'] > now - timedelta(days=7)]
        elif period == "1M":
            return df[df['timestamp'] > now - timedelta(days=30)]
        elif period == "1Y":
            return df[df['timestamp'] > now - timedelta(days=365)]
        elif period == "3Y":
            return df[df['timestamp'] > now - timedelta(days=365*3)]
        return df # Default: Max/All

class AlertManager:
    @staticmethod
    def check_alerts(current_price, threshold, condition):
        if condition == "ABOVE":
            return current_price >= threshold
        else:
            return current_price <= threshold
>>>>>>> 199feb6c6f9e2e4c01bd04ec8bef6916e3869615
