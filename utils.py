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
