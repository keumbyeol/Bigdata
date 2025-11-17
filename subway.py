import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

# -------------------------------
# 기본 헤더
# -------------------------------
st.header("서울 지하철 승하차 인원 (2025년 9월)")

# -------------------------------
# 데이터 불러오기
# -------------------------------
subway = pd.read_csv("subway.csv")

# ✅ 사용일자 형식 변환 (YYYYMMDD → datetime)
subway['사용일자'] = pd.to_datetime(subway['사용일자'], format='%Y%m%d')

st.dataframe(subway.head())

# -------------------------------
# 🔹 사이드바 메뉴
# -------------------------------
st.sidebar.title("분석 옵션")
menu = st.sidebar.radio(
    "분석 유형 선택",
    ["노선별 분석", "역별 분석", "날짜별 추이 분석"]
)

# =========================================================
# ① 🚇 노선별 분석
# =========================================================
if menu == "노선별 분석":
    st.subheader("🚇 노선별 분석 결과")

    # 노선별 총 승하차 인원
    result = subway.groupby("노선명")\
        .agg(노선별총승차=("승차총승객수", "sum"),
             노선별총하차=("하차총승객수", "sum"))


    # 노선별 평균 승하차 인원
    result1 = subway.groupby("노선명")\
        .agg(노선별평균승차=("승차총승객수", "mean"),
             노선별평균하차=("하차총승객수", "mean"))


    # 상위 7개 노선 평균 시각화
    result2 = result1.sort_values("노선별평균승차", ascending=False).head(7)
    result2_melted = result2.reset_index().melt(
        id_vars="노선명",
        value_vars=["노선별평균승차", "노선별평균하차"],
        var_name="구분",
        value_name="평균승객수"
    )

    fig2 = plt.figure(figsize=(8, 5))
    sns.barplot(data=result2_melted, x="노선명", y="평균승객수", hue="구분")
    plt.title("상위 7개 노선의 평균 승차/하차 인원")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # 노선명 검색 기능
    station_line = st.text_input("🔍 조회할 노선명을 입력하세요")
    if station_line:
        station_data = subway[subway['노선명'].str.contains(station_line)]
        station_lines = station_data.groupby('노선명', as_index=False)\
            .agg(노선별승차총수=('승차총승객수', 'sum'),
                 노선별하차총수=('하차총승객수', 'sum'),
                노선별승차평균=('승차총승객수', 'mean'))
        st.dataframe(station_lines[['노선명', '노선별승차총수', '노선별하차총수','노선별승차평균']])

# =========================================================
# ② 🚉 역별 분석
# =========================================================
elif menu == "역별 분석":
    st.subheader("🚉 역별 분석 결과")

    # 역별 평균 승하차 인원
    result3 = subway.groupby("역명")\
        .agg(역별평균승차=("승차총승객수", "mean"),
             역별평균하차=("하차총승객수", "mean"))\
        .sort_values("역별평균승차", ascending=False)\
        .head(5)

    result3_melted = result3.reset_index().melt(
        id_vars="역명",
        value_vars=["역별평균승차", "역별평균하차"],
        var_name="구분",
        value_name="평균승객수"
    )

    fig1 = plt.figure(figsize=(8, 5))
    sns.barplot(data=result3_melted, x="역명", y="평균승객수", hue="구분")
    plt.title("상위 5개 역의 평균 승차/하차 인원")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # 역명 검색 기능 (총 승/하차 + 최대 승차일/승차수)
    station_name = st.text_input("🔍 조회할 역명을 입력하세요")
    if station_name:
        station_data = subway[subway['역명'].str.contains(station_name)]

        # 1️⃣ 역별 총 승/하차
        station_result = station_data.groupby('역명', as_index=False)\
            .agg(역별승차총수=('승차총승객수', 'sum'),
                 역별하차총수=('하차총승객수', 'sum'),
                역별승차평균=('승차총승객수', 'mean'))

        # 2️⃣ 역별 최대 승차일 및 승차수
        max_rides = station_data.loc[station_data.groupby('역명')['승차총승객수'].idxmax(),
                                     ['역명', '사용일자', '승차총승객수']]
        max_rides = max_rides.rename(columns={
            '사용일자': '최다승차일',
            '승차총승객수': '최다승차수'
        })

        # 3️⃣ 병합
        station_result = station_result.merge(max_rides, on='역명')

        # 4️⃣ 화면에 표시
        st.dataframe(station_result[['역명', '역별승차총수','역별하차총수', '역별승차평균', '최다승차일', '최다승차수']])

# =========================================================
# ③ 📅 날짜별 추이 분석
# =========================================================
elif menu == "날짜별 추이 분석":
    st.subheader("📅 날짜별 추이 분석")

    # 날짜별 전체 승하차 합계
    date_result = subway.groupby("사용일자")\
        .agg(총승차=("승차총승객수", "sum"),
             총하차=("하차총승객수", "sum")).reset_index()

    fig3 = plt.figure(figsize=(10, 5))
    sns.lineplot(data=date_result, x="사용일자", y="총승차", label="승차")
    sns.lineplot(data=date_result, x="사용일자", y="총하차", label="하차")
    plt.title("날짜별 총 승차/하차 인원 추이 (2025년 9월)")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

    # 요일별 평균 승하차 분석
    subway['요일'] = subway['사용일자'].dt.day_name()
    weekday_result = subway.groupby("요일")\
        .agg(평균승차=("승차총승객수", "mean"),
             평균하차=("하차총승객수", "mean")).reset_index()

    # 겹치지 않게 옆으로
    weekday_melted = weekday_result.melt(id_vars="요일", value_vars=["평균승차", "평균하차"],
                                         var_name="구분", value_name="평균승객수")

    fig4 = plt.figure(figsize=(8, 5))
    sns.barplot(data=weekday_melted, x="요일", y="평균승객수", hue="구분")
    plt.title("요일별 평균 승차/하차 인원")
    st.pyplot(fig4)

    # 특정 노선의 날짜별 추이
    line_list = sorted(subway['노선명'].unique())
    select_line = st.selectbox("🔍 날짜별 추이를 볼 노선을 선택하세요", line_list)

    line_trend = subway[subway['노선명'] == select_line]\
        .groupby("사용일자")\
        .agg(총승차=("승차총승객수", "sum"),
             총하차=("하차총승객수", "sum")).reset_index()

    fig5 = px.line(line_trend, x="사용일자", y=["총승차", "총하차"],
                   title=f"{select_line}의 날짜별 승하차 추이")
    st.plotly_chart(fig5)
