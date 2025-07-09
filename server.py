import csv
import re
from datetime import datetime, date, timedelta
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import json
from flask_mail import Mail, Message
from collections import defaultdict
PRICING_FILE = "static/pricing.json"
app = Flask(__name__, static_folder='static')
CORS(app)

# Konfiguracja ścieżek
UPLOADS_DIR = "static/uploads"
JSON_DIR = "static/posts"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)
VISITS_FILE = "visits.csv"
UNIQUE_VISITS_FILE = "unique_visits.csv"
COUNTRY_CACHE = {}

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jolantamservice@gmail.com'
app.config['MAIL_PASSWORD'] = 'ctjwssxsjovpsaea'  # lub hasło aplikacji, jeśli używasz 2FA
app.config['MAIL_DEFAULT_SENDER'] = 'jolantamservice@gmail.com'

mail = Mail(app)

# Helper functions
def get_country_from_ip(ip):
    if ip in COUNTRY_CACHE:
        return COUNTRY_CACHE[ip]

    if ip in ('127.0.0.1', '::1'):
        country = "Localhost"
    else:
        try:
            response = requests.get(f"https://ipapi.co/{ip}/country_name/", timeout=10)
            country = response.text.strip() if response.status_code == 200 else "Unknown"
        except Exception:
            country = "Error"

    COUNTRY_CACHE[ip] = country
    return country


@app.route("/send-email", methods=["POST"])
def send_email():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone", "")
    message = data.get("message")

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f8f8f8; padding: 20px;">
        <div style="background-color: #ffffff; border-radius: 8px; padding: 20px; max-width: 600px; margin: auto; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color: #1d3557;">📬 Nowa wiadomość z formularza kontaktowego</h2>
            <p><strong>Imię i nazwisko:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Telefon:</strong> {phone if phone else 'Nie podano'}</p>
            <hr style="border: none; border-top: 1px solid #ccc;" />
            <p><strong>Wiadomość:</strong></p>
            <p style="white-space: pre-line;">{message}</p>
            <hr style="border: none; border-top: 1px solid #ccc; margin-top: 30px;" />
            <p style="font-size: 12px; color: #888;">
                To jest wiadomość wygenerowana automatycznie przez formularz kontaktowy na stronie 
                <a href="https://jolatrener.pl" style="color: #457b9d;">jolatrener.pl</a>.
                Nie odpowiadaj bezpośrednio na tę wiadomość.
            </p>
        </div>
    </body>
    </html>
    """

    msg = Message(
        subject=f"📩 Wiadomość od {name} – formularz kontaktowy jolatrener.pl",
        recipients=["jolamiszcz@gmail.com"],
        sender="jolantamservice@gmail.com"
    )
    msg.html = html_content

    try:
        mail.send(msg)
        return jsonify({"success": True, "message": "Wiadomość została wysłana."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

CSV_FILE = "newsletter_emails.csv"

# Prosty regex walidujący e-mail
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

@app.route("/subscribe-newsletter", methods=["POST"])
def subscribe_newsletter():
    data = request.get_json()
    email = data.get("email")

    if not email or not is_valid_email(email):
        return jsonify({"success": False, "message": "Nieprawidłowy adres e-mail."}), 400

    # Sprawdź czy email już istnieje w pliku
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            if any(row and row[0] == email for row in reader):
                return jsonify({"success": False, "message": "Ten e-mail już jest zapisany."}), 409

    # Zapisz e-mail do pliku CSV z datą
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, datetime.now().isoformat()])

    return jsonify({"success": True, "message": f"{email} został zapisany do newslettera."}), 200
@app.route('/api/visit_countries')
def visit_countries():
    country_stats = {}

    if os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 3:
                        country = parts[2]
                        country_stats[country] = country_stats.get(country, 0) + 1

    # Sortuj kraje malejąco po liczbie wizyt
    sorted_countries = sorted(country_stats.items(), key=lambda x: x[1], reverse=True)

    # Przygotuj dane dla top 10 krajów + "Inne"
    top_countries = {}
    other_count = 0
    for i, (country, count) in enumerate(sorted_countries):
        if i < 10:
            top_countries[country] = count
        else:
            other_count += count

    if other_count > 0:
        top_countries['Inne'] = other_count

    return jsonify(top_countries)
def log_visit(ip):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    country = get_country_from_ip(ip)
    is_new = False

    if not os.path.exists(UNIQUE_VISITS_FILE) or ip not in open(UNIQUE_VISITS_FILE).read():
        is_new = True
        with open(UNIQUE_VISITS_FILE, 'a') as f:
            f.write(f"{ip}\n")

    with open(VISITS_FILE, 'a') as f:
        f.write(f"{timestamp},{ip},{country},{int(is_new)}\n")


# API Endpoints
@app.route('/')
def serve_index():
    return send_from_directory("static", "strona.html")


@app.route('/log_visit')
def visit_logger():
    ip = request.remote_addr
    log_visit(ip)
    return "Visit logged"


@app.route('/today_visits')
def today_visits():
    try:
        today = date.today().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        today_new = 0
        today_returning = 0
        yesterday_new = 0

        if os.path.exists(VISITS_FILE):
            with open(VISITS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        parts = line.strip().split(',')
                        if len(parts) >= 4:
                            timestamp, ip, country, is_new = parts[0], parts[1], parts[2], parts[3] == '1'

                            if timestamp.startswith(today):
                                if is_new:
                                    today_new += 1
                                else:
                                    today_returning += 1
                            elif timestamp.startswith(yesterday) and is_new:
                                yesterday_new += 1

        return jsonify({
            'today_new_users': today_new,
            'today_returning_users': today_returning,
            'yesterday_new_users': yesterday_new,
            'change': today_new - yesterday_new if yesterday_new else 0
        })
    except Exception as e:
        app.logger.error(f"Error in today_visits: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/visit_stats')
def visit_stats():
    period = int(request.args.get('period', 7))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period)

    stats = {
        'labels': [],
        'new_users': [],
        'returning_users': []
    }

    # Generate date labels
    for i in range(period + 1):
        date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        stats['labels'].append(date)
        stats['new_users'].append(0)
        stats['returning_users'].append(0)

    # Count visits
    if os.path.exists(VISITS_FILE):
        with open(VISITS_FILE, 'r') as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split(',')
                    if len(parts) >= 4:
                        timestamp, ip, country, is_new = parts[0], parts[1], parts[2], parts[3] == '1'
                        visit_date = timestamp.split()[0]

                        if visit_date in stats['labels']:
                            index = stats['labels'].index(visit_date)
                            if is_new:
                                stats['new_users'][index] += 1
                            else:
                                stats['returning_users'][index] += 1

    return jsonify(stats)


@app.route('/api/visit_distribution')
def visit_distribution():
    dist_type = request.args.get('type', 'hours')  # Fixed: removed extra parenthesis
    data = {'labels': [], 'values': []}

    if dist_type == 'hours':
        data['labels'] = [f'{h}:00' for h in range(24)]
        data['values'] = [0] * 24

        if os.path.exists(VISITS_FILE):
            with open(VISITS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        timestamp = line.strip().split(',')[0]
                        hour = int(timestamp.split()[1].split(':')[0])
                        data['values'][hour] += 1

    elif dist_type == 'days':
        days = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']
        data['labels'] = days
        data['values'] = [0] * 7

        if os.path.exists(VISITS_FILE):
            with open(VISITS_FILE, 'r') as f:
                for line in f:
                    if line.strip():
                        timestamp = line.strip().split(',')[0]
                        date_obj = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        weekday = date_obj.weekday()
                        data['values'][weekday] += 1
    return jsonify(data)

# Post management endpoints (unchanged from your original code)
@app.route('/api/posts', methods=['GET'])
def get_posts_list():
    try:
        files = os.listdir(JSON_DIR)
        posts = sorted([f for f in files if f.endswith('.json')], reverse=True)
        return jsonify(posts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/post/<post_id>', methods=['GET'])
def get_post_details(post_id):
    try:
        post_path = os.path.join(JSON_DIR, f"{post_id}.json")
        if not os.path.exists(post_path):
            return jsonify({"error": "Post not found"}), 404

        with open(post_path, 'r', encoding='utf-8') as f:
            post_data = json.load(f)

        if 'cover_image' in post_data and post_data['cover_image']:
            post_data['cover_url'] = f"/static/uploads/{post_data['cover_image']}"

        return jsonify(post_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/upload-post', methods=["POST"])
def upload_post():
    try:
        if 'json' not in request.files:
            return jsonify({"error": "Brak pliku JSON"}), 400

        json_file = request.files['json']
        json_data = json.load(json_file)

        cover_filename = None
        if 'cover' in request.files:
            cover_file = request.files['cover']
            cover_ext = os.path.splitext(cover_file.filename)[1]
            cover_filename = f"cover_{uuid.uuid4()}{cover_ext}"
            cover_file.save(os.path.join(UPLOADS_DIR, cover_filename))
            json_data['cover_image'] = cover_filename

        media_files = request.files.getlist('media')
        media_info = []

        for file in media_files:
            ext = os.path.splitext(file.filename)[1]
            media_filename = f"media_{uuid.uuid4()}{ext}"
            file.save(os.path.join(UPLOADS_DIR, media_filename))

            old_src = f"media://{file.filename}"
            new_src = f"/static/uploads/{media_filename}"
            json_data['html'] = json_data['html'].replace(old_src, new_src)

            media_info.append({
                "original_name": file.filename,
                "saved_name": media_filename,
                "type": file.content_type.split('/')[0]
            })

        post_id = str(uuid.uuid4())
        json_data['media'] = media_info

        with open(os.path.join(JSON_DIR, f"{post_id}.json"), 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            "message": "Post zapisany",
            "post_id": post_id,
            "cover_image": cover_filename
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOADS_DIR, filename)


@app.route('/api/post/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    try:
        post_path = os.path.join(JSON_DIR, f"{post_id}.json")
        if not os.path.exists(post_path):
            return jsonify({"error": "Post not found"}), 404
        os.remove(post_path)
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


@app.route('/api/pricing', methods=['GET', 'POST', 'PUT', 'DELETE'])
def manage_pricing():
    try:
        if request.method == 'GET':
            # Pobierz cały cennik
            if not os.path.exists(PRICING_FILE):
                with open(PRICING_FILE, 'w') as f:
                    json.dump({"categories": []}, f)

            with open(PRICING_FILE, 'r') as f:
                pricing_data = json.load(f)
            return jsonify(pricing_data)

        elif request.method == 'POST':
            # Dodaj nową kategorię
            data = request.get_json()
            with open(PRICING_FILE, 'r+') as f:
                pricing_data = json.load(f)
                new_category = {
                    "id": str(uuid.uuid4()),
                    "title": data.get('title', 'Nowa kategoria'),
                    "description": data.get('description', ''),
                    "items": []
                }
                pricing_data['categories'].append(new_category)
                f.seek(0)
                json.dump(pricing_data, f, indent=2, ensure_ascii=False)
                f.truncate()
            return jsonify({"message": "Category added", "id": new_category["id"]}), 201

        elif request.method == 'PUT':
            # Edytuj istniejącą kategorię lub ofertę
            data = request.get_json()
            with open(PRICING_FILE, 'r+') as f:
                pricing_data = json.load(f)

                if 'category_id' in data:
                    # Edycja kategorii
                    for category in pricing_data['categories']:
                        if category['id'] == data['category_id']:
                            if 'title' in data:
                                category['title'] = data['title']
                            if 'description' in data:
                                category['description'] = data['description']
                            break

                if 'item_id' in data:
                    # Edycja oferty
                    for category in pricing_data['categories']:
                        for item in category['items']:
                            if item['id'] == data['item_id']:
                                if 'name' in data:
                                    item['name'] = data['name']
                                if 'price' in data:
                                    item['price'] = data['price']
                                if 'description' in data:
                                    item['description'] = data['description']
                                if 'features' in data:
                                    item['features'] = data['features']
                                break

                f.seek(0)
                json.dump(pricing_data, f, indent=2, ensure_ascii=False)
                f.truncate()
            return jsonify({"message": "Update successful"})

        elif request.method == 'DELETE':
            # Usuń kategorię lub ofertę
            data = request.get_json()
            with open(PRICING_FILE, 'r+') as f:
                pricing_data = json.load(f)

                if 'category_id' in data:
                    # Usuń kategorię
                    pricing_data['categories'] = [
                        c for c in pricing_data['categories']
                        if c['id'] != data['category_id']
                    ]

                if 'item_id' in data:
                    # Usuń ofertę
                    for category in pricing_data['categories']:
                        category['items'] = [
                            i for i in category['items']
                            if i['id'] != data['item_id']
                        ]

                f.seek(0)
                json.dump(pricing_data, f, indent=2, ensure_ascii=False)
                f.truncate()
            return jsonify({"message": "Delete successful"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/pricing/items', methods=['POST', 'DELETE'])
def manage_pricing_items():
    try:
        # Load existing pricing data or create new file
        if not os.path.exists(PRICING_FILE):
            with open(PRICING_FILE, 'w') as f:
                json.dump({"categories": []}, f)

        with open(PRICING_FILE, 'r') as f:
            pricing_data = json.load(f)

        if request.method == 'GET':
            return jsonify(pricing_data)
        if request.method == 'POST':
            # Dodaj nową ofertę do kategorii
            data = request.get_json()
            with open(PRICING_FILE, 'r+') as f:
                pricing_data = json.load(f)

                for category in pricing_data['categories']:
                    if category['id'] == data['category_id']:
                        # W funkcji manage_pricing() podczas dodawania/edycji oferty
                        new_item = {
                            "id": str(uuid.uuid4()),
                            "name": data.get('name', 'Nowa oferta'),
                            "price": data.get('price', 0),
                            "price_per_unit": data.get('price_per_unit', ''),  # Nowe pole
                            "description": data.get('description', ''),
                            "features": data.get('features', [])
                        }
                        category['items'].append(new_item)
                        break

                f.seek(0)
                json.dump(pricing_data, f, indent=2, ensure_ascii=False)
                f.truncate()
            return jsonify({"message": "Item added", "id": new_item["id"]}), 201

        elif request.method == 'DELETE':
            # Usuń ofertę z kategorii
            data = request.get_json()
            with open(PRICING_FILE, 'r+') as f:
                pricing_data = json.load(f)

                for category in pricing_data['categories']:
                    category['items'] = [
                        i for i in category['items']
                        if i['id'] != data['item_id']
                    ]

                f.seek(0)
                json.dump(pricing_data, f, indent=2, ensure_ascii=False)
                f.truncate()
            return jsonify({"message": "Item deleted"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# Path to transactions storage
TRANSACTIONS_FILE = 'transactions.json'

# Ensure the transactions file exists
if not os.path.exists(TRANSACTIONS_FILE):
    with open(TRANSACTIONS_FILE, 'w') as f:
        json.dump([], f)


def load_transactions():
    """
    Wczytuje listę transakcji z pliku JSON.
    """
    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_transactions(transactions):
    """
    Zapisuje listę transakcji do pliku JSON z formatowaniem.
    """
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """
    Zwraca wszystkie zapisane transakcje.
    """
    transactions = load_transactions()
    return jsonify(transactions), 200


@app.route('/api/transactions/<string:tx_id>', methods=['GET'])
def get_transaction(tx_id):
    """
    Zwraca pojedynczą transakcję po jej ID.
    """
    transactions = load_transactions()
    for tx in transactions:
        if tx['id'] == tx_id:
            return jsonify(tx), 200
    return jsonify({'error': 'Transaction not found'}), 404


@app.route('/api/transactions', methods=['POST'])
def create_transaction():
    """
    Dodaje nową transakcję.
    Oczekuje JSON z polami:
      - first_name, last_name, address, email, phone
      - purchase_date (ISO YYYY-MM-DD lub timestamp)
      - items (lista zakupionych pozycji)
      - offer_id, price
      - comment (opcjonalnie)
    """
    data = request.get_json()
    # Weryfikacja wymaganych pól
    required = ['first_name', 'last_name', 'address', 'email', 'phone',
                'purchase_date', 'items', 'offer_id', 'price']
    missing = [field for field in required if field not in data]
    if missing:
        return jsonify({'error': f'Missing fields: {', '.join(missing)}'}), 400

    # Stwórz rekord transakcji
    transaction = {
        'id': str(uuid.uuid4()),
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'address': data['address'],
        'email': data['email'],
        'phone': data['phone'],
        'purchase_date': data['purchase_date'],
        'items': data['items'],
        'offer_id': data['offer_id'],
        'price': data['price'],
        'comment': data.get('comment', ''),
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }

    # Dodaj do magazynu
    transactions = load_transactions()
    transactions.append(transaction)
    save_transactions(transactions)

    return jsonify(transaction), 201
@app.route('/send-newsletter', methods=['POST'])
def send_newsletter():
    data = request.get_json()
    post_title = data.get("title")
    post_description = data.get("description")
    post_link = data.get("link")  # np. /blog/123 lub pełny link

    if not post_title or not post_description or not post_link:
        return jsonify({"success": False, "message": "Brakuje danych posta"}), 400

    if not os.path.exists("newsletter_emails.csv"):
        return jsonify({"success": False, "message": "Brak subskrybentów."}), 404

    # Wczytaj e-maile z pliku CSV
    with open("newsletter_emails.csv", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        subscribers = [row[0] for row in reader if row]

    if not subscribers:
        return jsonify({"success": False, "message": "Brak zapisanych e-maili."}), 404

    # Wyślij maila do każdego
    for email in subscribers:
        msg = Message(
            subject=f"🆕 Nowy post na blogu: {post_title}",
            recipients=[email],
            html=f"""
        <html>
          <body style="margin:0; padding:20px; font-family:Arial, sans-serif; background-color:#f4f4f4;">
            <div style="max-width:600px; margin:0 auto; background-color:#ffffff; border-radius:8px;
                        box-shadow:0 2px 8px rgba(0,0,0,0.1); overflow:hidden;">

              <div style="background-color:#457b9d; padding:20px; text-align:center; color:#ffffff;">
                <h2 style="margin:0;">Nowy post na jolatrener.pl</h2>
              </div>

              <div style="padding:20px; color:#333333; line-height:1.5;">
                <p>Cześć!</p>
                <p>
                  Na blogu <a href="https://jolatrener.pl" style="color:#1d3557; text-decoration:none;">
                  jolatrener.pl</a> pojawił się właśnie nowy wpis:
                </p>

                <h3 style="color:#1d3557; margin-top:10px;">{post_title}</h3>
                <p style="margin:10px 0;">{post_description}</p>

                <div style="text-align:center; margin:30px 0;">
                  <a href="{post_link}"
                     style="display:inline-block; background-color:#1d3557; color:#ffffff; text-decoration:none;
                            padding:12px 24px; border-radius:4px; font-weight:bold;">
                    👉 Przeczytaj teraz
                  </a>
                </div>

                <hr style="border:none; border-top:1px solid #e0e0e0; margin:30px 0;">

                <p style="font-size:12px; color:#888888; text-align:center;">
                  To jest wiadomość automatyczna wysłana na podstawie subskrypcji newslettera.<br>
                  Jeśli nie chcesz już otrzymywać powiadomień, możesz <a href="https://jolatrener.pl/unsubscribe"
                  style="color:#457b9d; text-decoration:none;">wypisać się tutaj</a>.
                </p>
              </div>

            </div>
          </body>
        </html>
        """

        )
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Błąd przy wysyłce do {email}: {e}")
            continue

    return jsonify({"success": True, "message": f"Wysłano powiadomienia do {len(subscribers)} subskrybentów."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8127, debug=True)