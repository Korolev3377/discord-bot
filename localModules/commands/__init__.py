import importlib

def get(cmd_name):
    try:
        module = importlib.import_module(f"{cmd_name}", __name__)
        return getattr(module, "command")
    except (ImportError, AttributeError):
        return None
