# pages/1_Dessert_Production_Analysis.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- 설정 (Configuration) ---
st.set_page_config(
    page_title="냉동 디저트 생산량 분석",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🍦 냉동 디저트 생산량 분석 (1972-2019)")

# --- 1. 데이터 로드 (Data Loading) - 파일 경로 및 인코딩 문제 해결 ---
@st.cache_data
def load_data_final():
    file_name = 'Frozen_Dessert_Production.csv'
    
    # 시도할 경로 목록
    possible_paths = [
        file_name, # 1차 시도: 앱의 루트 폴더 (Streamlit Cloud 기본 경로)
        os.path.join(os.path.dirname(__file__), '..', file_name) # 2차 시도: pages 폴더 기준 상위 폴더
    ]
    
    encodings = ['utf-8', 'cp949', 'euc-kr']

    for path in possible_paths:
        for encoding in encodings:
            try:
                data = pd.read_csv(path, encoding=encoding)
                st.success(f"✅ 파일이 성공적으로 로드되었습니다. (경로: {path}, 인코딩: {encoding})")
                
                # 데이터 전처리
                data.columns = ['Date', 'Production_Index']
                data['Date'] = pd.to_datetime(data['Date'])
                data = data.set_index('Date')
                return data
            except FileNotFoundError:
                continue 
            except Exception:
                continue
    
    # 모든 시도 실패 시
    st.error("⚠️ **데이터 파일(Frozen_Dessert_Production.csv)을 찾을 수 없습니다!**")
    st.error("파일이 아래 구조대로 위치하는지 확인해주세요.")
    st.markdown(
        """
        ```
        frozen_dessert_app/ (앱의 루트)
        ├── Frozen_Dessert_Production.csv  <-- 이 위치에 파일이 있어야 합니다!
        ├── pages/
        │   └── 1_Dessert_Production_Analysis.py
        └── requirements.txt
        ```
        """
    )
    st.stop()

data = load_data_final()

# ----------------------------------------------------
# 📌 기간 선택 기능 (슬라이더) 추가
# ----------------------------------------------------

min_year = data.index.year.min()
max_year = data.index.year.max()

st.sidebar.header("🗓️ 기간 선택 필터")
start_year, end_year = st.sidebar.slider(
    "분석 기간을 선택하세요:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

# 선택된 기간으로 데이터 필터링
start_date = f'{start_year}-01-01'
end_date = f'{end_year}-12-31'
data_filtered = data.loc[start_date:end_date]

st.info(f"선택된 분석 기간: **{start_year}년 1월 ~ {end_year}년 12월**")
st.markdown("---")


# --- 2. 데이터 전처리 및 요약 (Data Preprocessing and Summary) ---
# **(필터링된 데이터를 사용하여 재계산 및 표시)**

st.header("🔍 데이터 탐색 및 요약")
st.markdown("---")

# 2.2. 데이터프레임 확인
st.subheader(f"데이터 미리보기 ({start_year}년 ~ {end_year}년)")
st.dataframe(data_filtered.head())

# 2.3. 기본 정보 요약
st.subheader("데이터 구조 (전체 기간)")
buffer = pd.io.common.StringIO()
data_filtered.info(buf=buffer) # info는 전체 데이터셋의 구조를 보여주는 것이 일반적입니다.
s = buffer.getvalue()
st.text(s)

# 2.4. 통계 요약
st.subheader(f"통계 요약 ({start_year}년 ~ {end_year}년)")
st.dataframe(data_filtered.describe().T)

# 2.5. 추가 분석: 계절성 및 연도별
# 월별 평균 생산 지수 (선택된 기간의 데이터로 재계산)
monthly_avg = data_filtered['Production_Index'].groupby(data_filtered.index.month).mean()
monthly_avg.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
st.subheader(f"월별 평균 생산 지수 (선택 기간: {start_year}년 ~ {end_year}년)")
st.dataframe(monthly_avg.to_frame(name='Monthly_Avg_Index'))
st.info("이 평균값은 선택된 기간의 계절성을 반영합니다. 기간에 따라 계절적 패턴이 미세하게 변화하는지 확인할 수 있습니다.")

st.markdown("---")

# --- 3. Plotly 시각화 (Plotly Visualization) ---

st.header("📊 생산량 시계열 시각화")

# 3.1. 깔끔하고 인터랙티브한 시계열 선 그래프 (Line Chart)
fig_line = px.line(
    data_filtered.reset_index(), # 필터링된 데이터 사용
    x='Date',
    y='Production_Index',
    title=f'냉동 디저트 월별 생산 지수 ({start_year}년 ~ {end_year}년)',
    labels={'Production_Index': '생산 지수 (IPN31152N)', 'Date': '날짜'},
    template='plotly_white'
)
fig_line.update_traces(line=dict(color='blue'))
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# --- 4. 추가 시각화: 월별 평균 막대 그래프 (Seasonal Bar Chart) ---

st.header("🌈 월별 평균 생산 지수 막대 그래프")

# 4.1. 월별 평균 데이터를 Plotly에 맞게 정리
# (재계산된 monthly_avg 사용)
monthly_avg_df = monthly_avg.reset_index()
monthly_avg_df.columns = ['Month', 'Monthly_Avg_Index'] 

# 4.2. Plotly 막대 그래프 생성
fig_bar = px.bar(
    monthly_avg_df, # 수정된 데이터프레임 사용
    x='Month', 
    y='Monthly_Avg_Index', 
    title=f'월별 평균 생산 지수 ({start_year}년 ~ {end_year}년)',
    labels={'Month': '월', 'Monthly_Avg_Index': '평균 생산 지수'},
    color='Monthly_Avg_Index', 
    color_continuous_scale=px.colors.sequential.Rainbow, 
    template='plotly_white'
)

# X축 레이블을 월 이름으로 명확하게 설정
fig_bar.update_xaxes(tickvals=monthly_avg_df['Month'].tolist(), ticktext=monthly_avg_df['Month'].tolist())

st.plotly_chart(fig_bar, use_container_width=True)
