# 💹 StockManagement - Cryptocurrency Dashboard

StockManagement is a Django-powered web application that simulates a real-time cryptocurrency trading platform. It allows users to view live cryptocurrency prices, register/login to their account, and "buy" cryptocurrencies in a simulated environment.

---

## 📌 Features

- 🔐 **User Authentication**
  - Login & logout functionality using Django’s built-in auth system.

- 📊 **Live Cryptocurrency Prices**
  - Automatically fetches and updates crypto prices using external API integration (e.g., CoinGecko).

- 🛒 **Simulated Crypto Purchase**
  - Logged-in users can “buy” cryptocurrencies. Purchases are tracked per user.

- 🗑️ **Delete & Manage Holdings**
  - Easily manage your own crypto holdings (delete functionality included).

- 🎨 **Modern UI**
  - Designed with Bootstrap 5 in a clean black-and-white theme.
  - Responsive and intuitive table layout for market viewing.

---

## 🏗️ Tech Stack

| Layer         | Technology              |
|--------------|--------------------------|
| Framework     | Django 4.x               |
| Frontend      | HTML, CSS, Bootstrap 5   |
| Database      | SQLite (default)         |
| Authentication| Django auth              |
| External API  | CoinGecko API (via `requests`) |
| Styling       | Custom CSS (in `/static/css/style.css`) |

---

## 🔧 Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/stockmanagement.git
cd stockmanagement

- Create a Virtual Environment:

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

- Install requirements

pip install -r requirements.txt
pip install django requests

- Apply migration and runserver

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

```

Project Structure:
stockmanagement/
├── stockmanagement/        # Django project settings
├── stockmanager/           # App with views, models, urls
│   ├── templates/          # HTML templates
│   │   └── stockmanager/
│   │       ├── add_stock.html
│   │       ├── login.html
│   │       └── stock_list.html
│   ├── static/
│   │   └── css/style.css
├── db.sqlite3              # Database file
├── manage.py               # Django CLI
