"""
六爻排盘核心逻辑 (Liu Yao - Six Lines Divination Logic)

Each of the 64 hexagrams is identified by a 6-bit integer (0-63) where:
- bit 0 (LSB) = line 1 (bottom)  1 = yang (solid), 0 = yin (broken)
- bit 5 (MSB) = line 6 (top)

Trigrams (3-bit, same encoding):
- 0 = 000 = 坤 Kun (Earth)
- 1 = 001 = 震 Zhen (Thunder)
- 2 = 010 = 坎 Kan (Water)
- 3 = 011 = 兑 Dui (Lake)
- 4 = 100 = 艮 Gen (Mountain)
- 5 = 101 = 离 Li (Fire)
- 6 = 110 = 巽 Xun (Wind)
- 7 = 111 = 乾 Qian (Heaven)
"""

import random
import string
from datetime import datetime

# 64 hexagrams indexed by their binary value (0-63)
# lower trigram = bits 0-2, upper trigram = bits 3-5
HEXAGRAMS: dict[int, dict] = {
    63: {"number": 1,  "name": "乾", "pinyin": "Qian",     "english": "The Creative",              "judgment": "元亨利贞"},
    0:  {"number": 2,  "name": "坤", "pinyin": "Kun",      "english": "The Receptive",             "judgment": "元亨，利牝马之贞"},
    17: {"number": 3,  "name": "屯", "pinyin": "Zhun",     "english": "Difficulty at the Beginning","judgment": "元亨利贞，勿用有攸往，利建侯"},
    34: {"number": 4,  "name": "蒙", "pinyin": "Meng",     "english": "Youthful Folly",            "judgment": "亨。匪我求童蒙，童蒙求我"},
    23: {"number": 5,  "name": "需", "pinyin": "Xu",       "english": "Waiting",                   "judgment": "有孚，光亨，贞吉，利涉大川"},
    58: {"number": 6,  "name": "讼", "pinyin": "Song",     "english": "Conflict",                  "judgment": "有孚，窒惕，中吉，终凶"},
    2:  {"number": 7,  "name": "师", "pinyin": "Shi",      "english": "The Army",                  "judgment": "贞，丈人，吉，无咎"},
    16: {"number": 8,  "name": "比", "pinyin": "Bi",       "english": "Holding Together",          "judgment": "吉。原筮，元永贞，无咎"},
    55: {"number": 9,  "name": "小畜","pinyin": "Xiao Xu", "english": "Small Taming",              "judgment": "亨，密云不雨，自我西郊"},
    59: {"number": 10, "name": "履", "pinyin": "Lü",       "english": "Treading",                  "judgment": "履虎尾，不咥人，亨"},
    7:  {"number": 11, "name": "泰", "pinyin": "Tai",      "english": "Peace",                     "judgment": "小往大来，吉亨"},
    56: {"number": 12, "name": "否", "pinyin": "Pi",       "english": "Standstill",                "judgment": "否之匪人，不利君子贞，大往小来"},
    61: {"number": 13, "name": "同人","pinyin": "Tong Ren","english": "Fellowship",                "judgment": "同人于野，亨，利涉大川，利君子贞"},
    47: {"number": 14, "name": "大有","pinyin": "Da You",  "english": "Great Possession",          "judgment": "元亨"},
    4:  {"number": 15, "name": "谦", "pinyin": "Qian",     "english": "Modesty",                   "judgment": "亨，君子有终"},
    8:  {"number": 16, "name": "豫", "pinyin": "Yu",       "english": "Enthusiasm",                "judgment": "利建侯行师"},
    25: {"number": 17, "name": "随", "pinyin": "Sui",      "english": "Following",                 "judgment": "元亨利贞，无咎"},
    38: {"number": 18, "name": "蛊", "pinyin": "Gu",       "english": "Work on the Decayed",       "judgment": "元亨，利涉大川，先甲三日，后甲三日"},
    3:  {"number": 19, "name": "临", "pinyin": "Lin",      "english": "Approach",                  "judgment": "元亨利贞，至于八月有凶"},
    48: {"number": 20, "name": "观", "pinyin": "Guan",     "english": "Contemplation",             "judgment": "盥而不荐，有孚颙若"},
    41: {"number": 21, "name": "噬嗑","pinyin": "Shi Ke",  "english": "Biting Through",            "judgment": "亨，利用狱"},
    37: {"number": 22, "name": "贲", "pinyin": "Bi",       "english": "Grace",                     "judgment": "亨，小利有攸往"},
    32: {"number": 23, "name": "剥", "pinyin": "Bo",       "english": "Splitting Apart",           "judgment": "不利有攸往"},
    1:  {"number": 24, "name": "复", "pinyin": "Fu",       "english": "Return",                    "judgment": "亨，出入无疾，朋来无咎"},
    57: {"number": 25, "name": "无妄","pinyin": "Wu Wang",  "english": "Innocence",                "judgment": "元亨利贞，其匪正有眚，不利有攸往"},
    39: {"number": 26, "name": "大畜","pinyin": "Da Xu",   "english": "Great Taming",              "judgment": "利贞，不家食吉，利涉大川"},
    33: {"number": 27, "name": "颐", "pinyin": "Yi",       "english": "Nourishment",               "judgment": "贞吉，观颐，自求口实"},
    30: {"number": 28, "name": "大过","pinyin": "Da Guo",  "english": "Great Excess",              "judgment": "栋桡，利有攸往，亨"},
    18: {"number": 29, "name": "坎", "pinyin": "Kan",      "english": "The Abysmal",               "judgment": "有孚，维心亨，行有尚"},
    45: {"number": 30, "name": "离", "pinyin": "Li",       "english": "The Clinging",              "judgment": "利贞，亨，畜牝牛，吉"},
    28: {"number": 31, "name": "咸", "pinyin": "Xian",     "english": "Influence",                 "judgment": "亨利贞，取女吉"},
    14: {"number": 32, "name": "恒", "pinyin": "Heng",     "english": "Duration",                  "judgment": "亨，无咎，利贞，利有攸往"},
    60: {"number": 33, "name": "遁", "pinyin": "Dun",      "english": "Retreat",                   "judgment": "亨，小利贞"},
    15: {"number": 34, "name": "大壮","pinyin": "Da Zhuang","english": "Great Power",              "judgment": "利贞"},
    40: {"number": 35, "name": "晋", "pinyin": "Jin",      "english": "Progress",                  "judgment": "康侯用锡马蕃庶，昼日三接"},
    5:  {"number": 36, "name": "明夷","pinyin": "Ming Yi",  "english": "Darkening of the Light",   "judgment": "利艰贞"},
    53: {"number": 37, "name": "家人","pinyin": "Jia Ren",  "english": "The Family",               "judgment": "利女贞"},
    43: {"number": 38, "name": "睽", "pinyin": "Kui",      "english": "Opposition",                "judgment": "小事吉"},
    20: {"number": 39, "name": "蹇", "pinyin": "Jian",     "english": "Obstruction",               "judgment": "利西南，不利东北，利见大人，贞吉"},
    10: {"number": 40, "name": "解", "pinyin": "Jie",      "english": "Deliverance",               "judgment": "利西南，无所往，其来复吉，有攸往夙吉"},
    35: {"number": 41, "name": "损", "pinyin": "Sun",      "english": "Decrease",                  "judgment": "有孚，元吉，无咎，可贞，利有攸往"},
    49: {"number": 42, "name": "益", "pinyin": "Yi",       "english": "Increase",                  "judgment": "利有攸往，利涉大川"},
    31: {"number": 43, "name": "夬", "pinyin": "Guai",     "english": "Breakthrough",              "judgment": "扬于王庭，孚号，有厉，告自邑，不利即戎，利有攸往"},
    62: {"number": 44, "name": "姤", "pinyin": "Gou",      "english": "Coming to Meet",            "judgment": "女壮，勿用取女"},
    24: {"number": 45, "name": "萃", "pinyin": "Cui",      "english": "Gathering Together",        "judgment": "亨，王假有庙，利见大人，亨，利贞，用大牲吉"},
    6:  {"number": 46, "name": "升", "pinyin": "Sheng",    "english": "Pushing Upward",            "judgment": "元亨，用见大人，勿恤，南征吉"},
    26: {"number": 47, "name": "困", "pinyin": "Kun",      "english": "Oppression",                "judgment": "亨，贞，大人吉，无咎，有言不信"},
    22: {"number": 48, "name": "井", "pinyin": "Jing",     "english": "The Well",                  "judgment": "改邑不改井，无丧无得，往来井井"},
    29: {"number": 49, "name": "革", "pinyin": "Ge",       "english": "Revolution",                "judgment": "巳日乃孚，元亨利贞，悔亡"},
    46: {"number": 50, "name": "鼎", "pinyin": "Ding",     "english": "The Cauldron",              "judgment": "元吉，亨"},
    9:  {"number": 51, "name": "震", "pinyin": "Zhen",     "english": "The Arousing",              "judgment": "亨，震来虩虩，笑言哑哑，震惊百里，不丧匕鬯"},
    36: {"number": 52, "name": "艮", "pinyin": "Gen",      "english": "Keeping Still",             "judgment": "艮其背，不获其身，行其庭，不见其人，无咎"},
    52: {"number": 53, "name": "渐", "pinyin": "Jian",     "english": "Development",               "judgment": "女归吉，利贞"},
    11: {"number": 54, "name": "归妹","pinyin": "Gui Mei",  "english": "The Marrying Maiden",      "judgment": "征凶，无攸利"},
    13: {"number": 55, "name": "丰", "pinyin": "Feng",     "english": "Abundance",                 "judgment": "亨，王假之，勿忧，宜日中"},
    44: {"number": 56, "name": "旅", "pinyin": "Lü",       "english": "The Wanderer",              "judgment": "小亨，旅贞吉"},
    54: {"number": 57, "name": "巽", "pinyin": "Xun",      "english": "The Gentle",                "judgment": "小亨，利有攸往，利见大人"},
    27: {"number": 58, "name": "兑", "pinyin": "Dui",      "english": "The Joyous",                "judgment": "亨，利贞"},
    50: {"number": 59, "name": "涣", "pinyin": "Huan",     "english": "Dispersion",                "judgment": "亨，王假有庙，利涉大川，利贞"},
    19: {"number": 60, "name": "节", "pinyin": "Jie",      "english": "Limitation",                "judgment": "亨，苦节不可贞"},
    51: {"number": 61, "name": "中孚","pinyin": "Zhong Fu", "english": "Inner Truth",              "judgment": "豚鱼吉，利涉大川，利贞"},
    12: {"number": 62, "name": "小过","pinyin": "Xiao Guo","english": "Small Excess",              "judgment": "亨，利贞，可小事，不可大事"},
    21: {"number": 63, "name": "既济","pinyin": "Ji Ji",   "english": "After Completion",          "judgment": "亨小，利贞，初吉终乱"},
    42: {"number": 64, "name": "未济","pinyin": "Wei Ji",  "english": "Before Completion",         "judgment": "亨，小狐汔济，濡其尾，无攸利"},
}


def generate_reading_number() -> str:
    """Generate a unique short reading identifier, e.g. LY-20260225-A1B2"""
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    date_str = datetime.utcnow().strftime("%Y%m%d")
    return f"LY-{date_str}-{suffix}"


def cast_hexagram() -> dict:
    """
    Cast a hexagram using the three-coin method.

    Each of the 6 lines is determined by tossing 3 coins:
      - heads=3, tails=2
      - sum = 6 (old yin,  changing → yang), 7 (young yang), 8 (young yin), 9 (old yang, changing → yin)
    Lines are ordered from bottom (line 1) to top (line 6).
    """
    lines: list[int] = []
    for _ in range(6):
        # Each coin: heads=3, tails=2
        coin_sum = sum(random.choice([2, 3]) for _ in range(3))
        lines.append(coin_sum)

    # Build base hexagram binary (yang=1, yin=0); bit i = line i+1
    base_bits = 0
    for i, line in enumerate(lines):
        if line in (7, 9):  # yang
            base_bits |= 1 << i

    # Build changed hexagram (changing lines flip polarity)
    changed_bits = base_bits
    changing_lines: list[int] = []
    for i, line in enumerate(lines):
        if line == 9:  # old yang → yin
            changed_bits &= ~(1 << i)
            changing_lines.append(i + 1)
        elif line == 6:  # old yin → yang
            changed_bits |= 1 << i
            changing_lines.append(i + 1)

    base_hex = HEXAGRAMS[base_bits]
    changed_hex = HEXAGRAMS[changed_bits] if changing_lines else None

    return {
        "lines": lines,
        "base_bits": base_bits,
        "hexagram": base_hex,
        "changed_hexagram": changed_hex,
        "changing_lines": changing_lines,
    }
