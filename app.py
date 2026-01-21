"""
MCP Server per Umamusume Database.
Espone il database SQLite via HTTP per Claude.
"""

from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Il database viene caricato nella stessa cartella del server
DB_PATH = os.path.join(os.path.dirname(__file__), 'umamusume.db')


def get_db():
    """Connessione al database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Health check e info."""
    return jsonify({
        'status': 'ok',
        'service': 'Umamusume MCP Server',
        'database': os.path.exists(DB_PATH)
    })


@app.route('/query', methods=['POST'])
def query():
    """
    Esegue una query SQL sul database.
    Body: {"sql": "SELECT * FROM support_cards LIMIT 5"}
    """
    try:
        data = request.get_json()
        sql = data.get('sql', '')

        if not sql:
            return jsonify({'error': 'No SQL query provided'}), 400

        # Sicurezza: solo SELECT permessi
        sql_lower = sql.lower().strip()
        if not sql_lower.startswith('select'):
            return jsonify({'error': 'Only SELECT queries allowed'}), 403

        conn = get_db()
        cur = conn.cursor()
        cur.execute(sql)

        # Converti risultati in lista di dizionari
        columns = [desc[0] for desc in cur.description]
        rows = [dict(zip(columns, row)) for row in cur.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'columns': columns,
            'rows': rows,
            'count': len(rows)
        })

    except sqlite3.Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/tables', methods=['GET'])
def tables():
    """Lista tutte le tabelle del database."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cur.fetchall()]
        conn.close()
        return jsonify({'tables': tables})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/schema/<table_name>', methods=['GET'])
def schema(table_name):
    """Schema di una tabella specifica."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table_name})")
        columns = [{'name': row[1], 'type': row[2]} for row in cur.fetchall()]
        conn.close()
        return jsonify({'table': table_name, 'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/info', methods=['GET'])
def info():
    """Restituisce le istruzioni per Claude dalla tabella database_info."""
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT category, key, value, description FROM database_info")
        rows = cur.fetchall()
        conn.close()

        info_dict = {}
        for row in rows:
            cat = row[0]
            if cat not in info_dict:
                info_dict[cat] = []
            info_dict[cat].append({
                'key': row[1],
                'value': row[2],
                'description': row[3]
            })

        return jsonify(info_dict)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
