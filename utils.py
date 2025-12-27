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
        Legacy method kept for compatibility, now redirects to RateManager.
        """
        return RateManager.get_final_rates()

class RateManager:
    CONFIG_FILE = "rate_config.json"
    BASE_API_URL = "https://open.er-api.com/v6/latest/CNY"
    
    @staticmethod
    def get_base_rate():
        """Fetches the official CNY -> THB rate from a stable open API."""
        try:
            resp = requests.get(RateManager.BASE_API_URL, timeout=5)
            data = resp.json()
            # 1 CNY = X THB
            return float(data['rates']['THB'])
        except Exception as e:
            print(f"Base Rate Error: {e}")
            return 4.50 # Fallback

    @staticmethod
    def load_config():
        """Loads the manual offset from local config."""
        if not os.path.exists(RateManager.CONFIG_FILE):
            return {"offset": 0.0}
        try:
            import json
            with open(RateManager.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"offset": 0.0}

    @staticmethod
    def save_offset(real_superrich_price):
        """Calculates and saves the offset based on manual input."""
        base = RateManager.get_base_rate()
        offset = real_superrich_price - base
        
        import json
        with open(RateManager.CONFIG_FILE, 'w') as f:
            json.dump({"offset": offset, "last_calibrated_base": base, "manual_price": real_superrich_price}, f)
        return offset

    @staticmethod
    def get_final_rates():
        """
        Returns the final calculated rates:
        1. Fetch Base Rate (CNY->THB)
        2. Apply Offset
        3. Round to nearest 0.05
        4. Calculate Reverse (THB->CNY) = Buy Rate + 0.20
        """
        base = RateManager.get_base_rate()
        config = RateManager.load_config()
        offset = config.get("offset", 0.0)
        
        raw_buy = base + offset
        
        # Rounding rule: Nearest 0.05 (e.g. 4.48 -> 4.50, 4.42 -> 4.40)
        # Logic: round(x * 20) / 20
        final_buy = round(raw_buy * 20) / 20
        
        # Reverse Rate logic: Buy Rate + 0.20 (e.g. 4.50 + 0.20 = 4.70)
        final_sell = final_buy + 0.20
        
        return {
            "buy": final_buy,  # The "SuperRich" Anchor
            "sell": final_sell, # The Reverse Rate
            "base_ref": base,
            "is_calibrated": True
        }

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
