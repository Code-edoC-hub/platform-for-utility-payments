from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import re
import random
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'database.db'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

translations = {
    'en': {
        'title': 'Interactive Online Utility Payment',
        'description': 'Welcome to the online platform for convenient payment of your utility bills.',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'username': 'Username',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'submit': 'Submit',
        'dashboard': 'Dashboard',
        'welcome_user': 'Welcome,',
        'bills': 'Your Utility Bills',
        'amount': 'Amount',
        'due_date': 'Due Date',
        'status': 'Status',
        'paid': 'Paid',
        'unpaid': 'Unpaid',
        'pay': 'Pay',
        'payment_history': 'Payment History',
        'date': 'Date',
        'language': 'Language',
        'change_lang': 'Change Language',
        'registration': 'Registration',
        'error_user_exists': 'Username already exists',
        'error_password_mismatch': 'Passwords do not match',
        'error_invalid_credentials': 'Invalid username or password',
        'payment_success': 'Payment successful',
        'pay_bill': 'Pay Bill',
        'no_payments': 'No payments made yet.',
        'home': 'Home',
        'news_title_1': 'Electricity Price Increase',
        'news_content_1': 'Starting next month, the electricity tariff will increase by 5%, affecting all households.',
        'news_title_2': 'New Payment Methods',
        'news_content_2': 'We have introduced payments via popular mobile wallets for your convenience.',
        'news_title_3': 'Scheduled Maintenance',
        'news_content_3': 'Our platform will undergo maintenance on the 20th. Please plan your payments accordingly.',
        'news_title_4': 'New Mobile App',
        'news_content_4': 'We are excited to announce the launch of our new mobile application! Now you can manage your utility payments on the go.',
        'select_language': 'Select Language',
        'uzbek': 'Uzbek',
        'russian': 'Russian',
        'english': 'English',
        'passport_number': 'Passport Number & Series',
        'phone_number': 'Phone Number',
        'email': 'Email (optional)',
        'water_supply': 'Water Supply',
        'electricity': 'Electricity',
        'gas_supply': 'Gas Supply',
        'sewage': 'Sewage',
        'heating': 'Heating',
        'waste_disposal': 'Waste Disposal',
        'current_month_info': 'Current Month Information',
        'consumption': 'Consumption',
        'tariff': 'Tariff',
        'total_amount': 'Total Amount',
        'select_month': 'Select Month',
        'select_year': 'Select Year',
        'view': 'View',
        'january': 'January',
        'february': 'February',
        'march': 'March',
        'april': 'April',
        'may': 'May',
        'june': 'June',
        'july': 'July',
        'august': 'August',
        'september': 'September',
        'october': 'October',
        'november': 'November',
        'december': 'December',
        'last_paid_receipts': 'Last Paid Receipts',
        'receipt_number': 'Receipt Number',
        'payment_date': 'Payment Date',
        'login_as_staff': 'Login as Staff',
        'login_as_user': 'Login as User',
        'staff_key': 'Staff Key',
        'login_another_way': 'Login Another Way',
        'choose_auth_method': 'Choose Authentication Method',
        'service_not_connected': 'This service is not yet connected by the student',
        'username_requirements': 'Username must be 3-20 characters long and contain only letters, numbers, and underscores',
        'password_requirements': 'Password must be at least 8 characters long and contain both letters and numbers',
        'passport_requirements': 'Passport number must be 2 uppercase letters followed by 7 digits',
        'phone_requirements': 'Phone number must start with +998 followed by 9 digits',
        'username_error': 'Invalid username format',
        'password_error': 'Invalid password format',
        'password_mismatch': 'Passwords do not match',
        'passport_error': 'Invalid passport number format',
        'phone_error': 'Invalid phone number format',
        'email_error': 'Invalid email format',
        'registration_success': 'Registration successful! Please log in.',
        'username_exists': 'Username already exists',
        'please_correct_errors': 'Please correct the errors in the form',
        'admin_dashboard': 'Admin Dashboard',
        'enter_username': 'Enter username',
        'search_user': 'Search User',
        'user_found': 'User found in database',
        'user_not_found': 'User not found in database',
        'generate_receipts': 'Generate Receipts',
        'payment_for': 'Payment For',
        'show_users': 'Show Users',
        'hide_users': 'Hide Users',
        'full_name': 'Full Name',
        'address': 'Address',
        'account_number': 'Account Number',
        'save_changes': 'Save Changes',
        'housing_type': 'Housing Type',
        'registered': 'Registered',
        'last_login': 'Last Login',
        'notifications': 'Notifications'
    },
    'ru': {
        'title': 'Интерактивная онлайн-оплата коммунальных услуг ArtPay',
        'headword': 'Интерактивная онлайн-оплата коммунальных услуг',
        'description': 'Добро пожаловать на онлайн-платформу для удобной оплаты ваших коммунальных услуг.',
        'login': 'Войти',
        'register': 'Регистрация',
        'logout': 'Выйти',
        'username': 'Имя пользователя',
        'password': 'Пароль',
        'confirm_password': 'Подтвердите пароль',
        'submit': 'Отправить',
        'dashboard': 'Личный кабинет',
        'personal_account': 'Личный кабинет',
        'payments': 'Платежи',
        'welcome_user': 'Добро пожаловать,',
        'bills': 'Ваши коммунальные начисления',
        'amount': 'Сумма',
        'due_date': 'Срок оплаты',
        'status': 'Статус',
        'paid': 'Оплачено',
        'unpaid': 'Не оплачено',
        'pay': 'Оплатить',
        'payment_history': 'История платежей',
        'date': 'Дата',
        'language': 'Язык',
        'change_lang': 'Сменить язык',
        'registration': 'Регистрация',
        'error_user_exists': 'Пользователь с таким именем уже существует',
        'error_password_mismatch': 'Пароли не совпадают',
        'error_invalid_credentials': 'Неверное имя пользователя или пароль',
        'payment_success': 'Платеж успешно выполнен',
        'pay_bill': 'Оплатить счет',
        'no_payments': 'Платежи еще не производились.',
        'home': 'Главная',
        'news_title_1': 'Повышение тарифа на электроэнергию',
        'news_content_1': '⚠️ Внимание! Изменение тарифа на электроэнергию\n\nУважаемые пользователи!\n\nСо следующего месяца произойдёт плановое повышение тарифа на электроэнергию.\n\nИзменение составит +5% и затронет все категории домохозяйств без исключения.\n\nЭто повышение связано с увеличением себестоимости производства и поставки электроэнергии, а также необходимостью модернизации инфраструктуры энергоснабжения.\n\nМы рекомендуем вам заранее ознакомиться с новыми тарифами в вашем личном кабинете и, при необходимости, скорректировать свои потребительские привычки, чтобы избежать резкого увеличения расходов.\n\nСпасибо за понимание и сотрудничество.',
        'news_title_2': 'Новые способы оплаты',
        'news_content_2': '💡 Мы постоянно работаем над тем, чтобы сделать оплату коммунальных услуг максимально удобной и быстрой для наших пользователей. 📱 Теперь вы можете оплачивать счета не только с помощью банковских карт, но и через популярные мобильные кошельки:💳 Click💸 Payme📲 Apelsin💼 Uzcard/MasterCard через мобильные приложения🏦 Прямые переводы через онлайн-банкинг🎯 Эти способы оплаты позволяют производить транзакции всего за несколько кликов, без очередей и бумажной волокиты.⏰ Все платежи обрабатываются мгновенно, и вы получаете электронную квитанцию сразу после завершения оплаты. 🔐 Кроме того, система полностью безопасна — все данные зашифрованы и соответствуют современным стандартам защиты.',
        'news_title_3': 'Плановое обслуживание',
        'news_content_3': '🛠 Плановое техническое обслуживание📢 Уважаемые пользователи!Наша платформа будет проходить плановое техническое обслуживание 🧰 20-го числа текущего месяца.🕘 В это время возможны временные перебои в работе сайта, включая:❌ недоступность страницы входа и регистрации,💳 невозможность проведения онлайн-платежей,📉 задержка в отображении информации о счетах.Мы проводим эти работы для:🔒 повышения безопасности данных,🚀 улучшения скорости загрузки сервиса,🧹 оптимизации базы данных и устранения мелких ошибок.🔔 Пожалуйста, заранее планируйте оплату счетов, чтобы избежать неудобств во время техработ.✅ После завершения обслуживания платформа возобновит работу в штатном режиме, и все функции будут доступны в полном объеме.🙏 Благодарим вас за понимание и терпение!',
        'news_title_4': 'Новое мобильное приложение',
        'news_content_4': '📱 Мы рады сообщить о запуске нашего нового мобильного приложения! Теперь вы можете управлять оплатой коммунальных услуг в любое время и в любом месте. Приложение доступно для iOS и Android. Основные функции:💳 Быстрая оплата счетов📊 Просмотр истории платежей🔔 Уведомления о новых счетах📱 Удобный интерфейс и быстрый доступ к личному кабинетуСкачайте приложение прямо сейчас и оцените новый уровень комфорта при оплате коммунальных услуг!',
        'select_language': 'Выберите язык',
        'uzbek': 'Узбекский',
        'russian': 'Русский',
        'english': 'Английский',
        'passport_number': 'Номер и серия паспорта',
        'phone_number': 'Номер телефона',
        'email': 'Email (необязательно)',
        'water_supply': 'Водоснабжение',
        'electricity': 'Электроснабжение',
        'gas_supply': 'Газоснабжение',
        'sewage': 'Водоотведение',
        'heating': 'Отопление',
        'waste_disposal': 'Вывоз бытовых отходов',
        'current_month_info': 'Информация за текущий месяц',
        'consumption': 'Потребление',
        'tariff': 'Тариф',
        'total_amount': 'Итоговая сумма',
        'select_month': 'Выберите месяц',
        'select_year': 'Выберите год',
        'view': 'Показать',
        'january': 'Январь',
        'february': 'Февраль',
        'march': 'Март',
        'april': 'Апрель',
        'may': 'Май',
        'june': 'Июнь',
        'july': 'Июль',
        'august': 'Август',
        'september': 'Сентябрь',
        'october': 'Октябрь',
        'november': 'Ноябрь',
        'december': 'Декабрь',
        'last_paid_receipts': 'Последние оплаченные квитанции',
        'receipt_number': 'Номер квитанции',
        'payment_date': 'Дата оплаты',
        'login_as_staff': 'Войти как сотрудник',
        'login_as_user': 'Войти как пользователь',
        'staff_key': 'Ключ сотрудника',
        'login_another_way': 'Войти другим способом',
        'choose_auth_method': 'Выберите способ входа',
        'service_not_connected': 'Данный сервис еще не подключен студентом',
        'username_requirements': 'Имя пользователя должно быть длиной 3-20 символов и содержать только буквы, цифры и подчеркивания',
        'password_requirements': 'Пароль должен быть не менее 8 символов и содержать как буквы, так и цифры',
        'passport_requirements': 'Номер паспорта должен состоять из 2 заглавных букв и 7 цифр',
        'phone_requirements': 'Номер телефона должен начинаться с +998 и содержать 9 цифр',
        'username_error': 'Неверный формат имени пользователя',
        'password_error': 'Неверный формат пароля',
        'password_mismatch': 'Пароли не совпадают',
        'passport_error': 'Неверный формат номера паспорта',
        'phone_error': 'Неверный формат номера телефона',
        'email_error': 'Неверный формат email',
        'registration_success': 'Регистрация успешна! Пожалуйста, войдите в систему.',
        'username_exists': 'Пользователь с таким именем уже существует',
        'please_correct_errors': 'Пожалуйста, исправьте ошибки в форме',
        'admin_dashboard': 'Панель администратора',
        'enter_username': 'Введите имя пользователя',
        'search_user': 'Найти пользователя',
        'user_found': 'Пользователь найден в базе данных',
        'user_not_found': 'Пользователь не найден в базе данных',
        'generate_receipts': 'Создать квитанции',
        'payment_for': 'За что оплата',
        'show_users': 'Показать пользователей',
        'hide_users': 'Скрыть пользователей',
        'full_name': 'ФИО',
        'address': 'Адрес',
        'account_number': 'Номер лицевого счёта',
        'save_changes': 'Сохранить изменения',
        'housing_type': 'Тип жилья',
        'registered': 'Зарегистрирован',
        'last_login': 'Последний вход',
        'notifications': 'Уведомления'
    },
    'uz': {
        'title': 'Interactive Online Utility Payment',
        'description': 'Welcome to the online platform for convenient payment of your utility bills.',
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'username': 'Username',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'submit': 'Submit',
        'dashboard': 'Dashboard',
        'welcome_user': 'Welcome,',
        'bills': 'Your Utility Bills',
        'amount': 'Amount',
        'due_date': 'Due Date',
        'status': 'Status',
        'paid': 'Paid',
        'unpaid': 'Unpaid',
        'pay': 'Pay',
        'payment_history': 'Payment History',
        'date': 'Date',
        'language': 'Language',
        'change_lang': 'Change Language',
        'registration': 'Registration',
        'error_user_exists': 'Username already exists',
        'error_password_mismatch': 'Passwords do not match',
        'error_invalid_credentials': 'Invalid username or password',
        'payment_success': 'Payment successful',
        'pay_bill': 'Pay Bill',
        'no_payments': 'No payments made yet.',
        'home': 'Home',
        'news_title_1': 'Electricity Price Increase',
        'news_content_1': 'Starting next month, the electricity tariff will increase by 5%, affecting all households.',
        'news_title_2': 'New Payment Methods',
        'news_content_2': 'We have introduced payments via popular mobile wallets for your convenience.',
        'news_title_3': 'Scheduled Maintenance',
        'news_content_3': 'Our platform will undergo maintenance on the 20th. Please plan your payments accordingly.',
        'news_title_4': 'New Mobile App',
        'news_content_4': 'We are excited to announce the launch of our new mobile application! Now you can manage your utility payments on the go.',
        'select_language': 'Select Language',
        'uzbek': 'Uzbek',
        'russian': 'Russian',
        'english': 'English',
        'passport_number': 'Passport Number & Series',
        'phone_number': 'Phone Number',
        'email': 'Email (optional)',
        'water_supply': 'Water Supply',
        'electricity': 'Electricity',
        'gas_supply': 'Gas Supply',
        'sewage': 'Sewage',
        'heating': 'Heating',
        'waste_disposal': 'Waste Disposal',
        'current_month_info': 'Current Month Information',
        'consumption': 'Consumption',
        'tariff': 'Tariff',
        'total_amount': 'Total Amount',
        'select_month': 'Select Month',
        'select_year': 'Select Year',
        'view': 'View',
        'january': 'January',
        'february': 'February',
        'march': 'March',
        'april': 'April',
        'may': 'May',
        'june': 'June',
        'july': 'July',
        'august': 'August',
        'september': 'September',
        'october': 'October',
        'november': 'November',
        'december': 'December',
        'last_paid_receipts': 'Last Paid Receipts',
        'receipt_number': 'Receipt Number',
        'payment_date': 'Payment Date',
        'login_as_staff': 'Login as Staff',
        'login_as_user': 'Login as User',
        'staff_key': 'Staff Key',
        'login_another_way': 'Login Another Way',
        'choose_auth_method': 'Choose Authentication Method',
        'service_not_connected': 'This service is not yet connected by the student',
        'username_requirements': 'Foydalanuvchi nomi 3-20 belgidan iborat bo\'lishi va faqat harflar, raqamlar va pastki chiziqdan iborat bo\'lishi kerak',
        'password_requirements': 'Parol kamida 8 belgidan iborat bo\'lishi va harflar va raqamlarni o\'z ichiga olishi kerak',
        'passport_requirements': 'Passport raqami 2 ta katta harf va 7 ta raqamdan iborat bo\'lishi kerak',
        'phone_requirements': 'Telefon raqami +998 bilan boshlanishi va 9 ta raqamdan iborat bo\'lishi kerak',
        'username_error': 'Noto\'g\'ri foydalanuvchi nomi formati',
        'password_error': 'Noto\'g\'ri parol formati',
        'password_mismatch': 'Parollar mos kelmaydi',
        'passport_error': 'Noto\'g\'ri passport raqami formati',
        'phone_error': 'Noto\'g\'ri telefon raqami formati',
        'email_error': 'Noto\'g\'ri email formati',
        'registration_success': 'Ro\'yxatdan o\'tish muvaffaqiyatli! Iltimos, tizimga kiring.',
        'username_exists': 'Bunday foydalanuvchi nomi allaqachon mavjud',
        'please_correct_errors': 'Iltimos, formadagi xatolarni tuzating',
        'admin_dashboard': 'Admin paneli',
        'enter_username': 'Foydalanuvchi nomini kiriting',
        'search_user': 'Foydalanuvchini qidirish',
        'user_found': 'Foydalanuvchi ma\'lumotlar bazasida topildi',
        'user_not_found': 'Foydalanuvchi ma\'lumotlar bazasida topilmadi',
        'generate_receipts': 'Generate Receipts',
        'payment_for': 'Nima uchun to\'lov',
        'show_users': 'Показать пользователей',
        'hide_users': 'Скрыть пользователей',
        'full_name': 'To\'liq ism',
        'address': 'Manzil',
        'account_number': 'Hisob raqami',
        'save_changes': 'O\'zgarishlarni saqlash',
        'housing_type': 'Uy-joy turi',
        'registered': 'Ro\'yxatdan o\'tgan',
        'last_login': 'Oxirgi kirish',
        'notifications': 'Xabarnomalar'
    }
}

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def init_db():
    with app.app_context():
        db = get_db()
        # Создаем таблицы, если они еще не существуют
        db.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                passport TEXT,
                phone TEXT,
                email TEXT,
                is_staff INTEGER DEFAULT 0,
                address TEXT,
                full_name TEXT,
                account_number TEXT
            );
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                due_date TEXT NOT NULL,
                paid INTEGER DEFAULT 0,
                utility_type TEXT NOT NULL,
                month INTEGER,
                year INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bill_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id),
                FOREIGN KEY(bill_id) REFERENCES bills(id)
            );
            CREATE TABLE IF NOT EXISTS utility_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                utility_type TEXT NOT NULL,
                month INTEGER NOT NULL,
                year INTEGER NOT NULL,
                previous_reading REAL,
                current_reading REAL,
                consumption REAL,
                tariff REAL,
                amount REAL,
                paid INTEGER DEFAULT 0,
                generation_date TEXT,
                adjustments TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS waste_receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                receipt_number TEXT NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT NOT NULL,
                paid INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        ''')

        # Проверяем, существуют ли новые столбцы в таблице bills
        cursor = db.execute("PRAGMA table_info(bills)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'utility_type' not in columns:
            db.execute('ALTER TABLE bills ADD COLUMN utility_type TEXT')
        if 'month' not in columns:
            db.execute('ALTER TABLE bills ADD COLUMN month INTEGER')
        if 'year' not in columns:
            db.execute('ALTER TABLE bills ADD COLUMN year INTEGER')

        # Проверяем, существуют ли новые столбцы в таблице utility_data
        cursor = db.execute("PRAGMA table_info(utility_data)")
        columns = [info[1] for info in cursor.fetchall()]
        
        new_columns = {
            'previous_reading': 'REAL',
            'current_reading': 'REAL',
            'generation_date': 'TEXT',
            'adjustments': 'TEXT'
        }
        
        for column, type_ in new_columns.items():
            if column not in columns:
                db.execute(f'ALTER TABLE utility_data ADD COLUMN {column} {type_}')

        # Проверяем, существуют ли столбцы passport, phone, email, is_staff в таблице users
        cursor = db.execute("PRAGMA table_info(users)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'passport' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN passport TEXT')
        if 'phone' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN phone TEXT')
        if 'email' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN email TEXT')
        if 'is_staff' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN is_staff INTEGER DEFAULT 0')
        if 'address' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN address TEXT')
        if 'full_name' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN full_name TEXT')
        if 'account_number' not in columns:
            db.execute('ALTER TABLE users ADD COLUMN account_number TEXT')

        # Проверяем, существует ли столбец paid в таблице waste_receipts
        cursor = db.execute("PRAGMA table_info(waste_receipts)")
        columns = [info[1] for info in cursor.fetchall()]
        if 'paid' not in columns:
            db.execute('ALTER TABLE waste_receipts ADD COLUMN paid INTEGER DEFAULT 0')

        # Проверяем, существует ли тестовый админ
        admin = query_db('SELECT id FROM users WHERE username = ?', ['admin'], one=True)
        if not admin:
            # Создаем тестового админа
            pw_hash = generate_password_hash('admin')
            db.execute('INSERT INTO users (username, password, is_staff) VALUES (?, ?, ?)',
                      ('admin', pw_hash, 1))
            db.commit()

        db.commit()

def get_locale():
    lang = session.get('lang', 'ru')
    return lang if lang in translations else 'ru'

def t(key):
    lang = get_locale()
    return translations[lang].get(key, key)

@app.before_request
def load_user():
    g.user = None
    if 'user_id' in session:
        user = query_db('SELECT * FROM users WHERE id = ?', [session['user_id']], one=True)
        g.user = user

@app.route('/')
def index():
    return render_template('index.html', t=t, g=g, lang=get_locale())

@app.route('/change_language', methods=['POST'])
def change_language():
    lang = request.form.get('lang', 'ru')
    if lang in ['ru', 'en']:  # Exclude 'uz' until translations are added
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        passport = request.form['passport']
        phone = request.form['phone']
        email = request.form['email']
        
        # Проверка совпадения паролей
        if password != confirm_password:
            return render_template('register.html', t=t, error=t('password_mismatch'), lang=get_locale())
        
        # Проверка существования пользователя
        cursor = get_db().cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone() is not None:
            return render_template('register.html', t=t, error=t('username_exists'), lang=get_locale())
        
        # Проверка формата паспорта (2 буквы + 7 цифр)
        if not re.match(r'^[A-Z]{2}\d{7}$', passport):
            return render_template('register.html', t=t, error=t('passport_error'), lang=get_locale())
        
        # Проверка формата телефона (+998 и 9 цифр)
        if not re.match(r'^\+998\d{9}$', phone):
            return render_template('register.html', t=t, error=t('phone_error'), lang=get_locale())
        
        # Проверка формата email (если email указан)
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return render_template('register.html', t=t, error=t('email_error'), lang=get_locale())
        
        # Хеширование пароля
        hashed_password = generate_password_hash(password)
        
        # Добавление пользователя в базу данных
        cursor.execute('''
            INSERT INTO users (username, password, passport, phone, email, is_staff)
            VALUES (?, ?, ?, ?, ?, 0)
        ''', (username, hashed_password, passport, phone, email))
        get_db().commit()
        
        # Перенаправление на страницу логина при успешной регистрации
        flash(t('registration_success'), 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', t=t, lang=get_locale())

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        staff_key = request.form.get('staff_key', '')
        
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        
        if user:
            if user['is_staff']:
                # Проверка для сотрудника
                if username == 'admin' and password == 'admin' and staff_key == '22':
                    session['user_id'] = user['id']
                    return redirect(url_for('dashboard'))
                else:
                    error = t('error_invalid_credentials')
            else:
                # Обычная проверка для пользователя
                if check_password_hash(user['password'], password):
                    session['user_id'] = user['id']
                    return redirect(url_for('dashboard'))
                else:
                    error = t('error_invalid_credentials')
        else:
            error = t('error_invalid_credentials')
            
    return render_template('login.html', t=t, error=error, lang=get_locale())

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    db = get_db()
    message = None

    if request.method == 'POST':
        bill_id = request.form.get('bill_id')
        bill = query_db('SELECT * FROM bills WHERE id = ? AND user_id = ? AND paid = 0', (bill_id, user_id), one=True)
        if bill:
            payment_date = datetime.date.today().isoformat()
            db.execute('INSERT INTO payments (user_id, bill_id, amount, payment_date) VALUES (?, ?, ?, ?)', 
                       (user_id, bill['id'], bill['amount'], payment_date))
            db.execute('UPDATE bills SET paid = 1 WHERE id = ?', (bill['id'],))
            db.commit()
            message = t('payment_success')

    bills = query_db('SELECT * FROM bills WHERE user_id = ? ORDER BY due_date ASC', (user_id,))
    payments = query_db('''
        SELECT p.amount, p.payment_date, b.due_date 
        FROM payments p 
        JOIN bills b ON p.bill_id = b.id
        WHERE p.user_id = ?
        ORDER BY p.payment_date DESC
    ''', (user_id,))

    return render_template('dashboard.html', t=t, g=g, bills=bills, payments=payments, message=message, lang=get_locale())

def utility_route(utility_type, title_key):
    def route():
        if not g.user:
            return redirect(url_for('login'))
        user_id = g.user['id']
        current_month = datetime.date.today().month
        current_year = datetime.date.today().year
        
        selected_month = int(request.form.get('month', current_month))
        selected_year = int(request.form.get('year', current_year))
        
        utility_data = query_db('''
            SELECT consumption, tariff, amount, paid 
            FROM utility_data 
            WHERE user_id = ? AND utility_type = ? AND month = ? AND year = ?
        ''', (user_id, utility_type, selected_month, selected_year), one=True)
        
        return render_template('utility.html', t=t, g=g, lang=get_locale(), utility_data=utility_data, 
                               selected_month=selected_month, selected_year=selected_year, current_year=current_year, 
                               utility_type=utility_type, title_key=title_key)
    return route

@app.route('/water_supply', methods=['GET', 'POST'])
def water_supply():
    return utility_route('water', 'water_supply')()

@app.route('/electricity', methods=['GET', 'POST'])
def electricity():
    return utility_route('electricity', 'electricity')()

@app.route('/gas_supply', methods=['GET', 'POST'])
def gas_supply():
    return utility_route('gas', 'gas_supply')()

@app.route('/sewage', methods=['GET', 'POST'])
def sewage():
    return utility_route('sewage', 'sewage')()

@app.route('/heating', methods=['GET', 'POST'])
def heating():
    return utility_route('heating', 'heating')()

@app.route('/waste_disposal', methods=['GET', 'POST'])
def waste_disposal():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    
    receipts = query_db('SELECT receipt_number, amount, payment_date FROM waste_receipts WHERE user_id = ? ORDER BY payment_date DESC', (user_id,))
    
    return render_template('waste_disposal.html', t=t, g=g, lang=get_locale(), receipts=receipts)

@app.route('/check_user/<username>')
def check_user():
    try:
        if not g.user or not g.user['is_staff']:
            return jsonify({'error': 'Unauthorized'}), 401
            
        user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
        print(f"Searching for user: {username}, Found: {user}")  # Добавляем отладочный вывод
        
        if user:
            return jsonify({
                'found': True,
                'message': t('user_found'),
                'user': {
                    'username': user['username'],
                    'is_staff': bool(user['is_staff']),
                    'passport': user['passport'],
                    'phone': user['phone'],
                    'email': user['email']
                }
            })
        else:
            return jsonify({
                'found': False,
                'message': t('user_not_found')
            })
    except Exception as e:
        print(f"Error in check_user: {str(e)}")  # Добавляем отладочный вывод
        return jsonify({
            'error': f'Ошибка при поиске пользователя: {str(e)}'
        }), 500

@app.route('/get_all_users')
def get_all_users():
    try:
        if not g.user or not g.user['is_staff']:
            return jsonify({'error': 'Unauthorized'}), 401
            
        users = query_db('SELECT username, is_staff, passport, phone, email FROM users')
        print(f"Found users: {users}")  # Отладочный вывод
        
        return jsonify({
            'users': [{
                'username': user['username'],
                'is_staff': bool(user['is_staff']),
                'passport': user['passport'],
                'phone': user['phone'],
                'email': user['email']
            } for user in users]
        })
    except Exception as e:
        print(f"Error in get_all_users: {str(e)}")  # Отладочный вывод
        return jsonify({
            'error': f'Ошибка при получении списка пользователей: {str(e)}'
        }), 500

@app.route('/create_test_users', methods=['POST'])
def create_test_users():
    try:
        if not g.user or not g.user['is_staff']:
            return jsonify({'error': 'Unauthorized'}), 401
        
        test_users = [
            ('AzizTest', 'pass123', 'AA1234567', '+998901234567', 'aziz.test@example.com', 'г. Ташкент, ул. Примерная, д. 12, кв. 45', 'Азизов Азиз Азизович', '123456789'),
            ('BekzodTest', 'pass123', 'BB1234567', '+998902345678', 'bekzod.test@example.com', 'г. Самарканд, ул. Образцовая, д. 5, кв. 10', 'Бекзодов Бекзод Бекзодович', '987654321'),
            ('ArturTest', 'pass123', 'CC1234567', '+998903456789', 'artur.test@example.com', 'г. Бухара, ул. Учебная, д. 7, кв. 22', 'Артуров Артур Артурович', '112233445')
        ]
        
        db = get_db()
        created_users = []
        
        for username, password, passport, phone, email, address, full_name, account_number in test_users:
            try:
                # Проверяем, существует ли пользователь
                existing_user = query_db('SELECT id FROM users WHERE username = ?', [username], one=True)
                if not existing_user:
                    pw_hash = generate_password_hash(password)
                    db.execute('''
                        INSERT INTO users (username, password, passport, phone, email, is_staff, address, full_name, account_number)
                        VALUES (?, ?, ?, ?, ?, 0, ?, ?, ?)
                    ''', (username, pw_hash, passport, phone, email, address, full_name, account_number))
                    created_users.append(username)
            except Exception as e:
                print(f"Error creating user {username}: {str(e)}")
                continue
        
        db.commit()
        
        if created_users:
            return jsonify({
                'message': f'Созданы тестовые пользователи: {", ".join(created_users)}'
            })
        else:
            return jsonify({
                'message': 'Все тестовые пользователи уже существуют'
            })
    except Exception as e:
        print(f"Error in create_test_users: {str(e)}")
        return jsonify({
            'error': f'Ошибка при создании тестовых пользователей: {str(e)}'
        }), 500

@app.route('/delete_test_users', methods=['POST'])
def delete_test_users():
    try:
        if not g.user or not g.user['is_staff']:
            return jsonify({'error': 'Unauthorized'}), 401
        
        test_usernames = ['AzizTest', 'BekzodTest', 'ArturTest']
        db = get_db()
        deleted_users = []
        
        for username in test_usernames:
            try:
                # Проверяем, существует ли пользователь
                existing_user = query_db('SELECT id FROM users WHERE username = ?', [username], one=True)
                if existing_user:
                    db.execute('DELETE FROM users WHERE username = ? AND is_staff = 0', [username])
                    deleted_users.append(username)
            except Exception as e:
                print(f"Error deleting user {username}: {str(e)}")
                continue
        
        db.commit()
        
        if deleted_users:
            return jsonify({
                'message': f'Удалены тестовые пользователи: {", ".join(deleted_users)}'
            })
        else:
            return jsonify({
                'message': 'Тестовые пользователи не найдены'
            })
    except Exception as e:
        print(f"Error in delete_test_users: {str(e)}")
        return jsonify({
            'error': f'Ошибка при удалении тестовых пользователей: {str(e)}'
        }), 500

@app.route('/payments')
@login_required
def payments():
    # Get payment history
    payments = query_db('''
        SELECT p.id, p.amount, p.payment_date, b.utility_type
        FROM payments p
        JOIN bills b ON p.bill_id = b.id
        WHERE p.user_id = ? AND b.utility_type IS NOT NULL
        ORDER BY p.payment_date DESC
    ''', (g.user['id'],))

    # Get unpaid bills for each utility type with consumption data
    water_data = query_db('''
        SELECT b.*, ud.previous_reading, ud.current_reading, ud.consumption, ud.tariff
        FROM bills b
        JOIN utility_data ud ON b.user_id = ud.user_id 
            AND b.utility_type = ud.utility_type 
            AND b.month = ud.month 
            AND b.year = ud.year
        WHERE b.user_id = ? AND b.utility_type = 'water' AND b.paid = 0
        ORDER BY b.due_date DESC
        LIMIT 1
    ''', (g.user['id'],), one=True)

    electricity_data = query_db('''
        SELECT b.*, ud.previous_reading, ud.current_reading, ud.consumption, ud.tariff
        FROM bills b
        JOIN utility_data ud ON b.user_id = ud.user_id 
            AND b.utility_type = ud.utility_type 
            AND b.month = ud.month 
            AND b.year = ud.year
        WHERE b.user_id = ? AND b.utility_type = 'electricity' AND b.paid = 0
        ORDER BY b.due_date DESC
        LIMIT 1
    ''', (g.user['id'],), one=True)

    gas_data = query_db('''
        SELECT b.*, ud.previous_reading, ud.current_reading, ud.consumption, ud.tariff
        FROM bills b
        JOIN utility_data ud ON b.user_id = ud.user_id 
            AND b.utility_type = ud.utility_type 
            AND b.month = ud.month 
            AND b.year = ud.year
        WHERE b.user_id = ? AND b.utility_type = 'gas' AND b.paid = 0
        ORDER BY b.due_date DESC
        LIMIT 1
    ''', (g.user['id'],), one=True)

    heating_data = query_db('''
        SELECT b.*, ud.previous_reading, ud.current_reading, ud.consumption, ud.tariff
        FROM bills b
        JOIN utility_data ud ON b.user_id = ud.user_id 
            AND b.utility_type = ud.utility_type 
            AND b.month = ud.month 
            AND b.year = ud.year
        WHERE b.user_id = ? AND b.utility_type = 'heating' AND b.paid = 0
        ORDER BY b.due_date DESC
        LIMIT 1
    ''', (g.user['id'],), one=True)

    waste_data = query_db('''
        SELECT b.*
        FROM bills b
        WHERE b.user_id = ? AND b.utility_type = 'waste' AND b.paid = 0
        ORDER BY b.due_date DESC
        LIMIT 1
    ''', (g.user['id'],), one=True)

    current_date = datetime.datetime.now()
    
    return render_template('payments.html', 
                         t=t,
                         g=g,
                         lang=get_locale(),
                         payments=payments,
                         water_data=water_data,
                         electricity_data=electricity_data,
                         gas_data=gas_data,
                         heating_data=heating_data,
                         waste_data=waste_data,
                         current_date=current_date)

@app.route('/pay_water', methods=['POST'])
def pay_water():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    db = get_db()
    db.execute('''
        UPDATE utility_data 
        SET paid = 1 
        WHERE user_id = ? AND utility_type = ? AND month = ? AND year = ?
    ''', (user_id, 'water', current_month, current_year))
    db.commit()
    
    return redirect(url_for('payments'))

@app.route('/pay_electricity', methods=['POST'])
def pay_electricity():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    db = get_db()
    db.execute('''
        UPDATE utility_data 
        SET paid = 1 
        WHERE user_id = ? AND utility_type = ? AND month = ? AND year = ?
    ''', (user_id, 'electricity', current_month, current_year))
    db.commit()
    
    return redirect(url_for('payments'))

@app.route('/pay_gas', methods=['POST'])
def pay_gas():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    db = get_db()
    db.execute('''
        UPDATE utility_data 
        SET paid = 1 
        WHERE user_id = ? AND utility_type = ? AND month = ? AND year = ?
    ''', (user_id, 'gas', current_month, current_year))
    db.commit()
    
    return redirect(url_for('payments'))

@app.route('/pay_heating', methods=['POST'])
def pay_heating():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    db = get_db()
    db.execute('''
        UPDATE utility_data 
        SET paid = 1 
        WHERE user_id = ? AND utility_type = ? AND month = ? AND year = ?
    ''', (user_id, 'heating', current_month, current_year))
    db.commit()
    
    return redirect(url_for('payments'))

@app.route('/pay_waste', methods=['POST'])
def pay_waste():
    if not g.user:
        return redirect(url_for('login'))
    user_id = g.user['id']
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    
    db = get_db()
    db.execute('''
        UPDATE waste_receipts 
        SET paid = 1 
        WHERE user_id = ? AND payment_date LIKE ?
    ''', (user_id, f'{current_year}-{current_month:02d}-%'))
    db.commit()
    
    return redirect(url_for('payments'))

@app.route('/generate_receipts', methods=['POST'])
def generate_receipts():
    if not g.user:
        return redirect(url_for('login'))
    
    user_id = g.user['id']
    current_date = datetime.date.today()
    next_month = current_date.replace(day=1) + datetime.timedelta(days=32)
    next_month = next_month.replace(day=1)
    
    db = get_db()
    
    # Utility companies and their receipt titles
    utilities = {
        'water': {
            'company': 'Уз "Водоканал"',
            'title': 'Квитанция по оплате водоснабжения',
            'unit': 'м³'
        },
        'electricity': {
            'company': 'Уз "Энергосбыт"',
            'title': 'Квитанция по оплате электроэнергии',
            'unit': 'кВт·ч'
        },
        'gas': {
            'company': 'Уз "Газпром"',
            'title': 'Квитанция по оплате газоснабжения',
            'unit': 'м³'
        },
        'heating': {
            'company': 'Уз "Теплосеть"',
            'title': 'Квитанция по оплате отопления',
            'unit': 'Гкал'
        }
    }
    
    # Generate receipts for each utility
    for utility_type, info in utilities.items():
        # Generate two receipts for each utility - one paid, one unpaid
        for is_paid in [True, False]:
            # Generate random readings
            previous_reading = random.randint(1000, 10000)
            current_reading = previous_reading + random.randint(100, 500)
            consumption = current_reading - previous_reading
            tariff = random.randint(400, 1000)
            amount = consumption * tariff
            
            # Create utility data with detailed information
            db.execute('''
                INSERT INTO utility_data 
                (user_id, utility_type, month, year, 
                previous_reading, current_reading, consumption, 
                tariff, amount, paid, generation_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                utility_type,
                next_month.month,
                next_month.year,
                previous_reading,
                current_reading,
                consumption,
                tariff,
                amount,
                1 if is_paid else 0,
                "2025-04-15"
            ))
            
            # Create bill
            db.execute('''
                INSERT INTO bills 
                (user_id, amount, due_date, paid, utility_type, month, year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                amount,
                next_month.isoformat(),
                1 if is_paid else 0,
                utility_type,
                next_month.month,
                next_month.year
            ))
            
            # If paid, create payment record
            if is_paid:
                bill_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
                db.execute('''
                    INSERT INTO payments 
                    (user_id, bill_id, amount, payment_date)
                    VALUES (?, ?, ?, ?)
                ''', (
                    user_id,
                    bill_id,
                    amount,
                    current_date.isoformat()
                ))
    
    db.commit()
    return redirect(url_for('payments'))

@app.route('/edit_user/<username>', methods=['POST'])
def edit_user(username):
    if not g.user or not g.user['is_staff']:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Обновляем только те поля, которые не пустые
    fields = ['full_name', 'address', 'account_number', 'passport', 'phone', 'email']
    updates = []
    values = []
    for field in fields:
        if data.get(field):
            updates.append(f'{field} = ?')
            values.append(data[field])
    if not updates:
        return jsonify({'message': 'Нет изменений'})
    values.append(username)
    get_db().execute(f'UPDATE users SET {", ".join(updates)} WHERE username = ?', values)
    get_db().commit()
    return jsonify({'message': 'Данные пользователя обновлены'})

@app.route('/admin/edit_user/<username>')
def admin_edit_user(username):
    if not g.user or not g.user['is_staff']:
        return redirect(url_for('login'))
    user = query_db('SELECT * FROM users WHERE username = ?', [username], one=True)
    if not user:
        return render_template('admin_edit_user.html', error='Пользователь не найден', t=t, lang=get_locale())
    return render_template('admin_edit_user.html', user=user, t=t, lang=get_locale())

# created by artur

Архитектура базы данных:

Система аутентификации:
Реализована система регистрации и входа
Поддержка разных типов пользователей (обычные пользователи и персонал)
Безопасное хранение паролей через хеширование
Многоязычность:
Поддержка трех языков (русский, английский, узбекский)
Система переводов через словарь translations
Динамическое переключение языков
Безопасность:
Хеширование паролей
Проверка авторизации через декоратор @login_required
Валидация входных данных
Защита от несанкционированного доступа к админ-функциям