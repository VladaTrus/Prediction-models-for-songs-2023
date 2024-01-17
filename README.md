# Предсказательные модели для песен

**Команда:**

- Трус Владлена
- Прудникова Дарья
- Кириллов Никита

**Куратор:**

- Ершов Иван

## Описание проекта

Наш проект посвящен созданию предсказательных моделей для анализа музыки с
использованием методов обработки естественного языка (NLP) и глубокого обучения
(DL). Мы будем исследовать текстовые данные песен, а также аудиозаписи, чтобы
понять их характеристики и свойства, а затем попытаемся объединить полученные
модели в итоговую гибридную модель.

В качестве MVP планируется разработка веб-сервиса для автоматического
формирования плейлистов на основе этих моделей

## Этапы работы

1. **Сбор данных**: Сбор большой коллекции аудиозаписей различных жанров и
   стилей, а также метаданных о каждой композиции.

2. **Предобработка данных и разведочный анализ (EDA)**:

   - Проведем предварительную обработку аудиофайлов, включая извлечение
     признаков, а также обработку метаданных, таких как название песни и
     исполнитель, харатеристики песен
   - Подготовим .ipynb-файл с исследованием собранных данных
   - Выделить наиболее релевантные для дальнейшнего исследования фичи и при
     необходимости сгенерировать кастомные

3. **Применение ML-подходов**:

- Построение бейзлайн модели классификации жанров и подготовка полного
  ML-пайплайна
- Дальнейшая разработка различных моделей классического машинного обучения для
  анализа музыки, включая модели для распознавания жанра, настроения,
  идентификации инструментов/артистов и многие другие. Проведем валидацию
  моделей

4. **Применение DL-подходов**:

   - Поиск DL-решений для работы со звуком и текстовыми данными
   - Доработка и оптимизация моделей, а также тюнинг параметров и улучшение
     качества и скорости работы моделей.
   - Объединение моделей, использующих разные типы данных

5. **Разработка метрики схожести песен при использовании различных подходов**
   (пункт со звездочкой)

6. **Интеграция модели в веб-сервис**: Разработаем веб-сервис для конечных
   пользователей, которое позволит им воспользоваться нашими моделями для
   генерации плейлистов.

## Данные

Для нашего проекта мы будем использовать разнообразные наборы данных, включая:

- [API Spotify](https://developer.spotify.com/documentation/web-api) Для
  выгрузки метаданых, исполнителей и признаков песен Например: acousticness,
  danceability, energy, instrumentalness, key, tempo, mode, loudness,
  speechiness

- [Описание песен](https://www.kaggle.com/datasets/bricevergnou/spotify-recommendation)
  Готовый датасет с Kaggle

- [LastFM](https://www.last.fm/music/+free-music-downloads) Для выгрузки
  аудиотреков

---
