import streamlit as st
from utils import ThaiGoldScraper
import os

st.set_page_config(page_title="Thai Gold Live", layout="wide", initial_sidebar_state="collapsed")

# 缓存 2 分钟，确保数据足够新鲜
@st.cache_data(ttl=120)
def get_all_data():
    prices = ThaiGoldScraper.get_latest_prices()
    rates = ThaiGoldScraper.get_realtime_rates()
    return prices, rates

prices, rates = get_all_data()

# 页面标题
st.markdown("<h1 style='text-align: center; color: #D4AF37;'>🏆 泰国黄金 & 汇率实时监控</h1>", unsafe_allow_html=True)

# 第一部分：汇率监控
st.subheader("🌍 汇率监控 (CNY/THB)")
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("人民币买入价 (1元兑泰铢)", f"{rates['buy']:.3f}")
    st.caption(f"数据来源: {rates['source']}")
with col_b:
    st.metric("参考卖出价", f"{rates['sell']:.3f}")
with col_c:
    # 简单的倒数计算，方便看 1泰铢兑多少人民币
    thb_to_cny = 1 / rates['buy'] if rates['buy'] > 0 else 0
    st.metric("1泰铢折合人民币", f"{thb_to_cny:.3f}")

st.divider()

# 第二部分：金价展示
if prices:
    st.subheader("📊 今日金价 (Gold Traders Association)")
    c1, c2 = st.columns(2)
    with c1:
        st.info("🏆 金条 (Bullion)")
        st.metric("卖出 (Sell)", f"{prices['bullion_sell']:,.0f} THB")
        st.metric("买入 (Buy)", f"{prices['bullion_buy']:,.0f} THB")
    with c2:
        st.warning("💍 金饰 (Ornament)")
        st.metric("卖出 (Sell)", f"{prices['ornament_sell']:,.0f} THB")
        st.metric("买入参考", f"{prices['tax_base']:,.0f} THB")
    
    st.caption(f"🕒 最后更新时间: {prices['update_time']}")

    # 第三部分：计算器
    st.divider()
    st.subheader("🧮 购金成本快速计算")
    w_col, f_col = st.columns(2)
    with w_col:
        weight = st.number_input("黄金重量 (Baht/铢)", min_value=0.0, value=1.0, step=0.5)
    with f_col:
        fee = st.number_input("加工费 (Gamnuy/泰铢)", min_value=0, value=500, step=100)
    
    total_thb = (weight * prices['bullion_sell']) + fee
    total_cny = total_thb / rates['buy']
    
    res1, res2 = st.columns(2)
    res1.success(f"**预计支出 (泰铢):** {total_thb:,.2f} THB")
    res2.success(f"**约合 (人民币):** {total_cny:,.2f} CNY")

else:
    st.error("无法获取金价数据，请稍后刷新。")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Data source: SuperRich Thailand & GTA Thailand</div>", unsafe_allow_html=True)
