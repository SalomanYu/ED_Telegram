# ED_Telegram 
<i>v.1.0<i>

## Description
Данный репозиторий предназначен для хранения телеграм-ботов
с помощью которых стажеры-разработчики будут обучать наш алгоритм
по автоматическому выявлению дубликатов в списке навыков

На текущий момент в репозитории представлено два бота:
- Один для подтверждения корректности подобранной пары похожих навыков
- Второй для исправления грамматических ошибок, если они есть

[//]: # (ADd Image)
![](Data/img/pic1.jpg)

## Описание работы 
### 1. DuplicateRemoverBot

Первым делом стажер должен поработать с этим ботом, чтобы указать ему
на одинаковые навыки, от которых следует избавиться в нашей итоговой БД.
Благодаря этому, мы уменьшим количество проверок для второго бота, так
как ему придется работать с укороченной базой.

### Algorithm DuplicateRemoverBot
1. Подготовить для работы бота стартовый набор данных
- xlsx-таблица, в которой будет полный список "грязных" навыков

| id  | name                 |
|-----|----------------------|
| 1   | Усидчивость          |
| 2   | Python3              |
| ... | ...........          |
| n   | Ведение документации |

- SQL-таблица, содержащая список потенциальных дубликатов вида

| id  | original        | duplicate                | percent |
|-----|-----------------|--------------------------|-----|
| 32  | грамотная речь  | грамотная устная и письменная речь | 100 |
| 45  | ориентация на результат | нацеленность на результат| 79  |
| 371 | пользователь пк | отличное знание пк       | 99  |

<b>original</b> - наименование навыка, с которым сравнивается второй навык. Если
второй навык действительно окажется дубликатом,
то дубликат будет удален, а оригинал оставлен в БД <br/>
<b>id</b> - номер duplicate, благодаря этому значению 
мы можем точно удалить нужный навык <br/>
<b>percent</b> - процент схожести двух навыков
