document.getElementById('imageInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('previewBox').style.display = 'block';
        document.querySelector('.upload-area p').textContent = '✅ ' + file.name;
    };
    reader.readAsDataURL(file);
});

async function predict() {
    const crop  = document.getElementById('cropSelect').value;
    const image = document.getElementById('imageInput').files[0];

    if (!crop)  { showError('⚠️ Please select a crop first'); return; }
    if (!image) { showError('⚠️ Please upload an image first'); return; }

    document.getElementById('resultBox').style.display  = 'none';
    document.getElementById('weatherBox').style.display = 'none';
    document.getElementById('errorBox').style.display   = 'none';
    document.getElementById('loading').style.display    = 'block';
    document.getElementById('predictBtn').disabled      = true;

    const formData = new FormData();
    formData.append('crop', crop);
    formData.append('image', image);

    try {
        const response = await fetch('/predict', { method: 'POST', body: formData });
        const data = await response.json();

        document.getElementById('loading').style.display = 'none';
        document.getElementById('predictBtn').disabled   = false;

        if (data.error) { showError('❌ ' + data.error); return; }

        // Show disease results
        document.getElementById('diseaseName').textContent    = data.disease;
        document.getElementById('treatmentText').textContent  = data.treatment;
        document.getElementById('preventionText').textContent = data.prevention;
        document.getElementById('resultBox').style.display    = 'block';

        // Show weather results
        document.getElementById('weatherTemp').textContent     = data.weather.temperature;
        document.getElementById('weatherHumidity').textContent = data.weather.humidity;
        document.getElementById('weatherRain').textContent     = data.weather.rainfall;
        document.getElementById('weatherDry').textContent      = data.weather.dry_weather;
        document.getElementById('weatherTip').textContent      = data.weather.risk_tip;
        document.getElementById('weatherBox').style.display    = 'block';

        document.getElementById('resultBox').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('predictBtn').disabled   = false;
        showError('❌ Could not connect to server. Make sure Flask is running.');
    }
}

function showError(message) {
    document.getElementById('errorText').textContent  = message;
    document.getElementById('errorBox').style.display = 'block';
    document.getElementById('loading').style.display  = 'none';
    document.getElementById('predictBtn').disabled    = false;
}

function resetForm() {
    document.getElementById('cropSelect').value           = '';
    document.getElementById('imageInput').value           = '';
    document.getElementById('previewBox').style.display   = 'none';
    document.getElementById('resultBox').style.display    = 'none';
    document.getElementById('weatherBox').style.display   = 'none';
    document.getElementById('errorBox').style.display     = 'none';
    document.querySelector('.upload-area p').textContent  = 'Click here to upload image';
}