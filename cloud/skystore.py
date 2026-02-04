import os

UPLOAD_ROOT = "uploads"

def save_file(user, file):
    user_dir = os.path.join(UPLOAD_ROOT, user)
    os.makedirs(user_dir, exist_ok=True)

    file_path = os.path.join(user_dir, file.filename)
    file.save(file_path)

    return file.filename


def list_files(user):
    user_dir = os.path.join(UPLOAD_ROOT, user)
    if not os.path.exists(user_dir):
        return []
    return os.listdir(user_dir)


def get_file(user, filename):
    user_dir = os.path.join(UPLOAD_ROOT, user)
    return os.path.join(user_dir, filename)
