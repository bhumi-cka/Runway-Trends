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
designers = ['YSL','Chanel','Dior','Balenciaga','Louis Vuitton','Hermès','Givenchy','Valentino']
seasons = ['Spring Summer','Fall Winter']
years = ['2021','2022','2023','2024','2025']
shows = ['Paris','New York','Milan','London']

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
            if similarities[i].item() > 20: 
                features.append(feature.split()[0])
        features=set(features)
        features=list
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
    <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@400;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: #ffffff;
            color: #000000;
            line-height: 1.6;
        }
        
        .header {
            text-align: center;
            padding: 40px 20px 25px;
            background: #000000;
            color: white;
            margin-bottom: 25px;
        }
        
        .header h1 {
            font-family: 'Bodoni Moda', serif;
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 8px;
            text-transform: uppercase;
        }
        
        .header p {
            font-size: 1rem;
            font-weight: 300;
            letter-spacing: 1px;
            opacity: 0.9;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 15px;
        }
        
        .filters {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            border: 1px solid #e9ecef;
            border-top: 3px solid #000000;
        }
        
        .main-filters {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .filter-group {
            position: relative;
        }
        
        .filter-label {
            display: block;
            font-size: 0.8rem;
            font-weight: 500;
            color: #000000;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .filter-select {
            width: 100%;
            padding: 8px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            background: white;
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
            color: #000000;
            transition: all 0.3s ease;
            appearance: none;
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%23000000' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
            background-position: right 10px center;
            background-repeat: no-repeat;
            background-size: 14px;
            padding-right: 35px;
            height: 36px;
        }
        
        .filter-select:focus {
            outline: none;
            border-color: #000000;
            box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
        }
        
        .filter-select:hover {
            border-color: #000000;
        }
        
        .filter-select option:checked {
            background-color: #000000;
            color: white;
        }
        
        .selected-items {
            min-height: 40px;
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            background: #f8f9fa;
            margin-bottom: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: flex-start;
        }
        
        .selected-items:empty::before {
            content: "None selected";
            color: #6c757d;
            font-style: italic;
            font-size: 0.85rem;
        }
        
        .selected-tag {
            background: #000000;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .selected-tag:hover {
            background: #444444;
            transform: translateY(-1px);
        }
        
        .selected-tag::after {
            content: "×";
            font-size: 1rem;
            font-weight: bold;
        }
        
        .features-section {
            border-top: 1px solid #e9ecef;
            padding-top: 20px;
        }
        
        .features-label {
            font-size: 0.9rem;
            font-weight: 500;
            color: #000000;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .selected-features {
            min-height: 40px;
            padding: 10px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            background: #f8f9fa;
            margin-bottom: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: flex-start;
        }
        
        .selected-features:empty::before {
            content: "No features selected";
            color: #6c757d;
            font-style: italic;
            font-size: 0.85rem;
        }
        
        .selected-feature-tag {
            background: #000000;
            color: white;
            padding: 4px 8px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .selected-feature-tag:hover {
            background: #444444;
            transform: translateY(-1px);
        }
        
        .selected-feature-tag::after {
            content: "×";
            font-size: 1rem;
            font-weight: bold;
        }
        
        .features-input-container {
            position: relative;
        }
        
        .features-input {
            width: 100%;
            padding: 8px 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            background: white;
            font-size: 0.9rem;
            font-family: 'Inter', sans-serif;
            color: #000000;
            transition: all 0.3s ease;
            height: 45px;
        }
        
        .features-input:focus {
            outline: none;
            border-color: #000000;
            box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
        }
        
        .features-dropdown {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 2px solid #000000;
            border-top: none;
            border-radius: 0 0 8px 8px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        }
        
        .features-dropdown.show {
            display: block;
        }
        
        .feature-option {
            padding: 10px 15px;
            cursor: pointer;
            transition: all 0.3s ease;
            border-bottom: 1px solid #f8f9fa;
        }
        
        .feature-option:hover,
        .feature-option.highlighted {
            background: #000000;
            color: white;
        }
        
        .feature-option:last-child {
            border-bottom: none;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 20px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Inter', sans-serif;
        }
        
        .btn-primary {
            background: #000000;
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 15px rgba(0, 0, 0, 0.2);
        }
        
        .btn-secondary {
            background: white;
            color: #000000;
            border: 2px solid #e9ecef;
        }
        
        .btn-secondary:hover {
            background: #f8f9fa;
            border-color: #000000;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .image-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 1px solid #f8f9fa;
            border-top: 2px solid #000000;
            height: auto;
        }
        
        .image-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
        }
        
        .image-container {
            padding: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .image-container img {
            max-width: 100%;
            max-height: 280px;
            object-fit: contain;
            transition: transform 0.3s ease;
        }
        
        .image-card:hover .image-container img {
            transform: scale(1.03);
        }
        
        .no-results {
            grid-column: 1 / -1;
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        
        .no-results h3 {
            font-family: 'Bodoni Moda', serif;
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: #000000;
        }
        
        .no-results p {
            font-size: 1rem;
            opacity: 0.8;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2rem;
            }
            
            .main-filters {
                grid-template-columns: 1fr;
                gap: 15px;
            }
            
            .image-grid {
                grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
                gap: 15px;
            }
            
            .filters {
                padding: 20px;
            }
            
            .container {
                padding: 0 10px;
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
                    <div id="selected-designers" class="selected-items">
                        {% for designer in selected_designer %}
                        <span class="selected-tag" onclick="removeDesigner('{{ designer }}')">{{ designer }}</span>
                        {% endfor %}
                    </div>
                    <select id="designer-select" class="filter-select" onchange="addDesigner()">
                        <option value="">Select brand...</option>
                        {% for designer in designers %}
                        <option value="{{ designer }}">{{ designer }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label" for="season-select">Season</label>
                    <div id="selected-seasons" class="selected-items">
                        {% for season in selected_season %}
                        <span class="selected-tag" onclick="removeSeason('{{ season }}')">{{ season }}</span>
                        {% endfor %}
                    </div>
                    <select id="season-select" class="filter-select" onchange="addSeason()">
                        <option value="">Select season...</option>
                        {% for season in seasons %}
                        <option value="{{ season }}">{{ season }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label" for="year-select">Year</label>
                    <div id="selected-years" class="selected-items">
                        {% for year in selected_year %}
                        <span class="selected-tag" onclick="removeYear('{{ year }}')">{{ year }}</span>
                        {% endfor %}
                    </div>
                    <select id="year-select" class="filter-select" onchange="addYear()">
                        <option value="">Select year...</option>
                        {% for year in years %}
                        <option value="{{ year }}">{{ year }}</option>
                        {% endfor %}
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="filter-label" for="show-select">Show</label>
                    <div id="selected-shows" class="selected-items">
                        {% for show in selected_show %}
                        <span class="selected-tag" onclick="removeShow('{{ show }}')">{{ show }}</span>
                        {% endfor %}
                    </div>
                    <select id="show-select" class="filter-select" onchange="addShow()">
                        <option value="">Select show...</option>
                        {% for show in shows %}
                        <option value="{{ show }}">{{ show }}</option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="features-section">
                <label class="features-label" for="features-input">Features</label>
                <div id="selected-features" class="selected-features">
                    {% for feature in selected_features %}
                    <span class="selected-feature-tag" onclick="removeFeature('{{ feature }}')">{{ feature }}</span>
                    {% endfor %}
                </div>
                <div class="features-input-container">
                    <input type="text" id="features-input" class="features-input" placeholder="Type to search features..." 
                           oninput="filterFeatures()" onfocus="showDropdown()">
                    <div id="features-dropdown" class="features-dropdown">
                        {% for feature in labels %}
                        <div class="feature-option" onclick="selectFeature('{{ feature }}')">{{ feature }}</div>
                        {% endfor %}
                    </div>
                </div>
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
        let selectedDesigners = [{% for designer in selected_designer %}'{{ designer }}'{% if not loop.last %},{% endif %}{% endfor %}];
        let selectedSeasons = [{% for season in selected_season %}'{{ season }}'{% if not loop.last %},{% endif %}{% endfor %}];
        let selectedYears = [{% for year in selected_year %}'{{ year }}'{% if not loop.last %},{% endif %}{% endfor %}];
        let selectedShows = [{% for show in selected_show %}'{{ show }}'{% if not loop.last %},{% endif %}{% endfor %}];
        let selectedFeatures = [{% for feature in selected_features %}'{{ feature }}'{% if not loop.last %},{% endif %}{% endfor %}];
        
        const allFeatures = [{% for feature in labels %}'{{ feature }}'{% if not loop.last %},{% endif %}{% endfor %}];
        let filteredFeatures = [...allFeatures];
        let highlightedIndex = -1;
        let dropdownVisible = false;
        
        function addDesigner() {
            const select = document.getElementById('designer-select');
            const designer = select.value;
            
            if (designer && !selectedDesigners.includes(designer)) {
                selectedDesigners.push(designer);
                updateSelectedDesignersDisplay();
            }
            
            select.value = '';
        }
        
        function removeDesigner(designer) {
            selectedDesigners = selectedDesigners.filter(d => d !== designer);
            updateSelectedDesignersDisplay();
        }
        
        function updateSelectedDesignersDisplay() {
            const container = document.getElementById('selected-designers');
            container.innerHTML = '';
            
            selectedDesigners.forEach(designer => {
                const tag = document.createElement('span');
                tag.className = 'selected-tag';
                tag.textContent = designer;
                tag.onclick = () => removeDesigner(designer);
                container.appendChild(tag);
            });
        }
        
        function addSeason() {
            const select = document.getElementById('season-select');
            const season = select.value;
            
            if (season && !selectedSeasons.includes(season)) {
                selectedSeasons.push(season);
                updateSelectedSeasonsDisplay();
            }
            
            select.value = '';
        }
        
        function removeSeason(season) {
            selectedSeasons = selectedSeasons.filter(s => s !== season);
            updateSelectedSeasonsDisplay();
        }
        
        function updateSelectedSeasonsDisplay() {
            const container = document.getElementById('selected-seasons');
            container.innerHTML = '';
            
            selectedSeasons.forEach(season => {
                const tag = document.createElement('span');
                tag.className = 'selected-tag';
                tag.textContent = season;
                tag.onclick = () => removeSeason(season);
                container.appendChild(tag);
            });
        }
        
        function addYear() {
            const select = document.getElementById('year-select');
            const year = select.value;
            
            if (year && !selectedYears.includes(year)) {
                selectedYears.push(year);
                updateSelectedYearsDisplay();
            }
            
            select.value = '';
        }
        
        function removeYear(year) {
            selectedYears = selectedYears.filter(y => y !== year);
            updateSelectedYearsDisplay();
        }
        
        function updateSelectedYearsDisplay() {
            const container = document.getElementById('selected-years');
            container.innerHTML = '';
            
            selectedYears.forEach(year => {
                const tag = document.createElement('span');
                tag.className = 'selected-tag';
                tag.textContent = year;
                tag.onclick = () => removeYear(year);
                container.appendChild(tag);
            });
        }
        
        function addShow() {
            const select = document.getElementById('show-select');
            const show = select.value;
            
            if (show && !selectedShows.includes(show)) {
                selectedShows.push(show);
                updateSelectedShowsDisplay();
            }
            
            select.value = '';
        }
        
        function removeShow(show) {
            selectedShows = selectedShows.filter(s => s !== show);
            updateSelectedShowsDisplay();
        }
        
        function updateSelectedShowsDisplay() {
            const container = document.getElementById('selected-shows');
            container.innerHTML = '';
            
            selectedShows.forEach(show => {
                const tag = document.createElement('span');
                tag.className = 'selected-tag';
                tag.textContent = show;
                tag.onclick = () => removeShow(show);
                container.appendChild(tag);
            });
        }
        
        function filterFeatures() {
            const input = document.getElementById('features-input');
            const query = input.value.toLowerCase();
            
            filteredFeatures = allFeatures.filter(feature => 
                feature.toLowerCase().includes(query)
            );
            
            updateFeaturesDropdown();
            highlightedIndex = -1;
            
            // Show dropdown if not already visible
            showDropdown();
        }
        
        function updateFeaturesDropdown() {
            const dropdown = document.getElementById('features-dropdown');
            dropdown.innerHTML = '';
            
            filteredFeatures.forEach((feature, index) => {
                const option = document.createElement('div');
                option.className = 'feature-option';
                option.textContent = feature;
                option.onclick = function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    selectFeature(feature);
                };
                dropdown.appendChild(option);
            });
        }
        
        function showDropdown() {
            const dropdown = document.getElementById('features-dropdown');
            dropdown.classList.add('show');
            dropdownVisible = true;
            
            // Add event listener to document to close dropdown when clicking outside
            setTimeout(() => {
                document.addEventListener('click', closeDropdownOnClickOutside);
            }, 100);
        }
        
        function closeDropdownOnClickOutside(event) {
            const dropdown = document.getElementById('features-dropdown');
            const input = document.getElementById('features-input');
            
            if (!dropdown.contains(event.target) && event.target !== input) {
                hideDropdown();
            }
        }
        
        function hideDropdown() {
            const dropdown = document.getElementById('features-dropdown');
            dropdown.classList.remove('show');
            dropdownVisible = false;
            document.removeEventListener('click', closeDropdownOnClickOutside);
        }
        
        document.getElementById('features-input').addEventListener('keydown', function(event) {
            const dropdown = document.getElementById('features-dropdown');
            const options = dropdown.querySelectorAll('.feature-option');
            
            if (event.key === 'ArrowDown') {
                event.preventDefault();
                highlightedIndex = Math.min(highlightedIndex + 1, options.length - 1);
                updateHighlight(options);
            } else if (event.key === 'ArrowUp') {
                event.preventDefault();
                highlightedIndex = Math.max(highlightedIndex - 1, -1);
                updateHighlight(options);
            } else if (event.key === 'Enter') {
                event.preventDefault();
                if (highlightedIndex >= 0 && options[highlightedIndex]) {
                    selectFeature(filteredFeatures[highlightedIndex]);
                }
            } else if (event.key === 'Escape') {
                hideDropdown();
            }
        });
        
        function updateHighlight(options) {
            options.forEach((option, index) => {
                option.classList.toggle('highlighted', index === highlightedIndex);
                
                if (index === highlightedIndex) {
                    option.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }
            });
        }
        
        function selectFeature(feature) {
            if (feature && !selectedFeatures.includes(feature)) {
                selectedFeatures.push(feature);
                updateSelectedFeaturesDisplay();
            }
            
            document.getElementById('features-input').value = '';
            filterFeatures();
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
        
        // Initialize features dropdown
        updateFeaturesDropdown();
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