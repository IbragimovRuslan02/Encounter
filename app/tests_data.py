"""Каталог психологических тестов: вопросы, варианты, шкалы результатов.

Каждый тест содержит:
- name:        название
- description: краткое описание
- icon:        эмодзи-иконка
- questions:   список вопросов; у каждого — text и список options с type
- results:     словарь {type: человекочитаемая формулировка результата}
"""

TESTS: dict = {

    # ───────────────── 1. Тип мышления ─────────────────
    "thinking": {
        "name": "Какой твой тип мышления?",
        "description": "Логика, интуиция, креатив или практика — что сильнее?",
        "icon": "🧠",
        "questions": [
            {"text": "Когда есть сложная задача, ты чаще…", "options": [
                {"text": "Разбираю по шагам и анализирую", "type": "analytical"},
                {"text": "Ищу необычную идею", "type": "creative"},
                {"text": "Доверяю внутреннему чувству", "type": "intuitive"},
                {"text": "Делаю так, как работает на практике", "type": "practical"},
            ]},
            {"text": "Что важнее в решении?", "options": [
                {"text": "Точность и доказательность", "type": "analytical"},
                {"text": "Оригинальность подхода", "type": "creative"},
                {"text": "Ощущение правильности", "type": "intuitive"},
                {"text": "Быстрый рабочий результат", "type": "practical"},
            ]},
            {"text": "Тебя больше привлекает…", "options": [
                {"text": "Данные, цифры, логика", "type": "analytical"},
                {"text": "Идеи, визуал, творчество", "type": "creative"},
                {"text": "Люди, эмоции, смыслы", "type": "intuitive"},
                {"text": "Инструменты, процессы, практика", "type": "practical"},
            ]},
            {"text": "В споре ты обычно…", "options": [
                {"text": "Опираюсь на факты", "type": "analytical"},
                {"text": "Нахожу нестандартный аргумент", "type": "creative"},
                {"text": "Чувствую, где правда по контексту", "type": "intuitive"},
                {"text": "Предлагаю конкретное решение", "type": "practical"},
            ]},
            {"text": "Когда учишься новому, ты…", "options": [
                {"text": "Сначала понимаю теорию", "type": "analytical"},
                {"text": "Учусь через эксперименты", "type": "creative"},
                {"text": "Ловлю суть на интуиции", "type": "intuitive"},
                {"text": "Сразу практикую на задачах", "type": "practical"},
            ]},
            {"text": "Если план меняется в последний момент…", "options": [
                {"text": "Пересчитываю и перестраиваю план", "type": "analytical"},
                {"text": "Использую шанс придумать лучше", "type": "creative"},
                {"text": "Слушаю ощущение, куда идти", "type": "intuitive"},
                {"text": "Беру ближайший рабочий вариант", "type": "practical"},
            ]},
            {"text": "Тебе проще объяснить мысль через…", "options": [
                {"text": "Схему/структуру", "type": "analytical"},
                {"text": "Метафору/пример", "type": "creative"},
                {"text": "Ощущение/настроение", "type": "intuitive"},
                {"text": "Инструкцию/шаги", "type": "practical"},
            ]},
            {"text": "При выборе покупки ты…", "options": [
                {"text": "Сравниваю характеристики", "type": "analytical"},
                {"text": "Выбираю то, что вдохновляет", "type": "creative"},
                {"text": "Беру то, что «моё» по ощущению", "type": "intuitive"},
                {"text": "Беру то, что точно пригодится", "type": "practical"},
            ]},
            {"text": "Когда видишь проблему, ты…", "options": [
                {"text": "Ищу первопричину", "type": "analytical"},
                {"text": "Вижу несколько альтернатив", "type": "creative"},
                {"text": "Чувствую скрытый контекст", "type": "intuitive"},
                {"text": "Сразу приступаю к исправлению", "type": "practical"},
            ]},
            {"text": "В команде ты чаще…", "options": [
                {"text": "Систематизирую и считаю", "type": "analytical"},
                {"text": "Генерю идеи", "type": "creative"},
                {"text": "Чувствую людей и атмосферу", "type": "intuitive"},
                {"text": "Закрываю задачи руками", "type": "practical"},
            ]},
            {"text": "Твоя сильная сторона — это…", "options": [
                {"text": "Логика и структурность", "type": "analytical"},
                {"text": "Воображение и креатив", "type": "creative"},
                {"text": "Интуиция и эмпатия", "type": "intuitive"},
                {"text": "Эффективность и действие", "type": "practical"},
            ]},
            {"text": "Когда читаешь материал, ты…", "options": [
                {"text": "Выделяю тезисы и факты", "type": "analytical"},
                {"text": "Ищу новые идеи и связи", "type": "creative"},
                {"text": "Чувствую общий смысл", "type": "intuitive"},
                {"text": "Ищу применимость", "type": "practical"},
            ]},
            {"text": "Сложные эмоции ты осмысливаешь через…", "options": [
                {"text": "Анализ причин", "type": "analytical"},
                {"text": "Творчество/самовыражение", "type": "creative"},
                {"text": "Интуитивное проживание", "type": "intuitive"},
                {"text": "Действия и режим", "type": "practical"},
            ]},
            {"text": "Если нужно выбрать между двумя вариантами…", "options": [
                {"text": "Сравню объективные критерии", "type": "analytical"},
                {"text": "Выберу более интересный", "type": "creative"},
                {"text": "Выберу то, что откликается", "type": "intuitive"},
                {"text": "Выберу более полезный", "type": "practical"},
            ]},
            {"text": "Тебе комфортнее работать, когда…", "options": [
                {"text": "Есть чёткая логика и правила", "type": "analytical"},
                {"text": "Есть свобода придумывать", "type": "creative"},
                {"text": "Есть смысл и атмосфера", "type": "intuitive"},
                {"text": "Есть конкретная цель и дедлайн", "type": "practical"},
            ]},
        ],
        "results": {
            "analytical": "Аналитический склад ума",
            "creative":   "Креативное мышление",
            "intuitive":  "Интуитивное мышление",
            "practical":  "Практичный подход",
        },
    },

    # ───────────────── 2. Стиль одежды ─────────────────
    "style": {
        "name": "Какой твой стиль одежды?",
        "description": "Casual, Classic, Trendy или Avant‑garde.",
        "icon": "👔",
        "questions": [
            {"text": "Главный критерий выбора одежды:", "options": [
                {"text": "Удобство", "type": "casual"},
                {"text": "Элегантность", "type": "classic"},
                {"text": "Тренды", "type": "trendy"},
                {"text": "Самовыражение", "type": "avant"},
            ]},
            {"text": "Твой образ ближе к…", "options": [
                {"text": "База/джинсы", "type": "casual"},
                {"text": "Минимализм/классика", "type": "classic"},
                {"text": "Яркие сочетания", "type": "trendy"},
                {"text": "Эксперименты", "type": "avant"},
            ]},
            {"text": "Аксессуары — это…", "options": [
                {"text": "Минимум", "type": "casual"},
                {"text": "Деталь статуса", "type": "classic"},
                {"text": "Часть тренда", "type": "trendy"},
                {"text": "Главный акцент", "type": "avant"},
            ]},
            {"text": "Твои любимые цвета в одежде:", "options": [
                {"text": "Спокойные нейтральные", "type": "casual"},
                {"text": "Чёрный/белый/тёмно-синий", "type": "classic"},
                {"text": "Сезонные модные оттенки", "type": "trendy"},
                {"text": "Контрасты и необычные сочетания", "type": "avant"},
            ]},
            {"text": "Выбор обуви:", "options": [
                {"text": "Удобные и проверенные модели", "type": "casual"},
                {"text": "Качественная классика", "type": "classic"},
                {"text": "Что носят все сейчас", "type": "trendy"},
                {"text": "Необычные коллаборации", "type": "avant"},
            ]},
            {"text": "Гардероб ближе к идее…", "options": [
                {"text": "10 вещей на все случаи", "type": "casual"},
                {"text": "Капсула, всё сочетается", "type": "classic"},
                {"text": "Много новинок сезона", "type": "trendy"},
                {"text": "Уникальные находки", "type": "avant"},
            ]},
            {"text": "Если пригласили на мероприятие…", "options": [
                {"text": "Оденусь как обычно", "type": "casual"},
                {"text": "Выберу строгий костюм", "type": "classic"},
                {"text": "Посмотрю тренды и подберу", "type": "trendy"},
                {"text": "Сделаю яркий образ", "type": "avant"},
            ]},
            {"text": "Отношение к брендам:", "options": [
                {"text": "Мне всё равно", "type": "casual"},
                {"text": "Ценю качество и репутацию", "type": "classic"},
                {"text": "Ношу то, что популярно", "type": "trendy"},
                {"text": "Ищу нишевые марки", "type": "avant"},
            ]},
            {"text": "Если одежда рвётся…", "options": [
                {"text": "Зашью/заменю на похожую", "type": "casual"},
                {"text": "Куплю такую же модель", "type": "classic"},
                {"text": "Возьму что-то поновее", "type": "trendy"},
                {"text": "Сделаю фишку из повреждения", "type": "avant"},
            ]},
            {"text": "В одежде важнее…", "options": [
                {"text": "Чтобы было удобно весь день", "type": "casual"},
                {"text": "Чтобы выглядело статусно", "type": "classic"},
                {"text": "Чтобы соответствовать сезону", "type": "trendy"},
                {"text": "Чтобы выделяться", "type": "avant"},
            ]},
            {"text": "Где покупаешь одежду?", "options": [
                {"text": "Базовые магазины", "type": "casual"},
                {"text": "Классические бутики", "type": "classic"},
                {"text": "ТЦ, новые коллекции", "type": "trendy"},
                {"text": "Секонд-хенд/малые бренды", "type": "avant"},
            ]},
            {"text": "Идеальный гардероб — это…", "options": [
                {"text": "Минимум и универсальность", "type": "casual"},
                {"text": "Качество и долговечность", "type": "classic"},
                {"text": "Актуальность и обновления", "type": "trendy"},
                {"text": "Самовыражение и характер", "type": "avant"},
            ]},
            {"text": "Если бы был дресс-код…", "options": [
                {"text": "Выбрал бы комфортное", "type": "casual"},
                {"text": "Идеально по правилам", "type": "classic"},
                {"text": "Стилём выделился", "type": "trendy"},
                {"text": "Превратил в перформанс", "type": "avant"},
            ]},
            {"text": "Одежда для тебя — это…", "options": [
                {"text": "Фон", "type": "casual"},
                {"text": "Инвестиция", "type": "classic"},
                {"text": "Способ быть в теме", "type": "trendy"},
                {"text": "Искусство", "type": "avant"},
            ]},
            {"text": "Цвет одежды чаще…", "options": [
                {"text": "Серый/синий/чёрный", "type": "casual"},
                {"text": "Тёмная палитра", "type": "classic"},
                {"text": "Сезонный акцент", "type": "trendy"},
                {"text": "Яркий микс", "type": "avant"},
            ]},
        ],
        "results": {
            "casual":  "Casual — комфорт прежде всего",
            "classic": "Classic — элегантность и статус",
            "trendy":  "Trendy — всегда в тренде",
            "avant":   "Avant‑garde — выделяешься из толпы",
        },
    },

    # ───────────────── 3. Карьера ─────────────────
    "career": {
        "name": "Какое направление карьеры тебе подходит?",
        "description": "Корпорация, творчество, фриланс или своё дело.",
        "icon": "💼",
        "questions": [
            {"text": "Что для тебя важнее в работе?", "options": [
                {"text": "Стабильность", "type": "corporate"},
                {"text": "Самовыражение", "type": "creative"},
                {"text": "Свобода графика", "type": "freelance"},
                {"text": "Влияние и рост", "type": "entrepreneur"},
            ]},
            {"text": "Какой ритм ближе?", "options": [
                {"text": "План/процессы", "type": "corporate"},
                {"text": "Вдохновение/проекты", "type": "creative"},
                {"text": "Свой темп", "type": "freelance"},
                {"text": "Быстрый рост", "type": "entrepreneur"},
            ]},
            {"text": "Где хочешь работать через 5 лет?", "options": [
                {"text": "Сильная компания", "type": "corporate"},
                {"text": "Студия/продакшн", "type": "creative"},
                {"text": "Удалённо", "type": "freelance"},
                {"text": "Своя компания", "type": "entrepreneur"},
            ]},
            {"text": "Что пугает больше?", "options": [
                {"text": "Хаос", "type": "corporate"},
                {"text": "Рутина", "type": "creative"},
                {"text": "Нестабильный доход", "type": "freelance"},
                {"text": "Большая ответственность", "type": "entrepreneur"},
            ]},
            {"text": "Где видишь команду?", "options": [
                {"text": "Коллеги в офисе", "type": "corporate"},
                {"text": "Творческая команда", "type": "creative"},
                {"text": "Партнёры онлайн", "type": "freelance"},
                {"text": "Свои люди в команде", "type": "entrepreneur"},
            ]},
            {"text": "Откуда ждёшь главный доход?", "options": [
                {"text": "Зарплата/бонусы", "type": "corporate"},
                {"text": "Проекты/гонорары", "type": "creative"},
                {"text": "Заказы", "type": "freelance"},
                {"text": "Прибыль бизнеса", "type": "entrepreneur"},
            ]},
            {"text": "Что важнее в задаче?", "options": [
                {"text": "Чёткость ТЗ", "type": "corporate"},
                {"text": "Простор для идеи", "type": "creative"},
                {"text": "Гибкость сроков", "type": "freelance"},
                {"text": "Большой результат", "type": "entrepreneur"},
            ]},
            {"text": "Кто твой идеальный клиент/начальник?", "options": [
                {"text": "Корпоративный", "type": "corporate"},
                {"text": "Креативный директор", "type": "creative"},
                {"text": "Заказчик проектов", "type": "freelance"},
                {"text": "Инвестор/рынок", "type": "entrepreneur"},
            ]},
            {"text": "Сколько риска готов на старте?", "options": [
                {"text": "Минимум", "type": "corporate"},
                {"text": "Средний", "type": "creative"},
                {"text": "Умеренный", "type": "freelance"},
                {"text": "Высокий", "type": "entrepreneur"},
            ]},
            {"text": "Что важнее в команде?", "options": [
                {"text": "Структура", "type": "corporate"},
                {"text": "Креатив", "type": "creative"},
                {"text": "Автономия", "type": "freelance"},
                {"text": "Видение", "type": "entrepreneur"},
            ]},
            {"text": "Где ты учишься эффективнее?", "options": [
                {"text": "Тренинги компании", "type": "corporate"},
                {"text": "Мастер-классы", "type": "creative"},
                {"text": "На своих проектах", "type": "freelance"},
                {"text": "У наставника/в жизни", "type": "entrepreneur"},
            ]},
            {"text": "К чему стремишься через 3 года?", "options": [
                {"text": "Рост должности", "type": "corporate"},
                {"text": "Сильное портфолио", "type": "creative"},
                {"text": "Поток заказов", "type": "freelance"},
                {"text": "Свой продукт/команда", "type": "entrepreneur"},
            ]},
            {"text": "Твой подход к обучению:", "options": [
                {"text": "Курсы/сертификации", "type": "corporate"},
                {"text": "Насмотренность/практика", "type": "creative"},
                {"text": "Только нужное мне", "type": "freelance"},
                {"text": "Учусь для роста", "type": "entrepreneur"},
            ]},
            {"text": "Какой формат ближе на старте?", "options": [
                {"text": "Компания/отдел", "type": "corporate"},
                {"text": "Студия/агентство", "type": "creative"},
                {"text": "Фриланс", "type": "freelance"},
                {"text": "Стартап", "type": "entrepreneur"},
            ]},
            {"text": "Что тебя вдохновляет в работе?", "options": [
                {"text": "Карьерная лестница", "type": "corporate"},
                {"text": "Признание идей", "type": "creative"},
                {"text": "Свобода выбора", "type": "freelance"},
                {"text": "Стратегия", "type": "entrepreneur"},
            ]},
        ],
        "results": {
            "corporate":    "Подходит корпоративная среда",
            "creative":     "Подходит творческая профессия",
            "freelance":    "Подходит фриланс/удалёнка",
            "entrepreneur": "Подходит предпринимательство",
        },
    },
}
