document.addEventListener('DOMContentLoaded', async function() {
    // Check authentication
    if (!authService.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }

    try {
        // Get current user info
        const user = await authService.getCurrentUser();

        if (!user.is_admin) {
            window.location.href = 'student-dashboard.html';
            return;
        }

        // Update user info
        document.getElementById('userInfo').textContent = `${user.username} (Administrator)`;

        // Load dashboard data
        await loadDashboardData();

        // Set up event listeners
        setupEventListeners();

    } catch (error) {
        console.error('Error loading dashboard:', error);
        authService.logout();
    }
});

async function loadDashboardData() {
    try {
        // Load classes
        const classes = await authService.makeAuthenticatedRequest('/classes');
        document.getElementById('classCount').textContent = classes.length;
        await updateRecentClasses(classes);

        // Load actual student count
        await loadStudentCount();

        // For now, set placeholder data for resources
        document.getElementById('resourceCount').textContent = '0';

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadStudentCount() {
    try {
        const users = await authService.makeAuthenticatedRequest('/auth/users');
        const studentCount = users.filter(user => !user.is_admin).length;
        document.getElementById('studentCount').textContent = studentCount;
    } catch (error) {
        console.error('Error loading student count:', error);
        document.getElementById('studentCount').textContent = '0';
    }
}

async function updateRecentClasses(classes) {
    const container = document.getElementById('recentClasses');

    if (classes.length === 0) {
        container.innerHTML = '<p>No classes created yet. <a href="#" id="createFirstClass">Create your first class</a></p>';
        return;
    }

    const recentClasses = classes.slice(0, 5);

    // Get total flashcard count for comparison
    let totalFlashcards = 0;
    try {
        const allFlashcards = await authService.makeAuthenticatedRequest('/flashcards');
        totalFlashcards = allFlashcards.length;
    } catch (error) {
        console.error('Error loading total flashcards:', error);
    }

    // Load additional data for each class
    const classesWithData = await Promise.all(recentClasses.map(async (cls) => {
        let fileCount = 0;
        let flashcardCount = 0;

        try {
            // Get file count
            const slides = await authService.makeAuthenticatedRequest(`/slides/class/${cls.id}`);
            fileCount = slides.length;

            // Get flashcard count
            const flashcards = await authService.makeAuthenticatedRequest(`/flashcards/class/${cls.id}`);
            flashcardCount = flashcards.length;
        } catch (error) {
            console.error(`Error loading data for class ${cls.id}:`, error);
        }

        return {
            ...cls,
            fileCount,
            flashcardCount,
            totalFlashcards
        };
    }));

    container.innerHTML = classesWithData.map(cls => `
        <div class="class-item" data-class-id="${cls.id}" onclick="openConfigureClassModal(${cls.id}, '${cls.name}')">
            <h5>${cls.name}</h5>
            <p>${cls.description || 'No description'}</p>
            <div class="class-stats">
                <div class="stat-item">📄 ${cls.fileCount} files</div>
                <div class="stat-item">📚 ${cls.flashcardCount}/${cls.totalFlashcards} flashcards</div>
            </div>
        </div>
    `).join('');
}

function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', function() {
        authService.logout();
    });

    // Quick action buttons
    document.getElementById('createClassBtn').addEventListener('click', function() {
        openCreateClassModal();
    });

    document.getElementById('uploadResourceBtn').addEventListener('click', function() {
        uploadResource();
    });

    document.getElementById('manageUsersBtn').addEventListener('click', function() {
        manageUsers();
    });

    document.getElementById('manageFlashcardsBtn').addEventListener('click', function() {
        manageFlashcards();
    });

    // Modal event listeners
    setupModalEventListeners();

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

function setupModalEventListeners() {
    const modal = document.getElementById('createClassModal');
    const closeBtn = document.getElementById('closeCreateClassModal');
    const cancelBtn = document.getElementById('cancelCreateClass');
    const form = document.getElementById('createClassForm');

    // Close modal events
    closeBtn.addEventListener('click', closeCreateClassModal);
    cancelBtn.addEventListener('click', closeCreateClassModal);

    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeCreateClassModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeCreateClassModal();
        }
    });

    // Form submission
    form.addEventListener('submit', handleCreateClassSubmit);
}

function openCreateClassModal() {
    const modal = document.getElementById('createClassModal');
    modal.classList.add('active');

    // Clear form
    document.getElementById('createClassForm').reset();
    clearFormErrors();
    hideSuccessMessage();

    // Focus on first input
    setTimeout(() => {
        document.getElementById('className').focus();
    }, 100);
}

function closeCreateClassModal() {
    const modal = document.getElementById('createClassModal');
    modal.classList.remove('active');
}

function clearFormErrors() {
    const formGroups = document.querySelectorAll('.form-group');
    formGroups.forEach(group => {
        group.classList.remove('error');
    });
}

function showFormError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const formGroup = field.closest('.form-group');
    const errorDiv = formGroup.querySelector('.form-error');

    formGroup.classList.add('error');
    errorDiv.textContent = message;
}

function showSuccessMessage() {
    const successDiv = document.getElementById('createClassSuccess');
    successDiv.classList.add('show');

    setTimeout(() => {
        hideSuccessMessage();
    }, 3000);
}

function hideSuccessMessage() {
    const successDiv = document.getElementById('createClassSuccess');
    successDiv.classList.remove('show');
}

async function handleCreateClassSubmit(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('submitCreateClass');
    const className = document.getElementById('className').value.trim();
    const description = document.getElementById('classDescription').value.trim();

    // Clear previous errors
    clearFormErrors();

    // Validation
    if (!className) {
        showFormError('className', 'Please enter a class name');
        return;
    }

    if (className.length < 2) {
        showFormError('className', 'Class name must be at least 2 characters');
        return;
    }

    // Set loading state
    submitBtn.classList.add('loading');
    submitBtn.textContent = 'Creating...';

    try {
        const newClass = await authService.makeAuthenticatedRequest('/classes/', {
            method: 'POST',
            body: JSON.stringify({
                name: className,
                description: description || null
            })
        });

        showSuccessMessage();
        loadDashboardData(); // Refresh data

        // Reset form and close modal after delay
        setTimeout(() => {
            closeCreateClassModal();
        }, 1500);

    } catch (error) {
        console.error('Error creating class:', error);

        if (error.message.includes('already exists')) {
            showFormError('className', 'A class with this name already exists');
        } else {
            showFormError('className', 'Failed to create class. Please try again.');
        }
    } finally {
        // Remove loading state
        submitBtn.classList.remove('loading');
        submitBtn.textContent = 'Create Class';
    }
}

function uploadResource() {
    showInfo('Resource upload feature coming soon!');
}

async function manageUsers() {
    const modal = document.getElementById('manageUsersModal');
    modal.classList.add('active');

    // Setup modal listeners if not already done
    if (!modal.hasAttribute('data-listeners-setup')) {
        setupUserModalListeners();
        modal.setAttribute('data-listeners-setup', 'true');
    }

    // Load classes for assignment dropdown
    await loadClassesForAssignment();

    // Load existing users
    await loadUsers();
}

function setupUserModalListeners() {
    document.getElementById('closeUsersModal').onclick = closeUsersModal;
    document.getElementById('cancelUsers').onclick = closeUsersModal;
    document.getElementById('createUserForm').onsubmit = handleCreateUser;
}

function closeUsersModal() {
    document.getElementById('manageUsersModal').classList.remove('active');
}

async function loadClassesForAssignment() {
    try {
        const classes = await authService.makeAuthenticatedRequest('/classes');

        // Setup custom dropdown
        setupCustomDropdown();

        const menu = document.getElementById('assignClassMenu');

        // Clear existing options
        menu.innerHTML = '<div class="dropdown-item" data-value="">Select a class (optional)</div>';

        classes.forEach(cls => {
            const item = document.createElement('div');
            item.className = 'dropdown-item';
            item.setAttribute('data-value', cls.id);
            item.textContent = cls.name;
            menu.appendChild(item);
        });

        // Add click handlers to items
        menu.querySelectorAll('.dropdown-item').forEach(item => {
            item.addEventListener('click', function() {
                selectDropdownItem(item);
            });
        });

    } catch (error) {
        console.error('Error loading classes:', error);
    }
}

function setupCustomDropdown() {
    const trigger = document.getElementById('assignClassTrigger');
    const menu = document.getElementById('assignClassMenu');
    const dropdown = document.getElementById('assignClassDropdown');

    if (!trigger || !menu) return;

    // Remove existing listeners
    trigger.replaceWith(trigger.cloneNode(true));
    const newTrigger = document.getElementById('assignClassTrigger');

    newTrigger.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleDropdown();
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!dropdown.contains(e.target)) {
            closeDropdown();
        }
    });
}

function toggleDropdown() {
    const trigger = document.getElementById('assignClassTrigger');
    const menu = document.getElementById('assignClassMenu');

    if (menu.classList.contains('active')) {
        closeDropdown();
    } else {
        openDropdown();
    }
}

function openDropdown() {
    const trigger = document.getElementById('assignClassTrigger');
    const menu = document.getElementById('assignClassMenu');

    trigger.classList.add('active');
    menu.classList.add('active');
}

function closeDropdown() {
    const trigger = document.getElementById('assignClassTrigger');
    const menu = document.getElementById('assignClassMenu');

    trigger.classList.remove('active');
    menu.classList.remove('active');
}

function selectDropdownItem(item) {
    const trigger = document.getElementById('assignClassTrigger');
    const textSpan = trigger.querySelector('.dropdown-text');
    const hiddenInput = document.getElementById('assignClass');

    // Update selected item visual state
    document.querySelectorAll('.dropdown-item').forEach(i => i.classList.remove('selected'));
    item.classList.add('selected');

    // Update display text and hidden input value
    textSpan.textContent = item.textContent;
    hiddenInput.value = item.getAttribute('data-value');

    closeDropdown();
}

async function loadUsers() {
    try {
        const users = await authService.makeAuthenticatedRequest('/auth/users');
        const usersList = document.getElementById('usersList');

        if (users.length === 0) {
            usersList.innerHTML = '<p>No students created yet</p>';
            return;
        }

        usersList.innerHTML = users.filter(user => !user.is_admin).map(user => `
            <div class="user-item">
                <div class="user-info">
                    <h6>${user.username}</h6>
                    <p>${user.email}</p>
                    <div class="user-classes" id="user-classes-${user.id}">
                        Loading classes...
                    </div>
                </div>
                <div class="user-actions">
                    <button class="user-action-btn assign" onclick="assignUserToClass(${user.id}, '${user.username}')">
                        Assign to Class
                    </button>
                    <button class="user-action-btn delete" onclick="deleteUser(${user.id}, '${user.username}')">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');

        // Load class assignments for each user
        users.filter(user => !user.is_admin).forEach(user => {
            loadUserClasses(user.id);
        });

    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('usersList').innerHTML = '<p>Error loading users</p>';
    }
}

async function loadUserClasses(userId) {
    try {
        const classes = await authService.makeAuthenticatedRequest(`/auth/users/${userId}/classes`);
        const classesDiv = document.getElementById(`user-classes-${userId}`);

        if (classes.length === 0) {
            classesDiv.textContent = 'Not assigned to any classes';
        } else {
            classesDiv.textContent = `Classes: ${classes.map(c => c.name).join(', ')}`;
        }
    } catch (error) {
        console.error('Error loading user classes:', error);
        const classesDiv = document.getElementById(`user-classes-${userId}`);
        if (classesDiv) {
            classesDiv.textContent = 'Error loading classes';
        }
    }
}

async function handleCreateUser(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');

    const userData = {
        username: formData.get('username'),
        email: formData.get('email'),
        password: formData.get('password')
    };

    const classId = formData.get('class_id');

    submitBtn.classList.add('loading');
    submitBtn.textContent = 'Creating...';

    try {
        // Create the user
        const newUser = await authService.makeAuthenticatedRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });

        // If a class was selected, assign the user to it
        if (classId) {
            await authService.makeAuthenticatedRequest(`/classes/${classId}/assign-user`, {
                method: 'POST',
                body: JSON.stringify({ user_id: newUser.id })
            });
        }

        // Show success message
        const successDiv = document.getElementById('usersSuccess');
        successDiv.textContent = `Student "${userData.username}" created successfully!`;
        successDiv.classList.add('show');

        setTimeout(() => {
            successDiv.classList.remove('show');
        }, 3000);

        // Reset form and reload users
        form.reset();
        await loadUsers();
        await loadDashboardData(); // Refresh dashboard stats

    } catch (error) {
        console.error('Error creating user:', error);
        alert('Error creating user: ' + error.message);
    } finally {
        submitBtn.classList.remove('loading');
        submitBtn.textContent = 'Create Student';
    }
}

async function assignUserToClass(userId, username) {
    try {
        const classes = await authService.makeAuthenticatedRequest('/classes');

        if (classes.length === 0) {
            alert('No classes available for assignment');
            return;
        }

        // Store current assignment context
        window.currentAssignUserId = userId;
        window.currentAssignUsername = username;

        // Open the assign modal
        const modal = document.getElementById('assignClassModal');
        document.getElementById('assignStudentName').textContent = username;
        modal.classList.add('active');

        // Setup modal listeners if not already done
        if (!modal.hasAttribute('data-listeners-setup')) {
            setupAssignModalListeners();
            modal.setAttribute('data-listeners-setup', 'true');
        }

        // Load classes in the grid
        await loadClassesForAssignGrid(classes);

    } catch (error) {
        console.error('Error loading classes for assignment:', error);
        showError('Failed to load classes for assignment');
    }
}

function setupAssignModalListeners() {
    // Close modal events
    document.getElementById('closeAssignModal').onclick = closeAssignModal;

    // Close modal when clicking outside
    const modal = document.getElementById('assignClassModal');
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeAssignModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeAssignModal();
        }
    });
}

function closeAssignModal() {
    document.getElementById('assignClassModal').classList.remove('active');
    document.getElementById('assignMessage').style.display = 'none';
}

async function loadClassesForAssignGrid(classes) {
    const grid = document.getElementById('assignClassGrid');
    const userId = window.currentAssignUserId;

    if (classes.length === 0) {
        grid.innerHTML = '<p>No classes available for assignment</p>';
        return;
    }

    // Get user's current class assignments
    let userClasses = [];
    try {
        userClasses = await authService.makeAuthenticatedRequest(`/auth/users/${userId}/classes`);
    } catch (error) {
        console.error('Error loading user classes:', error);
    }

    const userClassIds = userClasses.map(cls => cls.id);

    grid.innerHTML = classes.map(cls => {
        const isAssigned = userClassIds.includes(cls.id);

        return `
            <div class="assign-class-item" data-class-id="${cls.id}">
                <div class="assign-class-info">
                    <h5>${cls.name}</h5>
                    <p>${cls.description || 'No description available'}</p>
                </div>
                <div class="assign-class-actions">
                    <button class="assign-toggle-btn ${isAssigned ? 'assigned' : 'unassigned'}"
                            onclick="toggleClassAssignment(${cls.id}, '${cls.name}', ${isAssigned})">
                        ${isAssigned ? 'Assigned' : 'Unassigned'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function toggleClassAssignment(classId, className, isCurrentlyAssigned) {
    if (isCurrentlyAssigned) {
        await handleClassUnassignment(classId, className);
    } else {
        await handleClassAssignment(classId, className);
    }
}

async function handleClassAssignment(classId, className) {
    const userId = window.currentAssignUserId;
    const username = window.currentAssignUsername;

    if (!userId) {
        showError('Assignment error: User information not found');
        return;
    }

    // Show loading state
    const messageDiv = document.getElementById('assignMessage');
    messageDiv.textContent = `Assigning ${username} to ${className}...`;
    messageDiv.className = 'assign-message loading';
    messageDiv.style.display = 'block';

    try {
        await authService.makeAuthenticatedRequest(`/classes/${classId}/assign-user`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });

        // Show success message
        messageDiv.textContent = `✅ ${username} successfully assigned to ${className}`;
        messageDiv.className = 'assign-message success';

        // Refresh the grid to show updated assignment status
        setTimeout(async () => {
            const classes = await authService.makeAuthenticatedRequest('/classes');
            await loadClassesForAssignGrid(classes);
            await loadUsers(); // Refresh the user list
            await loadDashboardData(); // Refresh dashboard stats
            messageDiv.style.display = 'none';
        }, 1500);

    } catch (error) {
        console.error('Error assigning user to class:', error);
        messageDiv.textContent = `❌ Failed to assign ${username} to ${className}`;
        messageDiv.className = 'assign-message error';
    }
}

async function handleClassUnassignment(classId, className) {
    const userId = window.currentAssignUserId;
    const username = window.currentAssignUsername;

    if (!userId) {
        showError('Unassignment error: User information not found');
        return;
    }

    // Show loading state
    const messageDiv = document.getElementById('assignMessage');
    messageDiv.textContent = `Removing ${username} from ${className}...`;
    messageDiv.className = 'assign-message loading';
    messageDiv.style.display = 'block';

    try {
        await authService.makeAuthenticatedRequest(`/classes/${classId}/unassign-user`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });

        // Show success message
        messageDiv.textContent = `✅ ${username} successfully removed from ${className}`;
        messageDiv.className = 'assign-message success';

        // Refresh the grid to show updated assignment status
        setTimeout(async () => {
            const classes = await authService.makeAuthenticatedRequest('/classes');
            await loadClassesForAssignGrid(classes);
            await loadUsers(); // Refresh the user list
            await loadDashboardData(); // Refresh dashboard stats
            messageDiv.style.display = 'none';
        }, 1500);

    } catch (error) {
        console.error('Error unassigning user from class:', error);
        messageDiv.textContent = `❌ Failed to remove ${username} from ${className}`;
        messageDiv.className = 'assign-message error';
    }
}

async function deleteUser(userId, username) {
    if (!confirm(`Are you sure you want to delete user "${username}"?\n\nThis action cannot be undone.`)) {
        return;
    }

    try {
        await authService.makeAuthenticatedRequest(`/auth/users/${userId}`, {
            method: 'DELETE'
        });

        showSuccess(`User "${username}" deleted successfully`);

        // Refresh both user list and dashboard stats
        await loadUsers();
        await loadDashboardData();

    } catch (error) {
        console.error('Error deleting user:', error);
        showError('Failed to delete user: ' + error.message);
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

function showSuccess(message) {
    alert('✅ ' + message); // Simple alert for now, can be enhanced later
}

function showError(message) {
    alert('❌ ' + message);
}

function showInfo(message) {
    alert('ℹ️ ' + message);
}

// Global variables for slide management
let currentClassId = null;
let selectedFiles = [];
let currentSlides = [];
let currentSlideIndex = 0;

// Slide Management Functions
async function openSlidesModal(classId, className) {
    currentClassId = classId;
    const modal = document.getElementById('manageSlidesModal');
    const title = document.getElementById('manageSlidesTitle');

    title.textContent = `Manage Content - ${className}`;
    modal.classList.add('active');

    // Clear previous state
    clearFileSelection();

    // Load existing slides
    await loadClassSlides(classId);

    // Setup slide modal event listeners only if not already set up
    if (!modal.hasAttribute('data-listeners-setup')) {
        setupSlideModalListeners();
        modal.setAttribute('data-listeners-setup', 'true');
    }
}

function setupSlideModalListeners() {
    // Close modal
    document.getElementById('closeSlidesModal').onclick = closeSlidesModal;
    document.getElementById('cancelSlides').onclick = closeSlidesModal;

    // File upload area for drag and drop
    const uploadArea = document.getElementById('fileUploadArea');

    // Drag and drop
    uploadArea.ondragover = (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    };

    uploadArea.ondragleave = () => {
        uploadArea.classList.remove('dragover');
    };

    uploadArea.ondrop = (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFileSelection({ target: { files: e.dataTransfer.files } });
    };

    // Upload actions
    const clearBtn = document.getElementById('clearFiles');
    const uploadBtn = document.getElementById('uploadFiles');

    if (clearBtn) {
        clearBtn.addEventListener('click', clearFileSelection);
    }

    if (uploadBtn) {
        uploadBtn.addEventListener('click', function() {
            console.log('Upload button clicked!');
            uploadSelectedFiles();
        });
    }

    // View slides functionality is now handled by clicking individual slides
}

function closeSlidesModal() {
    document.getElementById('manageSlidesModal').classList.remove('active');
    clearFileSelection();
}

function handleFileSelection(event) {
    console.log('handleFileSelection called', event);
    const files = Array.from(event.target.files);
    console.log('Files selected:', files.length);

    const validFiles = files.filter(file => {
        const validTypes = ['application/pdf'];
        const validExtensions = ['.pdf'];
        const maxSize = 10 * 1024 * 1024; // 10MB

        // Check by MIME type first
        if (validTypes.includes(file.type) && file.size <= maxSize) {
            return true;
        }

        // If MIME type is application/octet-stream, check by file extension
        if (file.type === 'application/octet-stream' && file.size <= maxSize) {
            const fileName = file.name.toLowerCase();
            return validExtensions.some(ext => fileName.endsWith(ext));
        }

        // Show error for non-PDF files
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            alert(`File "${file.name}" is not a PDF file. Only PDF files are supported.`);
        }

        return false;
    });

    console.log('Valid files:', validFiles.length);
    selectedFiles = [...selectedFiles, ...validFiles];
    updateFilePreview();
}

function updateFilePreview() {
    console.log('updateFilePreview called, selectedFiles:', selectedFiles.length);
    const preview = document.getElementById('filePreview');
    const fileList = document.getElementById('fileList');
    const fileStatus = document.getElementById('fileStatus');

    if (selectedFiles.length === 0) {
        fileList.innerHTML = 'No files selected yet';
        fileStatus.textContent = 'No files selected';
        fileStatus.classList.remove('has-files');
        console.log('No files to preview');
        return;
    }

    // Update file status
    const fileText = selectedFiles.length === 1 ? 'file selected' : 'files selected';
    fileStatus.textContent = `${selectedFiles.length} ${fileText}`;
    fileStatus.classList.add('has-files');

    console.log('Updating file preview with', selectedFiles.length, 'files');
    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-info">
                <div class="file-icon">${getFileIcon(file.type)}</div>
                <div class="file-details">
                    <h6>${file.name}</h6>
                    <p>${formatFileSize(file.size)}</p>
                </div>
            </div>
            <button class="file-remove" onclick="removeFile(${index})">&times;</button>
        </div>
    `).join('');
}

function getFileIcon(type) {
    // Only PDF files are supported
    return '📄';
}

function getFileTypeLabel(type) {
    // Only PDF files are supported
    return 'PDF Document';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFilePreview();
}

function clearFileSelection() {
    selectedFiles = [];
    document.getElementById('slideFileInput').value = '';
    const fileStatus = document.getElementById('fileStatus');
    fileStatus.textContent = 'No files selected';
    fileStatus.classList.remove('has-files');
    updateFilePreview();
}

async function uploadSelectedFiles() {
    console.log('uploadSelectedFiles called, selectedFiles:', selectedFiles.length);
    if (selectedFiles.length === 0) {
        console.log('No files selected');
        return;
    }

    if (!currentClassId) {
        console.error('No current class ID');
        alert('Error: No class selected');
        return;
    }

    console.log('Auth token:', authService.token ? 'Present' : 'Missing');

    const uploadBtn = document.getElementById('uploadFiles');
    uploadBtn.classList.add('loading');
    uploadBtn.textContent = 'Uploading...';

    try {
        let totalChunks = 0;
        let processedFiles = 0;

        for (const file of selectedFiles) {
            console.log('Uploading file:', file.name, file.type, file.size);

            // Update status to show current file being processed
            uploadBtn.textContent = `Processing ${file.name}...`;

            const formData = new FormData();
            formData.append('file', file);

            const title = encodeURIComponent(file.name.split('.')[0]);

            // Show spinner animation for vectorization
            uploadBtn.classList.add('vectorizing');
            uploadBtn.innerHTML = '⚡ Vectorizing document...';

            const response = await fetch(`http://localhost:8000/api/slides/upload/${currentClassId}?title=${title}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authService.token}`
                },
                body: formData
            });

            console.log('Upload response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Upload failed:', errorText);
                throw new Error(`Upload failed: ${errorText}`);
            }

            const result = await response.json();
            console.log('Upload successful:', result);

            processedFiles++;
            totalChunks += result.chunks_created || 0;
        }

        // Success with detailed information
        const successMessage = processedFiles === 1
            ? `Document uploaded and processed successfully! Created ${totalChunks} searchable chunks.`
            : `${processedFiles} documents uploaded successfully! Created ${totalChunks} searchable chunks total.`;

        document.getElementById('slidesSuccess').textContent = successMessage;
        document.getElementById('slidesSuccess').classList.add('show');

        setTimeout(() => {
            document.getElementById('slidesSuccess').classList.remove('show');
        }, 5000);

        clearFileSelection();
        await loadClassSlides(currentClassId);

    } catch (error) {
        console.error('Error uploading content:', error);
        alert('Error uploading content: ' + error.message);
    } finally {
        uploadBtn.classList.remove('loading', 'vectorizing');
        uploadBtn.textContent = 'Upload Content';
    }
}

async function loadClassSlides(classId) {
    try {
        console.log('Loading slides for class:', classId);
        const slides = await authService.makeAuthenticatedRequest(`/slides/class/${classId}`);
        console.log('Loaded slides:', slides.length, slides);
        currentSlides = slides;
        await updateSlidesGrid(slides);
    } catch (error) {
        console.error('Error loading slides:', error);
        updateSlidesGrid([]);
    }
}

function updateSlidesGrid(slides) {
    console.log('updateSlidesGrid called with', slides.length, 'slides');
    const grid = document.getElementById('slidesList');

    console.log('Grid element:', grid);

    if (slides.length === 0) {
        console.log('No slides, showing empty message');
        grid.innerHTML = '<p class="no-slides">No content uploaded yet</p>';
        return;
    }

    console.log('Displaying', slides.length, 'slides');
    grid.innerHTML = slides.map((slide, index) => `
        <div class="slide-thumbnail" onclick="viewSlideAt(${index})" data-slide-id="${slide.id}">
            <div class="slide-placeholder">
                <div class="file-icon-large">${getFileIcon(slide.file_type)}</div>
                <div class="slide-title">${slide.title}</div>
                <div class="file-type">${getFileTypeLabel(slide.file_type)}</div>
            </div>
            <div class="slide-actions">
                <button class="slide-action" onclick="event.stopPropagation(); deleteSlide(${slide.id})" title="Delete">
                    &times;
                </button>
            </div>
        </div>
    `).join('');
}

async function deleteSlide(slideId) {
    if (!confirm('Are you sure you want to delete this content and its vector embeddings?')) return;

    try {
        const response = await authService.makeAuthenticatedRequest(`/slides/${slideId}`, {
            method: 'DELETE'
        });

        // Show detailed success message about what was deleted
        const successMessage = response.vectors_deleted > 0
            ? `${response.detail} - ${response.message}`
            : response.detail;

        await loadClassSlides(currentClassId);

        // Show success message in the slides modal
        document.getElementById('slidesSuccess').textContent = successMessage;
        document.getElementById('slidesSuccess').classList.add('show');

        setTimeout(() => {
            document.getElementById('slidesSuccess').classList.remove('show');
        }, 5000);

    } catch (error) {
        console.error('Error deleting content:', error);
        showError('Failed to delete content');
    }
}

async function openSlideViewer() {
    if (currentSlides.length === 0) return;

    currentSlideIndex = 0;
    const modal = document.getElementById('slideViewerModal');
    modal.classList.add('active');

    setupViewerListeners();
    await displayCurrentSlide();
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

async function previousSlide() {
    if (currentSlideIndex > 0) {
        currentSlideIndex--;
        await displayCurrentSlide();
    }
}

async function nextSlide() {
    if (currentSlideIndex < currentSlides.length - 1) {
        currentSlideIndex++;
        await displayCurrentSlide();
    }
}

async function viewSlideAt(index) {
    currentSlideIndex = index;
    await openSlideViewer();
}

async function displayCurrentSlide() {
    const slide = currentSlides[currentSlideIndex];
    const container = document.getElementById('currentSlide');
    const counter = document.getElementById('slideCounter');
    const title = document.getElementById('viewerTitle');

    // Update counter and title
    counter.textContent = `${currentSlideIndex + 1} / ${currentSlides.length}`;
    title.textContent = slide.title;

    // Update navigation buttons
    document.getElementById('prevSlide').disabled = currentSlideIndex === 0;
    document.getElementById('nextSlide').disabled = currentSlideIndex === currentSlides.length - 1;

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

// Flashcard Management Functions
async function manageFlashcards() {
    try {
        // Load flashcards and categories
        await loadFlashcards();
        await loadFlashcardCategories();

        // Open modal
        const modal = document.getElementById('manageFlashcardsModal');
        modal.classList.add('active');

        // Setup flashcard modal event listeners
        setupFlashcardModalEventListeners();

    } catch (error) {
        console.error('Error opening flashcard management:', error);
        showError('Failed to load flashcards');
    }
}

function setupFlashcardModalEventListeners() {
    // Close modal events
    const modal = document.getElementById('manageFlashcardsModal');
    const closeBtn = document.getElementById('closeFlashcardsModal');
    const cancelBtn = document.getElementById('cancelFlashcards');

    closeBtn.addEventListener('click', closeFlashcardsModal);
    cancelBtn.addEventListener('click', closeFlashcardsModal);

    // Close modal when clicking outside
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeFlashcardsModal();
        }
    });

    // Action buttons
    document.getElementById('createFlashcardBtn').addEventListener('click', openCreateFlashcardModal);
    document.getElementById('bulkUploadBtn').addEventListener('click', openBulkUploadModal);
    document.getElementById('downloadFlashcardsBtn').addEventListener('click', downloadFlashcardsToExcel);

    // Category filter
    setupCategoryFilter();

    // Setup other modal event listeners
    setupFlashcardFormModalListeners();
    setupBulkUploadModalListeners();
    setupFlashcardViewerListeners();
}

function setupCategoryFilter() {
    const trigger = document.getElementById('categoryFilterTrigger');
    const menu = document.getElementById('categoryFilterMenu');

    // Remove existing event listeners if any
    trigger.replaceWith(trigger.cloneNode(true));
    const newTrigger = document.getElementById('categoryFilterTrigger');

    newTrigger.addEventListener('click', function() {
        newTrigger.classList.toggle('active');
        menu.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!newTrigger.contains(e.target) && !menu.contains(e.target)) {
            newTrigger.classList.remove('active');
            menu.classList.remove('active');
        }
    });
}

async function loadFlashcards(category = null) {
    try {
        let url = '/flashcards';
        if (category) {
            url += `?category=${encodeURIComponent(category)}`;
        }

        const flashcards = await authService.makeAuthenticatedRequest(url);
        updateFlashcardsList(flashcards);
        updateFlashcardsCount(flashcards.length, category);

    } catch (error) {
        console.error('Error loading flashcards:', error);
        document.getElementById('flashcardsList').innerHTML = '<p class="error">Failed to load flashcards</p>';
        document.getElementById('flashcardsCount').textContent = 'Error loading flashcards';
    }
}

function updateFlashcardsCount(count, category) {
    const countElement = document.getElementById('flashcardsCount');
    if (category) {
        countElement.textContent = `${count} flashcard${count !== 1 ? 's' : ''} in "${category}" category`;
    } else {
        countElement.textContent = `${count} total flashcard${count !== 1 ? 's' : ''}`;
    }
}

async function loadFlashcardCategories() {
    try {
        const categories = await authService.makeAuthenticatedRequest('/flashcards/categories');
        updateCategoryFilter(categories);

    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function updateCategoryFilter(categories) {
    const menu = document.getElementById('categoryFilterMenu');

    // Clear existing menu items
    menu.innerHTML = '';

    // Get current filter to highlight active item
    const currentFilter = document.getElementById('categoryFilterTrigger')
        .querySelector('.dropdown-text').textContent;

    // Add "All Categories" option
    const allCategoriesItem = document.createElement('div');
    allCategoriesItem.className = 'dropdown-item';
    allCategoriesItem.dataset.value = '';
    allCategoriesItem.textContent = 'All Categories';
    if (currentFilter === 'All Categories') {
        allCategoriesItem.classList.add('active');
    }
    allCategoriesItem.addEventListener('click', function() {
        selectCategoryFilter('All Categories', '');
    });
    menu.appendChild(allCategoriesItem);

    // Add category options
    categories.forEach(category => {
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.dataset.value = category;
        item.textContent = category;
        if (currentFilter === category) {
            item.classList.add('active');
        }
        item.addEventListener('click', function() {
            selectCategoryFilter(category, category);
        });
        menu.appendChild(item);
    });
}

function selectCategoryFilter(displayText, filterValue) {
    const trigger = document.getElementById('categoryFilterTrigger');
    const text = trigger.querySelector('.dropdown-text');
    const menu = document.getElementById('categoryFilterMenu');

    // Update display text
    text.textContent = displayText;

    // Close dropdown
    trigger.classList.remove('active');
    menu.classList.remove('active');

    // Remove active class from all items
    menu.querySelectorAll('.dropdown-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to selected item
    const selectedItem = menu.querySelector(`[data-value="${filterValue}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }

    // Load filtered flashcards
    loadFlashcards(filterValue || null);
}

function getCurrentCategoryFilter() {
    const triggerText = document.getElementById('categoryFilterTrigger')
        .querySelector('.dropdown-text').textContent;
    return triggerText === 'All Categories' ? null : triggerText;
}

function updateFlashcardsList(flashcards) {
    const container = document.getElementById('flashcardsList');

    if (flashcards.length === 0) {
        container.innerHTML = '<p class="no-flashcards">No flashcards found</p>';
        return;
    }

    container.innerHTML = flashcards.map(flashcard => `
        <div class="flashcard-item" onclick="viewFlashcard(${flashcard.id})" data-flashcard-id="${flashcard.id}">
            <div class="flashcard-item-header">
                <h4 class="flashcard-term">${flashcard.term}</h4>
                <div class="flashcard-actions-btn">
                    <button class="flashcard-action edit" onclick="event.stopPropagation(); editFlashcard(${flashcard.id})" title="Edit">✏️</button>
                    <button class="flashcard-action delete" onclick="event.stopPropagation(); deleteFlashcard(${flashcard.id})" title="Delete">🗑️</button>
                </div>
            </div>
            <p class="flashcard-definition">${flashcard.definition}</p>
            ${flashcard.category ? `<span class="flashcard-category">${flashcard.category}</span>` : ''}
        </div>
    `).join('');
}

function closeFlashcardsModal() {
    const modal = document.getElementById('manageFlashcardsModal');
    modal.classList.remove('active');
}

// Individual Flashcard Creation
function setupFlashcardFormModalListeners() {
    const modal = document.getElementById('flashcardFormModal');
    const closeBtn = document.getElementById('closeFlashcardFormModal');
    const cancelBtn = document.getElementById('cancelFlashcardForm');
    const form = document.getElementById('flashcardForm');

    closeBtn.addEventListener('click', closeFlashcardFormModal);
    cancelBtn.addEventListener('click', closeFlashcardFormModal);

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeFlashcardFormModal();
        }
    });

    form.addEventListener('submit', handleFlashcardFormSubmit);
}

function openCreateFlashcardModal() {
    window.editingFlashcardId = null;
    const modal = document.getElementById('flashcardFormModal');
    const title = document.getElementById('flashcardFormTitle');
    const submitBtn = document.getElementById('submitFlashcardForm');

    title.textContent = 'Create Flashcard';
    submitBtn.textContent = 'Create Flashcard';

    // Clear form
    document.getElementById('flashcardForm').reset();
    clearFlashcardFormErrors();
    hideFlashcardFormSuccess();

    modal.classList.add('active');
}

function editFlashcard(flashcardId) {
    window.editingFlashcardId = flashcardId;

    // Find flashcard data from the DOM or make API call
    authService.makeAuthenticatedRequest(`/flashcards/${flashcardId}`)
        .then(flashcard => {
            const modal = document.getElementById('flashcardFormModal');
            const title = document.getElementById('flashcardFormTitle');
            const submitBtn = document.getElementById('submitFlashcardForm');

            title.textContent = 'Edit Flashcard';
            submitBtn.textContent = 'Update Flashcard';

            // Populate form
            document.getElementById('flashcardTerm').value = flashcard.term;
            document.getElementById('flashcardDefinition').value = flashcard.definition;
            document.getElementById('flashcardCategory').value = flashcard.category || '';

            clearFlashcardFormErrors();
            hideFlashcardFormSuccess();

            modal.classList.add('active');
        })
        .catch(error => {
            console.error('Error loading flashcard:', error);
            showError('Failed to load flashcard for editing');
        });
}

async function handleFlashcardFormSubmit(e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const flashcardData = {
        term: formData.get('term'),
        definition: formData.get('definition'),
        category: formData.get('category') || null
    };

    try {
        const submitBtn = document.getElementById('submitFlashcardForm');
        submitBtn.classList.add('loading');

        let response;
        if (window.editingFlashcardId) {
            response = await authService.makeAuthenticatedRequest(`/flashcards/${window.editingFlashcardId}`, {
                method: 'PUT',
                body: JSON.stringify(flashcardData)
            });
        } else {
            response = await authService.makeAuthenticatedRequest('/flashcards', {
                method: 'POST',
                body: JSON.stringify(flashcardData)
            });
        }

        // Show success message
        showFlashcardFormSuccess(window.editingFlashcardId ? 'Flashcard updated successfully!' : 'Flashcard created successfully!');

        // Refresh flashcards list with current filter
        const currentCategory = getCurrentCategoryFilter();
        await loadFlashcards(currentCategory);
        await loadFlashcardCategories();

        // Close modal after short delay
        setTimeout(() => {
            closeFlashcardFormModal();
        }, 1500);

    } catch (error) {
        console.error('Error saving flashcard:', error);
        showError('Failed to save flashcard');
    } finally {
        const submitBtn = document.getElementById('submitFlashcardForm');
        submitBtn.classList.remove('loading');
    }
}

function closeFlashcardFormModal() {
    const modal = document.getElementById('flashcardFormModal');
    modal.classList.remove('active');
    window.editingFlashcardId = null;
}

function clearFlashcardFormErrors() {
    document.querySelectorAll('#flashcardFormModal .form-error').forEach(error => {
        error.style.display = 'none';
    });
    document.querySelectorAll('#flashcardFormModal .form-group').forEach(group => {
        group.classList.remove('error');
    });
}

function showFlashcardFormSuccess(message) {
    const successDiv = document.getElementById('flashcardFormSuccess');
    successDiv.textContent = message;
    successDiv.classList.add('show');
}

function hideFlashcardFormSuccess() {
    const successDiv = document.getElementById('flashcardFormSuccess');
    successDiv.classList.remove('show');
}

function showFlashcardsSuccess(message) {
    const successDiv = document.getElementById('flashcardsSuccess');
    successDiv.textContent = message;
    successDiv.classList.add('show');
    setTimeout(() => {
        hideFlashcardsSuccess();
    }, 3000);
}

function hideFlashcardsSuccess() {
    const successDiv = document.getElementById('flashcardsSuccess');
    successDiv.classList.remove('show');
}

// Bulk Upload Functionality
function setupBulkUploadModalListeners() {
    const modal = document.getElementById('bulkUploadModal');
    const closeBtn = document.getElementById('closeBulkUploadModal');
    const cancelBtn = document.getElementById('cancelBulkUpload');
    const form = document.getElementById('bulkUploadForm');

    closeBtn.addEventListener('click', closeBulkUploadModal);
    cancelBtn.addEventListener('click', closeBulkUploadModal);

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeBulkUploadModal();
        }
    });

    form.addEventListener('submit', handleBulkUploadSubmit);
}

function openBulkUploadModal() {
    const modal = document.getElementById('bulkUploadModal');

    // Clear form
    document.getElementById('bulkUploadForm').reset();
    clearBulkUploadErrors();
    hideBulkUploadSuccess();

    // Reset file status
    const fileStatus = document.getElementById('excelFileStatus');
    fileStatus.textContent = 'No file selected';
    fileStatus.classList.remove('has-files');

    modal.classList.add('active');
}

function handleExcelFileSelection(event) {
    const fileInput = event.target;
    const fileStatus = document.getElementById('excelFileStatus');

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];

        // Validate file type
        if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
            fileStatus.textContent = 'Invalid file type. Please select an Excel file (.xlsx or .xls)';
            fileStatus.classList.remove('has-files');
            fileInput.value = '';
            return;
        }

        fileStatus.textContent = `Selected: ${file.name} (${formatFileSize(file.size)})`;
        fileStatus.classList.add('has-files');
    } else {
        fileStatus.textContent = 'No file selected';
        fileStatus.classList.remove('has-files');
    }
}

async function handleBulkUploadSubmit(e) {
    e.preventDefault();

    const fileInput = document.getElementById('bulkExcelFile');
    const file = fileInput.files[0];

    if (!file) {
        showError('Please select an Excel file to upload');
        return;
    }

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.xlsx') && !file.name.toLowerCase().endsWith('.xls')) {
        showError('Invalid file type. Please select an Excel file (.xlsx or .xls)');
        return;
    }

    try {
        const submitBtn = document.getElementById('submitBulkUpload');
        submitBtn.classList.add('loading');
        submitBtn.textContent = 'Processing Excel file...';

        // Create FormData for file upload
        const formData = new FormData();
        formData.append('file', file);

        // Upload to the Excel endpoint
        const response = await fetch(`${authService.baseURL}/flashcards/bulk-excel`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authService.token}`
            },
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to upload Excel file');
        }

        const flashcards = await response.json();

        // Show success message
        showBulkUploadSuccess(`Successfully created ${flashcards.length} flashcards from Excel file!`);

        // Refresh flashcards list with current filter
        const currentCategory = getCurrentCategoryFilter();
        await loadFlashcards(currentCategory);
        await loadFlashcardCategories();

        // Close modal after short delay
        setTimeout(() => {
            closeBulkUploadModal();
        }, 2000);

    } catch (error) {
        console.error('Error uploading Excel file:', error);
        showError(error.message || 'Failed to upload Excel file');
    } finally {
        const submitBtn = document.getElementById('submitBulkUpload');
        submitBtn.classList.remove('loading');
        submitBtn.textContent = 'Upload Flashcards';
    }
}

function closeBulkUploadModal() {
    const modal = document.getElementById('bulkUploadModal');
    modal.classList.remove('active');
}

function clearBulkUploadErrors() {
    document.querySelectorAll('#bulkUploadModal .form-error').forEach(error => {
        error.style.display = 'none';
    });
}

function showBulkUploadSuccess(message) {
    const successDiv = document.getElementById('bulkUploadSuccess');
    successDiv.textContent = message;
    successDiv.classList.add('show');
}

function hideBulkUploadSuccess() {
    const successDiv = document.getElementById('bulkUploadSuccess');
    successDiv.classList.remove('show');
}

async function deleteFlashcard(flashcardId) {
    if (!confirm('Are you sure you want to delete this flashcard?')) {
        return;
    }

    try {
        await authService.makeAuthenticatedRequest(`/flashcards/${flashcardId}`, {
            method: 'DELETE'
        });

        // Refresh flashcards list with current filter
        const currentCategory = getCurrentCategoryFilter();
        await loadFlashcards(currentCategory);
        showInfo('Flashcard deleted successfully');

    } catch (error) {
        console.error('Error deleting flashcard:', error);
        showError('Failed to delete flashcard');
    }
}

// Flashcard Viewer
function setupFlashcardViewerListeners() {
    const modal = document.getElementById('flashcardViewerModal');
    const closeBtn = document.getElementById('closeFlashcardViewer');
    const prevBtn = document.getElementById('prevFlashcard');
    const nextBtn = document.getElementById('nextFlashcard');
    const flashcardContent = document.getElementById('currentFlashcard');

    closeBtn.addEventListener('click', closeFlashcardViewer);
    prevBtn.addEventListener('click', previousFlashcard);
    nextBtn.addEventListener('click', nextFlashcard);

    // Flip flashcard on click
    flashcardContent.addEventListener('click', flipFlashcard);

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        if (!modal.classList.contains('active')) return;

        if (e.key === 'ArrowLeft') previousFlashcard();
        if (e.key === 'ArrowRight') nextFlashcard();
        if (e.key === ' ') {
            e.preventDefault();
            flipFlashcard();
        }
        if (e.key === 'Escape') closeFlashcardViewer();
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeFlashcardViewer();
        }
    });
}

async function viewFlashcard(flashcardId) {
    try {
        // Get all flashcards for navigation
        const currentCategory = document.getElementById('categoryFilterTrigger')
            .querySelector('.dropdown-text').textContent;
        const isAllCategories = currentCategory === 'All Categories';

        let url = '/flashcards';
        if (!isAllCategories) {
            url += `?category=${encodeURIComponent(currentCategory)}`;
        }

        const flashcards = await authService.makeAuthenticatedRequest(url);

        window.currentFlashcards = flashcards;
        window.currentFlashcardIndex = flashcards.findIndex(fc => fc.id === flashcardId);

        if (window.currentFlashcardIndex === -1) {
            throw new Error('Flashcard not found');
        }

        openFlashcardViewer();
        displayCurrentFlashcard();

    } catch (error) {
        console.error('Error viewing flashcard:', error);
        showError('Failed to open flashcard viewer');
    }
}

function openFlashcardViewer() {
    const modal = document.getElementById('flashcardViewerModal');
    modal.classList.add('active');
}

function closeFlashcardViewer() {
    const modal = document.getElementById('flashcardViewerModal');
    modal.classList.remove('active');

    // Reset flip state
    const flashcardContent = document.getElementById('currentFlashcard');
    flashcardContent.classList.remove('flipped');
}

function displayCurrentFlashcard() {
    if (!window.currentFlashcards || window.currentFlashcardIndex < 0) return;

    const flashcard = window.currentFlashcards[window.currentFlashcardIndex];
    const counter = document.getElementById('flashcardCounter');
    const termDisplay = document.getElementById('flashcardTermDisplay');
    const definitionDisplay = document.getElementById('flashcardDefinitionDisplay');
    const prevBtn = document.getElementById('prevFlashcard');
    const nextBtn = document.getElementById('nextFlashcard');
    const flashcardContent = document.getElementById('currentFlashcard');

    // Update counter
    counter.textContent = `${window.currentFlashcardIndex + 1} / ${window.currentFlashcards.length}`;

    // Update content
    termDisplay.textContent = flashcard.term;
    definitionDisplay.textContent = flashcard.definition;

    // Update navigation buttons
    prevBtn.disabled = window.currentFlashcardIndex === 0;
    nextBtn.disabled = window.currentFlashcardIndex === window.currentFlashcards.length - 1;

    // Reset to front side
    flashcardContent.classList.remove('flipped');
}

function flipFlashcard() {
    const flashcardContent = document.getElementById('currentFlashcard');
    flashcardContent.classList.toggle('flipped');
}

function previousFlashcard() {
    if (window.currentFlashcardIndex > 0) {
        window.currentFlashcardIndex--;
        displayCurrentFlashcard();
    }
}

function nextFlashcard() {
    if (window.currentFlashcardIndex < window.currentFlashcards.length - 1) {
        window.currentFlashcardIndex++;
        displayCurrentFlashcard();
    }
}

async function downloadFlashcardsToExcel() {
    try {
        // Get current filtered flashcards (respect the category filter)
        const currentFilter = getCurrentCategoryFilter();
        let flashcards;

        if (currentFilter) {
            flashcards = await authService.makeAuthenticatedRequest(`/flashcards?category=${encodeURIComponent(currentFilter)}`);
        } else {
            flashcards = await authService.makeAuthenticatedRequest('/flashcards');
        }

        if (flashcards.length === 0) {
            showInfo('No flashcards available to download.');
            return;
        }

        // Create CSV content (Excel can open CSV files)
        const csvContent = createFlashcardsCSV(flashcards);

        // Create and download file
        const blob = new Blob([csvContent], { type: 'text/csv;charset-utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        link.setAttribute('href', url);
        link.setAttribute('download', `flashcards_${new Date().toISOString().split('T')[0]}.csv`);
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

        const filterText = currentFilter ? ` (${currentFilter} category)` : '';
        showFlashcardsSuccess(`Downloaded ${flashcards.length} flashcards${filterText} to Excel file!`);

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

// Configure Class Functions
function openConfigureClassModal(classId, className) {
    window.currentConfigureClassId = classId;
    window.currentConfigureClassName = className;

    const modal = document.getElementById('configureClassModal');
    const title = document.getElementById('configureClassTitle');

    title.textContent = `Configure ${className}`;

    // Setup event listeners
    setupConfigureClassListeners();

    modal.classList.add('active');
}

function setupConfigureClassListeners() {
    // Close modal events
    const modal = document.getElementById('configureClassModal');
    const closeBtn = document.getElementById('closeConfigureClassModal');
    const cancelBtn = document.getElementById('cancelConfigureClass');

    closeBtn.addEventListener('click', closeConfigureClassModal);
    cancelBtn.addEventListener('click', closeConfigureClassModal);

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeConfigureClassModal();
        }
    });

    // Option buttons
    document.getElementById('configureFlashcardsBtn').addEventListener('click', function() {
        // Close Configure Class modal first
        closeConfigureClassModal();
        // Then open flashcards modal
        setTimeout(() => {
            openClassFlashcardsModal();
        }, 300);
    });
    document.getElementById('configureContentBtn').addEventListener('click', function() {
        // Close Configure Class modal first
        closeConfigureClassModal();
        // Then open content modal
        setTimeout(() => {
            openSlidesModal(window.currentConfigureClassId, window.currentConfigureClassName);
        }, 300);
    });
}

function closeConfigureClassModal() {
    const modal = document.getElementById('configureClassModal');
    modal.classList.remove('active');
}

// Class Flashcards Assignment Functions
function openClassFlashcardsModal() {
    try {
        // Load flashcards and class data
        loadClassFlashcardsData();

        // Open modal
        const modal = document.getElementById('classFlashcardsModal');
        const title = document.getElementById('classFlashcardsTitle');

        title.textContent = `Assign Flashcards to ${window.currentConfigureClassName}`;
        modal.classList.add('active');

        // Setup event listeners
        setupClassFlashcardsListeners();

    } catch (error) {
        console.error('Error opening class flashcards modal:', error);
        showError('Failed to load flashcard assignment interface');
    }
}

function setupClassFlashcardsListeners() {
    // Close modal events
    const modal = document.getElementById('classFlashcardsModal');
    const closeBtn = document.getElementById('closeClassFlashcardsModal');
    const cancelBtn = document.getElementById('cancelClassFlashcards');
    const saveBtn = document.getElementById('saveFlashcardAssignments');

    closeBtn.addEventListener('click', closeClassFlashcardsModal);
    cancelBtn.addEventListener('click', closeClassFlashcardsModal);
    saveBtn.addEventListener('click', saveFlashcardAssignments);

    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeClassFlashcardsModal();
        }
    });

    // Category filter will be setup after data is loaded
}

function setupAssignmentCategoryFilter() {
    const trigger = document.getElementById('assignCategoryFilterTrigger');
    const menu = document.getElementById('assignCategoryFilterMenu');

    // Remove existing event listeners if any
    trigger.replaceWith(trigger.cloneNode(true));
    const newTrigger = document.getElementById('assignCategoryFilterTrigger');

    newTrigger.addEventListener('click', function() {
        newTrigger.classList.toggle('active');
        menu.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!newTrigger.contains(e.target) && !menu.contains(e.target)) {
            newTrigger.classList.remove('active');
            menu.classList.remove('active');
        }
    });
}

async function loadClassFlashcardsData() {
    try {
        // Load all flashcards
        const allFlashcards = await authService.makeAuthenticatedRequest('/flashcards');

        // Load flashcards assigned to this class
        const classFlashcards = await authService.makeAuthenticatedRequest(`/flashcards/class/${window.currentConfigureClassId}`);

        // Load categories
        const categories = await authService.makeAuthenticatedRequest('/flashcards/categories');
        console.log('Loaded categories for assignment:', categories);

        // Store data globally
        window.allFlashcards = allFlashcards;
        window.classFlashcards = classFlashcards;
        window.assignmentChanges = new Set(); // Track changes

        // Update UI
        updateAssignmentCategoryFilter(categories);
        updateFlashcardAssignmentList(allFlashcards);
        updateAssignmentSummary();

        // Setup dropdown functionality after categories are loaded
        setupAssignmentCategoryFilter();

    } catch (error) {
        console.error('Error loading class flashcards data:', error);
        document.getElementById('flashcardAssignmentList').innerHTML = '<p class="error">Failed to load flashcards</p>';
    }
}

function updateAssignmentCategoryFilter(categories) {
    console.log('updateAssignmentCategoryFilter called with:', categories);
    const menu = document.getElementById('assignCategoryFilterMenu');
    console.log('Assignment category filter menu element:', menu);

    if (!menu) {
        console.error('Assignment category filter menu not found!');
        return;
    }

    // Clear existing menu items
    menu.innerHTML = '';

    // Add "All Categories" option
    const allCategoriesItem = document.createElement('div');
    allCategoriesItem.className = 'dropdown-item active';
    allCategoriesItem.dataset.value = '';
    allCategoriesItem.textContent = 'All Categories';
    allCategoriesItem.addEventListener('click', function() {
        selectAssignmentCategoryFilter('All Categories', '');
    });
    menu.appendChild(allCategoriesItem);

    // Add category options
    categories.forEach(category => {
        console.log('Adding category to assignment filter:', category);
        const item = document.createElement('div');
        item.className = 'dropdown-item';
        item.dataset.value = category;
        item.textContent = category;
        item.addEventListener('click', function() {
            selectAssignmentCategoryFilter(category, category);
        });
        menu.appendChild(item);
    });

    console.log('Assignment category filter updated. Menu now has', menu.children.length, 'items');
}

function selectAssignmentCategoryFilter(displayText, filterValue) {
    const trigger = document.getElementById('assignCategoryFilterTrigger');
    const text = trigger.querySelector('.dropdown-text');
    const menu = document.getElementById('assignCategoryFilterMenu');

    // Update display text
    text.textContent = displayText;

    // Close dropdown
    trigger.classList.remove('active');
    menu.classList.remove('active');

    // Remove active class from all items
    menu.querySelectorAll('.dropdown-item').forEach(item => {
        item.classList.remove('active');
    });

    // Add active class to selected item
    const selectedItem = menu.querySelector(`[data-value="${filterValue}"]`);
    if (selectedItem) {
        selectedItem.classList.add('active');
    }

    // Filter flashcards
    const filteredFlashcards = filterValue ?
        window.allFlashcards.filter(fc => fc.category === filterValue) :
        window.allFlashcards;

    updateFlashcardAssignmentList(filteredFlashcards);
}

function updateFlashcardAssignmentList(flashcards) {
    const container = document.getElementById('flashcardAssignmentList');

    if (flashcards.length === 0) {
        container.innerHTML = '<p class="no-flashcards-assign">No flashcards found</p>';
        return;
    }

    container.innerHTML = flashcards.map(flashcard => {
        const isAssigned = window.classFlashcards.some(cf => cf.id === flashcard.id);
        return `
            <div class="flashcard-assignment-item ${isAssigned ? 'assigned' : ''}" data-flashcard-id="${flashcard.id}">
                <div class="assignment-flashcard-header">
                    <h5 class="assignment-flashcard-term">${flashcard.term}</h5>
                </div>
                <p class="assignment-flashcard-definition">${flashcard.definition}</p>
                ${flashcard.category ? `<span class="assignment-flashcard-category">${flashcard.category}</span>` : ''}
                <button class="assignment-toggle-btn ${isAssigned ? 'assigned' : 'unassigned'}" onclick="toggleFlashcardAssignment(${flashcard.id})">
                    ${isAssigned ? 'Assigned' : 'Assign'}
                </button>
            </div>
        `;
    }).join('');
}

function toggleFlashcardAssignment(flashcardId) {
    const item = document.querySelector(`[data-flashcard-id="${flashcardId}"]`);
    const button = item.querySelector('.assignment-toggle-btn');
    const isCurrentlyAssigned = item.classList.contains('assigned');

    if (isCurrentlyAssigned) {
        // Unassign
        item.classList.remove('assigned');
        button.classList.remove('assigned');
        button.classList.add('unassigned');
        button.textContent = 'Assign';

        // Remove from class flashcards
        window.classFlashcards = window.classFlashcards.filter(cf => cf.id !== flashcardId);
    } else {
        // Assign
        item.classList.add('assigned');
        button.classList.remove('unassigned');
        button.classList.add('assigned');
        button.textContent = 'Assigned';

        // Add to class flashcards
        const flashcard = window.allFlashcards.find(fc => fc.id === flashcardId);
        if (flashcard) {
            window.classFlashcards.push(flashcard);
        }
    }

    // Track change
    window.assignmentChanges.add(flashcardId);
    updateAssignmentSummary();
}

function updateAssignmentSummary() {
    const summaryElement = document.getElementById('assignmentCount');
    const count = window.classFlashcards.length;
    const plural = count === 1 ? 'flashcard' : 'flashcards';
    summaryElement.textContent = `${count} ${plural} assigned to this class`;
}

async function saveFlashcardAssignments() {
    try {
        const saveBtn = document.getElementById('saveFlashcardAssignments');
        saveBtn.classList.add('loading');
        saveBtn.textContent = 'Saving...';

        // Get current flashcard IDs
        const flashcardIds = window.classFlashcards.map(fc => fc.id);

        // Use existing assignment endpoint for each flashcard
        for (const flashcardId of flashcardIds) {
            await authService.makeAuthenticatedRequest(`/flashcards/${flashcardId}/assign`, {
                method: 'POST',
                body: JSON.stringify({
                    flashcard_id: flashcardId,
                    class_ids: [window.currentConfigureClassId]
                })
            });
        }

        // Show success message
        showClassFlashcardsSuccess(`Successfully assigned ${flashcardIds.length} flashcards to ${window.currentConfigureClassName}!`);

        // Close modal after short delay
        setTimeout(() => {
            closeClassFlashcardsModal();
        }, 1500);

    } catch (error) {
        console.error('Error saving flashcard assignments:', error);
        showError('Failed to save flashcard assignments');
    } finally {
        const saveBtn = document.getElementById('saveFlashcardAssignments');
        saveBtn.classList.remove('loading');
        saveBtn.textContent = 'Save Assignments';
    }
}

function closeClassFlashcardsModal() {
    const modal = document.getElementById('classFlashcardsModal');
    modal.classList.remove('active');
}

function showClassFlashcardsSuccess(message) {
    const successDiv = document.getElementById('classFlashcardsSuccess');
    successDiv.textContent = message;
    successDiv.classList.add('show');

    setTimeout(() => {
        successDiv.classList.remove('show');
    }, 3000);
}


/* Cache bust: Sat Sep 27 22:58:00 EDT 2025 */
