import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from dateutil.parser import parse
from sklearn.preprocessing import LabelEncoder
import os
import shutil
import sys
import subprocess

def eda_spotify_features():
    if os.path.exists('../spotify_features_data/'):
        shutil.rmtree('../spotify_features_data/')
    
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

    df = pd.read_csv('../spotify_features_data/spotify_features_data.csv')
    
    st.title('Разведочный анализ данных о клиентах')
    
    st.header('Статистики признаков')
    
    descr = df.describe(include='all')
    
    col = st.selectbox('Выберите признак:', df.columns, key=1)
    
    if df[col].dtype == object:
       col_info = {}
       col_info["Number of rows"] = descr[col]['count']
       col_info["Number of unique values"] = descr[col]['unique']
       col_info["Top value"] = descr[col]['top']
       col_info["Frequence of top value"] = descr[col]['freq']
       info_df = pd.DataFrame(list(col_info.items()), columns=['description', 'Value'])
       st.dataframe(info_df)
    elif df[col].dtype == float:  
       col_info = {}
       col_info["Number of rows"] = descr[col]['count']
       col_info["Mean value"] = descr[col]['mean']
       col_info["Std value"] = descr[col]['std']
       col_info["Min value"] = descr[col]['min']
       col_info["Max value"] = descr[col]['max']
       col_info["25% value"] = descr[col]['25%']
       col_info["50% value"] = descr[col]['50%']
       col_info["75% value"] = descr[col]['75%']
       info_df = pd.DataFrame(list(col_info.items()), columns=['description', 'Value'])
       st.dataframe(info_df)
    
    st.header('Пропущенные значения')
    
    gaps = df.isna().sum() + df.apply(lambda x : (x == ' ') | (x == '')).sum()
    st.dataframe(pd.DataFrame({'column': gaps[gaps != 0].index, 'count of missing values': gaps[gaps != 0].values}))
    
    st.write('''
            Заменим пропуски в total_followers на 0.
            
            Заменим пропущенные album_name на непропущенные album_artists_names,
            
            track_artists_names на непропущенные album_artists_names,
            
            track_name на непропущенные album_name,
    
            оставшиеся пропуски заменим на пустую строку.
            ''')
    
    df.loc[df["album_name"].isnull(), 'album_name'] = df["album_artists_names"]
    df.loc[df["track_artists_names"].isnull(), 'track_artists_names'] = df["album_artists_names"]
    df.loc[df["track_name"].isnull(), 'track_name'] = df["album_name"]
    df.loc[df["album_artists_names"].isnull(), 'album_artists_names'] = ' '
    df.loc[df["track_artists_names"].isnull(), 'track_artists_names'] = ' '
    
    st.header('Ошибочные значения и зависимые признаки')
    
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
    
    dates_check = df['album_release_data'].apply(is_date)
    st.dataframe(df[~dates_check]['album_release_data'])
    
    st.write('''
            Заменим неправильные даты на медианные.
            ''')
    
    df.loc[~dates_check, 'album_release_data'] = df['album_release_data'].mode()
    
    
    st.dataframe(pd.DataFrame(df[['track_type', 'type']].value_counts()))
    st.write('''
            Видим полное совпадение у признаков track_type и type
            ''')
    df.drop(['track_type', 'type'], axis=1, inplace=True)
    
    st.header('Категориальные признаки')
    
    st.write('''
            Заменим album_type с помощью LabelEncoder.
    
            Сделаем таргет target_genres на базе genres с помощью LabelEncoder.
            
            Заменим булевый признак track_explicit на 0 и 1.
            
            Разделим признак album_release_data на признаки album_release_year, album_release_month, album_release_day и album_release_dayofweek.
            ''')
    
    le = LabelEncoder()
    le.fit(df.album_type)
    ar1 = le.transform(df.album_type)
    df['album_type'] = ar1
    len(le.classes_)
    
    le = LabelEncoder()
    le.fit(df.genre)
    ar1 = le.transform(df.genre)
    df['target_genres'] = ar1
    len(le.classes_)
    
    df.track_explicit = df.track_explicit.replace({True: 1, False: 0})
    
    df['album_release_data_1'] = df['album_release_data'].apply(pd.to_datetime)
    
    df['album_release_year'] = df['album_release_data_1'].dt.year
    df['album_release_month'] = df['album_release_data_1'].dt.month
    df['album_release_day'] = df['album_release_data_1'].dt.day
    df['album_release_dayofweek'] = df['album_release_data_1'].dt.dayofweek
    
    df.drop(['album_release_data_1'], axis=1, inplace=True)
    
    st.header('Графики характеристик признаков')
    
    col1 = ['track_duration_ms', 'track_explicit',
           'track_popularity', 'danceability', 'energy', 'key', 'loudness',
           'mode', 'speechiness', 'acousticness', 'instrumentalness',
           'liveness', 'valence', 'tempo',
           'album_type', 'album_total_tracks', 'duration_ms', 'time_signature', 'total_followers',
           'album_release_year', 'album_release_month', 'album_release_day', 'album_release_dayofweek']
    
    st.subheader('Матрица корреляций')
    f, ax = plt.subplots(figsize=(20,15))
    sns.heatmap(df[col1 + ['target_genres']].corr(), ax=ax, annot=True)
    st.pyplot(f)
    
    st.subheader('Распределения признаков')
    
    col = st.selectbox('Выберите признак:', col1 + ['target_genres'], key=2)
    
    f, ax = plt.subplots()
    sns.set(rc={'figure.figsize':(7,5)})
    sns.set_style("whitegrid")
    feature = col
    sns.histplot(data=df, x=feature).set_title(f"Распределение признака {col}")
    st.pyplot(f)
    
    
    st.subheader('График попарных распределений признаков')
    f1 = st.selectbox("Выберите первый признак:", col1 + ['target_genres'], key=3)
    f2 = st.selectbox("Выберите второй признак:", col1 + ['target_genres'], key=4)
    
    f = plt.figure(figsize=(7,5))
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

    st.title('Разведочный анализ данных по текстам песен')
    DATA_PATH = '../spotify_features_data_temp'
    st.write('''
        На данный момент удалось достать 51280 треков. Из них 44641 и 6639 треков на английском и других языках.
        
        В дальнейшем работать будем только с английскими треками, а в разведочном анализе сравним характеристика по всем текстам
        ''')
    
    st.header('Распределение признака words_per_second')

    st.subheader('Треки на английском языке')
    st.image(f'{DATA_PATH}/distrib_eng.png', use_column_width='always')
    st.subheader('Треки на других языках')
    st.image(f'{DATA_PATH}/distrib_oth.png', use_column_width='always')

    st.write('''
        Распределение признака практически совпадает для текстов на разных языках
        ''')

    st.header('Самые "быстрые" и "медленные" жанры')
    st.write('''
        Оценка скорости жанров проводилась по принципу количество слов в тексте на секунду трека
        ''')
    st.subheader('Треки на английском языке')
    st.image(f'{DATA_PATH}/fastest_eng.png', use_column_width='always')
    st.subheader('Треки на других языках')
    st.image(f'{DATA_PATH}/fastest_oth.png', use_column_width='always')
    st.write('''
        Среди наиболее быстрых жанров в случае английских текстов можно выделить trap_cristiano, 
             который почти в три раза обгоняет ближайшего соседа. 
        В медленных жанров количество слов на секунду не превышает 0,01 слова в секунду. 
             Это могут быть почти инструментальные треки или даже жанры
    ''')

    st.header('По количеству слов в тексте')
    st.write('''
             Найдем жанры, выделяющиеся по количеству используемых слов в абсолютном значении
    ''')
    st.subheader('Треки на английском языке')
    st.image(f'{DATA_PATH}/most_least_words_eng.png', use_column_width='always')
    st.subheader('Треки на других языках')
    st.image(f'{DATA_PATH}/most_least_oth.png', use_column_width='always')
    st.write('''
            В треках на английском опять же выделается trap_cristiano, 
             а наименьшее число слов содержится во многих инструментальных жанрах
            В других языках подвиды hip hop'a занимают большую часть топа с большим числом слов, 
             а indie - с маленьким. Также по сравнению с английскими треками значение на порядок ниже (30 против 4)
    ''')

    st.header('Облаков слов')
    st.subheader('Треки на английском языке')
    st.image(f'{DATA_PATH}/Word_Cloud_eng.png')
    st.subheader('Треки на других языках')
    st.image(f'{DATA_PATH}/Word_Cloud_other.png')
    st.write('''
        В английских текстах песен чаще всего употребляются слова [know, love, got, yeah], 
             на облаке остальных языков можно заметить слова из испанского, немецкого и французских языков 
    ''')

    st.header('Артисты с наибольшим и наименьшим разнообразием слов')
    st.write('''
    Подсчет по среднему значению уникальных слов по артисту. Если в песне содержатся фиты, 
                песня отдельно учитывалась для каждого артиста
    ''')
    st.subheader('Артисты с наибольшим разнообразием слов')
    st.subheader('Треки на английском языке')
    st.image(f'{DATA_PATH}/most_unique_eng.png')
    st.subheader('Треки на других языках')
    st.image(f'{DATA_PATH}/most_unique_oth.png')
    st.subheader('Артисты с наименьшим разнообразием слов')
    st.subheader('Треки на английском языке') 
    st.image(f'{DATA_PATH}/least_unique_eng.png')
    st.subheader('Треки на других языках')
    st.image(f'{DATA_PATH}/least_unique_oth.png') 
     

if __name__ == "__main__":
    eda_spotify_features()
