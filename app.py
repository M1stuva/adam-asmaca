from flask import Flask, render_template, request, jsonify, make_response
import random
import uuid

app = Flask(__name__)

# Basit Veritabanı (Gerçek projede SQLite veya PostgreSQL kullanılmalı)
# Yapı: {user_id: {'name': str, 'level': int, 'score': int, 'current_word': str, 'guessed': list, 'lives': int}}
USERS = {}

# Kelime Havuzu (Seviyeli)
WORDS = {
    1: ["ELMA", "ARMUT", "KEDİ", "MASA", "KAPI"],
    2: ["PYTHON", "YAZILIM", "KLAVYE", "EKRAN", "RADYO"],
    3: ["ALGORİTMA", "BİLGİSAYAR", "MÜHENDİSLİK", "TELEVİZYON", "ÜNİVERSİTE"],
    4: ["SÜRDÜRÜLEBİLİRLİK", "PROFESYONELLİK", "KARAKTERİSTİK", "ELEKTROMANYETİK"]
}

def get_random_name():
    adjectives = ["Hızlı", "Zeki", "Cesur", "Gizemli", "Usta"]
    nouns = ["Kaplan", "Kartal", "Panda", "Ejderha", "Kurt"]
    return f"{random.choice(adjectives)} {random.choice(nouns)}"

def start_new_level(user_id):
    level = USERS[user_id]['level']
    # Maksimum seviye kontrolü (Eğer 4'ü geçerse 4'ten devam etsin veya oyun bitti desin)
    difficulty = min(level, 4)
    word = random.choice(WORDS[difficulty])
    
    USERS[user_id]['current_word'] = word
    USERS[user_id]['guessed'] = []
    USERS[user_id]['lives'] = 6
    return word

@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    
    # Kullanıcıyı tanı veya yeni oluştur
    if not user_id or user_id not in USERS:
        user_id = str(uuid.uuid4())
        USERS[user_id] = {
            'name': get_random_name(),
            'level': 1,
            'score': 0,
            'current_word': "",
            'guessed': [],
            'lives': 6
        }
        start_new_level(user_id)
        resp = make_response(render_template('index.html'))
        resp.set_cookie('user_id', user_id, max_age=60*60*24*30) # 30 Günlük Cookie
        return resp
    
    return render_template('index.html')

@app.route('/api/get_state', methods=['GET'])
def get_state():
    user_id = request.cookies.get('user_id')
    if not user_id or user_id not in USERS:
        return jsonify({'error': 'User not found'}), 404
    
    user = USERS[user_id]
    
    # Kelimeyi maskele (Örn: P _ T _ O N)
    display_word = [L if L in user['guessed'] else '_' for L in user['current_word']]
    
    return jsonify({
        'name': user['name'],
        'level': user['level'],
        'lives': user['lives'],
        'display_word': display_word,
        'game_over': user['lives'] <= 0,
        'victory': '_' not in display_word,
        'guessed_letters': user['guessed']
    })

@app.route('/api/guess', methods=['POST'])
def guess():
    user_id = request.cookies.get('user_id')
    data = request.json
    letter = data.get('letter').upper()
    
    user = USERS[user_id]
    
    if letter not in user['guessed'] and user['lives'] > 0:
        user['guessed'].append(letter)
        if letter not in user['current_word']:
            user['lives'] -= 1
            
    return get_state()

@app.route('/api/next_level', methods=['POST'])
def next_level():
    user_id = request.cookies.get('user_id')
    user = USERS[user_id]
    
    # Kazanıp kazanmadığını kontrol et
    display_word = [L if L in user['guessed'] else '_' for L in user['current_word']]
    if '_' not in display_word:
        user['level'] += 1
        start_new_level(user_id)
        
    return get_state()

@app.route('/api/restart', methods=['POST'])
def restart():
    user_id = request.cookies.get('user_id')
    # Seviyeyi sıfırla ama ismi koru
    USERS[user_id]['level'] = 1
    USERS[user_id]['lives'] = 6
    USERS[user_id]['guessed'] = []
    start_new_level(user_id)
    return get_state()

@app.route('/api/update_name', methods=['POST'])
def update_name():
    user_id = request.cookies.get('user_id')
    new_name = request.json.get('name')
    if new_name:
        USERS[user_id]['name'] = new_name
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)