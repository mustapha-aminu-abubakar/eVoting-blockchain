import os 
import glob

db_path = "./instance/"
db_files = glob.glob(os.path.join(db_path, "*.sqlite"))

for db in db_files:
    try:
        os.remove(db)
        print(f"Deleted {db}")
    except Exception as e:
        print(f"Error deleting {db}: {e}")
