import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# --- 設定檔案儲存路徑 ---
STAFF_FILE = "staff_list.json"
ORDER_FILE = "orders_data.json"

# --- 讀取/儲存資料的函數 ---
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_data

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 初始化資料 ---
initial_staff = ["文鴻", "舒荻", "卓憲", "序立", "述辰", "秉高", "其家", "茵婕", "品妤", "宛霖", "廷恩", "虹彣", "立涵", "喬菲", "智葳", "芸華", "立潔", "薇諠", "馥戎"]
staff = load_data(STAFF_FILE, initial_staff)
orders = load_data(ORDER_FILE, [])

# --- 網頁設定 ---
st.set_page_config(page_title="台大環職部德克士點餐", layout="wide")

# --- 菜單設定 ---
today_day = datetime.now().day
special_items = {
    8: {"品名": "咔滋脆皮炸雞", "價格": 75},
    18: {"品名": "超級脆乳雞腿堡", "價格": 149},
    28: {"品名": "雙層香酥脆雞堡", "價格": 119}
}

daily_menu = [
    ("起司蔬菜牛肉堡", 79), ("檸香雞腿堡", 119), ("椒香雞腿堡", 119), ("黃金Q蝦堡", 139),
    ("咔滋薯霸 (大)", 63), ("黃金薯餅", 38), ("紫金QQ球", 45), ("咔滋洋蔥圈", 49), 
    ("咔滋啃骨雞 (辣味)", 59), ("冰紅茶 (M)", 40), ("無糖綠茶 (M)", 40), 
    ("經典冰奶茶", 45), ("百事可樂 (M)", 38), ("七喜 (M)", 38), 
    ("鮮萃檸檬綠茶", 59), ("現磨美式咖啡 (M)", 48)
]

# --- 側邊欄：人員管理 ---
st.sidebar.title("👥 管理員後台")
with st.sidebar.expander("編輯人員名單"):
    new_person = st.text_input("新增姓名")
    if st.button("確認新增"):
        if new_person and new_person not in staff:
            staff.append(new_person)
            save_data(STAFF_FILE, staff)
            st.rerun()

    del_person = st.selectbox("刪除人員", ["--請選擇--"] + staff)
    if st.button("確認刪除"):
        if del_person != "--請選擇--":
            staff.remove(del_person)
            save_data(STAFF_FILE, staff)
            st.rerun()

if st.sidebar.button("🚨 清空今日所有訂單"):
    save_data(ORDER_FILE, [])
    st.rerun()

# --- 前台介面 ---
st.title("🍔 台大環職部 德克士會員日點餐")
st.write(f"今日日期：{datetime.now().strftime('%Y-%m-%d')} (每月 8, 18, 28 為會員日)")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("📍 我要點餐")
    user = st.selectbox("你是誰？", ["--請選擇--"] + staff)
    
    # 建立選單選項
    menu_options = []
    current_special = special_items.get(today_day)
    if current_special:
        menu_options.append(f"🔥 今日主打：{current_special['品名']} (${current_special['價格']})")
    for item, price in daily_menu:
        menu_options.append(f"{item} (${price})")
    
    selected_meal = st.radio("選擇餐點", menu_options)
    
    if st.button("送出訂單"):
        if user == "--請選擇--":
            st.error("請先選擇你的名字！")
        else:
            orders.append({"姓名": user, "餐點": selected_meal, "時間": datetime.now().strftime("%H:%M")})
            save_data(ORDER_FILE, orders)
            st.success(f"{user} 點餐成功！")
            st.rerun()

with col2:
    st.subheader("📊 訂購統計與湊對狀況")
    if orders:
        df = pd.DataFrame(orders)
        summary = df['餐點'].value_counts().reset_index()
        summary.columns = ['餐點', '數量']
        
        # 核心湊對邏輯
        def check_pairing(row):
            count = row['數量']
            if count % 2 == 0:
                return "✅ 已湊成偶數 (享+10元優惠)"
            else:
                return "⚠️ 還差 1 人湊對 (目前單數)"

        summary['優惠狀態'] = summary.apply(check_pairing, axis=1)
        
        # 美化表格顯示
        st.dataframe(summary, use_container_width=True)
        
        st.subheader("📝 詳細清單")
        st.table(df)
    else:
        st.info("目前還沒有人點餐，快當第一個！")

st.info("💡 湊對教學：如果你的餐點顯示「⚠️ 還差 1 人」，代表你是單數。可以去推坑同事點一樣的，這樣兩人都能享有 +10 元多一件的優惠！")