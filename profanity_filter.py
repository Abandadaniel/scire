from better_profanity import profanity
import re

class ProfanityFilter:
    def __init__(self):
        profanity.load_censor_words()
        
        self.sensitive_terms = [
            'terrorist', 'extremist', 'radical', 
            'jihadist', 'militant', 'insurgent'
        ]
    
    def censor_text(self, text: str, sensitive_mode: str = 'standard') -> str:
        censored = profanity.censor(text, '*')
        
        if sensitive_mode == 'news':
            for term in self.sensitive_terms:
                censored = re.sub(
                    rf'\b{term}\b', 
                    term[0] + '*' * (len(term) - 2) + term[-1] if len(term) > 2 else term[0] + '*',
                    censored,
                    flags=re.IGNORECASE
                )
        
        return censored
    
    def contains_profanity(self, text: str) -> bool:
        return profanity.contains_profanity(text)