# Настройка окружения (в папке с проектом)
```shell
pip install poetry
poetry install
poetry update
```

# Запуск
```shell
poetry run python main.py [-h] [--config CONFIG] [--destination DESTINATION] [--log LOG] input
```

- Посмотреть справку можно через аргумент `-h` / `--help`
- Требуется версия python 3.10.x
- Проверить версию можно с помощью `python -V`

# Описание конфига
## Глобальная секция

> Глобальные настройки

| Параметр  | Назначение                            |
|:----------|:--------------------------------------|
| separator | Разделитель.                          |
| field     | Поля, в которых производится поиск.   |
| extension | Расширение результирующего файла(ов). |

> Пример

```toml
separator = "-fides_delim-"
field = [1, 2]
extension = "weights"
```

## Секция rule
> Настройка ключевого слова

| Параметр | Назначение                                |
|:--------:|:------------------------------------------|
|   mode   | Режим обработки текста как в grep         |
|   text   | Текст или регулярное выражение для поиска |

## Секция suffix

| Параметр | Назначение                                    |
|:--------:|:----------------------------------------------|
|   file   | Имя файла с суффиксами                        |
| distance | Дистанция поиска относительно ключевого слова |

> Пример

```toml
[suffix."regexp"]
weight = 1
distance.right = 6
```

## Параметр distance
Дистанция указывается в следуюющем формате:
```
distance.[left/right/default]
```

- `distance.default` задает одновременно `left` и `right`
- `distance.[left/right]` может частично или полностью перекрыть `default`

Пример
```toml
# left = right
distance.default = 7
# Частично перекрывает дистанцию по умолчанию
distance.left = 5
```

# Коды ошибок

| Код | Описание                                                                      |
|:---:|:------------------------------------------------------------------------------|
|  1  | Файл / папка не существуют.                                                   |
|  2  | В конфиге не найдена секция `rule`                                            |
|  3  | В конфиге не найден глобальный параметр `separator`                           |
|  4  | Глобальный параметр конфигурации `field` должен быть числом или списком чисел |
|  5  | В конфиге не найден глобальный параметр `field`                               |
|  7  | Параметр конфигурации `distance` в секции `suffix` не найден                  |
|  8  | Параметр конфигурации `text` в секции `rule` не найден                        |
|  9  | В файле конфигурации не указан обязательный параметр field в секции domains   |
