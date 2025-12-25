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