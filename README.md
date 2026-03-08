# Telegram Shop Bot

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Aiogram Version](https://img.shields.io/badge/aiogram-3.x-green.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Бот-магазин с корзиной покупок для Telegram. Позволяет просматривать каталог товаров, добавлять их в корзину и оформлять заказы.

## Возможности

- Просмотр каталога товаров с пагинацией
- Управление корзиной (добавление/удаление товаров)
- Оформление заказов с указанием адреса и телефона
- История заказов пользователя
- Уведомления администратора о новых заказах
- Хранение данных в SQLite

## Структура базы данных

## Структура базы данных

### users
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор пользователя |
| telegram_id | INTEGER UNIQUE | ID пользователя в Telegram |
| username | TEXT | Имя пользователя (опционально) |

### products
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор товара |
| name | TEXT | Название товара |
| description | TEXT | Описание товара |
| price | INTEGER | Цена товара |

### carts
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор корзины |
| user_id | INTEGER | ID пользователя (внешний ключ) |

### cart_items
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор записи |
| cart_id | INTEGER | ID корзины (внешний ключ) |
| product_id | INTEGER | ID товара (внешний ключ) |
| quantity | INTEGER | Количество товара |
| added_at | TIMESTAMP | Дата добавления |

### orders
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор заказа |
| user_id | INTEGER | ID пользователя (внешний ключ) |
| address | TEXT | Адрес доставки |
| phone | TEXT | Номер телефона |
| total_amount | INTEGER | Общая сумма заказа |
| status | TEXT | Статус заказа |
| created_at | TIMESTAMP | Дата создания |

### order_items
| Поле | Тип | Описание |
|------|-----|----------|
| id | INTEGER PRIMARY KEY | Уникальный идентификатор записи |
| order_id | INTEGER | ID заказа (внешний ключ) |
| product_id | INTEGER | ID товара (внешний ключ) |
| product_name | TEXT | Название товара |
| price | INTEGER | Цена товара |
| quantity | INTEGER | Количество товара |

### Предварительные требования

- Python 3.9 или выше
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))

### Установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/yourusername/telegram-shop-bot.git
   cd telegram-shop-bot
