// Get main elements
const uploader = document.getElementById('uploader');
const results = document.getElementById('results');
const checkBtn = document.getElementById('checkBtn');
const clearBtn = document.getElementById('clearBtn');
const fileInput = document.getElementById('fileInput');
const fileNameDisplay = document.getElementById('fileName');
const dropArea = document.getElementById('dropArea');

// --- INITIAL STATE ---
// We start with the UPLOADER active, so hide the results.
uploader.classList.add('active');
results.classList.remove('active');

// Set initial file name for the uploader 
fileNameDisplay.textContent = 'IMG_0650.MOV'; 


// --- 1. LANGUAGE DROPDOWN ---
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


// --- 2. TABS ---
const tabs = document.querySelectorAll('.tab');
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
    });
});


// --- 3. FILE UPLOAD/CLEAR ---
fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (file) {
        fileNameDisplay.textContent = file.name;
    } else {
        fileNameDisplay.textContent = 'No file selected';
    }
});

clearBtn.addEventListener('click', () => {
    // Reset file input and display
    fileInput.value = '';
    fileNameDisplay.textContent = 'No file selected';
    // Show Uploader, hide Results
    uploader.classList.add('active');
    results.classList.remove('active');
});


// --- 4. SIMULATED DETECTION (Check Content) ---
checkBtn.addEventListener('click', () => {
    const fill = document.getElementById('progressFill');

    // 1. UI Flow: Hide Uploader and show Results
    uploader.classList.remove('active');
    results.classList.add('active');

    // 2. Populate Results (matching Pic2)
    const confidence = 91;
    document.getElementById('statusIcon').innerHTML = '<span class="icon">✓</span>';
    document.getElementById('resultHeading').innerHTML = `Likely Human-Created <span class="badge" id="confidenceBadge">Confidence: ${confidence}%</span>`;
    document.getElementById('resultDesc').textContent = 'The video displays natural motion, consistent lighting across frames, and authentic audio synchronization.';

    // 3. Start Progress Bar animation
    fill.style.width = '0%'; // Reset for effect
    setTimeout(() => { fill.style.width = confidence + '%'; }, 100);
});


// --- 5. ACCORDION ---
document.querySelectorAll('.accordion').forEach(acc => {
    const header = acc.querySelector('.acc-header');
    const body = acc.querySelector('.acc-body');
    const symbol = acc.querySelector('.acc-symbol');
    
    // Set initial symbol state based on the 'show' class
    const updateSymbol = () => {
        const isOpen = body.classList.contains('show');
        symbol.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
        symbol.textContent = '^'; // Always use caret as per design
    };
    
    // Initial check for accordions with 'show' class (acc2 in HTML)
    updateSymbol();

    header.addEventListener('click', () => {
        body.classList.toggle('show');
        updateSymbol();
    });
});