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
# 관리자 로그인
# =========================

ADMIN_PASSWORD = "1234"

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
                st.error("비밀번호 오류")

    else:
        st.success("관리자 모드")
        if st.button("로그아웃"):
            st.session_state.admin = False
            st.rerun()

# =========================
# 데이터
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

csv_file = "reservations.csv"
conf_csv_file = "conference_reservations.csv"

if not os.path.exists(csv_file):
    pd.DataFrame(columns=[
        "날짜","사용시간","강의실","소속학과","신청학과",
        "행사책임자","행사책임자연락처","신청자","신청자연락처",
        "참가대상","참가인원","사용기자재","사용목적"
    ]).to_csv(csv_file, index=False, encoding="utf-8-sig")

if not os.path.exists(conf_csv_file):
    pd.DataFrame(columns=[
        "날짜","사용시간","컨퍼런스실","소속학과",
        "사용자이름","사용자연락처","참가인원","사용목적"
    ]).to_csv(conf_csv_file, index=False, encoding="utf-8-sig")

df = pd.read_csv(csv_file, dtype=str).fillna("")
conf_df = pd.read_csv(conf_csv_file, dtype=str).fillna("")

# =========================
# 중복 시간 체크 함수
# =========================

def is_time_overlap(existing_time, new_start, new_end):
    try:
        e_start, e_end = existing_time.split("~")
        e_start = pd.to_datetime(e_start.strip())
        e_end = pd.to_datetime(e_end.strip())

        n_start = pd.to_datetime(new_start)
        n_end = pd.to_datetime(new_end)

        return not (n_end <= e_start or n_start >= e_end)
    except:
        return False

# =========================
# UI
# =========================

st.title("🏫 강의실 / 컨퍼런스실 예약 시스템")
st.markdown("---")

menu = st.sidebar.radio(
    "메뉴 선택",
    [
        "강의실 사용 신청",
        "강의실 전체 예약 현황",
        "강의실 예약 수정 / 삭제",
        "컨퍼런스실 사용 신청",
        "컨퍼런스실 전체 예약 현황",
        "컨퍼런스실 예약 수정 / 삭제",
    ]
)

# =========================================================
# 강의실 신청
# =========================================================

if menu == "강의실 사용 신청":

    st.header("강의실 사용 신청")

    with st.form("class_form"):

        date = st.date_input("날짜")
        start = st.time_input("시작")
        end = st.time_input("종료")

        classroom = st.selectbox(
            "강의실",
            list(classrooms.keys()),
            format_func=lambda x: f"{x} ({classrooms[x]})"
        )

        dept = classrooms[classroom]

        applicant_dept = st.text_input("신청 학과")
        purpose = st.text_input("사용 목적")
        manager = st.text_input("책임자")
        manager_phone = st.text_input("연락처")
        applicant = st.text_input("신청자")
        applicant_phone = st.text_input("신청자 연락처")
        target = st.text_input("참가 대상")
        count = st.number_input("인원", min_value=1)

        submit = st.form_submit_button("신청")

        if submit:

            # =========================
            # 🔴 중복 체크 (강의실)
            # =========================
            for _, r in df.iterrows():
                if str(r["날짜"]) == str(date) and str(r["강의실"]) == classroom:

                    if is_time_overlap(
                        r["사용시간"],
                        start.strftime("%H:%M"),
                        end.strftime("%H:%M")
                    ):
                        st.error("❌ 해당 시간에 이미 예약된 강의실입니다.")
                        st.stop()

            use_time = f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}"

            new = {
                "날짜": str(date),
                "사용시간": use_time,
                "강의실": classroom,
                "소속학과": dept,
                "신청학과": applicant_dept,
                "행사책임자": manager,
                "행사책임자연락처": manager_phone,
                "신청자": applicant,
                "신청자연락처": applicant_phone,
                "참가대상": target,
                "참가인원": str(count),
                "사용기자재": "",
                "사용목적": purpose
            }

            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            df.to_csv(csv_file, index=False, encoding="utf-8-sig")

            st.success("예약 완료")
            st.rerun()

# =========================================================
# 강의실 현황
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
            "height": 650
        })

        st.dataframe(df)

    else:
        st.info("예약 없음")

# =========================================================
# 강의실 수정 / 삭제 (관리자)
# =========================================================

elif menu == "강의실 예약 수정 / 삭제":

    if not st.session_state.admin:
        st.warning("관리자만 접근 가능합니다.")
        st.stop()

    st.header("강의실 수정 / 삭제")

    if len(df) > 0:

        selected = st.selectbox(
            "예약 선택",
            [f"{i} | {r['날짜']} | {r['강의실']} | {r['신청자']}" for i, r in df.iterrows()]
        )

        idx = int(selected.split("|")[0])
        row = df.loc[idx]

        st.markdown("### ✏️ 수정")

        new_date = st.date_input("날짜", pd.to_datetime(row["날짜"]))
        new_time = st.text_input("사용시간", row["사용시간"])
        new_class = st.text_input("강의실", row["강의실"])
        new_dept = st.text_input("신청학과", row["신청학과"])
        new_purpose = st.text_input("사용목적", row["사용목적"])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("수정 저장"):
                df.at[idx, "날짜"] = str(new_date)
                df.at[idx, "사용시간"] = new_time
                df.at[idx, "강의실"] = new_class
                df.at[idx, "신청학과"] = new_dept
                df.at[idx, "사용목적"] = new_purpose

                df.to_csv(csv_file, index=False, encoding="utf-8-sig")

                st.success("수정 완료")
                st.rerun()

        with col2:
            if st.button("삭제"):
                df = df.drop(idx).reset_index(drop=True)
                df.to_csv(csv_file, index=False, encoding="utf-8-sig")

                st.warning("삭제 완료")
                st.rerun()

    else:
        st.info("데이터 없음")

# =========================================================
# 컨퍼런스실 신청
# =========================================================

elif menu == "컨퍼런스실 사용 신청":

    st.header("컨퍼런스실 사용 신청")
    st.info(CONFERENCE_ROOM_NAME)

    with st.form("conf_form"):

        date = st.date_input("날짜")
        start = st.time_input("시작")
        end = st.time_input("종료")

        submit = st.form_submit_button("예약")

        if submit:

            # =========================
            # 🔴 중복 체크 (컨퍼런스실)
            # =========================
            for _, r in conf_df.iterrows():

                if str(r["날짜"]) == str(date):

                    if is_time_overlap(
                        r["사용시간"],
                        start.strftime("%H:%M"),
                        end.strftime("%H:%M")
                    ):
                        st.error("❌ 해당 시간에 이미 예약된 컨퍼런스실입니다.")
                        st.stop()

            use_time = f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}"

            new = {
                "날짜": str(date),
                "사용시간": use_time,
                "컨퍼런스실": CONFERENCE_ROOM_NAME,
                "소속학과": st.text_input("학과"),
                "사용자이름": st.text_input("이름"),
                "사용자연락처": st.text_input("연락처"),
                "참가인원": str(st.number_input("인원", min_value=1)),
                "사용목적": st.text_input("목적")
            }

            conf_df = pd.concat([conf_df, pd.DataFrame([new])], ignore_index=True)
            conf_df.to_csv(conf_csv_file, index=False, encoding="utf-8-sig")

            st.success("예약 완료")
            st.rerun()

# =========================================================
# 컨퍼런스실 현황
# =========================================================

elif menu == "컨퍼런스실 전체 예약 현황":

    st.header("컨퍼런스실 예약 현황")

    if len(conf_df) > 0:
        st.dataframe(conf_df)
    else:
        st.info("없음")

# =========================================================
# 컨퍼런스실 수정 / 삭제 (관리자)
# =========================================================

elif menu == "컨퍼런스실 예약 수정 / 삭제":

    if not st.session_state.admin:
        st.warning("관리자만 접근 가능합니다.")
        st.stop()

    st.header("컨퍼런스실 수정 / 삭제")

    if len(conf_df) > 0:

        selected = st.selectbox(
            "예약 선택",
            [f"{i} | {r['날짜']} | {r['사용자이름']}" for i, r in conf_df.iterrows()]
        )

        idx = int(selected.split("|")[0])
        row = conf_df.loc[idx]

        st.markdown("### ✏️ 수정")

        new_date = st.date_input("날짜", pd.to_datetime(row["날짜"]))
        new_time = st.text_input("사용시간", row["사용시간"])
        new_major = st.text_input("학과", row["소속학과"])
        new_name = st.text_input("이름", row["사용자이름"])
        new_phone = st.text_input("연락처", row["사용자연락처"])
        new_purpose = st.text_input("목적", row["사용목적"])

        col1, col2 = st.columns(2)

        with col1:
            if st.button("수정 저장"):
                conf_df.at[idx, "날짜"] = str(new_date)
                conf_df.at[idx, "사용시간"] = new_time
                conf_df.at[idx, "소속학과"] = new_major
                conf_df.at[idx, "사용자이름"] = new_name
                conf_df.at[idx, "사용자연락처"] = new_phone
                conf_df.at[idx, "사용목적"] = new_purpose

                conf_df.to_csv(conf_csv_file, index=False, encoding="utf-8-sig")

                st.success("수정 완료")
                st.rerun()

        with col2:
            if st.button("삭제"):
                conf_df = conf_df.drop(idx).reset_index(drop=True)
                conf_df.to_csv(conf_csv_file, index=False, encoding="utf-8-sig")

                st.warning("삭제 완료")
                st.rerun()

    else:
        st.info("데이터 없음")
