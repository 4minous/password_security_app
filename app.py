from flask import Flask, render_template, request, jsonify, session
import re
import secrets
import string
from typing import Dict

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production!

class PasswordSecurityExpert:
    def __init__(self):
        self.common_passwords = self._load_common_passwords()
        
    def _load_common_passwords(self) -> set:
        """Load common weak passwords"""
        common = {
            'password', '123456', '12345678', '1234', 'qwerty', 'abc123',
            'password1', '12345', '123456789', 'letmein', 'football',
            'admin', 'welcome', 'monkey', 'login', 'passw0rd', 'master',
            'hello', 'freedom', 'whatever', 'qazwsx', 'trustno1', 'sunshine'
        }
        return common

    def generate_strong_password(self, length: int = 16, 
                               include_uppercase: bool = True,
                               include_lowercase: bool = True,
                               include_numbers: bool = True,
                               include_symbols: bool = True) -> Dict:
        """
        Generate a cryptographically secure random password
        """
        try:
            if length < 8:
                return {'error': 'Password length should be at least 8 characters'}
            
            character_pool = ""
            
            if include_lowercase:
                character_pool += string.ascii_lowercase
            if include_uppercase:
                character_pool += string.ascii_uppercase
            if include_numbers:
                character_pool += string.digits
            if include_symbols:
                character_pool += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            
            if not character_pool:
                return {'error': 'At least one character type must be selected'}
            
            # Ensure at least one character from each selected type
            password_chars = []
            
            if include_lowercase:
                password_chars.append(secrets.choice(string.ascii_lowercase))
            if include_uppercase:
                password_chars.append(secrets.choice(string.ascii_uppercase))
            if include_numbers:
                password_chars.append(secrets.choice(string.digits))
            if include_symbols:
                password_chars.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
            
            # Fill the rest with random choices from the pool
            remaining_length = length - len(password_chars)
            for _ in range(remaining_length):
                password_chars.append(secrets.choice(character_pool))
            
            # Shuffle to avoid predictable patterns
            secrets.SystemRandom().shuffle(password_chars)
            
            password = ''.join(password_chars)
            
            # Analyze the generated password
            analysis = self.analyze_password_strength(password)
            
            return {
                'password': password,
                'analysis': analysis
            }
            
        except Exception as e:
            return {'error': f'Error generating password: {str(e)}'}

    def analyze_password_strength(self, password: str) -> Dict:
        """
        Analyze password strength and provide detailed feedback
        """
        score = 0
        feedback = []
        warnings = []
        
        # Length check
        if len(password) >= 16:
            score += 3
            feedback.append("Excellent length (16+ characters)")
        elif len(password) >= 12:
            score += 2
            feedback.append("Good length (12-15 characters)")
        elif len(password) >= 8:
            score += 1
            feedback.append("Minimum acceptable length (8-11 characters)")
        else:
            warnings.append("Too short (minimum 8 characters required)")
        
        # Character variety checks
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_symbol = bool(re.search(r'[^A-Za-z0-9]', password))
        
        char_types = sum([has_upper, has_lower, has_digit, has_symbol])
        
        if char_types >= 4:
            score += 2
            feedback.append("Contains all character types (upper, lower, numbers, symbols)")
        elif char_types == 3:
            score += 1
            feedback.append("Contains 3 character types")
        else:
            warnings.append(f"Limited character variety ({char_types} types)")
        
        # Specific character type feedback
        if has_upper:
            feedback.append("Contains uppercase letters")
        else:
            warnings.append("Missing uppercase letters")
            
        if has_lower:
            feedback.append("Contains lowercase letters")
        else:
            warnings.append("Missing lowercase letters")
            
        if has_digit:
            feedback.append("Contains numbers")
        else:
            warnings.append("Missing numbers")
            
        if has_symbol:
            feedback.append("Contains symbols")
        else:
            warnings.append("Missing symbols")
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            score -= 1
            warnings.append("Contains repeated characters")
        
        if re.search(r'(123|abc|qwerty|password|admin|welcome)', password.lower()):
            score -= 2
            warnings.append("Contains common patterns")
        
        # Check if it's a common password
        if password.lower() in self.common_passwords:
            score = 0
            warnings.append("This is a very common password - DO NOT USE!")
        
        # Entropy calculation
        entropy = self._calculate_entropy(password)
        if entropy > 100:
            score += 2
            feedback.append(f"High entropy ({entropy:.1f} bits)")
        elif entropy > 80:
            score += 1
            feedback.append(f"Moderate entropy ({entropy:.1f} bits)")
        else:
            warnings.append(f"Low entropy ({entropy:.1f} bits)")
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            score -= 1
            warnings.append("Contains sequential characters")
        
        # Determine strength level
        if score >= 7:
            strength = "Very Strong"
            strength_class = "very-strong"
            color = "#10b981"
        elif score >= 5:
            strength = "Strong"
            strength_class = "strong"
            color = "#059669"
        elif score >= 3:
            strength = "Moderate"
            strength_class = "moderate"
            color = "#d97706"
        else:
            strength = "Weak"
            strength_class = "weak"
            color = "#dc2626"
        
        return {
            'score': min(max(score, 0), 10),
            'strength': strength,
            'strength_class': strength_class,
            'color': color,
            'feedback': feedback,
            'warnings': warnings,
            'length': len(password),
            'entropy': entropy,
            'char_types': char_types
        }

    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        char_pool = 0
        if re.search(r'[a-z]', password):
            char_pool += 26
        if re.search(r'[A-Z]', password):
            char_pool += 26
        if re.search(r'[0-9]', password):
            char_pool += 10
        if re.search(r'[^A-Za-z0-9]', password):
            char_pool += 32
        
        if char_pool == 0:
            return 0
            
        return len(password) * (char_pool ** 0.5)

    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters"""
        password_lower = password.lower()
        sequences = ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij', 
                    'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr',
                    'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz',
                    '123', '234', '345', '456', '567', '678', '789']
        
        return any(seq in password_lower for seq in sequences)

# Initialize the security expert
security_expert = PasswordSecurityExpert()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/analyzer')
def analyzer():
    return render_template('analyzer.html')

@app.route('/generate-password', methods=['POST'])
def generate_password():
    data = request.get_json()
    
    length = int(data.get('length', 16))
    include_upper = data.get('include_upper', True)
    include_lower = data.get('include_lower', True)
    include_numbers = data.get('include_numbers', True)
    include_symbols = data.get('include_symbols', True)
    
    result = security_expert.generate_strong_password(
        length=length,
        include_uppercase=include_upper,
        include_lowercase=include_lower,
        include_numbers=include_numbers,
        include_symbols=include_symbols
    )
    
    return jsonify(result)

@app.route('/analyze-password', methods=['POST'])
def analyze_password():
    data = request.get_json()
    password = data.get('password', '')
    
    if not password:
        return jsonify({'error': 'No password provided'})
    
    analysis = security_expert.analyze_password_strength(password)
    
    return jsonify({
        'password': password,
        'analysis': analysis
    })

if __name__ == '__main__':
    app.run(debug=True)