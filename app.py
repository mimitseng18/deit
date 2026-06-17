import streamlit as st
import pandas as pd
import datetime
import os

# 設定網頁標題與圖示
st.set_page_config(page_title="全能飲食記帳與熱量大師", page_icon="🥗", layout="wide")

# 定義資料儲存的 CSV 檔案名稱
DATA_FILE = "diet_expense_record.csv"

# --- 食物熱量資料庫 ---
FOOD_CALORIE_DB = {
    # 🍳 【早餐類】
    "原味蛋餅": 260, "起司蛋餅": 340, "培根蛋餅": 370, "鮪魚蛋餅": 350,
    "肉排蛋吐司": 450, "火腿蛋三明治": 320, "卡拉雞腿堡": 580,
    "台式蘿蔔糕 (2片)": 310, "燒餅油條": 520, "大冰奶 (早餐店)": 250,
    # 🍱 【午、晚餐類】
    "炸雞腿便當": 950, "炸排骨便當": 880, "爌肉便當": 820, 
    "烤雞胸肉便當": 580, "招牌鯖魚便當": 670, "少油低卡健康餐盒": 480,
    "白飯 (碗/200g)": 280, "紅燒牛肉麵": 630, "牛肉乾麵": 720,
    "滷肉飯 (大)": 650, "高麗菜水餃 (10顆)": 600, "韭菜鍋貼 (10顆)": 750,
    "日式豚骨拉麵": 750, "大麥克漢堡": 550, "麥當勞薯條 (中)": 330,
    "小火鍋 (麻辣鍋)": 950, "小火鍋 (昆布大骨)": 550,
    # 🥛 【點心/下午茶/夜市類】
    "原味優格 (100g)": 65, "無糖優格 (100g)": 55, "希臘優格 (100g)": 95,
    "無糖希臘優格 (100g)": 60, "草莓風味優格 (杯)": 120, "大燕麥片 (40g)": 150,
    "地瓜 (中/150g)": 130, "即食雞胸肉 (100g)": 120, "茶葉蛋 (顆)": 75,
    "台式炸雞排": 650, "珍珠奶茶 (正常糖)": 650, "珍珠奶茶 (微糖)": 450,
    "美式咖啡/黑咖啡": 15, "拿鐵咖啡 (無糖)": 120, "燕麥拿鐵 (無糖)": 180
}

# 初始化或讀取歷史資料
if os.path.exists(DATA_FILE):
    st.session_state.records = pd.read_csv(DATA_FILE)
    # 這裡做了強化：確保日期轉換正確
    st.session_state.records['日期'] = pd.to_datetime(st.session_state.records['日期']).dt.date
else:
    st.session_state.records = pd.DataFrame(columns=["日期", "餐別", "項目名稱", "金額 (元)", "熱量 (kcal)"])

# 暫存自動帶入的數據
if "temp_name" not in st.session_state: st.session_state.temp_name = ""
if "temp_calories" not in st.session_state: st.session_state.temp_calories = 0

def save_data():
    st.session_state.records.to_csv(DATA_FILE, index=False)

# --- 網頁介面設計 ---
st.title("🥗 全功能飲食記帳 x 熱量管理系統")
st.write("結合歷史數據圖表，幫你輕鬆分析每日熱量攝取與消費趨勢！")

left_col, right_col = st.columns([1, 1.3])

# --- 左側欄位：搜尋與新增 ---
with left_col:
    st.markdown("### 🔍 地表最強食物熱量查詢")
    search_query = st.text_input("輸入你想吃的（例如：優格、蛋餅、便當）", placeholder="請輸入食物或飲料關鍵字...")
    
    if search_query:
        results = {k: v for k, v in FOOD_CALORIE_DB.items() if search_query.lower() in k.lower()}
        if results:
            st.info("💡 找到以下對應熱量，點擊「帶入資料」快速填寫：")
            for food, cal in results.items():
                col_food, col_btn = st.columns([3, 1])
                with col_food:
                    st.write(f"• **{food}**：約 `{cal}` kcal")
                with col_btn:
                    if st.button(f"帶入資料", key=f"btn_{food}"):
                        st.session_state.temp_name = food
                        st.session_state.temp_calories = cal
                        st.rerun()
        else:
            st.warning(" 找不到該食物，可以手動輸入名稱與估計熱量喔！")
            
    st.markdown("---")
    
    st.markdown("### ➕ 新增今日飲食紀錄")
    with st.form(key="add_record_form", clear_on_submit=False):
        input_date = st.date_input("日期", datetime.date.today())
        input_meal = st.selectbox("餐別", ["早餐", "午餐", "晚餐", "點心/飲料"])
        
        input_name = st.text_input("項目名稱", value=st.session_state.temp_name, placeholder="例如：起司蛋餅")
        input_price = st.number_input("金額 (新台幣)", min_value=0, step=1, value=0)
        input_calories = st.number_input("估計熱量 (kcal)", min_value=0, step=10, value=st.session_state.temp_calories)
        
        submit_button = st.form_submit_button(label="確認新增紀錄")

    if submit_button:
        if input_name.strip() == "":
            st.error("❌ 請輸入項目名稱！")
        else:
            new_row = pd.DataFrame([{
                "日期": input_date, "餐別": input_meal, "項目名稱": input_name,
                "金額 (元)": input_price, "熱量 (kcal)": input_calories
            }])
            st.session_state.records = pd.concat([st.session_state.records, new_row], ignore_index=True)
            save_data()
            st.success(f"✅ 已成功記錄：{input_name}！")
            
            st.session_state.temp_name = ""
            st.session_state.temp_calories = 0
            st.rerun()

# --- 右側欄位：數據儀表板、歷史分析圖表與歷史紀錄 ---
with right_col:
    today = datetime.date.today()
    today_records = st.session_state.records[st.session_state.records['日期'] == today]

    st.markdown("### 📊 今日數據摘要")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="💰 今日總花費", value=f"$ {today_records['金額 (元)'].sum()} 元")
    with col2:
        total_calories = today_records["熱量 (kcal)"].sum()
        if total_calories > 2200:
            st.metric(label="🔥 今日總熱量", value=f"{total_calories} kcal", delta="今日熱量偏高喔！", delta_color="inverse")
        else:
            st.metric(label="🔥 今日總熱量", value=f"{total_calories} kcal")
    with col3:
        st.metric(label="🍽️ 今日記錄餐數", value=f"{len(today_records)} 次")

    st.markdown("---")

    # 🔥 新功能：每日摘要趨勢分析
    st.markdown("### 📈 歷史每日攝取量與消費分析")
    
    if not st.session_state.records.empty:
        # 將資料依日期分組，計算每日的金額總和、熱量總和
        daily_summary = st.session_state.records.groupby('日期').agg({
            '熱量 (kcal)': 'sum',
            '金額 (元)': 'sum'
        }).sort_index()
        
        # 建立兩個分頁，一個看熱量趨勢，一個看花費趨勢
        tab1, tab2 = st.tabs(["🔥 每日總熱量趨勢", "💰 每日總花費趨勢"])
        
        with tab1:
            st.write("這段時間的每日熱量控制狀況：")
            # 畫出熱量折線圖
            st.line_chart(daily_summary['熱量 (kcal)'])
            
            # 計算平均值給使用者參考
            avg_cal = round(daily_summary['熱量 (kcal)'].mean(), 1)
            st.caption(f"💡 歷史每日平均攝取熱量：**{avg_cal} kcal**")
            
        with tab2:
            st.write("這段時間的每日伙食費支出狀況：")
            # 畫出金額折線圖
            st.line_chart(daily_summary['金額 (元)'])
            
            avg_price = round(daily_summary['金額 (元)'].mean(), 1)
            st.caption(f"💡 歷史每日平均餐費花費：**$ {avg_price} 元**")
            
    else:
        st.info("尚未有歷史數據可供生成圖表分析。")

    st.markdown("---")

    st.markdown("### 📋 所有歷史紀錄")
    if not st.session_state.records.empty:
        df_display = st.session_state.records.sort_values(by="日期", ascending=False).reset_index(drop=True)
        st.dataframe(df_display, use_container_width=True)
        
        if st.button("⚠️ 清空所有歷史紀錄"):
            st.session_state.records = pd.DataFrame(columns=["日期", "餐別", "項目名稱", "金額 (元)", "熱量 (kcal)"])
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.rerun()
    else:
        st.info("目前還沒有任何紀錄，快從左側新增第一筆吧！")