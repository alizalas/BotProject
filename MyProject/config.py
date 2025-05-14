import os

BOT_TOKEN = "7646186476:AAEZSEypnLhUnLaNifFXmaJYzSysJ6Jx-Rk"
COVERS_DIR = os.path.join(".", "covers")
CSV_DIR = os.path.join(".", "csv")
PAGINATION_CNT = 5

os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)