import pandas as pd
import streamlit as st

from config import DATA_PATH, FEATURES, TARGET


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    return df


def get_country_list(df):
    country_df = df[df["iso_code"].notna()].copy()
    countries = sorted(country_df["country"].dropna().unique())
    return countries


def create_model_dataset(df):
    required_columns = FEATURES + [TARGET, "country", "iso_code"]
    available_columns = [col for col in required_columns if col in df.columns]

    model_df = df[available_columns].copy()

    model_df = model_df[
        (model_df["iso_code"].notna()) &
        (model_df[TARGET].notna())
    ].copy()

    model_df = model_df.dropna(subset=FEATURES + [TARGET])

    return model_df, FEATURES, TARGET