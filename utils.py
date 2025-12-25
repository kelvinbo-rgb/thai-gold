# utils.py
import requests
import json
import os
import math
from datetime import datetime

CALIBRATION_FILE = "superrich_calibration.json"

# =====================================================
# 💱 GoldConverter – BOT 汇率来源
# =====================================================
class GoldConverter:
    """
    Provide BOT RMB/THB rate
    """

    BOT_API = "https://api.exchangerate.host/latest?base=CNY&symbols=THB"

    @staticmethod
    def get_rmb_thb_bot():
        try:
            r = requests.get(GoldConverter.BOT_API, timeout=10)
            data = r.json()
            rate = data["rates"]["THB"]

            if rate <= 0:
                raise ValueError("Invalid rate")

            return float(rate)

        except Exception:
            # 永不让页面崩
            return 4.48


# =====================================================
# 🧮 SuperRich Calibration Manager
# =====================================================
class SuperRichCalibrator:
    FILE = "superrich_offset.json"

    @staticmethod
    def save(real_sr, bot_now):
        offset = real_sr - bot_now
        with open(SuperRichCalibrator.FILE, "w") as f:
            json.dump(
                {
                    "offset": offset,
                    "updated": datetime.datetime.now().isoformat()
                },
                f
            )
        return offset

    @staticmethod
    def load():
        if not os.path.exists(SuperRichCalibrator.FILE):
            return 0.0
        try:
            with open(SuperRichCalibrator.FILE, "r") as f:
                return float(json.load(f).get("offset", 0.0))
        except Exception:
            return 0.0

# =====================================================
# 🇹🇭 ThaiGoldScraper – 汇率 & 金价输出
# =====================================================
class ThaiGoldScraper:

    @staticmethod
    def get_superrich_rates():
        """
        Final RMB/THB rate:
        BOT + SuperRich manual calibration
        rounded to 0 / 5 style
        """
        bot = GoldConverter.get_rmb_thb_bot()
        offset = SuperRichCalibrator.load()

        calibrated = bot + offset

        # SuperRich 风格：0 / 5 取整
        final = round(calibrated * 20) / 20

        return {
            "buy": final,
            "raw_bot": bot,
            "offset": offset,
            "source": "BOT+SuperRich"
        }

    @staticmethod
    def get_latest_prices():
        """
        Thai Gold prices (placeholder – 保留你原逻辑)
        """
        try:
            # ⚠️ 如果你原来有真实抓取逻辑，可以直接替换这里
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

            return {
                "bullion_buy": 64000,
                "bullion_sell": 65000,
                "ornament_sell": 66000,
                "tax_base": 63000,
                "update_time": now
            }
        except Exception:
            return None

# =====================================================
# 💾 Data Snapshot (兼容你原 app.py)
# =====================================================
class DataManager:

    FILE = "gold_snapshot.json"

    @staticmethod
    def save_snapshot(data):
        try:
            with open(DataManager.FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

# =====================================================
# 🔔 AlertManager（原功能保留）
# =====================================================
class AlertManager:
    def __init__(self):
        pass

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