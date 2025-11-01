import folium
from folium import MacroElement
from branca.element import Template


class DeliveryRouterUI(MacroElement):
    """Custom UI panel and routing functionality for delivery system"""

    _template = Template("""
        {% macro script(this, kwargs) %}

        // Global variables
        var pickupMarker = null;
        var deliveryMarker = null;
        var routeLine = null;
        var animationMarker = null;
        var routeCoordinates = [];
        var animationInterval = null;
        var currentAnimationIndex = 0;
        var clickMode = 'pickup'; // 'pickup', 'delivery', or 'none'
        var userLocation = null;

        // Initialize UI after map is ready
        document.addEventListener('DOMContentLoaded', function() {
            console.log('DOM loaded, initializing UI...');
            initializeUI();
            getUserLocation();
            setupMapClickHandler();
        });

        function getUserLocation() {
            if (navigator.geolocation) {
                console.log('Requesting user location...');
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        userLocation = [position.coords.latitude, position.coords.longitude];
                        {{ this._parent.get_name() }}.setView(userLocation, 13);
                        console.log('User location found:', userLocation);
                        showStatus('📍 Using your current location', 'success');

                        // Add a marker for user's location
                        L.marker(userLocation, {
                            icon: L.divIcon({
                                html: '<div style="background:#9b59b6;color:white;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;border:2px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3)">👤</div>',
                                iconSize: [30, 30],
                                className: 'user-location-marker'
                            })
                        }).bindPopup('Your current location').addTo({{ this._parent.get_name() }});
                    },
                    function(error) {
                        console.log('Geolocation error:', error.message);
                        showStatus('Using default location (Delhi)', 'info');
                        // Map will stay at default Delhi location
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 5000,
                        maximumAge: 0
                    }
                );
            } else {
                console.log('Geolocation not supported');
                showStatus('Geolocation not supported. Using Delhi.', 'info');
            }
        }

        function setupMapClickHandler() {
            {{ this._parent.get_name() }}.on('click', function(e) {
                if (clickMode === 'pickup') {
                    setPickupLocation(e.latlng.lat, e.latlng.lng, 
                        'Pickup: ' + e.latlng.lat.toFixed(4) + ', ' + e.latlng.lng.toFixed(4));
                    clickMode = 'delivery';
                    showStatus('📦 Now click to set DELIVERY location', 'info');
                    updateClickModeUI();
                } else if (clickMode === 'delivery') {
                    setDeliveryLocation(e.latlng.lat, e.latlng.lng, 
                        'Delivery: ' + e.latlng.lat.toFixed(4) + ', ' + e.latlng.lng.toFixed(4));
                    clickMode = 'none';
                    showStatus('✅ Both locations set! Calculate route now.', 'success');
                    updateClickModeUI();

                    // Enable route button
                    if (pickupMarker && deliveryMarker) {
                        document.getElementById('route-btn').disabled = false;
                    }
                }
            });
        }

        function updateClickModeUI() {
            var modeIndicator = document.getElementById('click-mode-indicator');
            var toggleBtn = document.getElementById('toggle-click-mode-btn');

            if (clickMode === 'pickup') {
                modeIndicator.innerHTML = '🖱️ Click mode: <strong style="color:#27ae60">PICKUP</strong>';
                modeIndicator.style.display = 'block';
                toggleBtn.textContent = '⏸️ Disable Click Mode';
                toggleBtn.className = 'btn btn-danger';
            } else if (clickMode === 'delivery') {
                modeIndicator.innerHTML = '🖱️ Click mode: <strong style="color:#e74c3c">DELIVERY</strong>';
                modeIndicator.style.display = 'block';
                toggleBtn.textContent = '⏸️ Disable Click Mode';
                toggleBtn.className = 'btn btn-danger';
            } else {
                modeIndicator.style.display = 'none';
                toggleBtn.textContent = '🖱️ Enable Click Mode';
                toggleBtn.className = 'btn btn-primary';
            }
        }

        function toggleClickMode() {
            if (clickMode === 'none') {
                clickMode = 'pickup';
                showStatus('📍 Click on map to set PICKUP location', 'info');
            } else {
                clickMode = 'none';
                showStatus('Click mode disabled', 'info');
            }
            updateClickModeUI();
        }

        function initializeUI() {
            console.log('Initializing UI...');

            // Add custom CSS
            var style = document.createElement('style');
            style.textContent = `
                .control-panel {
                    position: fixed;
                    top: 10px;
                    right: 10px;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    z-index: 1000;
                    width: 340px;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    max-height: 90vh;
                    overflow-y: auto;
                }
                .control-panel h2 {
                    margin: 0 0 15px 0;
                    color: #2c3e50;
                    font-size: 20px;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                .control-group {
                    margin-bottom: 15px;
                }
                .control-group label {
                    display: block;
                    font-weight: 600;
                    margin-bottom: 5px;
                    color: #34495e;
                    font-size: 14px;
                }
                .control-group input {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    font-size: 14px;
                    box-sizing: border-box;
                }
                .control-group input:focus {
                    outline: none;
                    border-color: #3498db;
                    box-shadow: 0 0 0 2px rgba(52,152,219,0.2);
                }
                .btn {
                    width: 100%;
                    padding: 12px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.3s;
                    margin-top: 10px;
                }
                .btn-primary {
                    background: #3498db;
                    color: white;
                }
                .btn-primary:hover {
                    background: #2980b9;
                    transform: translateY(-1px);
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                .btn-success {
                    background: #27ae60;
                    color: white;
                }
                .btn-success:hover {
                    background: #229954;
                }
                .btn-danger {
                    background: #e74c3c;
                    color: white;
                }
                .btn-danger:hover {
                    background: #c0392b;
                }
                .btn:disabled {
                    background: #95a5a6;
                    cursor: not-allowed;
                    transform: none;
                }
                .info-box {
                    background: #ecf0f1;
                    padding: 12px;
                    border-radius: 5px;
                    margin-top: 15px;
                    font-size: 13px;
                }
                .info-box div {
                    margin: 5px 0;
                    color: #2c3e50;
                }
                .info-box strong {
                    color: #2980b9;
                }
                .status-message {
                    margin-top: 10px;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 13px;
                    text-align: center;
                }
                .status-success {
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                }
                .status-error {
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f5c6cb;
                }
                .status-info {
                    background: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                }
                .click-mode-indicator {
                    background: #fff3cd;
                    color: #856404;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                    text-align: center;
                    font-size: 13px;
                    border: 2px dashed #ffc107;
                    animation: blink 1.5s infinite;
                }
                @keyframes blink {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                }
                .divider {
                    text-align: center;
                    margin: 15px 0;
                    color: #7f8c8d;
                    font-size: 12px;
                    position: relative;
                }
                .divider::before,
                .divider::after {
                    content: '';
                    position: absolute;
                    top: 50%;
                    width: 42%;
                    height: 1px;
                    background: #ddd;
                }
                .divider::before {
                    left: 0;
                }
                .divider::after {
                    right: 0;
                }
            `;
            document.head.appendChild(style);

            // Create UI panel
            var panel = document.createElement('div');
            panel.className = 'control-panel';
            panel.innerHTML = `
                <h2>🚚 Delivery Router Pro</h2>

                <button class="btn btn-primary" id="toggle-click-mode-btn" onclick="toggleClickMode()">
                    🖱️ Enable Click Mode
                </button>

                <div class="click-mode-indicator" id="click-mode-indicator" style="display:none;">
                    🖱️ Click mode: <strong>PICKUP</strong>
                </div>

                <div class="divider">OR USE SEARCH</div>

                <div class="control-group">
                    <label>📍 Pickup Location</label>
                    <input type="text" id="pickup-input" placeholder="Enter pickup address or place...">
                    <button class="btn btn-primary" onclick="searchLocation('pickup')">Search Pickup</button>
                </div>

                <div class="control-group">
                    <label>📦 Delivery Location</label>
                    <input type="text" id="delivery-input" placeholder="Enter delivery address or place...">
                    <button class="btn btn-primary" onclick="searchLocation('delivery')">Search Delivery</button>
                </div>

                <button class="btn btn-success" onclick="calculateRoute()" id="route-btn" disabled>
                    📏 Calculate Route
                </button>

                <button class="btn btn-success" onclick="startAnimation()" id="animate-btn" disabled>
                    🎬 Start Delivery Animation
                </button>

                <button class="btn btn-danger" onclick="clearAll()">
                    🗑️ Clear All
                </button>

                <div id="status-message"></div>

                <div class="info-box" id="route-info" style="display:none;">
                    <div><strong>Distance:</strong> <span id="distance">-</span></div>
                    <div><strong>Duration:</strong> <span id="duration">-</span></div>
                    <div><strong>ETA:</strong> <span id="eta">-</span></div>
                </div>
            `;
            document.body.appendChild(panel);

            // Start with click mode enabled by default
            clickMode = 'pickup';
            updateClickModeUI();
            showStatus('📍 Click on map to set PICKUP location', 'info');

            console.log('UI initialized successfully');
        }

        function showStatus(message, type) {
            var statusDiv = document.getElementById('status-message');
            statusDiv.className = 'status-message status-' + type;
            statusDiv.textContent = message;
            statusDiv.style.display = 'block';

            if (type !== 'error' && type !== 'info') {
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 4000);
            }
        }

        async function searchLocation(locationType) {
            var inputId = locationType + '-input';
            var query = document.getElementById(inputId).value.trim();

            if (!query) {
                showStatus('Please enter a location', 'error');
                return;
            }

            showStatus('Searching...', 'info');

            try {
                var url = 'https://nominatim.openstreetmap.org/search?format=json&q=' + 
                          encodeURIComponent(query) + '&limit=1';

                var response = await fetch(url, {
                    headers: {
                        'User-Agent': 'DeliveryRouterPro/1.0'
                    }
                });

                var data = await response.json();

                if (data.length === 0) {
                    showStatus('Location not found. Try a different search.', 'error');
                    return;
                }

                var lat = parseFloat(data[0].lat);
                var lon = parseFloat(data[0].lon);
                var displayName = data[0].display_name;

                if (locationType === 'pickup') {
                    setPickupLocation(lat, lon, displayName);
                } else {
                    setDeliveryLocation(lat, lon, displayName);
                }

                showStatus('Location found!', 'success');

                // Enable route button if both locations are set
                if (pickupMarker && deliveryMarker) {
                    document.getElementById('route-btn').disabled = false;
                }

            } catch (error) {
                console.error('Search error:', error);
                showStatus('Search failed. Please try again.', 'error');
            }
        }

        function setPickupLocation(lat, lon, name) {
            // Remove old marker
            if (pickupMarker) {
                {{ this._parent.get_name() }}.removeLayer(pickupMarker);
            }

            // Create custom icon
            var pickupIcon = L.divIcon({
                html: '<div style="background:#27ae60;color:white;width:35px;height:35px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;border:3px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3)">📍</div>',
                iconSize: [35, 35],
                className: 'custom-marker'
            });

            pickupMarker = L.marker([lat, lon], {icon: pickupIcon})
                .bindPopup('<b>Pickup Location</b><br>' + name)
                .addTo({{ this._parent.get_name() }});

            {{ this._parent.get_name() }}.setView([lat, lon], 13);
        }

        function setDeliveryLocation(lat, lon, name) {
            // Remove old marker
            if (deliveryMarker) {
                {{ this._parent.get_name() }}.removeLayer(deliveryMarker);
            }

            // Create custom icon
            var deliveryIcon = L.divIcon({
                html: '<div style="background:#e74c3c;color:white;width:35px;height:35px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;border:3px solid white;box-shadow:0 2px 5px rgba(0,0,0,0.3)">📦</div>',
                iconSize: [35, 35],
                className: 'custom-marker'
            });

            deliveryMarker = L.marker([lat, lon], {icon: deliveryIcon})
                .bindPopup('<b>Delivery Location</b><br>' + name)
                .addTo({{ this._parent.get_name() }});

            {{ this._parent.get_name() }}.setView([lat, lon], 13);
        }

        async function calculateRoute() {
            if (!pickupMarker || !deliveryMarker) {
                showStatus('Please set both pickup and delivery locations', 'error');
                return;
            }

            showStatus('Calculating route...', 'info');

            var pickupLatLng = pickupMarker.getLatLng();
            var deliveryLatLng = deliveryMarker.getLatLng();

            try {
                var url = 'https://router.project-osrm.org/route/v1/driving/' +
                          pickupLatLng.lng + ',' + pickupLatLng.lat + ';' +
                          deliveryLatLng.lng + ',' + deliveryLatLng.lat +
                          '?overview=full&geometries=geojson';

                var response = await fetch(url);
                var data = await response.json();

                if (data.code !== 'Ok') {
                    showStatus('Route calculation failed', 'error');
                    return;
                }

                // Remove old route
                if (routeLine) {
                    {{ this._parent.get_name() }}.removeLayer(routeLine);
                }

                // Get route coordinates
                var geometry = data.routes[0].geometry.coordinates;
                routeCoordinates = geometry.map(coord => [coord[1], coord[0]]);

                // Draw route
                routeLine = L.polyline(routeCoordinates, {
                    color: '#3498db',
                    weight: 5,
                    opacity: 0.7,
                    lineJoin: 'round'
                }).addTo({{ this._parent.get_name() }});

                // Fit bounds
                {{ this._parent.get_name() }}.fitBounds(routeLine.getBounds(), {padding: [50, 50]});

                // Update info
                var distance = (data.routes[0].distance / 1000).toFixed(2);
                var duration = Math.round(data.routes[0].duration / 60);
                var eta = new Date(Date.now() + data.routes[0].duration * 1000);

                document.getElementById('distance').textContent = distance + ' km';
                document.getElementById('duration').textContent = duration + ' mins';
                document.getElementById('eta').textContent = eta.toLocaleTimeString();
                document.getElementById('route-info').style.display = 'block';

                document.getElementById('animate-btn').disabled = false;

                showStatus('Route calculated successfully!', 'success');

            } catch (error) {
                console.error('Routing error:', error);
                showStatus('Failed to calculate route', 'error');
            }
        }

        function startAnimation() {
            if (routeCoordinates.length === 0) {
                showStatus('Please calculate a route first', 'error');
                return;
            }

            // Stop any existing animation
            if (animationInterval) {
                clearInterval(animationInterval);
            }

            // Remove old animation marker
            if (animationMarker) {
                {{ this._parent.get_name() }}.removeLayer(animationMarker);
            }

            currentAnimationIndex = 0;

            // Create delivery vehicle icon
            var vehicleIcon = L.divIcon({
                html: '<div style="background:#f39c12;color:white;width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;border:3px solid white;box-shadow:0 3px 8px rgba(0,0,0,0.4)">🚚</div>',
                iconSize: [40, 40],
                className: 'vehicle-marker'
            });

            animationMarker = L.marker(routeCoordinates[0], {icon: vehicleIcon})
                .bindPopup('🚚 Delivery in progress...')
                .addTo({{ this._parent.get_name() }});

            animationMarker.openPopup();

            showStatus('Delivery animation started!', 'success');

            // Animate along route
            var speed = 50; // milliseconds per step
            animationInterval = setInterval(() => {
                currentAnimationIndex++;

                if (currentAnimationIndex >= routeCoordinates.length) {
                    clearInterval(animationInterval);
                    animationMarker.setPopupContent('✅ Delivery completed!');
                    animationMarker.openPopup();
                    showStatus('Delivery completed!', 'success');
                    return;
                }

                var nextPos = routeCoordinates[currentAnimationIndex];
                animationMarker.setLatLng(nextPos);

                // Update popup with progress
                var progress = Math.round((currentAnimationIndex / routeCoordinates.length) * 100);
                animationMarker.setPopupContent('🚚 Delivery progress: ' + progress + '%');

            }, speed);
        }

        function clearAll() {
            // Clear markers
            if (pickupMarker) {
                {{ this._parent.get_name() }}.removeLayer(pickupMarker);
                pickupMarker = null;
            }
            if (deliveryMarker) {
                {{ this._parent.get_name() }}.removeLayer(deliveryMarker);
                deliveryMarker = null;
            }
            if (routeLine) {
                {{ this._parent.get_name() }}.removeLayer(routeLine);
                routeLine = null;
            }
            if (animationMarker) {
                {{ this._parent.get_name() }}.removeLayer(animationMarker);
                animationMarker = null;
            }

            // Stop animation
            if (animationInterval) {
                clearInterval(animationInterval);
                animationInterval = null;
            }

            // Clear inputs
            document.getElementById('pickup-input').value = '';
            document.getElementById('delivery-input').value = '';

            // Hide info
            document.getElementById('route-info').style.display = 'none';

            // Disable buttons
            document.getElementById('route-btn').disabled = true;
            document.getElementById('animate-btn').disabled = false;

            // Reset coordinates
            routeCoordinates = [];
            currentAnimationIndex = 0;

            // Reset click mode
            clickMode = 'pickup';
            updateClickModeUI();
            showStatus('📍 Click on map to set PICKUP location', 'info');

            // Reset map view to user location or Delhi
            if (userLocation) {
                {{ this._parent.get_name() }}.setView(userLocation, 13);
            } else {
                {{ this._parent.get_name() }}.setView([28.6139, 77.2090], 11);
            }
        }

        {% endmacro %}
    """)

    def __init__(self):
        super(DeliveryRouterUI, self).__init__()
        self._name = 'DeliveryRouterUI'


def create_delivery_map():
    """Create and save the delivery routing map"""

    print("Creating enhanced delivery routing system...")

    # Create base map centered on Delhi, India (fallback location)
    delivery_map = folium.Map(
        location=[28.6139, 77.2090],  # Delhi coordinates (fallback)
        zoom_start=11,
        tiles='OpenStreetMap',
        control_scale=True,
        prefer_canvas=True
    )

    # Add the custom UI and functionality
    delivery_ui = DeliveryRouterUI()
    delivery_map.add_child(delivery_ui)

    # Save the map
    output_file = 'delivery_router_pro.html'
    delivery_map.save(output_file)

    print(f"✓ Map saved successfully to: {output_file}")
    print(f"\n🎉 NEW FEATURES:")
    print(f"  ✅ Click on map to set locations (no typing needed!)")
    print(f"  ✅ Auto-detects your live GPS location")
    print(f"\n📖 How to use:")
    print(f"  1. Open {output_file} in your web browser")
    print(f"  2. Allow location access when prompted (optional)")
    print(f"  3. Click mode is enabled by default:")
    print(f"     - First click = Pickup location 📍")
    print(f"     - Second click = Delivery location 📦")
    print(f"  4. Or use the search bars for specific addresses")
    print(f"  5. Calculate route and animate delivery!")

    return delivery_map


if __name__ == '__main__':
    create_delivery_map()