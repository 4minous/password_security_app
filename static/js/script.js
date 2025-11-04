// Password Generator functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize length slider
    const lengthSlider = document.getElementById('passwordLength');
    const lengthValue = document.getElementById('lengthValue');
    
    if (lengthSlider) {
        lengthSlider.addEventListener('input', function() {
            lengthValue.textContent = this.value;
        });
    }

    // Generator form submission
    const generatorForm = document.getElementById('generatorForm');
    if (generatorForm) {
        generatorForm.addEventListener('submit', function(e) {
            e.preventDefault();
            generatePassword();
        });
    }

    // Analyzer form submission
    const analyzerForm = document.getElementById('analyzerForm');
    if (analyzerForm) {
        analyzerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            analyzePassword();
        });
    }
});

async function generatePassword() {
    const form = document.getElementById('generatorForm');
    const formData = new FormData(form);
    
    const data = {
        length: parseInt(formData.get('length')),
        include_upper: form.querySelector('[name="include_upper"]').checked,
        include_lower: form.querySelector('[name="include_lower"]').checked,
        include_numbers: form.querySelector('[name="include_numbers"]').checked,
        include_symbols: form.querySelector('[name="include_symbols"]').checked
    };

    showLoading('generator');

    try {
        const response = await fetch('/generate-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }

        displayGeneratedPassword(result);
    } catch (error) {
        alert('Error generating password: ' + error.message);
    } finally {
        hideLoading('generator');
    }
}

function displayGeneratedPassword(result) {
    const resultsSection = document.getElementById('resultsSection');
    const passwordField = document.getElementById('generatedPassword');
    const analysisDiv = document.getElementById('strengthAnalysis');

    passwordField.value = result.password;
    analysisDiv.innerHTML = createStrengthAnalysis(result.analysis);
    
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('fade-in');
}

async function analyzePassword() {
    const passwordInput = document.getElementById('passwordInput');
    const password = passwordInput.value.trim();

    if (!password) {
        alert('Please enter a password to analyze');
        return;
    }

    showLoading('analyzer');

    try {
        const response = await fetch('/analyze-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ password: password })
        });

        const result = await response.json();

        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }

        displayAnalysisResults(result);
    } catch (error) {
        alert('Error analyzing password: ' + error.message);
    } finally {
        hideLoading('analyzer');
    }
}

function displayAnalysisResults(result) {
    const resultsSection = document.getElementById('resultsSection');
    const summaryDiv = document.getElementById('strengthSummary');
    const analysisDiv = document.getElementById('detailedAnalysis');

    summaryDiv.innerHTML = createStrengthSummary(result.analysis);
    analysisDiv.innerHTML = createDetailedAnalysis(result.analysis);
    
    resultsSection.classList.remove('hidden');
    resultsSection.classList.add('fade-in');
}

function createStrengthSummary(analysis) {
    return `
        <div class="text-center mb-6">
            <div class="inline-flex items-center px-4 py-2 rounded-full ${getStrengthColorClass(analysis.strength_class)} text-white font-semibold mb-3">
                <i class="fas fa-shield-alt mr-2"></i>
                ${analysis.strength} (${analysis.score}/10)
            </div>
            <div class="strength-meter ${analysis.strength_class}">
                <div class="strength-fill"></div>
            </div>
            <p class="text-gray-600 mt-2">Length: ${analysis.length} characters | Entropy: ${analysis.entropy.toFixed(1)} bits</p>
        </div>
    `;
}

function createStrengthAnalysis(analysis) {
    return createStrengthSummary(analysis) + createDetailedAnalysis(analysis);
}

function createDetailedAnalysis(analysis) {
    let html = '<div class="space-y-3">';
    
    // Positive feedback
    if (analysis.feedback.length > 0) {
        analysis.feedback.forEach(item => {
            html += `
                <div class="feedback-item feedback-good">
                    <i class="fas fa-check-circle mr-3"></i>
                    ${item}
                </div>
            `;
        });
    }
    
    // Warnings
    if (analysis.warnings.length > 0) {
        analysis.warnings.forEach(item => {
            const isError = item.includes('DO NOT USE') || item.includes('very common');
            const className = isError ? 'feedback-error' : 'feedback-warning';
            const icon = isError ? 'fa-exclamation-circle' : 'fa-exclamation-triangle';
            
            html += `
                <div class="feedback-item ${className}">
                    <i class="fas ${icon} mr-3"></i>
                    ${item}
                </div>
            `;
        });
    }
    
    html += '</div>';
    return html;
}

function getStrengthColorClass(strengthClass) {
    const classes = {
        'weak': 'bg-red-500',
        'moderate': 'bg-orange-500',
        'strong': 'bg-green-500',
        'very-strong': 'bg-emerald-500'
    };
    return classes[strengthClass] || 'bg-gray-500';
}

function copyPassword() {
    const passwordField = document.getElementById('generatedPassword');
    passwordField.select();
    document.execCommand('copy');
    
    // Show copied feedback
    const button = event.target.closest('button');
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-check"></i>';
    button.classList.add('bg-green-600');
    
    setTimeout(() => {
        button.innerHTML = originalHTML;
        button.classList.remove('bg-green-600');
    }, 2000);
}

function togglePasswordVisibility() {
    const passwordInput = document.getElementById('passwordInput');
    const eyeIcon = document.getElementById('eyeIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeIcon.className = 'fas fa-eye-slash';
    } else {
        passwordInput.type = 'password';
        eyeIcon.className = 'fas fa-eye';
    }
}

function showLoading(type) {
    const spinner = document.getElementById('loadingSpinner');
    const results = document.getElementById('resultsSection');
    
    if (spinner) spinner.classList.remove('hidden');
    if (results) results.classList.add('hidden');
}

function hideLoading(type) {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) spinner.classList.add('hidden');
}