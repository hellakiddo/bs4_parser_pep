![Python](https://img.shields.io/badge/python-%233776AB.svg?style=for-the-badge&logo=python&logoColor=white)


# Парсер документации Python

## Технологии:
### Beautiful Soup
### Python
### 

Для работы проекта 

Клонируем репозиторий:
```python
git@github.com:Amir800S/bs4_parser_pep.git
```
Заходим в рабочую директорию 
```python
cd src/
```
## Режимы работы парсера 
### whats-new - выдает список изменений в версиях Python
```python
python main.py whats-new [аргумент]
```
### download - скачивает архив с документацией Python в PDF.
```python
python main.py download [аргумент]
```
### pep - выводит список статусов pep и их количество в статусе.
```python
python main.py pep [аргумент]
```
## Аргументы 
### -h - информация о командах.
```python
python main.py -h
```
### -c - очистка кеша перед.
```python
python main.py [режим парсера] -c
```
### -o {pretty,file}
pretty - выводит данные в командной строке в таблице
file - сохраняет данные в csv по пути ./results/
```python
python main.py [режим парсера] -o file
```

### Автор: [Сосламбеков Амир](https://github.com/Amir800S)