#!/usr/bin/env python3
"""
Logging utility for Azure RAG system
Provides consistent logging across all scripts
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logging(
    name: str = 'azure-rag',
    level: str = 'INFO',
    log_to_file: bool = True,
    log_dir: str = 'logs'
) -> logging.Logger:
    """
    Setup logging to file and console

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files

    Returns:
        Configured logger instance
    """
    # Create log directory
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

    # Generate log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = Path(log_dir) / f'{name}_{timestamp}.log' if log_to_file else None

    # Configure logging
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handler
    if log_to_file and log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always log everything to file
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers = []

    # Add handlers
    for handler in handlers:
        logger.addHandler(handler)

    # Prevent propagation to root logger
    logger.propagate = False

    if log_to_file and log_file:
        logger.info(f"Logging to: {log_file}")

    return logger


class ColoredFormatter(logging.Formatter):
    """Colored output formatter for console"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Color the level name
        record.levelname = f"{color}{record.levelname}{reset}"

        return super().format(record)


def setup_colored_logging(
    name: str = 'azure-rag',
    level: str = 'INFO',
    log_to_file: bool = True,
    log_dir: str = 'logs'
) -> logging.Logger:
    """
    Setup logging with colored output

    Args:
        name: Logger name
        level: Logging level
        log_to_file: Whether to log to file
        log_dir: Directory for log files

    Returns:
        Configured logger with colored output
    """
    # Create log directory
    if log_to_file:
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

    # Generate log filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = Path(log_dir) / f'{name}_{timestamp}.log' if log_to_file else None

    # Configure logging
    handlers = []

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = ColoredFormatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # File handler without colors
    if log_to_file and log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers
    logger.handlers = []

    # Add handlers
    for handler in handlers:
        logger.addHandler(handler)

    # Prevent propagation
    logger.propagate = False

    return logger


# Example usage
if __name__ == "__main__":
    # Test basic logging
    logger = setup_logging(name='test', level='DEBUG')

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")

    print("\n--- Testing colored logging ---\n")

    # Test colored logging
    colored_logger = setup_colored_logging(name='test-colored', level='DEBUG', log_to_file=False)

    colored_logger.debug("This is a debug message")
    colored_logger.info("This is an info message")
    colored_logger.warning("This is a warning message")
    colored_logger.error("This is an error message")
    colored_logger.critical("This is a critical message")

