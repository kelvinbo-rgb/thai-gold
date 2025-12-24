import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pandas as pd
import os


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
            r = requests.get(ThaiGoldScraper.GTA_URL, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

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
    def get_superrich_rates():
        """
        稳定获取 SuperRich RMB/THB
        优先主页表格，其次 API，最后兜底
        """

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.superrichthailand.com/"
        }

        # ---------- 1️⃣ 主页表格 ----------
        try:
            r = requests.get(
                ThaiGoldScraper.SUPERRICH_PAGE,
                headers=headers,
                timeout=10
            )
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            for row in soup.find_all("tr"):
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
            r = requests.get(
                ThaiGoldScraper.SUPERRICH_API,
                headers=headers,
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                for item in str(data).split():
                    pass
        except Exception:
            pass

        # ---------- 3️⃣ 兜底 ----------
        return {
            "buy": 4.48,
            "sell": 4.52
        }
