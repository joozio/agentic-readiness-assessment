"""Create the documented distributable directory."""
import shutil
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "src" / "ratecard"
TARGET = ROOT / "dist" / "ratecard"

if TARGET.parent.exists():
    shutil.rmtree(TARGET.parent)
TARGET.mkdir(parents=True)
shutil.copy2(SOURCE / "app.py", TARGET / "app.py")
shutil.copy2(SOURCE / "pricing.py", TARGET / "pricing.py")
print(TARGET)

