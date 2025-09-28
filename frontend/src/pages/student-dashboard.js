document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    if (!authService.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }

    try {
        // Get current user info
        const user = await authService.getCurrentUser();

        if (user.is_admin) {
            window.location.href = 'admin-dashboard.html';
            return;
        }

        // Update user info
        document.getElementById('userInfo').textContent = `${user.username} (Student)`;

        // Load user data
        await loadStudentData();

        // Set up event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Error loading dashboard:', error);
        authService.logout();
    }
});

async function loadStudentData() {
    try {
        // Load user's classes
        const classes = await authService.makeAuthenticatedRequest('/classes');
        updateClassList(classes);
        updateSidebarInfo(classes);

    } catch (error) {
        console.error('Error loading student data:', error);
        showError('Failed to load your classes');
    }
}

function updateSidebarInfo(classes) {
    const classesInfo = document.getElementById('classesInfo');
    if (classes.length === 0) {
        classesInfo.textContent = 'You are not enrolled in any classes yet.';
    } else {
        const classText = classes.length === 1 ? 'class' : 'classes';
        classesInfo.textContent = `You are enrolled in ${classes.length} ${classText}`;
    }
}

function updateClassList(classes) {
    const container = document.getElementById('myClasses');

    if (classes.length === 0) {
        container.innerHTML = `
            <div class="no-classes">
                <h3>No Classes Yet</h3>
                <p>You haven't been enrolled in any classes. Contact your administrator to get started.</p>
            </div>
        `;
        return;
    }

    container.innerHTML = classes.map(cls => `
        <div class="class-card">
            <div class="class-card-header">
                <h3>${cls.name}</h3>
                <p>${cls.description || 'No description available'}</p>
            </div>
            <div class="class-card-body">
                <div class="class-stats">
                    <div class="class-stat">
                        <span class="class-stat-number" id="content-count-${cls.id}">-</span>
                        <div class="class-stat-label">Documents</div>
                    </div>
                    <div class="class-stat">
                        <span class="class-stat-number" id="flashcard-count-${cls.id}">-</span>
                        <div class="class-stat-label">Flashcards</div>
                    </div>
                </div>
            </div>
            <div class="class-card-footer">
                <div class="class-access-buttons">
                    <button class="class-access-btn" onclick="event.stopPropagation(); viewClassDocuments(${cls.id}, '${cls.name}')" title="View Documents">
                        📄 Documents
                    </button>
                    <button class="class-access-btn" onclick="event.stopPropagation(); viewClassFlashcards(${cls.id}, '${cls.name}')" title="Study Flashcards">
                        🎴 Flashcards
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Load stats for each class
    classes.forEach(cls => {
        loadClassStats(cls.id);
    });
}

async function loadClassStats(classId) {
    try {
        // Load content stats
        const stats = await authService.makeAuthenticatedRequest(`/classes/${classId}/stats`);
        document.getElementById(`content-count-${classId}`).textContent = stats.content_count;

        // Load flashcard stats
        const flashcards = await authService.makeAuthenticatedRequest(`/flashcards/class/${classId}`);
        document.getElementById(`flashcard-count-${classId}`).textContent = flashcards.length;

    } catch (error) {
        console.error('Error loading class stats:', error);
        document.getElementById(`content-count-${classId}`).textContent = '-';
        document.getElementById(`flashcard-count-${classId}`).textContent = '-';
    }
}

function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', function() {
        authService.logout();
    });

    // Chat functionality
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendChatBtn');

    sendBtn.addEventListener('click', sendChatMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });
}

async function viewClassDocuments(classId, className) {
    try {
        // Load class content
        const slides = await authService.makeAuthenticatedRequest(`/slides/class/${classId}`);

        if (slides.length === 0) {
            showInfo(`No documents available for ${className} yet.`);
            return;
        }

        // Store current slides and open viewer
        window.currentSlides = slides;
        window.currentSlideIndex = 0;

        document.getElementById('viewerTitle').textContent = `${className} - Documents`;
        openSlideViewer();

    } catch (error) {
        console.error('Error loading class documents:', error);
        showError(`Failed to load documents for ${className}`);
    }
}

async function viewClassFlashcards(classId, className) {
    try {
        // Load class flashcards
        const flashcards = await authService.makeAuthenticatedRequest(`/flashcards/class/${classId}`);

        if (flashcards.length === 0) {
            showInfo(`No flashcards available for ${className} yet.`);
            return;
        }

        // Store current flashcards and open viewer
        window.currentFlashcards = flashcards;
        window.currentFlashcardIndex = 0;

        document.getElementById('flashcardViewerTitle').textContent = `${className} - Flashcards`;
        openFlashcardViewer();

    } catch (error) {
        console.error('Error loading class flashcards:', error);
        showError(`Failed to load flashcards for ${className}`);
    }
}

async function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) return;

    const chatMessages = document.getElementById('chatMessages');

    // Add user message
    addChatMessage(message, 'user');
    chatInput.value = '';

    try {
        const response = await authService.makeAuthenticatedRequest('/chat/', {
            method: 'POST',
            body: JSON.stringify({ message: message })
        });

        // Add assistant response
        addChatMessage(response.response, 'assistant');

    } catch (error) {
        console.error('Error sending chat message:', error);
        addChatMessage('Sorry, I encountered an error. Please try again.', 'assistant');
    }
}

function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    messageDiv.textContent = message;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showError(message) {
    alert('❌ ' + message);
}

function showInfo(message) {
    alert('ℹ️ ' + message);
}

// Slide viewer functionality
function openSlideViewer() {
    if (!window.currentSlides || window.currentSlides.length === 0) return;

    const modal = document.getElementById('slideViewerModal');
    modal.classList.add('active');

    setupViewerListeners();
    displayCurrentSlide();
}

function setupViewerListeners() {
    document.getElementById('closeViewer').onclick = closeSlideViewer;
    document.getElementById('prevSlide').onclick = previousSlide;
    document.getElementById('nextSlide').onclick = nextSlide;

    // Keyboard navigation
    document.onkeydown = (e) => {
        if (!document.getElementById('slideViewerModal').classList.contains('active')) return;

        if (e.key === 'ArrowLeft') previousSlide();
        if (e.key === 'ArrowRight') nextSlide();
        if (e.key === 'Escape') closeSlideViewer();
    };
}

function closeSlideViewer() {
    document.getElementById('slideViewerModal').classList.remove('active');
    document.onkeydown = null;
}

function previousSlide() {
    if (window.currentSlideIndex > 0) {
        window.currentSlideIndex--;
        displayCurrentSlide();
    }
}

function nextSlide() {
    if (window.currentSlideIndex < window.currentSlides.length - 1) {
        window.currentSlideIndex++;
        displayCurrentSlide();
    }
}

async function displayCurrentSlide() {
    const slide = window.currentSlides[window.currentSlideIndex];
    const container = document.getElementById('currentSlide');
    const counter = document.getElementById('slideCounter');

    // Update counter
    counter.textContent = `${window.currentSlideIndex + 1} / ${window.currentSlides.length}`;

    // Update navigation buttons
    document.getElementById('prevSlide').disabled = window.currentSlideIndex === 0;
    document.getElementById('nextSlide').disabled = window.currentSlideIndex === window.currentSlides.length - 1;

    // Show loading message
    container.innerHTML = '<div style="color: white; text-align: center; padding: 40px;">Loading content...</div>';

    try {
        // Fetch content with authentication
        const response = await fetch(`http://localhost:8000/api/slides/${slide.id}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${authService.token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to load content: ${response.status}`);
        }

        const blob = await response.blob();
        const blobUrl = URL.createObjectURL(blob);

        // Display PDF content using native browser viewer
        if (slide.file_type.includes('pdf')) {
            container.innerHTML = `
                <div style="width: 100%; height: 80vh; min-height: 600px; display: flex; flex-direction: column; background: #222;">
                    <div style="padding: 8px; background: rgba(0,0,0,0.7); text-align: center; flex-shrink: 0;">
                        <p style="margin: 0; color: white; font-size: 0.9rem;">📄 ${slide.title}</p>
                    </div>
                    <div style="flex: 1; min-height: 550px; background: white;">
                        <iframe
                            src="${blobUrl}"
                            style="width: 100%; height: 100%; border: none;"
                            title="${slide.title}">
                        </iframe>
                    </div>
                </div>
            `;
        } else {
            // For non-PDF files (should not occur with new restrictions)
            container.innerHTML = `
                <div style="color: white; text-align: center; padding: 40px;">
                    <div style="font-size: 4rem; margin-bottom: 20px;">⚠️</div>
                    <h3>Unsupported File Type</h3>
                    <p>Only PDF files are supported in this viewer</p>
                    <p style="color: #ccc; font-size: 0.9rem;">File type: ${slide.file_type}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading content:', error);
        container.innerHTML = `
            <div style="color: white; text-align: center; padding: 40px;">
                <h3>Error Loading Content</h3>
                <p style="color: #ff6b6b;">${error.message}</p>
                <p>Please try refreshing or contact support.</p>
            </div>
        `;
    }
}

// Flashcard viewer functionality
function openFlashcardViewer() {
    if (!window.currentFlashcards || window.currentFlashcards.length === 0) return;

    const modal = document.getElementById('flashcardViewerModal');
    modal.classList.add('active');

    setupFlashcardViewerListeners();
    displayCurrentFlashcard();
}

function setupFlashcardViewerListeners() {
    document.getElementById('closeFlashcardViewer').onclick = closeFlashcardViewer;
    document.getElementById('cancelFlashcardViewer').onclick = closeFlashcardViewer;
    document.getElementById('prevFlashcard').onclick = previousFlashcard;
    document.getElementById('nextFlashcard').onclick = nextFlashcard;
    document.getElementById('downloadFlashcardsBtn').onclick = downloadCurrentFlashcards;

    // Keyboard navigation
    document.onkeydown = (e) => {
        if (!document.getElementById('flashcardViewerModal').classList.contains('active')) return;

        if (e.key === 'ArrowLeft') previousFlashcard();
        if (e.key === 'ArrowRight') nextFlashcard();
        if (e.key === ' ') { e.preventDefault(); flipFlashcard(); }
        if (e.key === 'Escape') closeFlashcardViewer();
    };
}

function closeFlashcardViewer() {
    document.getElementById('flashcardViewerModal').classList.remove('active');
    document.onkeydown = null;
    // Reset flip state
    document.getElementById('flashcardContent').classList.remove('flipped');
}

function previousFlashcard() {
    if (window.currentFlashcardIndex > 0) {
        window.currentFlashcardIndex--;
        displayCurrentFlashcard();
        // Reset flip state when changing cards
        document.getElementById('flashcardContent').classList.remove('flipped');
    }
}

function nextFlashcard() {
    if (window.currentFlashcardIndex < window.currentFlashcards.length - 1) {
        window.currentFlashcardIndex++;
        displayCurrentFlashcard();
        // Reset flip state when changing cards
        document.getElementById('flashcardContent').classList.remove('flipped');
    }
}

function flipFlashcard() {
    const content = document.getElementById('flashcardContent');
    content.classList.toggle('flipped');
}

function displayCurrentFlashcard() {
    const flashcard = window.currentFlashcards[window.currentFlashcardIndex];
    const counter = document.getElementById('flashcardCounter');
    const category = document.getElementById('flashcardCategory');

    // Update content
    document.getElementById('flashcardTermDisplay').textContent = flashcard.term;
    document.getElementById('flashcardDefinitionDisplay').textContent = flashcard.definition;

    // Update counter
    counter.textContent = `${window.currentFlashcardIndex + 1} / ${window.currentFlashcards.length}`;

    // Update category
    if (flashcard.category) {
        category.textContent = flashcard.category;
        category.style.display = 'inline-block';
    } else {
        category.style.display = 'none';
    }

    // Update navigation buttons
    document.getElementById('prevFlashcard').disabled = window.currentFlashcardIndex === 0;
    document.getElementById('nextFlashcard').disabled = window.currentFlashcardIndex === window.currentFlashcards.length - 1;
}

function downloadCurrentFlashcards() {
    if (!window.currentFlashcards || window.currentFlashcards.length === 0) {
        showInfo('No flashcards available to download.');
        return;
    }

    try {
        // Create CSV content
        const csvContent = createFlashcardsCSV(window.currentFlashcards);

        // Create and download file
        const blob = new Blob([csvContent], { type: 'text/csv;charset-utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        // Get class name from the viewer title
        const viewerTitle = document.getElementById('flashcardViewerTitle').textContent;
        const className = viewerTitle.replace(' - Flashcards', '').replace(/[^a-zA-Z0-9]/g, '_');

        link.setAttribute('href', url);
        link.setAttribute('download', `${className}_flashcards_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();

        // Clean up DOM and URL
        try {
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
        } catch (cleanupError) {
            console.warn('Minor cleanup error (download still succeeded):', cleanupError);
        }

        showInfo(`Downloaded ${window.currentFlashcards.length} flashcards to Excel file!`);

    } catch (error) {
        console.error('Error downloading flashcards:', error);
        showError('Failed to download flashcards');
    }
}

function createFlashcardsCSV(flashcards) {
    // CSV headers
    const headers = ['Term', 'Definition', 'Category'];

    // Convert flashcards to CSV rows
    const rows = flashcards.map(flashcard => [
        `"${(flashcard.term || '').replace(/"/g, '""')}"`,
        `"${(flashcard.definition || '').replace(/"/g, '""')}"`,
        `"${(flashcard.category || '').replace(/"/g, '""')}"`
    ]);

    // Combine headers and rows
    const csvContent = [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    return csvContent;
}