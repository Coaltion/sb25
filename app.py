import streamlit as st
import pandas as pd
from datetime import datetime

# 页面设置
st.set_page_config(page_title="🏆 比赛记录查询", page_icon="🏆", layout="centered")

# 初始化数据（存储在 Streamlit 的缓存中，类似数据库）
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["ID", "Password", "Name", "Mode", "Result", "Detail", "XP", "Date"])

# ========== 管理员模式 ==========
def admin_mode():
    st.subheader("🔐 管理员：录入/管理记录")
    with st.form("add_record"):
        col1, col2 = st.columns(2)
        with col1:
            new_id = st.text_input("编号 (ID)")
            new_password = st.text_input("密码 (Password)")
            new_name = st.text_input("姓名 (Name)")
        with col2:
            new_mode = st.text_input("模式 (Mode)")
            new_result = st.text_input("结果 (Result)")
            new_detail = st.text_input("详情 (Detail)")
        new_xp = st.text_input("积分变化 (XP)")
        new_date = st.date_input("日期 (Date)", value=datetime.today())
        submitted = st.form_submit_button("➕ 添加记录")
        
        if submitted:
            if not new_id or not new_password:
                st.error("编号和密码为必填项")
            else:
                new_row = pd.DataFrame([{
                    "ID": new_id.strip(),
                    "Password": new_password.strip(),
                    "Name": new_name.strip(),
                    "Mode": new_mode.strip(),
                    "Result": new_result.strip(),
                    "Detail": new_detail.strip(),
                    "XP": new_xp.strip(),
                    "Date": new_date.strftime("%Y/%m/%d")
                }])
                st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
                st.success("✅ 记录添加成功！")
                st.rerun()
    
    # 显示所有数据
    st.subheader("📋 所有记录")
    if not st.session_state.data.empty:
        st.dataframe(st.session_state.data, use_container_width=True)
        
        # 删除记录功能
        with st.expander("🗑️ 删除记录"):
            delete_id = st.text_input("输入要删除的编号 (ID)")
            if st.button("删除该编号的所有记录"):
                if delete_id:
                    st.session_state.data = st.session_state.data[st.session_state.data["ID"] != delete_id.strip()]
                    st.success(f"已删除编号 {delete_id} 的所有记录")
                    st.rerun()
    else:
        st.info("暂无记录")

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
                # 按日期排序（最新的在前）
                result_sorted = result.sort_values("Date", ascending=False)
                for _, row in result_sorted.iterrows():
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
    if admin_password == "admin123":  # 默认密码，您可以修改
        admin_mode()
    elif admin_password:
        st.error("密码错误")
else:
    player_mode()

# 页脚
st.divider()
st.caption("📌 数据仅保存在当前会话中，刷新页面会重置。如需永久保存，请部署到 Streamlit Cloud。")
