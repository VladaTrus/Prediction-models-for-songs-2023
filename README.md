# Предсказательные модели для песен

**Команда:**
- Трус Владлена
- Прудникова Дарья
- Кириллов Никита

**Куратор:**
- Ершов Иван

## Описание проекта

  Наш проект посвящен созданию предсказательных моделей для анализа музыки с использованием методов обработки естественного языка (NLP) и глубокого обучения (DL). 
Мы будем исследовать текстовые данные песен, а также аудиозаписи, чтобы понять их характеристики и свойства, а затем попытаемся объединить полученные модели в итоговую гибридную модель.

В качестве MVP планируется разработка веб-сервиса для автоматического формирования плейлистов на основе этих моделей

## Этапы работы

1. **Сбор данных**: Сбор большой коллекции аудиозаписей различных жанров и стилей, а также метаданных о каждой композиции. 

2. **Предобработка данных и разведочный анализ (EDA)**:
   - Проведем предварительную обработку аудиофайлов, включая извлечение признаков, а также обработку метаданных, таких как название песни и исполнитель, харатеристики песен
   - Подготовим .ipynb-файл с исследованием собранных данных
   - Выделить наиболее релевантные для дальнейшнего исследования фичи и при необходимости сгенерировать кастомные

4. **Применение ML-подходов**:

  - Построение бейзлайн модели классификации жанров и подготовка полного ML-пайплайна  
  - Дальнейшая разработка различных моделей классического машинного обучения для анализа музыки, включая модели для распознавания жанра, настроения, идентификации инструментов/артистов и многие другие. Проведем валидацию моделей

4. **Применение DL-подходов**:

   - Поиск DL-решений для работы со звуком и текстовыми данными
   - Доработка и оптимизация моделей, а также тюнинг параметров и улучшение качества и скорости работы моделей.
   - Объединение моделей, использующих разные типы данных

5. **Разработка метрики схожести песен при использовании различных подходов** (пункт со звездочкой)

6. **Интеграция модели в веб-сервис**: Разработаем веб-сервис для конечных пользователей, которое позволит им воспользоваться нашими моделями для генерации плейлистов.

## Данные (ДОПИСАТЬ!!)

Для нашего проекта мы будем использовать разнообразные наборы данных с аудиозаписями, включая:

API Spotify

Данные с Kaggle: 

- [название_набора_данных_1](ссылка_на_набор_данных_1)
- [название_набора_данных_2](ссылка_на_набор_данных_2)
- [название_набора_данных_3](ссылка_на_набор_данных_3)

---

