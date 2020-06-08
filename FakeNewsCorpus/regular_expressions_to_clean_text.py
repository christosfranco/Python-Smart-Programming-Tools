def clean_text(content):

    # Set all words to be lowercased
    clean_text = content.lower()
    
    # Clean dates 
    date1 = r"\b(?:jan(?:uary|\.)?|feb(?:ruary|\.)?|mar(?:ch|\.)?|apr(?:il|\.)?|may|jun(?:e|\.)?|jul(?:y|\.)?|aug(?:ust|\.)?|sep(?:tember|\.)?|oct(?:ober|\.)?|(nov|dec)(?:ember|\.)?) (?:\d{1,2})(,)? (?:1\d{3}|2\d{3})(?=\D|$)"
    date2 = r"\b(\d{1, 2})? (?:jan(?:uary|\.)?|feb(?:ruary|\.)?|mar(?:ch|\.)?|apr(?:il|\.)?|may|jun(?:e|\.)?|jul(?:y|\.)?|aug(?:ust|\.)?|sep(?:tember|\.)?|oct(?:ober|\.)?|(nov|dec)(?:ember|\.)?) (?:1\d{3}|2\d{3})(?=\D|$)"
    date3 = r"\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|(nov|dec)(?:ember)?) (of)? (?:(?:\d{1,2})|(?:1\d{3}|2\d{3}))(?=\D|$)"                         
    date4 = r"(?:\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})"
    date_patterns = [date1, date2, date3, date4]
    
    for pattern in date_patterns:
        clean_text = re.sub(pattern, ' <DATE> ', clean_text)
    
    # Clean email
    email1 = r'([\w0-9._-]+@[\w0-9._-]+\.[\w0-9_-]+)'
    clean_text = re.sub(email1, ' <EMAIL> ', clean_text)
    
    # Clean URLs 
    url1 = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    clean_text = re.sub(url1, ' <URL> ', clean_text)
    
    # Clean numbers
    num1 = r'[0-9]+'
    clean_text = re.sub(num1, ' <NUM> ', clean_text)
    
    # Clean multiple white spaces, tabs, and newlines
    space1 = r"\s+"
    clean_text = re.sub(space1, ' ', clean_text)
    clean_text = clean_text.replace('\n', '')
    
    # Remove ^ since we use them as delimiter
    clean_text = clean_text.replace('^', '')
    
    # Remove "
    clean_text = clean_text.replace('"', '')
    
    # Remove { since we use them as delimiter
    clean_text = clean_text.replace('{', '')
    clean_text = clean_text.replace('}', '')
    
    return clean_text
