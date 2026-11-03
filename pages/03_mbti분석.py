from pathlib import Path
import pandas as pd
import streamlit as st

# 현재 py 파일은 pages 폴더, CSV는 프로젝트 최상위 폴더
PROJECT_ROOT = Path(__file__).resolve().parent.parent

def load_csv():
    # 우선순위대로 CSV 파일 찾기
    candidates = [
        PROJECT_ROOT / "countriesMBTI_16types.csv",
        PROJECT_ROOT / "countriesMBTI_16types (1).csv",
        PROJECT_ROOT / "countriesMBTI_16types (2).csv",
    ]

    # 정확한 이름이 없으면 비슷한 이름을 자동 검색
    csv_path = next((path for path in candidates if path.is_file()), None)

    if csv_path is None:
        matches = list(PROJECT_ROOT.rglob("countriesMBTI_16types*.csv"))
        if matches:
            csv_path = matches[0]

    if csv_path is None:
        st.error("CSV 파일을 찾을 수 없습니다.")
        st.write("현재 프로젝트 경로:", str(PROJECT_ROOT))
        st.write("프로젝트 최상위 폴더의 파일 목록:")
        st.write([p.name for p in PROJECT_ROOT.iterdir()])
        st.stop()

    try:
        return pd.read_csv(csv_path, encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(csv_path, encoding="cp949")


@st.cache_data
def get_data():
    return load_csv()


df = get_data()
