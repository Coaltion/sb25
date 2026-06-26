import streamlit as st
import pandas as pd
from datetime import datetime

# 页面设置
st.set_page_config(page_title="🏆 比赛记录查询", page_icon="🏆", layout="centered")

# 初始化数据
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["ID", "Password", "Name", "Mode", "Result", "Detail", "XP", "Date"])

# ========== 管理员模式 ==========
def admin_mode():
    st.subheader("🔐 管理员：选择参赛者并添加记录")
    
    if st.session_state.data.empty:
        st.warning("⚠️ 暂无参赛者，请先添加")
        # 快速添加参赛者
        with st.form("quick_add_player"):
            st.caption("添加新参赛者")
            col1, col2, col3 = st.columns(3)
            with col1:
                new_id = st.text_input("编号 (ID)")
            with col2:
                new_password = st.text_input("密码 (Password)")
            with col3:
                new_name = st.text_input("姓名 (Name)")
            if st.form_submit_button("➕ 添加参赛者"):
                if new_id and new_password and new_name:
                    new_row = pd.DataFrame([{
                        "ID": new_id.strip(),
                        "Password": new_password.strip(),
                        "Name": new_name.strip(),
                        "Mode": "",
                        "Result": "",
                        "Detail": "",
                        "XP": "",
                        "Date": ""
                    }])
                    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                    st.success(f"✅ 参赛者 {new_name} 已添加")
                    st.rerun()
                else:
                    st.error("请填写完整信息")
        return
    
    # 获取所有参赛者列表
    players = st.session_state.data.drop_duplicates(subset=["ID", "Name"])
    player_options = {f"{row['ID']} - {row['Name']}": row['ID'] for _, row in players.iterrows()}
    
    # 选择参赛者
    selected_label = st.selectbox("选择参赛者", list(player_options.keys()))
    selected_id = player_options[selected_label]
    
    # 获取该参赛者的所有记录
    player_data = st.session_state.data[st.session_state.data["ID"] == selected_id]
    player_name = player_data.iloc[0]["Name"] if not player_data.empty else ""
    
    # 显示该参赛者的记录
    st.subheader(f"📊 {player_name} 的比赛记录")
    
    if not player_data.empty:
        # 过滤掉空记录（只有编号没有比赛信息的）
        valid_records = player_data[player_data["Mode"] != ""]
        if not valid_records.empty:
            # 按日期排序（最新的在前）
            sorted_records = valid_records.sort_values("Date", ascending=False)
            # 限制最多显示6条
            display_records = sorted_records.head(6)
            
            for _, row in display_records.iterrows():
                with st.container(border=True):
                    col_a, col_b = st.columns([2, 1])
                    with col_a:
                        st.markdown(f"**{row['Mode']}**")
                        if row['Detail']:
                            st.caption(row['Detail'])
                    with col_b:
                        result_text = row['Result']
                        if "VICTORY" in result_text.upper() or "WIN" in result_text.upper():
                            st.markdown(f"🟢 **{result_text}**")
                        elif "DEFEAT" in result_text.upper() or "LOSE" in result_text.upper():
                            st.markdown(f"🔴 **{result_text}**")
                        elif "CLEAR" in result_text.upper():
                            st.markdown(f"🟡 **{result_text}**")
                        else:
                            st.markdown(f"⚪ **{result_text}**")
                        if row['XP']:
                            st.text(row['XP'])
                        if row['Date']:
                            st.caption(f"📅 {row['Date']}")
            
            # 检查记录数量
            if len(valid_records) > 6:
                st.warning(f"⚠️ 该参赛者有 {len(valid_records)} 条记录，仅显示最新6条")
        else:
            st.info("该参赛者暂无比赛记录")
    else:
        st.info("该参赛者暂无比赛记录")
    
    # ========== 添加新比赛记录 ==========
    st.divider()
    st.subheader("➕ 添加新比赛记录")
    with st.form("add_record"):
        col1, col2 = st.columns(2)
        with col1:
            new_mode = st.text_input("模式 (Mode)", placeholder="例如 对战模式")
            new_result = st.text_input("结果 (Result)", placeholder="例如 VICTORY")
            new_detail = st.text_input("详情 (Detail)", placeholder="例如 AS(99.87%)")
        with col2:
            new_xp = st.text_input("积分变化 (XP)", placeholder="例如 18733 (↑66)")
            new_date = st.date_input("日期 (Date)", value=datetime.today())
        
        submitted = st.form_submit_button("➕ 添加记录")
        
        if submitted:
            if not new_mode:
                st.error("请输入模式")
            else:
                # 检查是否已有该参赛者的记录，如果有则复制姓名
                existing = st.session_state.data[st.session_state.data["ID"] == selected_id]
                name = existing.iloc[0]["Name"] if not existing.empty else player_name
                password = existing.iloc[0]["Password"] if not existing.empty else ""
                
                new_row = pd.DataFrame([{
                    "ID": selected_id,
                    "Password": password,
                    "Name": name,
                    "Mode": new_mode.strip(),
                    "Result": new_result.strip(),
                    "Detail": new_detail.strip(),
                    "XP": new_xp.strip(),
                    "Date": new_date.strftime("%Y/%m/%d")
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.success("✅ 记录添加成功！")
                st.rerun()

# ========== 参赛者查询模式 ==========
def player_mode():
    st.subheader("🔍 查询我的比赛记录")
    with st.form("query_form"):
        col1, col2 = st.columns(2)
        with col1:
            query_id = st.text_input("编号 (ID)")
        with col2:
            query_password = st.text_input("密码 (Password)", type="password")
        submitted = st.form_submit_button("查询")
    
    if submitted:
        if not query_id or not query_password:
            st.warning("请输入编号和密码")
        elif st.session_state.data.empty:
            st.warning("暂无数据")
        else:
            result = st.session_state.data[
                (st.session_state.data["ID"] == query_id.strip()) &
                (st.session_state.data["Password"] == query_password.strip())
            ]
            if result.empty:
                st.error("❌ 编号或密码错误")
            else:
                name = result.iloc[0]["Name"] if pd.notna(result.iloc[0]["Name"]) else "参赛者"
                st.success(f"✅ {name} 的比赛记录")
                # 过滤掉空记录
                valid_records = result[result["Mode"] != ""]
                if valid_records.empty:
                    st.info("暂无比赛记录")
                else:
                    # 按日期排序（最新的在前）
                    sorted_records = valid_records.sort_values("Date", ascending=False)
                    for _, row in sorted_records.iterrows():
                        with st.container(border=True):
                            col_a, col_b = st.columns([2, 1])
                            with col_a:
                                st.markdown(f"**{row['Mode']}**")
                                if row['Detail']:
                                    st.caption(row['Detail'])
                            with col_b:
                                result_text = row['Result']
                                if "VICTORY" in result_text.upper() or "WIN" in result_text.upper():
                                    st.markdown(f"🟢 **{result_text}**")
                                elif "DEFEAT" in result_text.upper() or "LOSE" in result_text.upper():
                                    st.markdown(f"🔴 **{result_text}**")
                                elif "CLEAR" in result_text.upper():
                                    st.markdown(f"🟡 **{result_text}**")
                                else:
                                    st.markdown(f"⚪ **{result_text}**")
                                if row['XP']:
                                    st.text(row['XP'])
                                if row['Date']:
                                    st.caption(f"📅 {row['Date']}")

# ========== 主界面 ==========
st.title("🏆 比赛记录系统")

# 选择模式
mode = st.radio("选择模式", ["参赛者查询", "管理员录入"], horizontal=True)

if mode == "管理员录入":
    admin_password = st.text_input("请输入管理员密码", type="password")
    if admin_password == "admin123":
        admin_mode()
    elif admin_password:
        st.error("密码错误")
else:
    player_mode()

st.divider()
st.caption("📌 数据仅保存在当前会话中，刷新页面会重置。")
