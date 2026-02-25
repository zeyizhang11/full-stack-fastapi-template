"""Six-Line Divination (六爻排盘) — hexagram data and casting logic."""

import random
import string
from datetime import datetime, timezone

# 64 hexagrams: index 1-64, keyed by binary representation (lines 1-6, bottom to top)
# Each line: 6=old yin (broken, changing), 7=young yang (solid), 8=young yin (broken), 9=old yang (solid, changing)
# Base hexagram: 6→8 (becomes yin), 9→7 (becomes yang); for lookup 7=yang=solid, 8=yin=broken

# Map (lower-trigram, upper-trigram) → hexagram number (King Wen sequence)
# Trigrams: qian=1(111), dui=2(110), li=3(101), zhen=4(100), xun=5(011), kan=6(010), gen=7(001), kun=8(000)
_TRIGRAM_MAP: dict[tuple[int, int], int] = {
    (1, 1): 1,  (1, 2): 43, (1, 3): 14, (1, 4): 34, (1, 5): 9,  (1, 6): 5,  (1, 7): 26, (1, 8): 11,
    (2, 1): 10, (2, 2): 58, (2, 3): 38, (2, 4): 54, (2, 5): 61, (2, 6): 60, (2, 7): 41, (2, 8): 19,
    (3, 1): 13, (3, 2): 49, (3, 3): 30, (3, 4): 55, (3, 5): 37, (3, 6): 63, (3, 7): 22, (3, 8): 36,
    (4, 1): 25, (4, 2): 17, (4, 3): 21, (4, 4): 51, (4, 5): 42, (4, 6): 3,  (4, 7): 27, (4, 8): 24,
    (5, 1): 44, (5, 2): 28, (5, 3): 50, (5, 4): 32, (5, 5): 57, (5, 6): 48, (5, 7): 18, (5, 8): 46,
    (6, 1): 6,  (6, 2): 47, (6, 3): 64, (6, 4): 40, (6, 5): 59, (6, 6): 29, (6, 7): 4,  (6, 8): 7,
    (7, 1): 33, (7, 2): 31, (7, 3): 56, (7, 4): 62, (7, 5): 53, (7, 6): 39, (7, 7): 52, (7, 8): 15,
    (8, 1): 12, (8, 2): 45, (8, 3): 35, (8, 4): 16, (8, 5): 20, (8, 6): 8,  (8, 7): 23, (8, 8): 2,
}

HEXAGRAMS: dict[int, dict] = {
    1:  {"zh": "乾", "pinyin": "Qián", "en": "The Creative", "judgment": "元亨，利贞。"},
    2:  {"zh": "坤", "pinyin": "Kūn", "en": "The Receptive", "judgment": "元亨，利牝马之贞。"},
    3:  {"zh": "屯", "pinyin": "Zhūn", "en": "Difficulty at the Beginning", "judgment": "元亨，利贞，勿用有攸往，利建侯。"},
    4:  {"zh": "蒙", "pinyin": "Méng", "en": "Youthful Folly", "judgment": "亨。匪我求童蒙，童蒙求我。"},
    5:  {"zh": "需", "pinyin": "Xū", "en": "Waiting", "judgment": "有孚，光亨，贞吉，利涉大川。"},
    6:  {"zh": "讼", "pinyin": "Sòng", "en": "Conflict", "judgment": "有孚，窒，惕，中吉，终凶。"},
    7:  {"zh": "师", "pinyin": "Shī", "en": "The Army", "judgment": "贞，丈人，吉无咎。"},
    8:  {"zh": "比", "pinyin": "Bǐ", "en": "Holding Together", "judgment": "吉。原筮，元永贞，无咎。"},
    9:  {"zh": "小畜", "pinyin": "Xiǎo Xù", "en": "Small Taming", "judgment": "亨。密云不雨，自我西郊。"},
    10: {"zh": "履", "pinyin": "Lǚ", "en": "Treading", "judgment": "履虎尾，不咥人，亨。"},
    11: {"zh": "泰", "pinyin": "Tài", "en": "Peace", "judgment": "小往大来，吉亨。"},
    12: {"zh": "否", "pinyin": "Pǐ", "en": "Standstill", "judgment": "否之匪人，不利君子贞，大往小来。"},
    13: {"zh": "同人", "pinyin": "Tóng Rén", "en": "Fellowship", "judgment": "同人于野，亨。利涉大川，利君子贞。"},
    14: {"zh": "大有", "pinyin": "Dà Yǒu", "en": "Great Possession", "judgment": "元亨。"},
    15: {"zh": "谦", "pinyin": "Qiān", "en": "Modesty", "judgment": "亨，君子有终。"},
    16: {"zh": "豫", "pinyin": "Yù", "en": "Enthusiasm", "judgment": "利建侯行师。"},
    17: {"zh": "随", "pinyin": "Suí", "en": "Following", "judgment": "元亨利贞，无咎。"},
    18: {"zh": "蛊", "pinyin": "Gǔ", "en": "Work on the Decayed", "judgment": "元亨，利涉大川。先甲三日，后甲三日。"},
    19: {"zh": "临", "pinyin": "Lín", "en": "Approach", "judgment": "元亨利贞，至于八月有凶。"},
    20: {"zh": "观", "pinyin": "Guān", "en": "Contemplation", "judgment": "盥而不荐，有孚颙若。"},
    21: {"zh": "噬嗑", "pinyin": "Shì Kè", "en": "Biting Through", "judgment": "亨，利用狱。"},
    22: {"zh": "贲", "pinyin": "Bì", "en": "Grace", "judgment": "亨，小利有攸往。"},
    23: {"zh": "剥", "pinyin": "Bō", "en": "Splitting Apart", "judgment": "不利有攸往。"},
    24: {"zh": "复", "pinyin": "Fù", "en": "Return", "judgment": "亨，出入无疾，朋来无咎。"},
    25: {"zh": "无妄", "pinyin": "Wú Wàng", "en": "Innocence", "judgment": "元亨利贞，其匪正有眚。"},
    26: {"zh": "大畜", "pinyin": "Dà Xù", "en": "Great Taming", "judgment": "利贞，不家食，吉，利涉大川。"},
    27: {"zh": "颐", "pinyin": "Yí", "en": "Nourishment", "judgment": "贞吉，观颐，自求口实。"},
    28: {"zh": "大过", "pinyin": "Dà Guò", "en": "Great Preponderance", "judgment": "栋桡，利有攸往，亨。"},
    29: {"zh": "坎", "pinyin": "Kǎn", "en": "The Abysmal", "judgment": "有孚，维心亨，行有尚。"},
    30: {"zh": "离", "pinyin": "Lí", "en": "The Clinging", "judgment": "利贞，亨，畜牝牛，吉。"},
    31: {"zh": "咸", "pinyin": "Xián", "en": "Influence", "judgment": "亨，利贞，取女吉。"},
    32: {"zh": "恒", "pinyin": "Héng", "en": "Duration", "judgment": "亨，无咎，利贞，利有攸往。"},
    33: {"zh": "遯", "pinyin": "Dùn", "en": "Retreat", "judgment": "亨，小利贞。"},
    34: {"zh": "大壮", "pinyin": "Dà Zhuàng", "en": "Great Power", "judgment": "利贞。"},
    35: {"zh": "晋", "pinyin": "Jìn", "en": "Progress", "judgment": "康侯用锡马蕃庶，昼日三接。"},
    36: {"zh": "明夷", "pinyin": "Míng Yí", "en": "Darkening of the Light", "judgment": "利艰贞。"},
    37: {"zh": "家人", "pinyin": "Jiā Rén", "en": "The Family", "judgment": "利女贞。"},
    38: {"zh": "睽", "pinyin": "Kuí", "en": "Opposition", "judgment": "小事吉。"},
    39: {"zh": "蹇", "pinyin": "Jiǎn", "en": "Obstruction", "judgment": "利西南，不利东北；利见大人，贞吉。"},
    40: {"zh": "解", "pinyin": "Xiè", "en": "Deliverance", "judgment": "利西南，无所往，其来复吉；有攸往，夙吉。"},
    41: {"zh": "损", "pinyin": "Sǔn", "en": "Decrease", "judgment": "有孚，元吉，无咎，可贞，利有攸往。"},
    42: {"zh": "益", "pinyin": "Yì", "en": "Increase", "judgment": "利有攸往，利涉大川。"},
    43: {"zh": "夬", "pinyin": "Guài", "en": "Breakthrough", "judgment": "扬于王庭，孚号，有厉，告自邑，不利即戎，利有攸往。"},
    44: {"zh": "姤", "pinyin": "Gòu", "en": "Coming to Meet", "judgment": "女壮，勿用取女。"},
    45: {"zh": "萃", "pinyin": "Cuì", "en": "Gathering Together", "judgment": "亨，王假有庙，利见大人，亨，利贞。"},
    46: {"zh": "升", "pinyin": "Shēng", "en": "Pushing Upward", "judgment": "元亨，用见大人，勿恤，南征吉。"},
    47: {"zh": "困", "pinyin": "Kùn", "en": "Oppression", "judgment": "亨，贞大人吉，无咎，有言不信。"},
    48: {"zh": "井", "pinyin": "Jǐng", "en": "The Well", "judgment": "改邑不改井，无丧无得，往来井井。"},
    49: {"zh": "革", "pinyin": "Gé", "en": "Revolution", "judgment": "巳日乃孚，元亨利贞，悔亡。"},
    50: {"zh": "鼎", "pinyin": "Dǐng", "en": "The Cauldron", "judgment": "元吉，亨。"},
    51: {"zh": "震", "pinyin": "Zhèn", "en": "The Arousing", "judgment": "亨。震来虩虩，笑言哑哑，震惊百里，不丧匕鬯。"},
    52: {"zh": "艮", "pinyin": "Gèn", "en": "Keeping Still", "judgment": "艮其背，不获其身，行其庭，不见其人，无咎。"},
    53: {"zh": "渐", "pinyin": "Jiàn", "en": "Development", "judgment": "女归吉，利贞。"},
    54: {"zh": "归妹", "pinyin": "Guī Mèi", "en": "The Marrying Maiden", "judgment": "征凶，无攸利。"},
    55: {"zh": "丰", "pinyin": "Fēng", "en": "Abundance", "judgment": "亨，王假之，勿忧，宜日中。"},
    56: {"zh": "旅", "pinyin": "Lǚ", "en": "The Wanderer", "judgment": "小亨，旅贞吉。"},
    57: {"zh": "巽", "pinyin": "Xùn", "en": "The Gentle", "judgment": "小亨，利有攸往，利见大人。"},
    58: {"zh": "兑", "pinyin": "Duì", "en": "The Joyous", "judgment": "亨，利贞。"},
    59: {"zh": "涣", "pinyin": "Huàn", "en": "Dispersion", "judgment": "亨，王假有庙，利涉大川，利贞。"},
    60: {"zh": "节", "pinyin": "Jié", "en": "Limitation", "judgment": "亨，苦节不可贞。"},
    61: {"zh": "中孚", "pinyin": "Zhōng Fú", "en": "Inner Truth", "judgment": "豚鱼吉，利涉大川，利贞。"},
    62: {"zh": "小过", "pinyin": "Xiǎo Guò", "en": "Small Preponderance", "judgment": "亨，利贞，可小事，不可大事。"},
    63: {"zh": "既济", "pinyin": "Jì Jì", "en": "After Completion", "judgment": "亨，小利贞，初吉终乱。"},
    64: {"zh": "未济", "pinyin": "Wèi Jì", "en": "Before Completion", "judgment": "亨，小狐汔济，濡其尾，无攸利。"},
}


def _trigram_number(bits: list[int]) -> int:
    """Convert 3 line values (1=yang, 0=yin) to trigram index 1-8."""
    val = bits[2] * 4 + bits[1] * 2 + bits[0]
    # trigram map: 7(111)→1, 6(110)→2, 5(101)→3, 4(100)→4, 3(011)→5, 2(010)→6, 1(001)→7, 0(000)→8
    return 8 - val


def _lines_to_hexagram(lines: list[int]) -> int:
    """Convert 6 line values (7=yang, 8=yin, 9=old-yang, 6=old-yin) to hexagram number.
    
    lines[0] = first (bottom) line, lines[5] = sixth (top) line.
    """
    yang_lines = [1 if v in (7, 9) else 0 for v in lines]
    lower = _trigram_number(yang_lines[0:3])
    upper = _trigram_number(yang_lines[3:6])
    return _TRIGRAM_MAP[(lower, upper)]


def _changed_lines_to_hexagram(lines: list[int]) -> int | None:
    """Return changed hexagram number, or None if no changing lines."""
    if not any(v in (6, 9) for v in lines):
        return None
    changed = []
    for v in lines:
        if v == 9:
            changed.append(8)  # old yang → yin
        elif v == 6:
            changed.append(7)  # old yin → yang
        else:
            changed.append(v)
    return _lines_to_hexagram(changed)


def cast_hexagram() -> dict:
    """Simulate three-coin method to cast a hexagram.
    
    Each coin: heads=3 (yang), tails=2 (yin).
    Three coins per line: sum = 6 (old yin), 7 (young yang), 8 (young yin), 9 (old yang).
    Returns dict with lines, hexagram_number, changed_hexagram_number.
    """
    lines = []
    for _ in range(6):
        coins = [random.choice([2, 3]) for _ in range(3)]
        lines.append(sum(coins))

    hexagram_number = _lines_to_hexagram(lines)
    changed_hexagram_number = _changed_lines_to_hexagram(lines)

    return {
        "lines": lines,
        "hexagram_number": hexagram_number,
        "changed_hexagram_number": changed_hexagram_number,
    }


def generate_reading_number() -> str:
    """Generate a human-readable reading ID like LY-20260225-A1B2."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"LY-{date_str}-{suffix}"
