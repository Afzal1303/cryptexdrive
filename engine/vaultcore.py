import os
from werkzeug.utils import secure_filename

BASE_UPLOAD_DIR = "uploads"


def get_user_dir(username):
    """
    Returns the directory path for a user.
    Creates it if it does not exist.
    """
    user_dir = os.path.join(BASE_UPLOAD_DIR, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir


def save_file(username, file):
    """
    Save uploaded file securely for a user
    """
    filename = secure_filename(file.filename)
    user_dir = get_user_dir(username)
    path = os.path.join(user_dir, filename)

    file.save(path)
    return filename


def list_files(username):
    """
    List all files belonging to a user
    """
    user_dir = get_user_dir(username)
    return os.listdir(user_dir)


def file_path(username, filename):
    """
    Get full file path for download
    """
    return os.path.join(get_user_dir(username), filename)
