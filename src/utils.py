import re

def camel_to_snake(camel: str) -> str:
    """Convert CamelCase to snake_case"""
    snake = re.sub(r'(?<!^)(?=[A-Z])', '_', camel).lower()
    return snake
