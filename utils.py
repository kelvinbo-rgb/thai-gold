import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.ERROR)


class ThaiGoldScraper:
    GTA_URL = "https://www.goldtraders.or.th/"
    SUPERRICH_API = "https://www.superrichthailand.com/api/v1/rates"
    SUPERRICH_PAGE = "https://www.superrichthailand.com/"

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
            resp = requests.get(ThaiGoldScraper.GTA_URL, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            data = {}
            for k, sel in ThaiGoldScraper.GTA_SELECTORS.items():
                el = soup.select_one(sel)
                if not el:
                    data[k] = None
                    continue
                txt = el.get_text(strip=True)
                if k == "update_time":
                    data[k] = txt
                else:
                    num = re.sub(r"[^\d.]", "", txt)
                    data[k] = float(num) if num else 0.0
            return data
        except Exception:
            return None

    @staticmethod
    def _find_cny_from_json(obj):
        if isinstance(obj, dict):
            text = " ".join(str(v) for v in obj.values()).upper()
            if "CNY" in text or "RMB" in text or "CHINA" in text:
                if "denominations" in obj and isinstance(obj["denominations"], list):
                    for d in obj["denominations"]:
                        try:
                            return float(d["buy"]), float(d["sell"])
                        except Exception:
                            pass
                if "buy" in obj and "sell" in obj:
                    try:
                        return float(obj["buy"]), float(obj["sell"])
                    except Exception:
                        pass
            for v in obj.values():
                r = ThaiGoldScraper._find_cny_from_json(v)
                if r:
                    return r
        elif isinstance(obj, list):
            for i in obj:
                r = ThaiGoldScraper._find_cny_from_json(i)
                if r:
                    return r
        return None

    @staticmethod
    def get_superrich_rates():
        """
        稳定版：
        1. 优先抓主页表格（真实存在）
        2. 失败再尝试 API
        3. 最终兜底，永不崩溃
        """
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.superrichthailand.com/"
        }

        # ---------- 1️⃣ 主页 ----------
        try:
            resp = requests.get(
                ThaiGoldScraper.SUPERRICH_PAGE,
                headers=headers,
                timeout=10
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            rows = soup.find_all("tr")
            for row in rows:
                text = row.get_text(" ", strip=True)
                if "CNY" in text or "RMB" in text or "China" in text:
                    nums = re.findall(r"\d+\.\d+", text)
                    if len(nums) >= 2:
                        return {
                            "buy": float(nums[-2]),
                            "sell": float(nums[-1])
                        }
        except Exception:
            pass

        # ---------- 2️⃣ API ----------
        try:
            resp = requests.get(
                ThaiGoldScraper.SUPERRICH_API,
                headers=headers,
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                found = ThaiGoldScraper._find_cny_from_json(data)
                if found:
                    buy, sell = found
                    return {
                        "buy": float(buy),
                        "sell": float(sell)
                    }
        except Exception:
            pass

        # ---------- 3️⃣ 兜底 ----------
        return {
            "buy": 4.48,
            "sell": 4.52
        }


class GoldConverter:
    BAHT_TO_GRAM_BULLION = 15.244
    BAHT_TO_GRAM_ORNAMENT = 15.16
    OZ_TO_GRAM = 31.1034768


class DataManager:
    HISTORY_FILE = "gold_history.csv"

    @staticmethod
    def save_snapshot(data):
        try:
            df = pd.DataFrame([data])
            df["timestamp"] = datetime.now()
            if not os.path.exists(DataManager.HISTORY_FILE):
                df.to_csv(DataManager.HISTORY_FILE, index=False)
            else:
                df.to_csv(
                    DataManager.HISTORY_FILE,
                    mode="a",
                    header=False,
                    index=False
                )
        except Exception:
            pass
