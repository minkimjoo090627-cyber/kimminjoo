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

# --- 1. 데이터 로드 (Data Loading) - 경로 문제 해결 ---
@st.cache_data
def load_data():
    file_name = 'Frozen_Dessert_Production.csv'
    data = None
    
    # 1차 시도: 앱의 루트 폴더에서 파일 이름으로 직접 접근 (Streamlit Cloud에서 가장 안정적)
    try:
        data = pd.read_csv(file_name)
        st.success("✅ 파일이 앱의 루트 폴더에서 성공적으로 로드되었습니다.")
        return data
    except FileNotFoundError:
        pass # 1차 시도 실패, 2차 시도 진행

    # 2차 시도: pages 폴더 내부에서 상위 폴더(..)로 접근 (사용자님의 원래 구조)
    try:
        # 현재 스크립트 경로에서 상위 폴더로 이동하여 CSV 파일 경로 설정
        relative_path = os.path.join(os.path.dirname(__file__), '..', file_name)
        data = pd.read_csv(relative_path)
        st.success("✅ 파일이 'pages' 폴더 상위 경로에서 성공적으로 로드되었습니다.")
        return data
    except FileNotFoundError:
        # 두 번 모두 실패했을 경우 오류 메시지 출력 후 앱 중단
        st.error("⚠️ **데이터 파일(Frozen_Dessert_Production.csv)을 찾을 수 없습니다!**")
        st.error("파일 경로를 확인해주세요. 예상되는 파일 위치는 다음과 같습니다.")
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
        st.stop() # 이후 코드 실행 중단
    except Exception as e:
        st.error(f"데이터 로딩 중 알 수 없는 오류 발생: {type(e).__name__}: {e}")
        st.stop()

data = load_data() # 데이터 로드 함수 호출

# --- 2. 데이터 전처리 및 요약 (Data Preprocessing and Summary) ---
# 데이터 로드에 성공했을 경우만 이어서 진행
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
fig_line = px.line(
    data.reset_index(),
    x='Date',
    y='Production_Index',
    title='냉동 디저트 월별 생산 지수 (1972-2019)',
    labels={'Production_Index': '생산 지수 (IPN31152N)', 'Date': '날짜'},
    template='plotly_white'
)
fig_line.update_traces(line=dict(color='blue'))
st.plotly_chart(fig_line, use_container_width=True)

# --- 4. 추가 시각화: 월별 평균 막대 그래프 (Seasonal Bar Chart) ---

st.header("🌈 월별 평균 생산 지수 막대 그래프")

# 월별 평균을 Plotly로 시각화
fig_bar = px.bar(
    monthly_avg.reset_index(),
    x='index',
    y='Monthly_Avg_Index',
    title='월별 평균 생산 지수',
    labels={'index': '월', 'Monthly_Avg_Index': '평균 생산 지수'},
    color='Monthly_Avg_Index',
    color_continuous_scale=px.colors.sequential.Rainbow, # 무지개 느낌의 색상 스케일
    template='plotly_white'
)
fig_bar.update_xaxes(tickvals=monthly_avg.index.tolist(), ticktext=monthly_avg.index.tolist())

st.plotly_chart(fig_bar, use_container_width=True)
