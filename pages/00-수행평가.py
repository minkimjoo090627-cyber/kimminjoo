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

# --- 1. 데이터 로드 (Data Loading) ---

# 파일 경로: pages 폴더 내의 스크립트에서 상위 폴더에 있는 CSV 파일을 참조
@st.cache_data
def load_data(file_path):
    try:
        # '..' 을 사용하여 상위 폴더 접근
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"오류: 파일을 찾을 수 없습니다. 경로를 확인해주세요: {file_path}")
        return None

# 현재 스크립트의 경로를 기반으로 상위 폴더의 CSV 파일 경로 설정
csv_file_path = os.path.join(os.path.dirname(__file__), '..', 'Frozen_Dessert_Production.csv')
data = load_data(csv_file_path)

if data is not None:
    # --- 2. 데이터 전처리 및 요약 (Data Preprocessing and Summary) ---
    
    # 2.1. 컬럼 이름 정리 및 날짜 포맷 변환
    data.columns = ['Date', 'Production_Index']
    data['Date'] = pd.to_datetime(data['Date'])
    data = data.set_index('Date')
    
    st.header("🔍 데이터 탐색 및 요약")
    
    # 2.2. 데이터프레임 확인
    st.subheader("데이터 미리보기")
    st.dataframe(data.head())

    # 2.3. 기본 정보 요약
    st.subheader("기본 정보 (Null 값, 데이터 타입)")
    buffer = pd.io.common.StringIO()
    data.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)
    
    # 2.4. 통계 요약
    st.subheader("통계 요약")
    st.dataframe(data.describe().T)

    # 2.5. 추가 분석: 계절성 및 연도별
    
    # 월별 평균 생산 지수
    monthly_avg = data['Production_Index'].groupby(data.index.month).mean()
    monthly_avg.index = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    st.subheader("월별 평균 생산 지수 (계절성 확인)")
    st.dataframe(monthly_avg.to_frame(name='Monthly_Avg_Index'))
    st.info("여름철(6월~8월)에 생산량이 가장 높고 겨울철에 가장 낮은 뚜렷한 **계절성**이 나타납니다.")

    # --- 3. Plotly 시각화 (Plotly Visualization) ---
    
    st.header("📊 생산량 시계열 시각화")

    # 3.1. 깔끔하고 인터랙티브한 시계열 선 그래프 (Line Chart)
    # 시계열 데이터이므로 선 그래프가 적절하며, 단일 시리즈이므로 '무지개 색'을 적용하기 어렵습니다.
    # 대신, Plotly의 기본 색상 테마를 사용하여 깔끔하고 인터랙티브한 그래프를 생성합니다.
    
    fig_line = px.line(
        data.reset_index(), # Plotly를 위해 인덱스를 컬럼으로 변환
        x='Date',
        y='Production_Index',
        title='냉동 디저트 월별 생산 지수 (1972-2019)',
        labels={'Production_Index': '생산 지수 (IPN31152N)', 'Date': '날짜'},
        template='plotly_white' # 깔끔한 템플릿 사용
    )

    # 인터랙티브 기능 추가 (드래그하여 확대/축소, 마우스 오버 정보)
    fig_line.update_traces(line=dict(color='blue')) # 선 색상 지정
    
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown(
        """
        - 그래프를 통해 시간이 지남에 따라 **전반적인 생산 지수**가 **증가**하는 **추세**와
        - 매년 여름에 최고점을 찍고 겨울에 최저점을 찍는 **강력한 계절성**을 확인할 수 있습니다.
        """
    )
    
    # --- 4. 추가 시각화: 월별 평균 막대 그래프 (Seasonal Bar Chart) ---
    
    # 사용자 요청에 따라 계절성을 보여주는 막대 그래프를 Plotly로 추가합니다.
    # '무지개 색' 느낌을 내기 위해 Plotly의 다양한 색상 스케일을 적용합니다.
    st.header("🌈 월별 평균 생산 지수 막대 그래프")
    
    # 월별 평균을 Plotly로 시각화
    fig_bar = px.bar(
        monthly_avg.reset_index(),
        x='index',
        y='Monthly_Avg_Index',
        title='월별 평균 생산 지수',
        labels={'index': '월', 'Monthly_Avg_Index': '평균 생산 지수'},
        color='Monthly_Avg_Index', # 막대 높이에 따라 색상 변화
        color_continuous_scale=px.colors.sequential.Rainbow, # 무지개 느낌의 색상 스케일
        template='plotly_white'
    )
    
    # X축 레이블을 월 이름으로 명확하게 설정
    fig_bar.update_xaxes(tickvals=monthly_avg.index.tolist(), ticktext=monthly_avg.index.tolist())
    
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("월별 평균 생산량 막대 그래프에서 여름철(6월, 7월, 8월)에 생산량이 가장 높은 것을 명확하게 볼 수 있습니다.")
