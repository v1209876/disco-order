import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import json
import os

# --- 設定時區為 UTC+8 (台北) ---
tz = timezone(timedelta(hours=8))

# --- 檔案路徑 ---
STAFF_FILE = "staff_list.json"
ORDER_FILE = "orders_data.json"

# --- 讀取/儲存資料函數 ---
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_data
    return default_data

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- 初始化資料 ---
# 預設名單
initial_staff = ["文鴻", "舒荻", "卓憲", "序立", "述辰", "秉高", "其家", "茵婕", "品妤", "宛霖", "廷恩", "虹彣", "立涵", "喬菲", "智葳", "芸華", "立潔", "薇諠", "馥戎"]

# 從檔案讀取，若無則用預設
if 'staff' not in st.session_state:
    st.session_state.staff = load_data(STAFF_FILE, initial_staff)
if 'orders' not in st.session_state:
    st.session_state.orders = load_data(ORDER_FILE, [])

# --- 網頁設定 ---
st.set_page_config(page_title="台大環職部 德克士訂餐系統", layout="wide")

# --- 菜單設定 ---
now_taipei = datetime.now(tz)
today_day = now_taipei.day

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

# --- 側邊欄：管理員後台 (需密碼) ---
st.sidebar.title("🔐 管理員後台")
admin_password = st.sidebar.text_input("輸入管理密碼", type="password")

if admin_password == "@ntuh121005":
    st.sidebar.success("密碼正確，已開啟管理權限")
    
    # 人員管理
    with st.sidebar.expander("👥 編輯人員名單"):
        new_person = st.sidebar.text_input("新增姓名")
        if st.sidebar.button("確認新增"):
            if new_person and new_person not in st.session_state.staff:
                st.session_state.staff.append(new_person)
                save_data(STAFF_FILE, st.session_state.staff)
                st.rerun()

        del_person = st.sidebar.selectbox("刪除人員", ["--請選擇--"] + st.session_state.staff)
        if st.sidebar.button("確認刪除"):
            if del_person != "--請選擇--":
                st.session_state.staff.remove(del_person)
                save_data(STAFF_FILE, st.session_state.staff)
                st.rerun()
    
    # 清空訂單
    if st.sidebar.button("🚨 清空今日所有訂單"):
        st.session_state.orders = []
        save_data(ORDER_FILE, [])
        st.rerun()
else:
    if admin_password != "":
        st.sidebar.error("密碼錯誤，請重新輸入")

# --- 前台介面 ---
st.title("🍔 台大環職部 德克士會員日點餐")
st.write(f"目前時間：{now_taipei.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")

col1, col2 = st.columns([1, 1.3])

with col1:
    st.subheader("📍 我要點餐")
    # 下拉選單顯示人員
    user = st.selectbox("你是誰？", ["--請選擇--"] + sorted(st.session_state.staff))
    
    # 建立選單選項
    menu_options = []
    current_special = special_items.get(today_day)
    if current_special:
        menu_options.append(f"🔥 今日主打：{current_special['品名']} (${current_special['價格']})")
        st.warning(f"今天是 {today_day} 號！主打商品是「{current_special['品名']}」，記得找人湊對喔！")
    
    for item, price in daily_menu:
        menu_options.append(f"{item} (${price})")
    
    selected_meal = st.radio("選擇餐點 (每人限點一項，如需多項請重複送出)", menu_options)
    
    if st.button("送出訂單"):
        if user == "--請選擇--":
            st.error("❌ 請先選擇你的名字！")
        else:
            new_order = {
                "姓名": user, 
                "餐點": selected_meal, 
                "點餐時間": datetime.now(tz).strftime("%H:%M:%S")
            }
            st.session_state.orders.append(new_order)
            save_data(ORDER_FILE, st.session_state.orders)
            st.success(f"✅ {user} 點餐成功！")
            st.rerun()

with col2:
    st.subheader("📊 訂購統計與湊對狀況")
    if st.session_state.orders:
        df = pd.DataFrame(st.session_state.orders)
        
        # 統計各餐點數量
        summary = df['餐點'].value_counts().reset_index()
        summary.columns = ['餐點', '目前份數']
        
        # 核心湊對邏輯
        def check_pairing(row):
            count = row['目前份數']
            if count % 2 == 0:
                return "✅ 已湊成對 (享+10元優惠)"
            else:
                return "⚠️ 尚缺 1 人湊對 (目前單數)"

        summary['優惠狀態'] = summary.apply(check_pairing, axis=1)
        
        # 顯示統計表
        st.dataframe(summary, use_container_width=True, hide_index=True)
        
        # 顯示詳細名單
        with st.expander("🔍 查看詳細點餐清單"):
            st.table(df)
            
        # 計算總金額 (初步估算，不含+10元邏輯，僅供參考)
        st.write("---")
        st.caption("提示：系統會自動標註單數品項，方便大家互相湊對節省餐費。")
    else:
        st.info("💡 目前還沒有人點餐，趕快推坑同事！")

st.markdown("---")
st.markdown("### 💡 德克士會員日規則提醒")
st.write("1. 每月 **8、18、28** 號為會員日。")
st.write("2. 只要點購指定品項，**加 10 元就多一件** (即兩份)。")
st.write("3. 為了讓大家都能省錢，若看到統計表顯示 **⚠️ 尚缺 1 人**，請盡量選擇該品項湊成偶數。")