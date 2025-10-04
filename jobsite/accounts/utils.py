import re

def format_phone_number(number: str) -> str:
    """
    Format a phone number:
    - US numbers (country code 1 or no code) → +1 (XXX) XXX-XXXX
    - Non-US numbers → +<country_code> <remaining digits>
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', number)
    
    # US number handling
    if (digits.startswith('1') and len(digits) == 11) or len(digits) == 10:
        # Extract country code
        country_code = '1'
        if len(digits) == 11:
            digits = digits[1:]  # remove leading 1
        
        # Format as (XXX) XXX-XXXX
        area_code = digits[:3]
        first_part = digits[3:6]
        second_part = digits[6:10]
        return f"+{country_code} ({area_code}) {first_part}-{second_part}"
    
    # Non-US number handling
    else:
        # Assume first 1-3 digits are country code (common practice)
        country_code = digits[:-10] if len(digits) > 10 else ''
        main_number = digits[-10:] if len(digits) > 10 else digits
        return f"+{country_code}{main_number}" if country_code else f"+{main_number}"