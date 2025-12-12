from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Conversion Data (Approximate standard sizes)
# Using a list of dictionaries where each dictionary represents a row of equivalent sizes.
# This approach handles the non-linear nature of shoe sizing better than simple formulas.

MENS_SIZES = [
    {"US": 6, "EU": 39, "UK": 5.5, "CM": 24},
    {"US": 6.5, "EU": 39, "UK": 6, "CM": 24.5},
    {"US": 7, "EU": 40, "UK": 6.5, "CM": 25},
    {"US": 7.5, "EU": 40.5, "UK": 7, "CM": 25.5},
    {"US": 8, "EU": 41, "UK": 7.5, "CM": 26},
    {"US": 8.5, "EU": 42, "UK": 8, "CM": 26.5},
    {"US": 9, "EU": 42.5, "UK": 8.5, "CM": 27},
    {"US": 9.5, "EU": 43, "UK": 9, "CM": 27.5},
    {"US": 10, "EU": 44, "UK": 9.5, "CM": 28},
    {"US": 10.5, "EU": 44.5, "UK": 10, "CM": 28.5},
    {"US": 11, "EU": 45, "UK": 10.5, "CM": 29},
    {"US": 11.5, "EU": 45.5, "UK": 11, "CM": 29.5},
    {"US": 12, "EU": 46, "UK": 11.5, "CM": 30},
    {"US": 13, "EU": 47.5, "UK": 12.5, "CM": 31},
    {"US": 14, "EU": 48.5, "UK": 13.5, "CM": 32},
    {"US": 15, "EU": 49.5, "UK": 14.5, "CM": 33}
]

WOMENS_SIZES = [
    {"US": 4, "EU": 35, "UK": 2, "CM": 20.8},
    {"US": 4.5, "EU": 35, "UK": 2.5, "CM": 21.3},
    {"US": 5, "EU": 35.5, "UK": 3, "CM": 21.6},
    {"US": 5.5, "EU": 36, "UK": 3.5, "CM": 22.2},
    {"US": 6, "EU": 36.5, "UK": 4, "CM": 22.5},
    {"US": 6.5, "EU": 37, "UK": 4.5, "CM": 23},
    {"US": 7, "EU": 37.5, "UK": 5, "CM": 23.5},
    {"US": 7.5, "EU": 38, "UK": 5.5, "CM": 23.8},
    {"US": 8, "EU": 38.5, "UK": 6, "CM": 24.1},
    {"US": 8.5, "EU": 39, "UK": 6.5, "CM": 24.6},
    {"US": 9, "EU": 40, "UK": 7, "CM": 25.1},
    {"US": 9.5, "EU": 40.5, "UK": 7.5, "CM": 25.4},
    {"US": 10, "EU": 41, "UK": 8, "CM": 25.9},
    {"US": 10.5, "EU": 42, "UK": 8.5, "CM": 26.2},
    {"US": 11, "EU": 42.5, "UK": 9, "CM": 26.7},
    {"US": 12, "EU": 44, "UK": 10, "CM": 27.6}
]

def find_closest_size(size_data, scale, value):
    """Finds the closest match in the given scale and returns the full row."""
    # Convert input value to float to handle strings like '9' or '9.5'
    try:
        val = float(value)
    except ValueError:
        return None

    closest_match = None
    min_diff = float('inf')

    for row in size_data:
        # Check if the scale exists in this row (it should)
        if scale in row:
            row_val = float(row[scale])
            diff = abs(row_val - val)
            if diff < min_diff:
                min_diff = diff
                closest_match = row
    
    # Optional: Define a threshold? 
    # For shoes, if you input 9.1 and we have 9 and 9.5, 9 is closest. 
    # If the difference is huge (e.g. input 100), it will still return the largest size.
    # We might want to cap it, but for a simple tool, 'closest' is usually fine 
    # or we can return None if diff is too large (> 2 sizes).
    
    if min_diff > 5: # Arbitrary large number to prevent matching garbage
        return None
        
    return closest_match

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    source_scale = data.get('scale') # e.g., 'US', 'EU'
    size_value = data.get('size')    # e.g., 9.5
    gender = data.get('gender')      # 'men' or 'women'

    if not all([source_scale, size_value, gender]):
        return jsonify({"error": "Missing required fields"}), 400

    size_chart = MENS_SIZES if gender == 'men' else WOMENS_SIZES
    
    result = find_closest_size(size_chart, source_scale, size_value)
    
    if result:
        return jsonify({
            "success": True,
            "input": {
                "scale": source_scale,
                "size": size_value,
                "gender": gender
            },
            "conversions": result
        })
    else:
        return jsonify({
            "success": False, 
            "error": "Size out of range or invalid."
        }), 404

if __name__ == '__main__':
    app.run(debug=True)
