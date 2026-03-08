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

## Быстрый старт

### Предварительные требования

- Python 3.9 или выше
- Telegram Bot Token (получить у [@BotFather](https://t.me/botfather))

### Установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/yourusername/telegram-shop-bot.git
   cd telegram-shop-bot
