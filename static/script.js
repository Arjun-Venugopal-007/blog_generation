document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('blogFormElement');
    const titleInput = document.getElementById('title');
    const descriptionInput = document.getElementById('description');
    const charCount = document.getElementById('charCount');
    const generateImageCheckbox = document.getElementById('generateImage');
    const titleError = document.getElementById('titleError');
    const descriptionError = document.getElementById('descriptionError');

    // Check if all required elements exist
    if (!form) {
        console.error('Form element with id "blogFormElement" not found');
        return;
    }
    const config = {
        title: { min: 3, max: 100 },
        description: { min: 10, max: 500, warn: 400, error: 450 }
    };

    descriptionInput.addEventListener('input', updateCharacterCount);
    titleInput.addEventListener('blur', validateTitle);
    descriptionInput.addEventListener('blur', validateDescription);
    titleInput.addEventListener('input', () => clearError(titleInput, titleError));
    descriptionInput.addEventListener('input', () => clearError(descriptionInput, descriptionError));
    form.addEventListener('submit', handleFormSubmit);
    titleInput.addEventListener('input', saveDraft);
    descriptionInput.addEventListener('input', saveDraft);
    generateImageCheckbox.addEventListener('change', handleImageCheckboxChange);
    form.addEventListener('submit', () => {
        localStorage.removeItem('blogDraft');
    });

    updateCharacterCount();
    loadDraft();

    function updateCharacterCount() {
        const currentLength = descriptionInput.value.length;
        charCount.textContent = currentLength;
        if (currentLength > config.description.error) {
            charCount.style.color = 'var(--error-color)';
        } else if (currentLength > config.description.warn) {
            charCount.style.color = 'var(--warning-color)';
        } else {
            charCount.style.color = 'var(--gray-400)';
        }
    }

    function validateTitle() {
        const title = titleInput.value.trim();
        if (!title) {
            showError(titleInput, titleError, 'Please enter a blog title');
            return false;
        }
        if (title.length < config.title.min) {
            showError(titleInput, titleError, `Title must be at least ${config.title.min} characters long`);
            return false;
        }
        if (title.length > config.title.max) {
            showError(titleInput, titleError, `Title must be less than ${config.title.max} characters`);
            return false;
        }
        clearError(titleInput, titleError);
        return true;
    }

    function validateDescription() {
        const description = descriptionInput.value.trim();
        if (!description) {
            showError(descriptionInput, descriptionError, 'Please enter a blog description');
            return false;
        }
        if (description.length < config.description.min) {
            showError(descriptionInput, descriptionError, `Description must be at least ${config.description.min} characters long`);
            return false;
        }
        if (description.length > config.description.max) {
            showError(descriptionInput, descriptionError, `Description must be less than ${config.description.max} characters`);
            return false;
        }
        clearError(descriptionInput, descriptionError);
        return true;
    }

    function showError(input, errorElement, message) {
        input.classList.add('error');
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }

    function clearError(input, errorElement) {
        input.classList.remove('error');
        errorElement.classList.remove('show');
        errorElement.textContent = '';
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        const isTitleValid = validateTitle();
        const isDescriptionValid = validateDescription();
        if (isTitleValid && isDescriptionValid) {
            try {
                if (!form) {
                    throw new Error('Form element not found');
                }
                const formData = new FormData(form);
                const endpoint = form.dataset.endpoint || '/generate';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    body: formData
                });
                if (!response.ok) {
                    let errorMessage = 'An error occurred';
                    try {
                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                            const errorData = await response.json();
                            errorMessage = errorData.message || errorMessage;
                        } else {
                            errorMessage = await response.text();
                        }
                    } catch (err) {
                        console.error('Error parsing response:', err);
                    }
                    if (response.status === 429) {
                        errorMessage = 'Rate limit exceeded. Please try again later.';
                    }
                    throw new Error(errorMessage);
                }
                const html = await response.text();
                document.open();
                document.write(html);
                document.close();
            } catch (error) {
                showAlert('Failed to generate blog: ' + error.message, 'error');
                console.error('Error:', error);
            }
        }
    }



    function showAlert(message, type = 'error') {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} fade-in`;
        alert.textContent = message;
        const card = document.querySelector('.card');
        card.insertBefore(alert, card.firstChild);
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }

    function sanitizeInput(input) {
        const div = document.createElement('div');
        div.textContent = input;
        return div.innerHTML;
    }

    const saveDraft = debounce(() => {
        const draft = {
            title: sanitizeInput(titleInput.value),
            description: sanitizeInput(descriptionInput.value),
            generateImage: generateImageCheckbox.checked,
            timestamp: Date.now()
        };
        localStorage.setItem('blogDraft', JSON.stringify(draft));
    }, 1000);

    function loadDraft() {
        const saved = localStorage.getItem('blogDraft');
        if (saved) {
            try {
                const draft = JSON.parse(saved);
                if (Date.now() - draft.timestamp < 4 * 60 * 60 * 1000) {
                    titleInput.value = draft.title || '';
                    descriptionInput.value = draft.description || '';
                    generateImageCheckbox.checked = draft.generateImage || false;
                    updateCharacterCount();
                    showAlert('Loaded saved draft', 'success');
                } else {
                    localStorage.removeItem('blogDraft');
                    showAlert('Draft expired and was cleared', 'info');
                }
            } catch (e) {
                console.error('Could not load saved draft:', e);
                showAlert('Failed to load saved draft', 'error');
            }
        }
    }

    function handleImageCheckboxChange() {
        if (generateImageCheckbox.checked) {
            const confirmGenerate = confirm('Generating an image may take additional time and resources. Continue?');
            if (!confirmGenerate) {
                generateImageCheckbox.checked = false;
            }
        }
        saveDraft();
    }

    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this, args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }
});