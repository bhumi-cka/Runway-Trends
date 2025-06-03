from flask import Flask, render_template_string, request, url_for, send_from_directory
import os
import json
from similarities import get_similarities
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)

# Configuration
IMAGE_FOLDER = "static/images"  # Change this to your local image directory
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# Labels from base.py
labels1 = {
    'components': ['dress', 'skirt', 'top', 'shirt', 'jacket'],
    'color': ['green', 'black', 'brown', 'burgundy', 'red', 'yellow', 'pink', 'blue'],
    'print': ['animal print', 'floral print', 'geometric print', 'striped print', 'camouflage print', 'abstract print'],
    'style': ['structured', 'flowy', 'oversized', 'ballgown'],
    'length': ['maxi', 'midi', 'mini'],
    'waistline': ['dropped waistline', 'empire waistline'],
    'fabric': ['leather', 'denim', 'lace', 'fur', 'sheer', 'metallic']
}

# Generate all feature labels
labels = []
for component in labels1['components']:
    labels.append(component)
    for key in labels1:
        if key != 'components' and key != 'length':
            li = labels1[key]
            for item in li:
                labels.append(item + f' {component}')

for comp in ['dress', 'skirt']:
    for l in ['mini', 'maxi', 'midi']:
        labels.append(f'{l} {comp}')

# Available options for filtering
designers = ['YSL']
seasons = ['Fall Winter']
years = ['2025']
shows = ['Paris']

# Cache for image features
image_features_cache = {}

def get_image_features(image_path):
    """Extract features from an image or get from cache"""
    if image_path in image_features_cache:
        return image_features_cache[image_path]
    
    try:
        similarities = get_similarities(image_path, labels)
        features = []
        
        for i, feature in enumerate(labels):
            if similarities[i].item() > 20:  # Threshold from base.py
                features.append(feature)
        
        image_features_cache[image_path] = features
        return features
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return []

def get_image_base64(image_path):
    """Convert image to base64 for embedding in HTML"""
    try:
        img = Image.open(image_path)
        # Resize for thumbnail - reduced size to fit better in cards
        img.thumbnail((400, 400))
        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=95)
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        print(f"Error converting image {image_path}: {e}")
        return ""

def scan_image_directory():
    """Scan the image directory and extract features"""
    all_images = []
    
    for designer in designers:
        for season in seasons:
            for year in years:
                for show in shows:
                    dir_path = os.path.join(IMAGE_FOLDER, f"{designer} {season} {year} {show}")
                    
                    if not os.path.exists(dir_path):
                        continue
                        
                    for filename in os.listdir(dir_path):
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_path = os.path.join(dir_path, filename)
                            features = get_image_features(image_path)
                            
                            all_images.append({
                                'path': image_path,
                                'filename': filename,
                                'designer': designer,
                                'season': season,
                                'year': year,
                                'show': show,
                                'features': features,
                                'base64': get_image_base64(image_path)
                            })
    
    return all_images

# HTML template with inline CSS
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>RUNWAY TRENDS</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            color: #212529;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            padding: 60px 20px 40px;
            background: linear-gradient(135deg, #000000 0%, #434343 100%);
            color: white;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-family: 'Playfair Display', serif;
            font-size: 3.5rem;
            font-weight: 700;
            letter-spacing: 3px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        
        .header p {
            font-size: 1.1rem;
            font-weight: 300;
            letter-spacing: 1px;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        .filters {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 50px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            border: 1px solid #e9ecef;
        }
        
        .main-filters {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }
        
        .filter-group {
            position: relative;
        }
        
        .filter-label {
            display: block;
            font-size: 0.9rem;
            font-weight: 500;
            color: #495057;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .filter-select {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            background: white;
            font-size: 1rem;
            font-family: 'Inter', sans-serif;
            color: #495057;
            transition: all 0.3s ease;
            appearance: none;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 12px center;
            background-repeat: no-repeat;
            background-size: 16px;
            padding-right: 45px;
            height: 45px;
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #000000;
            box-shadow: 0 0 0 3px rgba(0,0,0,0.1);
        }
        
        .filter-select:hover {
            border-color: #adb5bd;
        }
        
        .features-section {
            border-top: 1px solid #e9ecef;
            padding-top: 30px;
        }
        
        .features-label {
            font-size: 1.1rem;
            font-weight: 500;
            color: #495057;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .selected-features {
            min-height: 50px;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            background: #f8f9fa;
            margin-bottom: 15px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            align-items: flex-start;
        }
        
        .selected-features:empty::before {
            content: "No features selected";
            color: #6c757d;
            font-style: italic;
        }
        
        .selected-feature-tag {
            background: linear-gradient(135deg, #000000 0%, #434343 100%);
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .selected-feature-tag:hover {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            transform: translateY(-1px);
        }
        
        .selected-feature-tag::after {
            content: "×";
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .features-select {
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            background: white;
            font-size: 1rem;
            font-family: 'Inter', sans-serif;
            color: #495057;
            transition: all 0.3s ease;
            height: 60px;
        }
        
        .features-select:focus {
            outline: none;
            border-color: #000000;
            box-shadow: 0 0 0 3px rgba(0,0,0,0.1);
        }
        
        .action-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 30px;
        }
        
        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Inter', sans-serif;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #000000 0%, #434343 100%);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .btn-secondary {
            background: white;
            color: #495057;
            border: 2px solid #e9ecef;
        }
        
        .btn-secondary:hover {
            background: #f8f9fa;
            border-color: #adb5bd;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 30px;
            margin-bottom: 60px;
        }
        
        .image-card {
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border: 1px solid #f8f9fa;
        }
        
        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
        }
        
        .image-container {
            height: 400px;
            overflow: hidden;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .image-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }
        
        .image-card:hover .image-container img {
            transform: scale(1.05);
        }
        
        .no-results {
            text-align: center;
            padding: 100px 20px;
            color: #6c757d;
        }
        
        .no-results h3 {
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            margin-bottom: 15px;
            color: #495057;
        }
        
        .no-results p {
            font-size: 1.1rem;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5rem;
            }
            
            .main-filters {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .image-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            
            .filters {
                padding: 25px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Runway Trends</h1>
        <p>Discover the Future of Fashion</p>
    </div>
    
    <div class="container">
        <div class="filters">
            <div class="main-filters">
                <div class="filter-group">
                    <label class="filter-label" for="designer-select">Brand</label>
                    <select id="designer-select" class="filter-select" multiple>
                        {% for designer in designers %}
                        <option value="{{ designer }}" {% if designer in selected_designer %}selected{% endif %}>
                            {{ designer }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label" for="season-select">Season</label>
                    <select id="season-select" class="filter-select" multiple>
                        {% for season in seasons %}
                        <option value="{{ season }}" {% if season in selected_season %}selected{% endif %}>
                            {{ season }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label" for="year-select">Year</label>
                    <select id="year-select" class="filter-select" multiple>
                        {% for year in years %}
                        <option value="{{ year }}" {% if year in selected_year %}selected{% endif %}>
                            {{ year }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label" for="show-select">Show</label>
                    <select id="show-select" class="filter-select" multiple>
                        {% for show in shows %}
                        <option value="{{ show }}" {% if show in selected_show %}selected{% endif %}>
                            {{ show }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="features-section">
                <label class="features-label" for="features-select">Features</label>
                <div id="selected-features" class="selected-features">
                    {% for feature in selected_features %}
                    <span class="selected-feature-tag" onclick="removeFeature('{{ feature }}')">{{ feature }}</span>
                    {% endfor %}
                </div>
                <select id="features-select" class="features-select" onchange="addFeature()">
                    <option value="">Select a feature...</option>
                    {% for feature in labels %}
                    <option value="{{ feature }}">{{ feature }}</option>
                    {% endfor %}
                </select>
            </div>
            
            <div class="action-buttons">
                <button class="btn btn-primary" onclick="applyFilters()">Apply Filters</button>
                <button class="btn btn-secondary" onclick="clearFilters()">Clear All</button>
            </div>
        </div>
        
        <div class="image-grid">
            {% if filtered_images %}
                {% for image in filtered_images %}
                <div class="image-card">
                    <div class="image-container">
                        <img src="data:image/jpeg;base64,{{ image.base64 }}" alt="{{ image.filename }}">
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-results">
                    <h3>No Collections Found</h3>
                    <p>Try adjusting your filters to discover more runway looks</p>
                </div>
            {% endif %}
        </div>
    </div>
    
    <script>
        let selectedFeatures = [{% for feature in selected_features %}'{{ feature }}'{% if not loop.last %},{% endif %}{% endfor %}];
        
        function addFeature() {
            const select = document.getElementById('features-select');
            const feature = select.value;
            
            if (feature && !selectedFeatures.includes(feature)) {
                selectedFeatures.push(feature);
                updateSelectedFeaturesDisplay();
            }
            
            select.value = '';
        }
        
        function removeFeature(feature) {
            selectedFeatures = selectedFeatures.filter(f => f !== feature);
            updateSelectedFeaturesDisplay();
        }
        
        function updateSelectedFeaturesDisplay() {
            const container = document.getElementById('selected-features');
            container.innerHTML = '';
            
            selectedFeatures.forEach(feature => {
                const tag = document.createElement('span');
                tag.className = 'selected-feature-tag';
                tag.textContent = feature;
                tag.onclick = () => removeFeature(feature);
                container.appendChild(tag);
            });
        }
        
        function applyFilters() {
            const selectedDesigners = Array.from(document.getElementById('designer-select').selectedOptions)
                .map(option => option.value);
            const selectedSeasons = Array.from(document.getElementById('season-select').selectedOptions)
                .map(option => option.value);
            const selectedYears = Array.from(document.getElementById('year-select').selectedOptions)
                .map(option => option.value);
            const selectedShows = Array.from(document.getElementById('show-select').selectedOptions)
                .map(option => option.value);
            
            let url = '/?';
            if (selectedDesigners.length) url += selectedDesigners.map(d => `designer=${encodeURIComponent(d)}`).join('&') + '&';
            if (selectedSeasons.length) url += selectedSeasons.map(s => `season=${encodeURIComponent(s)}`).join('&') + '&';
            if (selectedYears.length) url += selectedYears.map(y => `year=${encodeURIComponent(y)}`).join('&') + '&';
            if (selectedShows.length) url += selectedShows.map(s => `show=${encodeURIComponent(s)}`).join('&') + '&';
            if (selectedFeatures.length) url += selectedFeatures.map(f => `feature=${encodeURIComponent(f)}`).join('&');
            
            window.location.href = url;
        }
        
        function clearFilters() {
            window.location.href = '/';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    # Get filter parameters
    selected_designer = request.args.getlist('designer')
    selected_season = request.args.getlist('season')
    selected_year = request.args.getlist('year')
    selected_show = request.args.getlist('show')
    selected_features = request.args.getlist('feature')
    
    # Scan image directory
    all_images = scan_image_directory()
    
    # Apply filters
    filtered_images = all_images
    
    if selected_designer:
        filtered_images = [img for img in filtered_images if img['designer'] in selected_designer]
    
    if selected_season:
        filtered_images = [img for img in filtered_images if img['season'] in selected_season]
    
    if selected_year:
        filtered_images = [img for img in filtered_images if img['year'] in selected_year]
    
    if selected_show:
        filtered_images = [img for img in filtered_images if img['show'] in selected_show]
    
    if selected_features:
        filtered_images = [img for img in filtered_images if all(feature in img['features'] for feature in selected_features)]
    
    # Render template
    return render_template_string(
        HTML_TEMPLATE,
        designers=designers,
        seasons=seasons,
        years=years,
        shows=shows,
        labels=labels,
        filtered_images=filtered_images,
        selected_designer=selected_designer,
        selected_season=selected_season,
        selected_year=selected_year,
        selected_show=selected_show,
        selected_features=selected_features
    )

if __name__ == '__main__':
    app.run(debug=True)