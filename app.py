from flask import Flask, jsonify
import os
import pymysql

app = Flask(__name__)

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'testuser')
DB_PASS = os.environ.get('DB_PASS', 'testpass')
DB_NAME = os.environ.get('DB_NAME', 'testdb')

@app.route('/')
def index():
    return jsonify(message="Hello from Flask!", db_host=DB_HOST)

@app.route('/count')
def count():
    # Connect to MySQL and show table count (create table if missing)
    try:
        conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME, cursorclass=pymysql.cursors.DictCursor)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS visits (id INT AUTO_INCREMENT PRIMARY KEY, t TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        cur.execute("INSERT INTO visits () VALUES ()")
        conn.commit()
        cur.execute("SELECT COUNT(*) AS cnt FROM visits")
        cnt = cur.fetchone()['cnt']
        cur.close()
        conn.close()
        return jsonify(visits=cnt)
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
