import aiosqlite
import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

#CLASS
class OrderState(StatesGroup):
    waiting_for_address = State()
    waiting_for_phone = State()
    confirm_order = State()

#DEFS
async def add_sample_products():
    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM products')
        count = await cursor.fetchone()

        if count[0] == 0:
            products = [
                ("Ноутбук", "Мощный игровой ноутбук", 1500),
                ("Смартфон", "Последняя модель с отличной камерой", 800),
                ("Наушники", "Беспроводные с шумоподавлением", 200),
                ("Клавиатура", "Механическая с подсветкой", 100),
                ("Мышь", "Игровая с 6 кнопками", 50),
                ("Монитор", "4K 27 дюймов", 400),
                ("Веб-камера", "Full HD с микрофоном", 70),
                ("Микрофон", "Для стримов и подкастов", 120),
                ("Внешний диск", "1TB SSD", 150),
                ("Принтер", "Лазерный цветной", 300)
            ]
            await db.executemany(
                "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                products
            )
            await db.commit()

async def regist_user(telegram_id: int, username: str = None):
    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute(
            'SELECT id FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        user = await cursor.fetchone()

        if user is None:
            await db.execute(
                'INSERT INTO users (telegram_id, username) VALUES (?, ?)',
                (telegram_id, username)
            )
            await db.commit()


#DB
async def init_db():
    async with aiosqlite.connect('buyers.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            telegram_id INTEGER UNIQUE,
            username TEXT
        )
    ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            price INTEGER
        )
    ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS carts(
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS cart_items(
            id INTEGER PRIMARY KEY,
            cart_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cart_id) REFERENCES carts (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            address TEXT,
            phone TEXT,
            total_amount INTEGER,
            status TEXT DEFAULT 'новый',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            product_name TEXT,
            price INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')


#BOT
TOKEN = 'YOUR_TOKEN'

dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    telegram_id = message.from_user.id
    username = message.from_user.username

    await init_db()
    await regist_user(telegram_id, username)
    await add_sample_products()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="Корзина", callback_data="view_cart")],
        [InlineKeyboardButton(text='Заказы', callback_data='orders')]
    ])

    await message.answer(
        text=f'Приветствую, {message.from_user.first_name}!',
        reply_markup=keyboard
        )

@dp.callback_query(F.data == 'catalog')
async def first_catalog(callback: types.CallbackQuery):
    await show_catalog(callback, 0)

@dp.callback_query(F.data.startswith('catalog_'))
async def handle_pagination(callback: types.CallbackQuery):
    page = int(callback.data.split('_')[1])
    await show_catalog(callback, page)

async def show_catalog(callback: types.CallbackQuery, page: int):
    
    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute('SELECT COUNT(*) FROM products')
        total = await cursor.fetchone()
        total_products = total[0]

        cursor = await db.execute(
            'SELECT id, name, description, price FROM products LIMIT 1 OFFSET ?',
            (page,)
        )
        product = await cursor.fetchone()
        
        if product:
            product_id, name, description, price = product

            buttons = []
            
            if page > 0:
                buttons.append(InlineKeyboardButton(
                    text='Назад', 
                    callback_data=f'catalog_{page-1}'
                ))
            
            if page < total_products - 1:
                buttons.append(InlineKeyboardButton(
                    text='Вперед', 
                    callback_data=f'catalog_{page+1}'
                ))
            
            # Кнопка добавления в корзину
            add_button = [InlineKeyboardButton(
                text='Добавить в корзину', 
                callback_data=f'add_{product_id}'
            )]
            
            # Собираем клавиатуру
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[buttons, add_button]
            )
            
            await callback.message.edit_text(
                f"*{name}*\n\n{description}\n\nЦена: {price}₽\n\nТовар {page+1} из {total_products}",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

@dp.callback_query(F.data.startswith('add_'))
async def add_to_cart(callback: types.CallbackQuery):
    product_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id

    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute(
            'SELECT id FROM users WHERE telegram_id = ?',
            (user_id,)
        )
        user = await cursor.fetchone()
        user_db_id = user[0]
        
        cursor = await db.execute(
            'SELECT id FROM carts WHERE user_id = ?',
            (user_db_id,)
        )
        cart = await cursor.fetchone()
        
        if not cart:
            cursor = await db.execute(
                'INSERT INTO carts (user_id) VALUES (?)',
                (user_db_id,)
            )
            cart_id = cursor.lastrowid
        else:
            cart_id = cart[0]
        
        cursor = await db.execute(
            'SELECT id, quantity FROM cart_items WHERE cart_id = ? AND product_id = ?',
            (cart_id, product_id)
        )
        cart_item = await cursor.fetchone()
        
        if cart_item:
            await db.execute(
                'UPDATE cart_items SET quantity = quantity + 1 WHERE id = ?',
                (cart_item[0],)
            )
        else:
            await db.execute(
                'INSERT INTO cart_items (cart_id, product_id, quantity) VALUES (?, ?, 1)',
                (cart_id, product_id)
            )
        
        await db.commit()

    await callback.answer('Товар добавлен в корзину', show_alert=False)

@dp.callback_query(F.data == 'view_cart')
async def show_carts(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute('''
            SELECT p.name, p.price, ci.quantity 
            FROM cart_items ci
            JOIN products p ON ci.product_id = p.id
            JOIN carts c ON ci.cart_id = c.id
            JOIN users u ON c.user_id = u.id
            WHERE u.telegram_id = ?
        ''', (user_id,))
        items = await cursor.fetchall()

    if not items:
        await callback.message.edit_text('Корзина пуста')
        return 
    
    cart_text = "*Ваша корзина:*\n\n"
    total = 0
    
    for name, price, quantity in items:
        cart_text += f"• {name} x{quantity} - {price * quantity}₽\n"
        total += price * quantity
    
    cart_text += f"\n*Итого: {total}₽*"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оформить заказ", callback_data="checkout")],
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(
        cart_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == 'checkout')
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите адрес доставки:')
    await state.set_state(OrderState.waiting_for_address)

@dp.message(OrderState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer('Введите номер телефона:')
    await state.set_state(OrderState.waiting_for_phone)

@dp.message(OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)

    data = await state.get_data()
    address = data.get('address')
    phone = data.get('phone')

    text = f"*Проверьте данные заказа:*\n\n"
    text += f"Адрес: {address}\n"
    text += f"Телефон: {phone}\n\n"
    text += "Всё верно?"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='Да, оформить', callback_data='confirm_order'),
            InlineKeyboardButton(text='Нет, заново', callback_data='cancel_order')
        ]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')
    await state.set_state(OrderState.confirm_order)

@dp.callback_query(OrderState.confirm_order, F.data == "confirm_order")
async def confirm_order(callback: types.CallbackQuery, state: FSMContext):
    
    data = await state.get_data()
    address = data.get('address')
    phone = data.get('phone')
    
    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute(
            'SELECT id FROM users WHERE telegram_id = ?',
            (callback.from_user.id,)
        )
        user = await cursor.fetchone()
        user_id = user[0]
    
        cursor = await db.execute('''
            SELECT ci.product_id, p.name, p.price, ci.quantity 
            FROM cart_items ci
            JOIN carts c ON ci.cart_id = c.id
            JOIN products p ON ci.product_id = p.id
            JOIN users u ON c.user_id = u.id
            WHERE u.id = ?
        ''', (user_id,))
        cart_items = await cursor.fetchall()

        total_amount = sum(price * quantity for _, _, price, quantity in cart_items)
        
        cursor = await db.execute('''
            INSERT INTO orders (user_id, address, phone, total_amount, status)
            VALUES (?, ?, ?, ?, 'новый')
        ''', (user_id, address, phone, total_amount))

        order_id = cursor.lastrowid

        for product_id, name, price, quantity in cart_items:
            await db.execute('''
                INSERT INTO order_items (order_id, product_id, product_name, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, product_id, name, price, quantity))
        
        await db.execute('''
            DELETE FROM cart_items 
            WHERE cart_id = (SELECT id FROM carts WHERE user_id = ?)
        ''', (user_id,))

        await db.commit()

    # Отправляем уведомление админу (замените ADMIN_ID на реальный ID)
    ADMIN_ID = 'ADMIN_ID'
    await callback.bot.send_message(
        ADMIN_ID,
        f"*Новый заказ!*\n\n"
        f"Пользователь: @{callback.from_user.username}\n"
        f"Адрес: {address}\n"
        f"Телефон: {phone}\n"
        f"Сумма: {total_amount}₽",
        parse_mode="Markdown"
    )

    await callback.message.edit_text("Заказ оформлен! Скоро с вами свяжутся.")
    await state.clear()

@dp.callback_query(OrderState.confirm_order, F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Оформление отменено. Можете начать заново из корзины.")
    await state.clear()

@dp.callback_query(F.data == 'back_to_menu')
async def back_to_menu(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="Корзина", callback_data="view_cart")],
        [InlineKeyboardButton(text='Заказы', callback_data='orders')]
    ])
    
    await callback.message.edit_text(
        text=f'Главное меню:',
        reply_markup=keyboard
    )

@dp.callback_query(F.data == 'orders')
async def show_orders(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    async with aiosqlite.connect('buyers.db') as db:
        cursor = await db.execute('''
            SELECT id, total_amount, status, created_at 
            FROM orders 
            WHERE user_id = (SELECT id FROM users WHERE telegram_id = ?)
            ORDER BY created_at DESC
            LIMIT 5
        ''', (user_id,))
        orders = await cursor.fetchall()
    
    if not orders:
        await callback.message.edit_text("📭 У вас пока нет заказов")
        return
    
    text = "*Ваши последние заказы:*\n\n"
    for order_id, amount, status, date in orders:
        text += f"Заказ #{order_id}\n"
        text += f"Сумма: {amount}₽\n"
        text += f"Статус: {status}\n"
        text += f"Дата: {date[:10]}\n\n"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
