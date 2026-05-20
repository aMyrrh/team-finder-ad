import uuid


def avatar_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1]
    return f"avatars/avatar_{uuid.uuid4()}.{ext}"
