import streamlit as st
import pandas as pd
from utils import ThaiGoldScraper, GoldConverter
import time
import os

st.set_page_config(page_title="Thailand Gold - 泰国黄金", layout="wide")

LANGS = {
    "CN": {
        "title": "泰国黄金实时报价", "bullion": "金条", "ornament": "金饰/首饰",
        "buy": "买入价", "sell": "卖出价", "converter": "计算器",
        "weight_baht": "重量 (Baht)", "gamnuy": "加工费 (Gamnuy)",
        "total": "总价 (泰铢)", "last_update": "最后更新",
        "exchange_rates": "汇率监控", "rmb_thb": "人民币/泰铢 (RMB/THB)",
        "gold_spot": "国际金价 (Spot)", "thb_usd": "泰铢/美元 (THB/USD)",
        "unit_converter": "单位换算", "baht": "泰铢 (Baht)", "gram": "克 (Gram)", "ounce": "盎司 (Ounce)",
        "main_title": "泰国黄金 (Thai Gold Live)", "investment_calc": "盈亏计算器",
        "buy_date": "买入日期", "buy_price": "买入单价", "buy_amount": "买入数量",
        "current_value": "当前市值", "profit_loss": "盈亏金额", "return_rate": "累计收益率",
        "annual_return": "年化收益率", "calc_settings": "设置", "gold_type": "类型",
        "alerts": "价格预警", "alert_target": "目标金条价", "alert_cond": "条件",
        "alert_above": "高于", "alert_below": "低于", "alert_reached": "🎯 已达标!",
        "alert_monitoring": "⏳ 监控中", "alert_set": "设定", "set_confirm": "设定成功!",
        "sponsor_title": "☕ 赞助作者", "sponsor_desc": "支持持续开发和分享。",
        "sponsor_alipay": "支付宝", "sponsor_promptpay": "泰国收款码", "sponsor_msg": "祝你梦想成真",
        "source": "数据源"
    }
}

# 默认中文
if "lang_choice" not in st.session_state: st.session_state.lang_choice = "CN"
lang_code = st.session_state.lang_choice
t = LANGS[lang_code]

st.markdown(f"""<div style="text-align: center; border-bottom: 2px solid #ffd700; margin-bottom: 20px;">
    <h1 style="color: #d4af37; margin: 0;">🏆 {t['main_title']}</h1>
</div>""", unsafe_allow_html=True)

# --- 缓存设置 ---
@st.cache_data(ttl=60) # 汇率每 60 秒自动更新一次
def fetch_ex_rates():
    return ThaiGoldScraper.get_superrich_rates()

@st.cache_data(ttl=60)
def fetch_gold_data():
    data = ThaiGoldScraper.get_latest_prices()
    return data

ex_rates = fetch_ex_rates()
prices = fetch_gold_data()

# --- 1. 汇率 ---
st.subheader(f"🌍 {t['exchange_rates']}")
rate_col1, rate_col2, rate_col3 = st.columns(3)
with rate_col1:
    st.metric(t['rmb_thb'], f"{ex_rates.get('buy', 0):.2f}")
    st.caption(f"📍 {t['source']}: {ex_rates.get('source', 'Unknown')}")
with rate_col2:
    val = prices['bullion_sell'] if prices else 0
    st.metric(f"{t['bullion']}({t['sell']})", f"{val:,.0f}")
with rate_col3:
    st.metric(t['thb_usd'], "34.50") # USD 保底

st.divider()

# --- 2. 价格 & 计算器 ---
if prices:
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"🏆 {t['bullion']}")
        st.metric(t['sell'], f"{prices['bullion_sell']:,.0f}")
        st.metric(t['buy'], f"{prices['bullion_buy']:,.0f}")
        b_weight = st.number_input(f"{t['weight_baht']}", min_value=0.0, value=1.0, key="b_w")
        st.write(f"👉 **{(b_weight * prices['bullion_sell']):,.2f} THB**")
    with col2:
        st.warning(f"💍 {t['ornament']}")
        st.metric(t['sell'], f"{prices['ornament_sell']:,.0f}")
        st.metric(t['buy'], f"{prices['tax_base']:,.0f}")
        o_weight = st.number_input(f"{t['weight_baht']}", min_value=0.0, value=1.0, key="o_w")
        st.write(f"👉 **{(o_weight * prices['ornament_sell']):,.2f} THB**")
    st.caption(f"🕒 {t['last_update']}: {prices['update_time']}")

# --- 3. 赞助 ---
st.divider()
st.markdown(f"<div style='text-align: center;'><h4>{t['sponsor_title']}</h4></div>", unsafe_allow_html=True)
s1, s2 = st.columns(2)
with s1: st.image("https://via.placeholder.com/200?text=Alipay", caption=t['sponsor_alipay'])
with s2: st.image("https://via.placeholder.com/200?text=PromptPay", caption=t['sponsor_promptpay'])
