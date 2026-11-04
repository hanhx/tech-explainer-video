"""One modern Chinese sans family, with regular/medium/semibold hierarchy."""
from pathlib import Path
from functools import lru_cache
import os
from PIL import ImageFont
_given=os.environ.get('EXPLAINER_FONT')
_found=list(Path('/System/Library/AssetsV2/com_apple_MobileAsset_Font7').glob('*/AssetData/PingFang.ttc'))
FONT=_given or (str(_found[0]) if _found else '/System/Library/Fonts/Hiragino Sans GB.ttc')
@lru_cache(None)
def font(size,weight='medium'):
 index={'regular':3,'medium':7,'bold':11}[weight] if 'PingFang' in FONT else (0 if Path(FONT).suffix.lower()!='.ttc' else (2 if weight=='bold' else 0))
 return ImageFont.truetype(FONT,max(1,round(size)),index=index)
