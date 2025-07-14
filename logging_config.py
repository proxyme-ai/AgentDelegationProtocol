"""Logging configuration for Agent Delegation Protocol."""

import logging
import logging.config
import os
from typing import Dict, Any
from config import config


def setup_logging() -> None:
    """Set up logging configuration."""
    
    logging_config: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': config.log_format
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
            },
            'json': {
                'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': config.log_level,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'detailed',
                'filename': 'agent_delegation.log',
                'mode': 'a'
            },
            'security': {
                'class': 'logging.FileHandler',
                'level': 'WARNING',
                'formatter': 'json',
                'filename': 'security.log',
                'mode': 'a'
            }
        },
        'loggers': {
            'auth_server': {
                'level': config.log_level,
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'resource_server': {
                'level': config.log_level,
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'security': {
                'level': 'WARNING',
                'handlers': ['console', 'security'],
                'propagate': False
            }
        },
        'root': {
            'level': config.log_level,
            'handlers': ['console']
        }
    }
    
    logging.config.dictConfig(logging_config)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def log_security_event(event_type: str, details: Dict[str, Any]) -> None:
    """Log security-related events."""
    security_logger = get_logger('security')
    security_logger.warning(f"Security Event: {event_type}", extra=details)


# Set up logging when module is imported
setup_logging()