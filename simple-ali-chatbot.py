"""Ali Restaurant chatbot - one Python file, no pip packages.
Run: python simple-ali-chatbot.py
Open: http://127.0.0.1:8001
This is a simple rule-based chatbot, not a trained AI model.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import json
import os
import sqlite3

# 1. Create a small database beside this Python file.
DATABASE = Path(os.environ.get('DATABASE_PATH', str(Path(__file__).with_name('simple-ali.db'))))
with sqlite3.connect(DATABASE) as db:
    db.execute('CREATE TABLE IF NOT EXISTS food (name TEXT PRIMARY KEY, price REAL, ingredients TEXT, arabic TEXT)')
    db.executemany('INSERT OR IGNORE INTO food VALUES (?, ?, ?, ?)', [
        ('burger', 8, 'beef, bread, lettuce and tomato', 'برغر'),
        ('pasta', 9, 'pasta, tomato and basil', 'باستا'),
        ('salad', 5, 'lettuce, cucumber and tomato', 'سلطة'),
        ('coffee', 2.5, 'coffee and water', 'قهوة'),
    ])
    db.execute('CREATE TABLE IF NOT EXISTS restaurant (name TEXT PRIMARY KEY, hours TEXT)')
    db.execute('INSERT OR IGNORE INTO restaurant VALUES (?, ?)', ('Ali Restaurant', 'Not supplied yet'))
db.close()


# 2. Match simple questions and answer using the database.
def reply(message, language, selected):
    text = message.lower().strip()
    arabic = language == 'ar'
    def say(english, translation):
        return translation if arabic else english

    with sqlite3.connect(DATABASE) as db:
        foods = db.execute('SELECT * FROM food').fetchall()
        hours = db.execute('SELECT hours FROM restaurant').fetchone()[0]
    db.close()

    # Remember the latest named dish for questions such as "its price".
    for food in foods:
        if food[0] in text or food[3] in text:
            selected = food[0]
    dish = next((food for food in foods if food[0] == selected), None)

    if any(word in text.split() for word in ['hello', 'hi', 'مرحبا', 'اهلا']):
        answer = say('Hello! Welcome to Ali Restaurant. What would you like to know?', 'أهلاً في مطعم علي! ماذا تريد أن تعرف؟')
    elif any(word in text for word in ['thanks', 'thank you', 'شكرا']):
        answer = say('You are welcome!', 'على الرحب والسعة!')
    elif any(word in text for word in ['hours', 'open', 'close', 'ساعات', 'يفتح']):
        answer = say('Opening hours: ' + hours, 'ساعات العمل: ' + ('لم تتم إضافتها بعد' if hours == 'Not supplied yet' else hours))
    elif any(word in text for word in ['address', 'phone', 'delivery', 'عنوان', 'هاتف', 'توصيل']):
        answer = say('That information has not been added yet.', 'لم تتم إضافة هذه المعلومات بعد.')
    elif any(word in text for word in ['vegetarian', 'no meat', "don't eat meat", 'نباتي', 'بدون لحم']):
        answer = say('You could choose pasta or salad. Which one do you prefer?', 'يمكنك اختيار الباستا أو السلطة. أيهما تفضل؟')
        selected = ''
    elif any(word in text for word in ['menu', 'choose', 'hungry', 'قائمة', 'جائع', 'اختيار']):
        answer = '\n'.join(f'{food[3] if arabic else food[0].title()}: ${food[1]:g}' for food in foods)
        selected = ''
    elif any(word in text for word in ['price', 'cost', 'how much', 'سعر', 'كم']):
        answer = say(f'{dish[0].title()} costs ${dish[1]:g}.' if dish else 'Which dish do you mean?', f'سعر {dish[3]} هو ${dish[1]:g}.' if dish else 'أي طبق تقصد؟')
    elif any(word in text for word in ['ingredients', 'contains', 'inside', 'مكونات']):
        # Ingredients are recorded in English to keep the example database small.
        answer = say('Ingredients: ' + dish[2] if dish else 'Which dish do you mean?', 'المكونات المسجلة بالإنجليزية: ' + dish[2] if dish else 'أي طبق تقصد؟')
    elif dish and (dish[0] in text or dish[3] in text):
        answer = say(f'{dish[0].title()} costs ${dish[1]:g}. You can ask about its ingredients.', f'سعر {dish[3]} هو ${dish[1]:g}. يمكنك السؤال عن مكوناته.')
    else:
        answer = say('I help with Ali Restaurant only. Ask about the menu, prices, ingredients or opening hours.', 'أساعدك بمعلومات مطعم علي فقط. اسأل عن القائمة أو الأسعار أو المكونات أو ساعات العمل.')
    return {'answer': answer, 'selected': selected}


# 3. The webpage is inside the same file. Its variables hold temporary memory.
PAGE = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><title>Ali Restaurant Chatbot</title>
<style>
body{font-family:Arial;background:#f3f4f6;max-width:650px;margin:40px auto;padding:20px}
#chat{background:white;min-height:300px;padding:20px;border-radius:10px}
p{white-space:pre-wrap;line-height:1.5}input{width:70%;padding:12px}button,select{padding:12px;margin:5px}
</style>
<h1>Ali Restaurant Chatbot</h1>
<select id="language"><option value="en">English</option><option value="ar">العربية</option></select>
<button onclick="resetChat()">New chat / محادثة جديدة</button>
<div id="chat"></div>
<form id="form"><input id="message" maxlength="500" placeholder="Ask Ali..." required><button id="send">Send</button></form>
<script>
let selected = ''; // Only the latest dish is remembered. Nothing is saved in the browser.
const chat = document.getElementById('chat');
const language = document.getElementById('language');
function addMessage(who, text) {
  const line = document.createElement('p');
  line.textContent = who + ': ' + text;
  chat.appendChild(line);
}
function resetChat() {
  selected = ''; chat.replaceChildren();
  chat.dir = language.value === 'ar' ? 'rtl' : 'ltr';
  addMessage('Ali', language.value === 'ar' ? 'أهلاً! اسألني عن مطعم علي.' : 'Welcome! Ask me about Ali Restaurant.');
}
language.onchange = resetChat;
document.getElementById('form').onsubmit = async function(event) {
  event.preventDefault();
  const input = document.getElementById('message');
  const button = document.getElementById('send');
  const message = input.value.trim();
  if (!message || button.disabled) return;
  button.disabled = true; language.disabled = true;
  addMessage('You', message); input.value = '';
  try {
    const response = await fetch('/chat', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({message, language:language.value, selected})});
    if (!response.ok) throw Error('Request failed');
    const data = await response.json();
    selected = data.selected; addMessage('Ali', data.answer);
  } catch(error) { addMessage('Ali', 'Please try again / حاول مرة أخرى'); }
  button.disabled = false; language.disabled = false; input.focus();
};
resetChat();
</script></html>'''


# 4. A local server displays the page and receives chat messages.
class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/':
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(PAGE.encode('utf-8'))

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if self.path != '/chat' or not 0 < length <= 5000:
                raise ValueError('Invalid request')
            data = json.loads(self.rfile.read(length))
            message = data.get('message')
            if not isinstance(message, str) or not message.strip() or len(message) > 500:
                raise ValueError('Invalid message')
            result = reply(message, data.get('language'), data.get('selected'))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))
        except (ValueError, AttributeError):
            self.send_error(400, 'Invalid message')


if __name__ == '__main__':
    print('Open http://127.0.0.1:8001 - press Ctrl+C to stop.')
    # Docker needs 0.0.0.0 inside the container; normal Python stays local.
    with HTTPServer((os.environ.get('HOST', '127.0.0.1'), 8001), Server) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Chatbot stopped.')
