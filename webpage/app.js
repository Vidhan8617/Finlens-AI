const figureColors = {
  revenue: '#4A90D9',
  net_income: '#27AE60',
  gross_profit: '#8E44AD',
  eps: '#E67E22'
};

document.getElementById('file-input').addEventListener('change', function(e) {
  if (e.target.files[0]) uploadFile(e.target.files[0]);
});

const uploadArea = document.getElementById('upload-area');
uploadArea.addEventListener('dragover', e => { e.preventDefault(); uploadArea.classList.add('dragover'); });
uploadArea.addEventListener('dragleave', () => uploadArea.classList.remove('dragover'));
uploadArea.addEventListener('drop', e => {
  e.preventDefault();
  uploadArea.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') uploadFile(file);
});

function uploadFile(file) {
  document.getElementById('upload-area').style.display = 'none';
  document.getElementById('loading').style.display = 'block';
  document.getElementById('results').style.display = 'none';
  document.getElementById('error-msg').style.display = 'none';

  const messages = [
    'Reading PDF pages...',
    'Extracting text...',
    'Searching for financial figures...',
    'Generating charts...',
    'Almost done...'
  ];

  let i = 0;
  const interval = setInterval(() => {
    document.getElementById('loading-text').textContent = messages[Math.min(i++, messages.length - 1)];
  }, 1200);

  const formData = new FormData();
  formData.append('file', file);

  fetch('/analyze', { method: 'POST', body: formData })
    .then(r => r.json())
    .then(data => {
      clearInterval(interval);
      document.getElementById('loading').style.display = 'none';

      if (!data.success) {
        document.getElementById('error-msg').textContent = 'Error: ' + data.error;
        document.getElementById('error-msg').style.display = 'block';
        document.getElementById('upload-area').style.display = 'block';
        return;
      }

      showResults(data);
    })
    .catch(() => {
      clearInterval(interval);
      document.getElementById('loading').style.display = 'none';
      document.getElementById('error-msg').textContent = 'Something went wrong. Is the server running?';
      document.getElementById('error-msg').style.display = 'block';
      document.getElementById('upload-area').style.display = 'block';
    });
}

function showResults(data) {
  document.getElementById('res-filename').textContent = data.filename;
  document.getElementById('res-time').textContent = 'Extracted at ' + data.extracted_at;
  document.getElementById('stat-pages').textContent = data.total_pages;
  document.getElementById('stat-text-pages').textContent = data.pages_with_text;
  document.getElementById('stat-figures').textContent = Object.keys(data.financials).length;

  const list = document.getElementById('figures-list');
  list.innerHTML = '';

  if (Object.keys(data.financials).length === 0) {
    list.innerHTML = '<p class="no-data">No financial figures found in this PDF.<br>Try a different report.</p>';
  } else {
    for (const [key, val] of Object.entries(data.financials)) {
      const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      const color = figureColors[key] || '#999';
      list.innerHTML += `
        <div class="figure-row">
          <div class="figure-label">
            <div class="figure-dot" style="background:${color}"></div>
            ${label}
          </div>
          <div class="figure-value" style="color:${color}">${val}</div>
        </div>`;
    }
  }

  if (data.chart) {
    document.getElementById('chart-img').src = 'data:image/png;base64,' + data.chart;
    document.getElementById('chart-section').style.display = 'block';
  } else {
    document.getElementById('chart-section').style.display = 'none';
  }

  document.getElementById('pdf-preview').src = 'data:image/png;base64,' + data.preview;
  document.getElementById('results').style.display = 'block';
}

function resetUI() {
  document.getElementById('results').style.display = 'none';
  document.getElementById('upload-area').style.display = 'block';
  document.getElementById('file-input').value = '';
}