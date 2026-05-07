import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

# =========================
# 페이지 설정
# =========================

st.set_page_config(
    page_title="강의실 / 컨퍼런스실 예약 시스템",
    layout="wide"
)

# =========================
# 관리자 설정
# =========================

ADMIN_PASSWORD = "9303"  # 원하는 비밀번호로 변경

if "admin" not in st.session_state:
    st.session_state.admin = False

with st.sidebar:
    st.markdown("## 🔐 관리자 로그인")

    if not st.session_state.admin:
        pw = st.text_input("비밀번호", type="password")

        if st.button("로그인"):
            if pw == ADMIN_PASSWORD:
                st.session_state.admin = True
                st.success("관리자 로그인 성공")
            else:
                st.error("비밀번호가 틀렸습니다")

    else:
        st.success("관리자 모드 활성화")
        if st.button("로그아웃"):
            st.session_state.admin = False
            st.rerun()

# =========================
# 강의실 정보
# =========================

classrooms = {
    "5101": "사회과학대학",
    "5303": "경제학전공",
    "5402": "행정학전공",
    "5403": "법학과",
    "5405": "정치외교학전공",
    "5503": "범죄교정심리학전공",
    "5504": "경찰행정학전공",
    "5505": "사회복지학전공",
    "5506": "사회복지학전공",
    "4107": "청소년학전공",
    "4205": "지식재산학전공",
    "4303": "무역학과",
    "4306": "무역학과",
    "4307": "응용통계학전공",
    "4308": "응용통계학전공"
}

CONFERENCE_ROOM_NAME = "교수연구동 A217호"

# =========================
# CSV 파일 설정
# =========================

csv_file = "reservations.csv"
conf_csv_file = "conference_reservations.csv"

if not os.path.exists(csv_file):
    pd.DataFrame(columns=[
        "날짜","사용시간","강의실","소속학과","신청학과","행사책임자",
        "행사책임자연락처","신청자","신청자연락처","참가대상",
        "참가인원","사용기자재","사용목적"
    ]).to_csv(csv_file, index=False, encoding="utf-8-sig")

if not os.path.exists(conf_csv_file):
    pd.DataFrame(columns=[
        "날짜","사용시간","컨퍼런스실","소속학과",
        "사용자이름","사용자연락처","참가인원","사용목적"
    ]).to_csv(conf_csv_file, index=False, encoding="utf-8-sig")

df = pd.read_csv(csv_file, dtype=str).fillna("")
conf_df = pd.read_csv(conf_csv_file, dtype=str).fillna("")

# =========================
# 타이틀
# =========================

st.title("강의실 / 컨퍼런스실 예약 시스템")
st.markdown("---")

# =========================
# 메뉴 (구분선 제거)
# =========================

st.sidebar.markdown("## 📚 강의실")
menu1 = st.sidebar.radio(
    "",
    [
        "강의실 사용 신청",
        "강의실 전체 예약 현황",
        "강의실 예약 수정 / 삭제",
    ]
)

st.sidebar.markdown("---")

st.sidebar.markdown("## 🏢 컨퍼런스실")
menu2 = st.sidebar.radio(
    "",
    [
        "컨퍼런스실 사용 신청",
        "컨퍼런스실 전체 예약 현황",
        "컨퍼런스실 예약 수정 / 삭제",
    ]
)

# =========================
# 시간 파싱
# =========================

def parse_time_parts(time_str, fallback_start="09:00", fallback_end="10:00"):
    try:
        start = time_str.split("~")[0].strip()
        end = time_str.split("~")[1].strip()
    except:
        start, end = fallback_start, fallback_end
    return start, end

# =========================================================
# 강의실 사용 신청
# =========================================================

if menu == "강의실 사용 신청":

    st.header("강의실 사용 신청")

    with st.form("reservation_form"):

        date = st.date_input("사용 날짜")

        start_time = st.time_input("시작 시간")
        end_time = st.time_input("종료 시간")

        use_time = f"{start_time.strftime('%H:%M')} ~ {end_time.strftime('%H:%M')}"

        classroom = st.selectbox(
            "강의실 선택",
            list(classrooms.keys()),
            format_func=lambda x: f"{x} ({classrooms[x]})"
        )

        department = classrooms[classroom]

        applicant_department = st.text_input("사용 신청 학과")
        purpose = st.text_input("사용 목적")
        event_manager = st.text_input("행사책임자")
        event_manager_phone = st.text_input("행사책임자 연락처")
        applicant = st.text_input("신청자")
        applicant_phone = st.text_input("신청자 연락처")
        participant_target = st.text_input("참가 대상")
        participant_count = st.number_input("참가 인원", min_value=1)

        submit = st.form_submit_button("예약 신청")

        if submit:
            new_data = {
                "날짜": str(date),
                "사용시간": use_time,
                "강의실": classroom,
                "소속학과": department,
                "신청학과": applicant_department,
                "행사책임자": event_manager,
                "행사책임자연락처": event_manager_phone,
                "신청자": applicant,
                "신청자연락처": applicant_phone,
                "참가대상": participant_target,
                "참가인원": str(participant_count),
                "사용기자재": "",
                "사용목적": purpose
            }

            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            df.to_csv(csv_file, index=False, encoding="utf-8-sig")

            st.success("예약 완료!")
            st.rerun()

# =========================================================
# 강의실 전체 예약 현황
# =========================================================

elif menu == "강의실 전체 예약 현황":

    st.header("강의실 예약 현황")

    if len(df) > 0:
        df["날짜"] = pd.to_datetime(df["날짜"])

        events = [
            {
                "title": f'{r["강의실"]} | {r["신청학과"]}',
                "start": r["날짜"].strftime("%Y-%m-%d"),
                "end": r["날짜"].strftime("%Y-%m-%d"),
            }
            for _, r in df.iterrows()
        ]

        calendar(events=events, options={
            "initialView": "dayGridMonth",
            "locale": "ko",
            "height": 700
        })

        st.dataframe(df)

    else:
        st.info("예약 없음")

# =========================================================
# 강의실 수정 / 삭제 (관리자 제한)
# =========================================================

elif menu == "강의실 예약 수정 / 삭제":

    if not st.session_state.admin:
        st.warning("관리자만 접근 가능합니다.")
        st.stop()

    st.header("강의실 예약 수정 / 삭제")

    if len(df) > 0:

        selected = st.selectbox(
            "예약 선택",
            [f"{i} | {r['날짜']} | {r['강의실']}" for i, r in df.iterrows()]
        )

        idx = int(selected.split("|")[0])

        if st.button("삭제"):
            df = df.drop(idx).reset_index(drop=True)
            df.to_csv(csv_file, index=False, encoding="utf-8-sig")
            st.success("삭제 완료")
            st.rerun()

    else:
        st.info("데이터 없음")

# =========================================================
# 컨퍼런스실 신청
# =========================================================

elif menu == "컨퍼런스실 사용 신청":

    st.header("컨퍼런스실 신청")

    with st.form("conf_form"):

        date = st.date_input("날짜")
        start = st.time_input("시작")
        end = st.time_input("종료")

        use_time = f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}"

        major = st.text_input("학과")
        name = st.text_input("이름")
        phone = st.text_input("연락처")
        count = st.number_input("인원", min_value=1)
        purpose = st.text_input("목적")

        if st.form_submit_button("예약"):
            new = {
                "날짜": str(date),
                "사용시간": use_time,
                "컨퍼런스실": CONFERENCE_ROOM_NAME,
                "소속학과": major,
                "사용자이름": name,
                "사용자연락처": phone,
                "참가인원": str(count),
                "사용목적": purpose
            }

            conf_df = pd.concat([conf_df, pd.DataFrame([new])], ignore_index=True)
            conf_df.to_csv(conf_csv_file, index=False, encoding="utf-8-sig")

            st.success("완료")
            st.rerun()

# =========================================================
# 컨퍼런스실 전체 현황
# =========================================================

elif menu == "컨퍼런스실 전체 예약 현황":

    st.header("컨퍼런스실 예약 현황")

    if len(conf_df) > 0:
        st.dataframe(conf_df)
    else:
        st.info("없음")

# =========================================================
# 컨퍼런스실 수정 / 삭제 (관리자 제한)
# =========================================================

elif menu == "컨퍼런스실 예약 수정 / 삭제":

    if not st.session_state.admin:
        st.warning("관리자만 접근 가능합니다.")
        st.stop()

    st.header("컨퍼런스실 수정 / 삭제")

    if len(conf_df) > 0:

        selected = st.selectbox(
            "선택",
            [f"{i} | {r['날짜']} | {r['사용자이름']}" for i, r in conf_df.iterrows()]
        )

        idx = int(selected.split("|")[0])

        if st.button("삭제"):
            conf_df = conf_df.drop(idx).reset_index(drop=True)
            conf_df.to_csv(conf_csv_file, index=False, encoding="utf-8-sig")
            st.success("삭제 완료")
            st.rerun()

    else:
        st.info("데이터 없음")
