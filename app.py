import streamlit as st
from utils import ThaiGoldScraper

st.set_page_config(page_title="Gold Monitor")

# 获取数据
prices = ThaiGoldScraper.get_latest_prices()
rates = ThaiGoldScraper.get_realtime_rates()

st.title("🏆 泰国金价与汇率")

if rates:
    st.subheader(f"汇率: {rates['buy']} (源: {rates['source']})")
else:
    st.error("汇率获取失败")

if prices:
    st.write(f"金条卖出价: {prices['bullion_sell']}")
    st.write(f"更新时间: {prices['update_time']}")
else:
    st.error("金价获取失败")

if st.button("手动刷新数据"):
    st.cache_data.clear()
    st.rerun()
