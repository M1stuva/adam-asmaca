document.addEventListener("DOMContentLoaded", () => {
    initGame();
    createKeyboard();
});

const letters = "ABCÇDEFGĞHİIJKLMNOÖPRSŞTUÜVYZ";

function createKeyboard() {
    const keyboard = document.getElementById('keyboard');
    keyboard.innerHTML = '';
    
    letters.split('').forEach(letter => {
        const btn = document.createElement('button');
        btn.innerText = letter;
        btn.classList.add('key-btn');
        btn.id = `btn-${letter}`;
        btn.onclick = () => guessLetter(letter);
        keyboard.appendChild(btn);
    });
}

function updateUI(data) {
    document.getElementById('username-input').value = data.name;
    document.getElementById('level-badge').innerText = `Seviye ${data.level}`;
    document.getElementById('lives-count').innerText = data.lives;
    document.getElementById('word-display').innerText = data.display_word.join(' ');
    
    // Klavye tuşlarını güncelle
    data.guessed_letters.forEach(letter => {
        const btn = document.getElementById(`btn-${letter}`);
        if(btn) btn.disabled = true;
    });

    // Adam görselini güncelle
    const parts = document.querySelectorAll('.part');
    parts.forEach(p => p.style.display = 'none');
    const errors = 6 - data.lives;
    for(let i=0; i<errors; i++) {
        if(parts[i]) parts[i].style.display = 'block';
    }

    // Oyun bitti mi?
    const controls = document.getElementById('controls');
    const msg = document.getElementById('status-message');
    const nextBtn = document.getElementById('next-level-btn');
    const restartBtn = document.getElementById('restart-btn');

    if (data.victory) {
        msg.innerText = "Tebrikler! Kazandın!";
        msg.style.color = "var(--primary)";
        controls.style.display = 'block';
        nextBtn.style.display = 'inline-block';
        restartBtn.style.display = 'none';
        disableAllKeys();
    } else if (data.game_over) {
        msg.innerText = "Kaybettin! Kelime oydu..."; // Backend'den kelimeyi tam göndermek gerekebilir
        msg.style.color = "var(--danger)";
        controls.style.display = 'block';
        nextBtn.style.display = 'none';
        restartBtn.style.display = 'inline-block';
        disableAllKeys();
    } else {
        msg.innerText = "";
        controls.style.display = 'none';
    }
}

function disableAllKeys() {
    const btns = document.querySelectorAll('.key-btn');
    btns.forEach(b => b.disabled = true);
}

// API ÇAĞRILARI

async function initGame() {
    const res = await fetch('/api/get_state');
    const data = await res.json();
    updateUI(data);
}

async function guessLetter(letter) {
    const res = await fetch('/api/guess', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({letter: letter})
    });
    const data = await res.json();
    updateUI(data);
}

async function nextLevel() {
    const res = await fetch('/api/next_level', {method: 'POST'});
    const data = await res.json();
    createKeyboard(); // Klavyeyi sıfırla
    updateUI(data);
}

async function restartGame() {
    const res = await fetch('/api/restart', {method: 'POST'});
    const data = await res.json();
    createKeyboard();
    updateUI(data);
}

async function updateName() {
    const name = document.getElementById('username-input').value;
    await fetch('/api/update_name', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: name})
    });
    alert("İsim güncellendi!");
}