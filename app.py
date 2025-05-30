from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from main import Circuit
import tempfile

app = Flask(__name__)
app.secret_key = 'secret'

circuit = Circuit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_params', methods=['POST'])
def update_params():
    data = request.get_json()
    try:
        global circuit
        circuit = Circuit(
            rows=int(data['rows']),
            row_width=int(data['row_width']),
            row_height=int(data['row_height']),
            max_cells=int(data['max_cells'])
        )
        return jsonify({"status": "success", "message": "Parameters updated"})
    except KeyError as e:
        return jsonify({"status": "error", "message": f"Missing parameter: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/load', methods=['POST'])
def load():
    file = request.files.get('file')
    if file:
        path = 'temp.txt'
        file.save(path)
        circuit.load_file(path)
        flash("File loaded successfully.")
    else:
        flash("No file selected.")
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    if not circuit.loaded:
        flash("Error: No file loaded. Please load a file first.", "error")
        return jsonify({
            "status": "error", 
            "message": "No file loaded. Please load a file first."
        })
    
    id = request.form['id']
    result = circuit.search_cell(id)
    if result:
        message = f"Cell {id} is in row {result[0]} at position x={result[1]}"
        flash(message, "success")
        return jsonify({
            "status": "success",
            "message": message,
            "cell": {
                "id": id, 
                "row": result[0], 
                "x": result[1],
                "found": True
            }
        })
    else:
        message = f"Cell {id} not found."
        flash(message, "error")
        return jsonify({
            "status": "error", 
            "message": message,
            "cell": {"found": False}
        })

@app.route('/insert', methods=['POST'])
def insert():
    if not circuit.loaded:
        flash("Error: No file loaded. Please load a file first.", "error")
        return redirect(url_for('index'))

    id = request.form['id']
    try:
        width = float(request.form['width'])
        height = float(request.form['height'])
        circuit.insert_cell(id, width, height)
        flash(f"Cell {id} inserted successfully.", "success")
    except ValueError as e:
        flash(f"Insertion error: {str(e)}", "error")
    except Exception as e:
        flash(f"Critical error: {str(e)}", "error")
    return redirect(url_for('index'))

@app.route('/remove', methods=['POST'])
def remove():
    if not circuit.loaded:
        flash("Error: No file loaded. Please load a file first.", "error")
        return redirect(url_for('index'))

    id = request.form['id']
    if circuit.remove_cell(id):
        flash(f"Cell {id} removed.", "success")
    else:
        flash(f"Cell {id} not found.", "error")
    return redirect(url_for('index'))

@app.route('/download')
def download():
    if not circuit.loaded:
        flash("Error: No file loaded. Nothing to download.", "error")
        return redirect(url_for('index'))

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8')
    for row in circuit.rows:
        for cell in row:
            temp.write(f"{cell.id} {cell.width} {cell.height}\n")
    temp.close()
    return send_file(temp.name, as_attachment=True, download_name="modified_circuit.txt")

@app.route('/circuit_json')
def circuit_json():
    data = []
    for row_idx, row in enumerate(circuit.rows):
        for cell in row:
            data.append({
                'id': cell.id,
                'x': cell.x,
                'y': row_idx,
                'width': cell.width,
                'height': cell.height
            })
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)