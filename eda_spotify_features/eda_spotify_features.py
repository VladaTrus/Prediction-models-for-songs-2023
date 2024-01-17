import os
import shutil
import subprocess
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from dateutil.parser import parse
from sklearn.preprocessing import LabelEncoder


def eda_spotify_features():
    if os.path.exists("../spotify_features_data/"):
        shutil.rmtree("../spotify_features_data/")

    def pull_data_with_dvc():
        cmd = [sys.executable, "-m", "dvc", "pull"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            st.write("Data pulled successfully!")
            st.write(result.stdout)
        else:
            st.write("Error pulling data!")
            st.write(result.stderr)

    # Use this function somewhere in your Streamlit app.
    pull_data_with_dvc()
    # os.system("dvc pull")

    df = pd.read_csv("../spotify_features_data/spotify_features_data.csv")

    st.title("Разведочный анализ данных о клиентах")

    st.header("Статистики признаков")

    descr = df.describe(include="all")

    col = st.selectbox("Выберите признак:", df.columns, key=1)

    if df[col].dtype == object:
        col_info = {}
        col_info["Number of rows"] = descr[col]["count"]
        col_info["Number of unique values"] = descr[col]["unique"]
        col_info["Top value"] = descr[col]["top"]
        col_info["Frequence of top value"] = descr[col]["freq"]
        info_df = pd.DataFrame(list(col_info.items()), columns=["description", "Value"])
        st.dataframe(info_df)
    elif df[col].dtype == float:
        col_info = {}
        col_info["Number of rows"] = descr[col]["count"]
        col_info["Mean value"] = descr[col]["mean"]
        col_info["Std value"] = descr[col]["std"]
        col_info["Min value"] = descr[col]["min"]
        col_info["Max value"] = descr[col]["max"]
        col_info["25% value"] = descr[col]["25%"]
        col_info["50% value"] = descr[col]["50%"]
        col_info["75% value"] = descr[col]["75%"]
        info_df = pd.DataFrame(list(col_info.items()), columns=["description", "Value"])
        st.dataframe(info_df)

    st.header("Пропущенные значения")

    gaps = df.isna().sum() + df.apply(lambda x: (x == " ") | (x == "")).sum()
    st.dataframe(
        pd.DataFrame(
            {
                "column": gaps[gaps != 0].index,
                "count of missing values": gaps[gaps != 0].values,
            }
        )
    )

    st.write(
        """
            Заменим пропуски в total_followers на 0.

            Заменим пропущенные album_name на непропущенные album_artists_names,

            track_artists_names на непропущенные album_artists_names,

            track_name на непропущенные album_name,

            оставшиеся пропуски заменим на пустую строку.
            """
    )

    df.loc[df["album_name"].isnull(), "album_name"] = df["album_artists_names"]
    df.loc[df["track_artists_names"].isnull(), "track_artists_names"] = df[
        "album_artists_names"
    ]
    df.loc[df["track_name"].isnull(), "track_name"] = df["album_name"]
    df.loc[df["album_artists_names"].isnull(), "album_artists_names"] = " "
    df.loc[df["track_artists_names"].isnull(), "track_artists_names"] = " "

    st.header("Ошибочные значения и зависимые признаки")

    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    dates_check = df["album_release_data"].apply(is_date)
    st.dataframe(df[~dates_check]["album_release_data"])

    st.write(
        """
            Заменим неправильные даты на медианные.
            """
    )

    df.loc[~dates_check, "album_release_data"] = df["album_release_data"].mode()

    st.dataframe(pd.DataFrame(df[["track_type", "type"]].value_counts()))
    st.write(
        """
            Видим полное совпадение у признаков track_type и type
            """
    )
    df.drop(["track_type", "type"], axis=1, inplace=True)

    st.header("Категориальные признаки")

    st.write(
        """
            Заменим album_type с помощью LabelEncoder.

            Сделаем таргет target_genres на базе genres с помощью LabelEncoder.

            Заменим булевый признак track_explicit на 0 и 1.

            Разделим признак album_release_data на признаки album_release_year, album_release_month, album_release_day и album_release_dayofweek.
            """
    )

    le = LabelEncoder()
    le.fit(df.album_type)
    ar1 = le.transform(df.album_type)
    df["album_type"] = ar1
    len(le.classes_)

    le = LabelEncoder()
    le.fit(df.genre)
    ar1 = le.transform(df.genre)
    df["target_genres"] = ar1
    len(le.classes_)

    df.track_explicit = df.track_explicit.replace({True: 1, False: 0})

    df["album_release_data_1"] = df["album_release_data"].apply(pd.to_datetime)

    df["album_release_year"] = df["album_release_data_1"].dt.year
    df["album_release_month"] = df["album_release_data_1"].dt.month
    df["album_release_day"] = df["album_release_data_1"].dt.day
    df["album_release_dayofweek"] = df["album_release_data_1"].dt.dayofweek

    df.drop(["album_release_data_1"], axis=1, inplace=True)

    st.header("Графики характеристик признаков")

    col1 = [
        "track_duration_ms",
        "track_explicit",
        "track_popularity",
        "danceability",
        "energy",
        "key",
        "loudness",
        "mode",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
        "album_type",
        "album_total_tracks",
        "duration_ms",
        "time_signature",
        "total_followers",
        "album_release_year",
        "album_release_month",
        "album_release_day",
        "album_release_dayofweek",
    ]

    st.subheader("Матрица корреляций")
    f, ax = plt.subplots(figsize=(20, 15))
    sns.heatmap(df[col1 + ["target_genres"]].corr(), ax=ax, annot=True)
    st.pyplot(f)

    st.subheader("Распределения признаков")

    col = st.selectbox("Выберите признак:", col1 + ["target_genres"], key=2)

    f, ax = plt.subplots()
    sns.set(rc={"figure.figsize": (7, 5)})
    sns.set_style("whitegrid")
    feature = col
    sns.histplot(data=df, x=feature).set_title(f"Распределение признака {col}")
    st.pyplot(f)

    st.subheader("График попарных распределений признаков")
    f1 = st.selectbox("Выберите первый признак:", col1 + ["target_genres"], key=3)
    f2 = st.selectbox("Выберите второй признак:", col1 + ["target_genres"], key=4)

    f = plt.figure(figsize=(7, 5))
    sns.scatterplot(x=df[f1], y=df[f2], data=df)
    plt.title(f"Попарное распределение {f1} и {f2}")
    plt.xlabel(f1)
    plt.ylabel(f2)
    st.pyplot(f)

    # st.subheader('График зависимости целевой переменной от признака')
    # f1 = st.selectbox("Выберите признак:", col1, key=5)

    # f = plt.figure(figsize=(7,5))
    # sns.histplot(data=df, x=f1, hue='target_genres', bins=40)
    # plt.xlabel('Целевая переменная жанр')
    # plt.ylabel(f1)
    # st.pyplot(f)


if __name__ == "__main__":
    eda_spotify_features()
