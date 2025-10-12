// ============================================
// MAIN.JS - Backend API Integration
// ============================================

// Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';  // Your FastAPI backend URL

// Language mapping
const LANGUAGE_MAP = {
    'English': 'en',
    'isiZulu': 'zu',
    'isiXhosa': 'xh',
    'Sesotho': 'st',
    'Afrikaans': 'af'
};

let currentLanguage = 'en';
let currentFile = null;
let currentTab = 'video';

// ============================================
// 1. INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Get main elements
    const uploader = document.getElementById('uploader');
    const results = document.getElementById('results');
    const checkBtn = document.getElementById('checkBtn');
    const clearBtn = document.getElementById('clearBtn');
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');
    const dropArea = document.getElementById('dropArea');

    // Initial state
    uploader.classList.add('active');
    results.classList.remove('active');

    // Initialize all features
    initLanguageDropdown();
    initTabs();
    initFileUpload();
    initAccordions();
    
    console.log('✅ Frontend initialized and connected to backend at:', API_BASE_URL);
}

// ============================================
// 2. PAGE TRANSLATION FUNCTIONS (Define early)
// ============================================
async function translatePage(language) {
    try {
        console.log(`🌍 Translating page to ${language}...`);
        
        // Translate UI elements immediately
        translateUIElements(language);
        
        console.log('✅ Page translated successfully to', language);
    } catch (error) {
        console.error('Translation error:', error);
    }
}

function translateUIElements(language) {
    // Complete translations for all supported languages
    const allTranslations = {
        'en': {
            'heroTitle': 'Protect yourself from AI-generated content',
            'heroDesc': 'Analyze text, images, and videos to detect AI-generated content. Get education and insights to protect yourself from misinformation and scams.',
            'tabText': 'Text',
            'tabImage': 'Image',
            'tabVideo': 'Video',
            'checkBtn': 'Check Content',
            'resultsTitle': 'Detection Results',
            'whatYouCanDo': 'What You Can Do',
            'howToSpot': 'How to Spot AI Content',
            'footerText': 'Protecting South African communities from digital deception',
            'fileSelected': 'File selected',
            'noFileSelected': 'No file selected'
        },
        'zu': {
            'heroTitle': 'Zivikele kokuqukethwe okudalwe yi-AI',
            'heroDesc': 'Hlaziya umbhalo, izithombe, namavidiyo ukuthola okuqukethwe okudalwe yi-AI. Thola imfundo nolwazi lokuzivikela ekwaziseni okungalungile nasemakhameni.',
            'tabText': 'Umbhalo',
            'tabImage': 'Isithombe',
            'tabVideo': 'Ividiyo',
            'checkBtn': 'Hlola Okuqukethwe',
            'resultsTitle': 'Imiphumela Yokuhlola',
            'whatYouCanDo': 'Ongakwenza',
            'howToSpot': 'Indlela Yokubona Okuqukethwe Kwe-AI',
            'footerText': 'Sivikela imiphakathi yaseNingizimu Afrika ekukhohliseni kwedijithali',
            'fileSelected': 'Ifayela likhethiwe',
            'noFileSelected': 'Alikho ifayela elikhethiwe'
        },
        'xh': {
            'heroTitle': 'Zikhusele kumxholo oveliswe yi-AI',
            'heroDesc': 'Hlalutya umbhalo, imifanekiso, neevidiyo ukufumanisa umxholo oveliswe yi-AI. Fumana imfundo nolwazi lokuzikhusela kulwazi olungalunganga nakubuqhophololo.',
            'tabText': 'Umbhalo',
            'tabImage': 'Umfanekiso',
            'tabVideo': 'Ividiyo',
            'checkBtn': 'Hlola Umxholo',
            'resultsTitle': 'Iziphumo Zokuhlola',
            'whatYouCanDo': 'Into Onokuyenza',
            'howToSpot': 'Indlela Yokubona Umxholo We-AI',
            'footerText': 'Sikhusela uluntu lwaseMzantsi Afrika ekukhohliseni kwedijithali',
            'fileSelected': 'Ifayile ikhethiwe',
            'noFileSelected': 'Akukho fayile ekhethiweyo'
        },
        'st': {
            'heroTitle': 'Itshireletse ho diteng tse hlahisitsweng ke AI',
            'heroDesc': 'Manollo mongolo, ditshwantsho, le divideo ho fumana diteng tse hlahisitsweng ke AI. Fumana thuto le tsebo ya ho itshireletsa ho tshediso e fosahetseng le dikgoka.',
            'tabText': 'Mongolo',
            'tabImage': 'Setshwantsho',
            'tabVideo': 'Video',
            'checkBtn': 'Hlahloba Diteng',
            'resultsTitle': 'Diphetho tsa Tlhahlobo',
            'whatYouCanDo': 'Seo o ka se etsang',
            'howToSpot': 'Mokhoa wa ho Bona Diteng tsa AI',
            'footerText': 'Ho sireletsa sechaba sa Afrika Borwa ho tsietso ya dijithale',
            'fileSelected': 'Faele e khethilwe',
            'noFileSelected': 'Ha ho faele e khethilweng'
        },
        'af': {
            'heroTitle': 'Beskerm jouself teen KI-gegenereerde inhoud',
            'heroDesc': 'Ontleed teks, beelde en video\'s om KI-gegenereerde inhoud op te spoor. Kry opvoeding en insigte om jouself teen wanligting en boelstreke te beskerm.',
            'tabText': 'Teks',
            'tabImage': 'Beeld',
            'tabVideo': 'Video',
            'checkBtn': 'Kontroleer Inhoud',
            'resultsTitle': 'Opsporingsresultate',
            'whatYouCanDo': 'Wat Jy Kan Doen',
            'howToSpot': 'Hoe om KI-inhoud te Herken',
            'footerText': 'Beskerm Suid-Afrikaanse gemeenskappe teen digitale misleiding',
            'fileSelected': 'Lêer gekies',
            'noFileSelected': 'Geen lêer gekies nie'
        }
    };
    
    const trans = allTranslations[language] || allTranslations['en'];
    
    console.log('Applying translations for:', language);
    
    // 1. Translate hero section
    const protectBtn = document.querySelector('.protect-btn');
    if (protectBtn) {
        protectBtn.innerHTML = `<span class="icon">◎</span> ${trans.heroTitle}`;
        console.log('✓ Translated hero title');
    }
    
    const heroDesc = document.querySelector('.hero-desc');
    if (heroDesc) {
        heroDesc.textContent = trans.heroDesc;
        console.log('✓ Translated hero description');
    }
    
    // 2. Translate tabs
    const textTab = document.querySelector('[data-tab="text"]');
    if (textTab) {
        textTab.innerHTML = `<span class="icon">📄</span> ${trans.tabText}`;
        console.log('✓ Translated text tab');
    }
    
    const imageTab = document.querySelector('[data-tab="image"]');
    if (imageTab) {
        imageTab.innerHTML = `<span class="icon">🖼️</span> ${trans.tabImage}`;
        console.log('✓ Translated image tab');
    }
    
    const videoTab = document.querySelector('[data-tab="video"]');
    if (videoTab) {
        videoTab.innerHTML = `<span class="icon">📹</span> ${trans.tabVideo}`;
        console.log('✓ Translated video tab');
    }
    
    // 3. Translate check button (only if not disabled/processing)
    const checkBtn = document.getElementById('checkBtn');
    if (checkBtn && !checkBtn.disabled) {
        checkBtn.textContent = trans.checkBtn;
        console.log('✓ Translated check button');
    }
    
    // 4. Translate results title
    const resultsTitle = document.querySelector('.results-title');
    if (resultsTitle) {
        resultsTitle.textContent = trans.resultsTitle;
        console.log('✓ Translated results title');
    }
    
    // 5. Translate accordion headers (keep icons and structure)
    const acc1Header = document.querySelector('#acc1 .acc-header');
    if (acc1Header) {
        const iconWrap = acc1Header.querySelector('.header-icon-wrap');
        const symbol = acc1Header.querySelector('.acc-symbol');
        if (iconWrap && symbol) {
            acc1Header.innerHTML = '';
            acc1Header.appendChild(iconWrap);
            acc1Header.appendChild(document.createTextNode(trans.whatYouCanDo + ' '));
            acc1Header.appendChild(symbol);
            console.log('✓ Translated accordion 1');
        }
    }
    
    const acc2Header = document.querySelector('#acc2 .acc-header');
    if (acc2Header) {
        const iconWrap = acc2Header.querySelector('.header-icon-wrap');
        const symbol = acc2Header.querySelector('.acc-symbol');
        if (iconWrap && symbol) {
            acc2Header.innerHTML = '';
            acc2Header.appendChild(iconWrap);
            acc2Header.appendChild(document.createTextNode(trans.howToSpot + ' '));
            acc2Header.appendChild(symbol);
            console.log('✓ Translated accordion 2');
        }
    }
    
    // 6. Translate footer
    const footerPill = document.querySelector('.footer-pill');
    if (footerPill) {
        footerPill.innerHTML = `<span class="icon">◎</span> ${trans.footerText}`;
        console.log('✓ Translated footer');
    }
    
    // 7. Translate file status if visible
    const fileSub = document.querySelector('.file-sub');
    if (fileSub && fileSub.textContent.includes('selected')) {
        const fileName = document.getElementById('fileName');
        if (fileName && fileName.textContent !== 'No file selected') {
            fileSub.textContent = trans.fileSelected;
        } else {
            fileSub.textContent = trans.noFileSelected;
        }
    }
    
    console.log('🎉 All UI elements translated!');
}

// ============================================
// 3. LANGUAGE DROPDOWN
// ============================================
function initLanguageDropdown() {
    const langBtn = document.getElementById('langBtn');
    const langMenu = document.getElementById('langMenu');

    langMenu.style.display = 'none';

    langBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isHidden = langMenu.style.display === 'none';
        langMenu.style.display = isHidden ? 'block' : 'none';
        langMenu.setAttribute('aria-hidden', isHidden ? 'false' : 'true');
    });

    document.addEventListener('click', (e) => {
        if (!langMenu.contains(e.target) && e.target !== langBtn) {
            langMenu.style.display = 'none';
            langMenu.setAttribute('aria-hidden', 'true');
        }
    });

    langMenu.querySelectorAll('.lang-item').forEach(item => {
        item.addEventListener('click', async () => {
            const selectedLang = item.textContent;
            currentLanguage = LANGUAGE_MAP[selectedLang] || 'en';
            
            langBtn.innerHTML = `<span class="icon">🌐</span> ${selectedLang} <span class="caret">▾</span>`;
            langMenu.style.display = 'none';
            langMenu.setAttribute('aria-hidden', 'true');
            
            console.log('Language changed to:', selectedLang, `(${currentLanguage})`);
            
            // Translate the entire page
            await translatePage(currentLanguage);
        });
    });
}

// ============================================
// 4. TABS (Text, Image, Video)
// ============================================
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const fileInput = document.getElementById('fileInput');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            currentTab = tab.getAttribute('data-tab');
            
            // Update file input accept attribute based on tab
            if (currentTab === 'text') {
                fileInput.setAttribute('accept', '.txt,.pdf,.docx,.doc');
            } else if (currentTab === 'image') {
                fileInput.setAttribute('accept', '.jpg,.jpeg,.png,.webp,.bmp');
            } else if (currentTab === 'video') {
                fileInput.setAttribute('accept', '.mp4,.mov,.avi,.mkv,.webm');
            }
            
            console.log('Tab switched to:', currentTab);
        });
    });
}

// ============================================
// 5. FILE UPLOAD
// ============================================
function initFileUpload() {
    const fileInput = document.getElementById('fileInput');
    const fileNameDisplay = document.getElementById('fileName');
    const dropArea = document.getElementById('dropArea');
    const clearBtn = document.getElementById('clearBtn');
    const checkBtn = document.getElementById('checkBtn');
    const uploader = document.getElementById('uploader');
    const results = document.getElementById('results');

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            currentFile = file;
            fileNameDisplay.textContent = file.name;
            
            // Update icon based on file type
            const fileIcon = dropArea.querySelector('.file-icon .icon');
            if (file.type.startsWith('video/')) {
                fileIcon.textContent = '📹';
            } else if (file.type.startsWith('image/')) {
                fileIcon.textContent = '🖼️';
            } else {
                fileIcon.textContent = '📄';
            }
            
            console.log('File selected:', file.name, `(${(file.size / 1024 / 1024).toFixed(2)} MB)`);
        }
    });

    // Clear button
    clearBtn.addEventListener('click', () => {
        fileInput.value = '';
        currentFile = null;
        fileNameDisplay.textContent = 'No file selected';
        uploader.classList.add('active');
        results.classList.remove('active');
        console.log('File cleared');
    });

    // Check Content button - MAIN DETECTION
    checkBtn.addEventListener('click', async () => {
        if (!currentFile) {
            alert('Please select a file first!');
            return;
        }

        // Show loading state
        checkBtn.disabled = true;
        checkBtn.textContent = 'Analyzing...';
        
        try {
            let result;
            
            // Route to appropriate API endpoint based on current tab
            if (currentTab === 'video') {
                result = await analyzeVideo(currentFile);
            } else if (currentTab === 'image') {
                result = await analyzeImage(currentFile);
            } else if (currentTab === 'text') {
                result = await analyzeDocument(currentFile);
            }
            
            // Display results
            displayResults(result);
            
            // Switch to results view
            uploader.classList.remove('active');
            results.classList.add('active');
            
        } catch (error) {
            console.error('Analysis error:', error);
            alert(`Error: ${error.message}`);
        } finally {
            checkBtn.disabled = false;
            checkBtn.textContent = 'Check Content';
        }
    });

    // Drag and drop
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropArea.style.borderColor = '#A5556E';
    });

    dropArea.addEventListener('dragleave', () => {
        dropArea.style.borderColor = '#E5A8B8';
    });

    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        dropArea.style.borderColor = '#E5A8B8';
        
        const file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });
}

// ============================================
// 6. API CALLS - VIDEO DETECTION
// ============================================
async function analyzeVideo(file) {
    const formData = new FormData();
    formData.append('file', file);

    console.log('📹 Analyzing video:', file.name, '(Language:', currentLanguage, ')');

    // Use correct endpoint with language parameter
    const response = await fetch(`${API_BASE_URL}/api/detect-with-audio?language=${currentLanguage}`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Video analysis result:', data);
    
    return {
        type: 'video',
        isAI: data.detection_result.is_ai_generated,
        confidence: data.detection_result.confidence_score,
        message: data.detection_result.message || '',
        warning: data.detection_result.warning || '',
        confidenceLabel: data.detection_result.confidence_label || 'Confidence',
        details: data.video_info,
        hasAudio: data.audio_info?.has_audio || false
    };
}

// ============================================
// 7. API CALLS - IMAGE DETECTION
// ============================================
async function analyzeImage(file) {
    const formData = new FormData();
    formData.append('file', file);

    console.log('🖼️ Analyzing image:', file.name, '(Language:', currentLanguage, ')');

    const response = await fetch(`${API_BASE_URL}/api/detect-image?language=${currentLanguage}`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Image analysis result:', data);
    
    return {
        type: 'image',
        isAI: data.detection_result.is_ai_generated,
        confidence: data.detection_result.confidence_score,
        message: data.detection_result.message || '',
        warning: data.detection_result.warning || '',
        confidenceLabel: data.detection_result.confidence_label || 'Confidence',
        details: data.image_info
    };
}
// ============================================
// 8. API CALLS - DOCUMENT DETECTION
// ============================================
async function analyzeDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    console.log('📄 Analyzing document:', file.name, '(Language:', currentLanguage, ')');

    const response = await fetch(`${API_BASE_URL}/api/detect-document?language=${currentLanguage}`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    console.log('Document analysis result:', data);
    
    return {
        type: 'document',
        isAI: data.detection_result.is_ai_generated,
        confidence: data.detection_result.confidence_score,
        message: data.detection_result.message || '',
        warning: data.detection_result.warning || '',
        confidenceLabel: data.detection_result.confidence_label || 'Confidence',
        details: data.document_info
    };
}

// ============================================
// 9. DISPLAY RESULTS
// ============================================
function displayResults(result) {
    const statusIcon = document.getElementById('statusIcon');
    const resultHeading = document.getElementById('resultHeading');
    const resultDesc = document.getElementById('resultDesc');
    const confidenceBadge = document.getElementById('confidenceBadge');
    const progressFill = document.getElementById('progressFill');
    const resultCard = document.getElementById('resultCard');

    const isAI = result.isAI;
    const confidence = Math.round(result.confidence);
    const customMessage = result.message;
    const warning = result.warning;
    const confidenceLabel = result.confidenceLabel || 'Confidence';

    // Update icon and styling
    if (isAI) {
        // AI-Generated
        statusIcon.innerHTML = '<span class="icon">⚠️</span>';
        statusIcon.style.backgroundColor = '#FFE8E8';
        statusIcon.style.color = '#D32F2F';
        resultCard.classList.remove('human-result');
        resultCard.classList.add('ai-result');
        
        // Use backend message if available, otherwise use default
        const headingText = customMessage || 'Likely AI-Generated';
        resultHeading.innerHTML = `${headingText} <span class="badge" id="confidenceBadge">${confidenceLabel}: ${confidence}%</span>`;
        
        // Use warning message from backend if available
        if (warning) {
            resultDesc.textContent = warning;
        } else {
            // Default description based on content type
            if (result.type === 'video') {
                resultDesc.textContent = 'This video shows patterns consistent with AI generation. Look for unnatural movements, inconsistent lighting, or irregular facial features.';
            } else if (result.type === 'image') {
                resultDesc.textContent = 'This image appears to be AI-generated. Check for distorted hands, unusual textures, or impossible reflections.';
            } else {
                resultDesc.textContent = 'This text shows characteristics typical of AI writing. Notice the formal tone and lack of personal anecdotes.';
            }
        }
    } else {
        // Human-Created
        statusIcon.innerHTML = '<span class="icon">✓</span>';
        statusIcon.style.backgroundColor = '#E6F7E6';
        statusIcon.style.color = '#74D480';
        resultCard.classList.remove('ai-result');
        resultCard.classList.add('human-result');
        
        // Use backend message if available
        const headingText = customMessage || 'Likely Human-Created';
        resultHeading.innerHTML = `${headingText} <span class="badge" id="confidenceBadge">${confidenceLabel}: ${confidence}%</span>`;
        
        // Use warning message from backend if available
        if (warning) {
            resultDesc.textContent = warning;
        } else {
            // Default description
            if (result.type === 'video') {
                resultDesc.textContent = 'The video displays natural motion, consistent lighting across frames, and authentic audio synchronization.';
            } else if (result.type === 'image') {
                resultDesc.textContent = 'This image shows characteristics of authentic photography with natural lighting and proper perspective.';
            } else {
                resultDesc.textContent = 'This text demonstrates natural human writing patterns with varied sentence structure and personal voice.';
            }
        }
    }

    // Animate progress bar
    progressFill.style.width = '0%';
    setTimeout(() => {
        progressFill.style.width = confidence + '%';
    }, 100);

    // Update accordion content based on result
    updateAccordionContent(isAI, result.type);

    console.log('✅ Results displayed:', isAI ? 'AI-Generated' : 'Human-Created', `(${confidence}%)`, 'Language:', currentLanguage);
}

// ============================================
// 10. UPDATE ACCORDION CONTENT
// ============================================
function updateAccordionContent(isAI, contentType) {
    const acc1Body = document.querySelector('#acc1 .acc-body ul');
    const acc2Body = document.querySelector('#acc2 .acc-body ul');

    // Update "What You Can Do" section
    if (isAI) {
        acc1Body.innerHTML = `
            <li>Verify information from multiple trusted sources</li>
            <li>Look for the original source or creator</li>
            <li>Be cautious about sharing this content</li>
            <li>Report suspicious content to relevant platforms</li>
        `;
    } else {
        acc1Body.innerHTML = `
            <li>This appears human-created, but always verify important information</li>
            <li>Check for updated information from the original source</li>
            <li>Consider the context and timing of the content</li>
        `;
    }

    // Keep "How to Spot AI Content" section the same (educational)
}

// ============================================
// 11. ACCORDION FUNCTIONALITY
// ============================================
function initAccordions() {
    document.querySelectorAll('.accordion').forEach(acc => {
        const header = acc.querySelector('.acc-header');
        const body = acc.querySelector('.acc-body');
        const symbol = acc.querySelector('.acc-symbol');
        
        const updateSymbol = () => {
            const isOpen = body.classList.contains('show');
            symbol.style.transform = isOpen ? 'rotate(180deg)' : 'rotate(0deg)';
        };
        
        updateSymbol();

        header.addEventListener('click', () => {
            body.classList.toggle('show');
            updateSymbol();
        });
    });
}

// ============================================
// 11. HEALTH CHECK (Optional - for testing)
// ============================================
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        console.log('Backend health check:', data);
        return data;
    } catch (error) {
        console.error('Backend is not available:', error);
        return null;
    }
}

// Check backend on load
checkBackendHealth();