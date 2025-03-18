import hashlib


def generate_hash(data: str) -> str:
    """生成 SHA256 哈希"""
    return hashlib.sha256(data.encode('utf-8')).hexdigest() 