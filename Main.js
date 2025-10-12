// Get main elements
const uploader = document.getElementById('uploader');
const results = document.getElementById('results');
const checkBtn = document.getElementById('checkBtn');
const clearBtn = document.getElementById('clearBtn');
const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
const dropArea = document.getElementById('dropArea');
const filePreview = document.getElementById('filePreview');

// --- INITIAL STATE ---
uploader.classList.add('active');
results.classList.remove('active');

// Default tab is "Video"
let currentMode = 'video';
updateUploader('video');

// --- LANGUAGE DROPDOWN ---
const langBtn = document.getElementById('langBtn');
const langMenu = document.getElementById('langMenu');
langMenu.style.display = 'none';

langBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  const isHidden = langMenu.style.display === 'block';
  langMenu.style.display = isHidden ? 'none' : 'block';
  langMenu.setAttribute('aria-hidden', isHidden ? 'true' : 'false');
});

document.addEventListener('click', (e) => {
  if (!langMenu.contains(e.target) && e.target !== langBtn) {
    langMenu.style.display = 'none';
    langMenu.setAttribute('aria-hidden', 'true');
  }
});

langMenu.querySelectorAll('.lang-item').forEach(item => {
  item.addEventListener('click', () => {
    langBtn.innerHTML = `<span class="icon">🌐</span> ${item.textContent} <span class="caret">▾</span>`;
    langMenu.style.display = 'none';
    langMenu.setAttribute('aria-hidden', 'true');
  });
});

// --- TABS ---
const tabs = document.querySelectorAll('.tab');
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const mode = tab.dataset.tab;
    updateUploader(mode);
  });
});

// --- UPDATE UPLOADER BASED ON TAB ---
function updateUploader(mode) {
  currentMode = mode;

  // Reset file input or textarea each time
  dropArea.innerHTML = '';

  if (mode === 'text') {
    // === TEXT MODE ===
    const textArea = document.createElement('textarea');
    textArea.id = 'textInput';
    textArea.placeholder = 'Type or paste text here...';
    textArea.style.width = '100%';
    textArea.style.height = '200px';
    textArea.style.fontSize = '1rem';
    textArea.style.padding = '15px';
    textArea.style.border = '2px dashed #E5A8B8';
    textArea.style.borderRadius = '16px';
    textArea.style.outline = 'none';
    textArea.style.resize = 'vertical';
    dropArea.appendChild(textArea);
  } else {
    // === IMAGE OR VIDEO MODE ===
    const newInput = document.createElement('input');
    newInput.type = 'file';
    newInput.id = 'fileInput';
    newInput.accept = mode === 'image' ? 'image/*' : 'video/*';
    newInput.style.opacity = '0';
    newInput.style.position = 'absolute';
    newInput.style.left = '0';
    newInput.style.top = '0';
    newInput.style.width = '100%';
    newInput.style.height = '100%';
    newInput.style.cursor = 'pointer';
    newInput.zIndex = '5';

    const inner = document.createElement('div');
    inner.className = 'drop-inner';
    inner.innerHTML = `
      <div class="file-preview" id="filePreview">
        <div class="file-icon">
          <span class="icon">${mode === 'image' ? '🖼️' : '📹'}</span>
        </div>
        <div class="file-name" id="fileName">No file selected</div>
        <div class="file-sub">Choose a ${mode} file</div>
      </div>
    `;

    dropArea.appendChild(newInput);
    dropArea.appendChild(inner);

    newInput.addEventListener('change', () => {
      const file = newInput.files[0];
      const nameDisplay = inner.querySelector('#fileName');
      if (file) {
        nameDisplay.textContent = file.name;
      } else {
        nameDisplay.textContent = 'No file selected';
      }
    });
  }
}

// --- CLEAR BUTTON ---
clearBtn.addEventListener('click', () => {
  updateUploader(currentMode);
  uploader.classList.add('active');
  results.classList.remove('active');
});

// --- CHECK BUTTON ---
checkBtn.addEventListener('click', () => {
  const fill = document.getElementById('progressFill');
   uploader.classList.add('active');
  results.classList.add('active');

  const confidence = 91;
  document.getElementById('statusIcon').innerHTML = '<span class="icon">✓</span>';
  document.getElementById('resultHeading').innerHTML = `Likely Human-Created <span class="badge" id="confidenceBadge">Confidence: ${confidence}%</span>`;
  document.getElementById('resultDesc').textContent =
    currentMode === 'text'
      ? 'The writing style appears natural and contextually coherent.'
      : currentMode === 'image'
      ? 'The image shows realistic lighting, proportions, and metadata.'
      : 'The video displays natural motion and authentic audio sync.';

  fill.style.width = '0%';
  setTimeout(() => { fill.style.width = confidence + '%'; }, 100);
});

// --- ACCORDION ---
document.querySelectorAll('.accordion').forEach(acc => {
  const header = acc.querySelector('.acc-header');
  const body = acc.querySelector('.acc-body');
  const symbol = acc.querySelector('.acc-symbol');

  const updateSymbol = () => {
    const isOpen = body.classList.contains('show');
    symbol.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
    symbol.textContent = '^';
  };
  updateSymbol();

  header.addEventListener('click', () => {
    body.classList.toggle('show');
    updateSymbol();
  });
});
