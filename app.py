import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
import json
import os

# --- 1. 基本設定與時區 ---
tz = timezone(timedelta(hours=8)) 
STAFF_FILE = "staff_list.json"
ORDER_FILE = "orders_data.json"
CONFIG_FILE = "system_config.json" # 用來紀錄上次重置的日期

st.set_page_config(page_title="台大環職部 德克士訂餐系統", layout="wide")

# --- 2. 資料處理函數 ---
def load_data(file_path, default_data):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return default_data
    return default_data

def save_data(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 初始化資料
initial_staff = ["文鴻", "舒荻", "卓憲", "序立", "述辰", "秉高", "其家", "茵婕", "品妤", "宛霖", "廷恩", "虹彣", "立涵", "喬菲", "智葳", "芸華", "立潔", "薇諠", "馥戎"]
if 'staff' not in st.session_state:
    st.session_state.staff = load_data(STAFF_FILE, initial_staff)
if 'orders' not in st.session_state:
    st.session_state.orders = load_data(ORDER_FILE, [])

# --- 3. 自動換日重置邏輯 ---
now_tpe = datetime.now(tz)
today_str = now_tpe.strftime("%Y-%m-%d")
config = load_data(CONFIG_FILE, {"last_reset_date": today_str})

if config["last_reset_date"] != today_str:
    # 如果日期變了，清空訂單
    st.session_state.orders = []
    save_data(ORDER_FILE, [])
    # 更新重置日期
    config["last_reset_date"] = today_str
    save_data(CONFIG_FILE, config)
    st.toast("🌞 偵測到新的一天，已自動重置訂餐表！")

# --- 4. 菜單資料定義 ---
special_items = {
    8: ("咔滋脆皮炸雞", 75, "咔滋脆皮炸雞.png"),
    18: ("超級酪乳雞腿堡", 149, "超級酪乳雞腿堡.png"),
    28: ("雙層香酥脆雞堡", 119, "雙層香酥脆雞堡.png")
}

regular_menu = [
    ("起司蔬菜牛肉堡", 79, "起司蔬菜牛肉堡.png"),
    ("檸香雞腿堡", 119, "檸香雞腿堡.png"),
    ("椒香雞腿堡", 119, "椒香雞腿堡.png"),
    ("黃金Q蝦堡", 139, "黃金Q蝦堡.png"),
    ("咔滋薯霸(大)", 63, "咔滋薯霸(大).png"),
    ("黃金薯餅", 38, "黃金薯餅.png"),
    ("紫金QQ球", 45, "紫金QQ球.png"),
    ("咔滋洋蔥圈", 49, "咔滋洋蔥圈.png"),
    ("咔滋啃骨雞(辣味)", 59, "咔滋啃骨雞(辣味).png"),
    ("冰紅茶(M)", 40, "冰紅茶(M).png"),
    ("無糖綠茶(M)", 40, "無糖綠茶(M).png"),
    ("經典冰奶茶", 45, "經典冰奶茶.png"),
    ("百事可樂(M)", 38, "百事可樂(M).png"),
    ("七喜(M)", 38, "七喜(M).png"),
    ("鮮萃檸檬綠茶", 59, "鮮萃檸檬綠茶.png"),
    ("現磨美式咖啡(M)", 48, "現磨美式咖啡(M).png")
]

# --- 5. 側邊欄：管理後台 ---
st.sidebar.title("🔐 管理後台")
pwd = st.sidebar.text_input("輸入管理密碼", type="password")

if pwd == "@ntuh121005":
    st.sidebar.success("管理權限已開啟")
    with st.sidebar.expander("👥 人員名單管理"):
        new_name_admin = st.sidebar.text_input("新增人員姓名")
        if st.sidebar.button("確認新增"):
            if new_name_admin and new_name_admin not in st.session_state.staff:
                st.session_state.staff.append(new_name_admin)
                save_data(STAFF_FILE, st.session_state.staff)
                st.rerun()
        
        del_name = st.sidebar.selectbox("刪除人員", ["--選擇人員--"] + st.session_state.staff)
        if st.sidebar.button("確認刪除"):
            if del_name != "--選擇人員--":
                st.session_state.staff.remove(del_name)
                save_data(STAFF_FILE, st.session_state.staff)
                st.rerun()

    if st.sidebar.button("🚨 清空所有點餐數據 (立即強制重置)"):
        st.session_state.orders = []
        save_data(ORDER_FILE, [])
        st.rerun()
elif pwd != "":
    st.sidebar.error("密碼錯誤")

# --- 6. 前台點餐介面 ---
st.title("🍔 台大環職部 | 德克士會員日點餐系統")
st.write(f"📅 今日日期：{now_tpe.strftime('%Y-%m-%d')} | 會員日：每月 8, 18, 28 號")

# --- 6.1 湊對看板 ---
st.subheader("📢 湊對即時看板 (單數品項提醒)")
if st.session_state.orders:
    all_selected = [o['餐點'] for o in st.session_state.orders]
    counts = pd.Series(all_selected).value_counts()
    odd_items = counts[counts % 2 != 0]
    
    if not odd_items.empty:
        cols = st.columns(min(len(odd_items), 5))
        for i, (name, count) in enumerate(odd_items.items()):
            cols[i % 5].warning(f"**{name}**\n目前 {count} 份\n⚠️ 還差 1 人湊對")
    else:
        st.success("✅ 目前所有品項皆已成雙，大家都能享受 +10 元優惠！")
else:
    st.info("目前還沒有人點餐。")

st.divider()

# --- 6.2 點餐與取消操作 ---
col_user, col_cancel = st.columns([2, 1])

with col_user:
    st.subheader("👤 第一步：誰要點餐？")
    user_options = ["--請選擇--", "➕ 新增姓名 (不在名單中)"] + sorted(st.session_state.staff)
    selected_user_type = st.selectbox("請選擇或新增您的姓名", user_options)
    
    final_user_name = ""
    if selected_user_type == "➕ 新增姓名 (不在名單中)":
        new_guest_name = st.text_input("請輸入您的姓名：")
        final_user_name = new_guest_name
    elif selected_user_type != "--請選擇--":
        final_user_name = selected_user_type

with col_cancel:
    # 這裡放取消功能
    st.subheader("⚠️ 點錯了？")
    if final_user_name and final_user_name != "➕ 新增姓名 (不在名單中)":
        my_orders = [idx for idx, o in enumerate(st.session_state.orders) if o['姓名'] == final_user_name]
        if my_orders:
            if st.button(f"撤回 {final_user_name} 的最後一筆訂單"):
                st.session_state.orders.pop(my_orders[-1])
                save_data(ORDER_FILE, st.session_state.orders)
                st.warning("已成功撤回訂單")
                st.rerun()
        else:
            st.caption("您目前沒有點餐記錄")
    else:
        st.caption("請先選擇姓名以使用撤回功能")

st.subheader("🍕 第二步：選擇餐點 (點擊下方按鈕即可送出)")

# 組合今日選單
today_special = special_items.get(now_tpe.day)
final_menu = []
if today_special:
    final_menu.append(("⭐今日限定主打", today_special[0], today_special[1], today_special[2]))

for item in regular_menu:
    final_menu.append(("常規品項", item[0], item[1], item[2]))

# 以網格方式顯示 (每行4個)
cols = st.columns(4)
for idx, (tag, name, price, img_file) in enumerate(final_menu):
    with cols[idx % 4]:
        if tag == "⭐今日限定主打":
            st.error(tag)
        else:
            st.caption(tag)
            
        img_path = os.path.join("img", img_file)
        if os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.warning(f"缺少圖片: {img_file}")
            
        st.write(f"**{name}**")
        st.write(f"原價: ${price}")
        
        if st.button(f"點選這項", key=f"btn_{idx}"):
            if final_user_name == "" or selected_user_type == "--請選擇--":
                st.error("❌ 請先在上方提供您的姓名！")
            else:
                if final_user_name not in st.session_state.staff:
                    st.session_state.staff.append(final_user_name)
                    save_data(STAFF_FILE, st.session_state.staff)
                
                new_entry = {
                    "姓名": final_user_name,
                    "餐點": name,
                    "時間": datetime.now(tz).strftime("%H:%M:%S")
                }
                st.session_state.orders.append(new_entry)
                save_data(ORDER_FILE, st.session_state.orders)
                st.balloons()
                st.rerun()

# --- 7. 後台統計清單 ---
st.divider()
st.subheader("📋 目前點餐明單 (供統計者核對)")
if st.session_state.orders:
    df_display = pd.DataFrame(st.session_state.orders)
    st.dataframe(df_display, use_container_width=True)
    
    st.write("📊 **品項總計：**")
    summary_df = df_display['餐點'].value_counts().reset_index()
    summary_df.columns = ['餐點', '總份數']
    st.table(summary_df)
else:
    st.write("目前尚無點餐資料")