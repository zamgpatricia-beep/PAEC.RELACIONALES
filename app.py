from flask import Flask, render_template, request, url_for
import sqlite3

app = Flask(__name__)

@app.route('/quimica')
def quimica():
    return render_template('quimica.html')

@app.route('/historia')
def historia():
    return render_template('historia.html')

def get_db_connection():
    conn = sqlite3.connect("base_imc.db")
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historial_imc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peso REAL NOT NULL,
            altura INTEGER NOT NULL,
            imc REAL NOT NULL,
            clasificacion TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tips')
def tips():
    return render_template('tips.html')

@app.route('/imc', methods=['GET', 'POST'])
def calcular_imc():
    resultado = None
    nota = None
    imagen_resultado = None  
    historial = [] 

    if request.method == 'POST':
        try:
            peso = float(request.form['peso'])
            altura_cm = float(request.form['altura'])
            altura_m = altura_cm / 100

            if peso > 0 and altura_m > 0:
                imc = peso / (altura_m ** 2)
                imc_redondeado = round(imc, 1)

                if imc_redondeado < 18.5:
                    clasificacion = "Bajo peso"
                    imagen_resultado = "css/img/cuerpo_bajo.jpg"
                elif 18.5 <= imc_redondeado <= 24.9:
                    clasificacion = "Peso normal o saludable"
                    imagen_resultado = "css/img/cuerpo_normal.jpg"
                elif 25.0 <= imc_redondeado <= 29.9:
                    clasificacion = "Sobrepeso"
                    imagen_resultado = "css/img/cuerpo_sobrepeso.jpg"
                elif 30.0 <= imc_redondeado <= 34.9:
                    clasificacion = "Obesidad grado I"
                    imagen_resultado = "css/img/cuerpo_obesidad.jpg"
                elif 35.0 <= imc_redondeado <= 39.9:
                    clasificacion = "Obesidad grado II"
                    imagen_resultado = "css/img/cuerpo_obesidad2.jpg"
                else: 
                    clasificacion = "Obesidad grado III (mórbida)"
                    imagen_resultado = "css/img/cuerpo_obesidad3.jpg"

                resultado = f"Tu IMC es {imc_redondeado} ({clasificacion})."
                nota = "NOTA: El IMC es una medida de referencia, no sustituye un diagnóstico médico."

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO historial_imc (peso, altura, imc, clasificacion) 
                    VALUES (?, ?, ?, ?)
                """, (peso, int(altura_cm), imc_redondeado, clasificacion))
                conn.commit()
                conn.close()

            else:
                resultado = "Por favor, introduce valores mayores a cero."

        except ValueError:
            resultado = "Por favor, introduce valores numéricos válidos."

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT peso, altura, imc, clasificacion, fecha FROM historial_imc ORDER BY fecha DESC LIMIT 10")
        historial = cursor.fetchall()
        conn.close()
    except Exception as e:
        print(f"Error al cargar el historial: {e}")

    return render_template('imc.html', 
                           resultado=resultado, 
                           nota=nota, 
                           imagen_resultado=imagen_resultado, 
                           historial=historial)

if __name__ == '__main__':
    app.run(debug=True)