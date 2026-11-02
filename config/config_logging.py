#config_logging.py
from pathlib import Path


LOG_PATH = Path(__file__).parent.parent / "logs" / "app.log"
Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'json': {'format': '%(asctime)s [%(levelname)s] %(message)s'},
        'console': { 'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s' },
    },
    
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_PATH,
            'maxBytes': 50 * 1024 * 1024,  # 50 МБ на файл
            'backupCount': 5,              # Хранить 5 старых файлов
            'encoding': 'utf-8',
            'formatter': 'json',
        },
        'console': {
            'level': 'INFO',  
            'class': 'logging.StreamHandler', 
            'formatter': 'console', 
            },
    },
    
    'loggers': {
        'chat': {'level': 'ERROR', 'propagate': True},
        'utils': {'level': 'ERROR', 'propagate': True},
        'run': {'level': 'INFO', 'propagate': True},
        'modules': {'level': 'INFO', 'propagate': True},
    },
    
    'root': {
        'level': 'INFO',
        'handlers': ['file']
    }
}