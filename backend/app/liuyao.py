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
    """Convert 3 line values (bits[0]=bottom-line/1st爻, bits[2]=top-line/3rd爻) to trigram index 1-8.

    先天六山序：乾1(111)屡8(000)。底爻为最高位 (MSB)。
    bits[0]=底爻=MSB，bits[2]=顶爻=LSB。
    """
    val = bits[0] * 4 + bits[1] * 2 + bits[2]   # 底爻(bits[0]) = MSB
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


# ---------------------------------------------------------------------------
# 时间起卦（邵雍先天八卦时间法）
# ---------------------------------------------------------------------------

# 中国传统时辰 (地支) → 数字 1-12
_DIZHI_HOUR: dict[str, int] = {
    "子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6,
    "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12,
}

def hour_to_dizhi_num(hour_24: int) -> int:
    """公历时(0-23) → 时支序号 1-12。子时(23:00-00:59)=1，丑时(01:00-02:59)=2，…"""
    adjusted = (hour_24 + 1) % 24
    return adjusted // 2 + 1


def solar_to_liuyao_params(year: int, month: int, day: int) -> tuple[int, int, int]:
    """公历日期 → (年支序号, 农历月, 农历日)。

    年支序号：子=1, 丑=2, 寅=3, 卯=4, 辰=5, 巳=6, 午=7, 未=8, 申=9, 酉=10, 戌=11, 亥=12
    取的是该公历日期对应的**农历年**的年支（立春前按上一农历年算）。
    """
    from lunardate import LunarDate
    ld = LunarDate.fromSolarDate(year, month, day)
    # (lunar_year - 4) % 12 → 地支下标 0=子; +1 → 1-based; 结果为0时取12
    branch_idx = (ld.year - 4) % 12          # 0=子,1=丑,...,6=午,...,11=亥
    year_branch = branch_idx + 1             # 1-12（永不为0）
    return year_branch, ld.month, ld.day


def cast_by_time(
    year_branch: int,   # 年支序号 子=1,…,亥=12（2026丙午→午=7）
    lunar_month: int,   # 农历月 1-12
    lunar_day: int,     # 农历日 1-30
    hour_24: int,       # 公历时 0-23（内部换算时支）
) -> dict:
    """时间起卦（邵雍先天法）。

    上卦 = (年支 + 农历月 + 农历日) mod 8，0取8。
    下卦 = (年支 + 农历月 + 农历日 + 时支) mod 8，0取8。
    动爻 = (年支 + 农历月 + 农历日 + 时支) mod 6，0取6。
    """
    dz = hour_to_dizhi_num(hour_24)
    base  = year_branch + lunar_month + lunar_day
    total = base + dz

    upper_idx   = base  % 8 or 8   # 1-8，先天八卦序
    lower_idx   = total % 8 or 8
    changing_line = total % 6 or 6  # 第几爻动

    lower_bits = _TRIGRAM_BITS[lower_idx]
    upper_bits = _TRIGRAM_BITS[upper_idx]

    lines: list[int] = []
    for i, bit in enumerate(lower_bits):
        pos = i + 1
        lines.append((9 if bit else 6) if pos == changing_line else (7 if bit else 8))
    for i, bit in enumerate(upper_bits):
        pos = i + 4
        lines.append((9 if bit else 6) if pos == changing_line else (7 if bit else 8))

    return {
        "lines": lines,
        "hexagram_number": _lines_to_hexagram(lines),
        "changed_hexagram_number": _changed_lines_to_hexagram(lines),
        "meta": {
            "method": "time",
            "year_branch": year_branch,
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "hour_branch": dz,
            "upper_trigram": upper_idx,
            "lower_trigram": lower_idx,
            "changing_line": changing_line,
        },
    }


def cast_by_solar_time(year: int, month: int, day: int, hour_24: int) -> dict:
    """公历时间起卦：自动将公历日期转换为（年支、农历月日），再调用 cast_by_time。"""
    year_branch, lunar_month, lunar_day = solar_to_liuyao_params(year, month, day)
    return cast_by_time(year_branch, lunar_month, lunar_day, hour_24)


# ---------------------------------------------------------------------------
# 报数起卦
# ---------------------------------------------------------------------------

def cast_by_numbers(upper_num: int, lower_num: int, changing_num: int) -> dict:
    """报数起卦：用户提供上卦数、下卦数（各取 mod 8，0→8）和动爻数（mod 6，0→6）。

    经典用法：用户随机说三个数字，系统分别对 8、8、6 取模得到上卦、下卦、动爻。
    """
    upper_idx = upper_num % 8 or 8
    lower_idx = lower_num % 8 or 8
    changing_line = changing_num % 6 or 6

    hexagram_number = _TRIGRAM_MAP[(lower_idx, upper_idx)]

    # 使用模块级 _TRIGRAM_BITS 还原爻线（bits[i=0]=底爻/第1爻）
    lower_bits = _TRIGRAM_BITS[lower_idx]
    upper_bits = _TRIGRAM_BITS[upper_idx]

    lines: list[int] = []
    for i, bit in enumerate(lower_bits):
        pos = i + 1
        if pos == changing_line:
            lines.append(9 if bit else 6)  # 老阳/老阴
        else:
            lines.append(7 if bit else 8)
    for i, bit in enumerate(upper_bits):
        pos = i + 4
        if pos == changing_line:
            lines.append(9 if bit else 6)
        else:
            lines.append(7 if bit else 8)

    changed_hexagram_number = _changed_lines_to_hexagram(lines)

    return {
        "lines": lines,
        "hexagram_number": hexagram_number,
        "changed_hexagram_number": changed_hexagram_number,
        "meta": {
            "method": "numbers",
            "upper_num": upper_num,
            "lower_num": lower_num,
            "changing_num": changing_num,
        },
    }


# ---------------------------------------------------------------------------
# 用户指定爻起卦（手动填写六爻）
# ---------------------------------------------------------------------------

def cast_by_manual(lines: list[int]) -> dict:
    """用户手动指定六爻（每爻：6=老阴, 7=少阳, 8=少阴, 9=老阳）。"""
    if len(lines) != 6:
        raise ValueError("Must provide exactly 6 lines.")
    for v in lines:
        if v not in (6, 7, 8, 9):
            raise ValueError(f"Each line must be 6, 7, 8, or 9. Got: {v}")

    hexagram_number = _lines_to_hexagram(lines)
    changed_hexagram_number = _changed_lines_to_hexagram(lines)

    return {
        "lines": lines,
        "hexagram_number": hexagram_number,
        "changed_hexagram_number": changed_hexagram_number,
        "meta": {"method": "manual"},
    }


def generate_reading_number() -> str:
    """Generate a human-readable reading ID like LY-20260225-A1B2."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"LY-{date_str}-{suffix}"


# ═══════════════════════════════════════════════════════════════════════════════
# 六爻完整批注引擎 ── 干支历 / 六神 / 纳甲 / 六亲 / 世应爻 / 伏神
# ═══════════════════════════════════════════════════════════════════════════════

HEAVENLY_STEMS   = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"]
EARTHLY_BRANCHES = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"]

BRANCH_ELEMENT: dict[str, str] = {
    "子":"水","丑":"土","寅":"木","卯":"木",
    "辰":"土","巳":"火","午":"火","未":"土",
    "申":"金","酉":"金","戌":"土","亥":"水",
}
WUXING_SHENG = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
WUXING_KE    = {"木":"土","土":"水","水":"火","火":"金","金":"木"}

# 先天八卦序 index(1-8) 对应的尔线 bits：[bottom_yang, mid_yang, top_yang]
# bottom(底爻/第1生)为 MSB（先天序：乾1=111,屡8=000）
_TRIGRAM_BITS: dict[int, list[int]] = {
    1: [1, 1, 1],  # 乾
    2: [1, 1, 0],  # 屌
    3: [1, 0, 1],  # 离
    4: [1, 0, 0],  # 震
    5: [0, 1, 1],  # 巧
    6: [0, 1, 0],  # 坎
    7: [0, 0, 1],  # 艮
    8: [0, 0, 0],  # 坤
}

# 纳甲表 (ls=下卦天干, us=上卦天干, lb=下卦地支, ub=上卦地支)
_NAJIA_TABLE: dict[int, dict] = {
    1: {"ls":"甲","us":"壬","lb":["子","寅","辰"],"ub":["午","申","戌"]},  # 乾
    2: {"ls":"丁","us":"丁","lb":["巳","卯","丑"],"ub":["亥","酉","未"]},  # 兑
    3: {"ls":"己","us":"己","lb":["卯","丑","亥"],"ub":["酉","未","巳"]},  # 离
    4: {"ls":"庚","us":"庚","lb":["子","寅","辰"],"ub":["午","申","戌"]},  # 震
    5: {"ls":"辛","us":"辛","lb":["丑","亥","酉"],"ub":["未","巳","卯"]},  # 巽
    6: {"ls":"戊","us":"戊","lb":["寅","子","戌"],"ub":["申","午","辰"]},  # 坎
    7: {"ls":"丙","us":"丙","lb":["辰","寅","子"],"ub":["戌","申","午"]},  # 艮
    8: {"ls":"乙","us":"癸","lb":["未","巳","卯"],"ub":["丑","亥","酉"]},  # 坤
}

# 八宫卦序 [八纯, 一世, 二世, 三世, 四世, 五世, 游魂, 归魂]
_BA_GONG: list[dict] = [
    {"name":"乾","element":"金","hexagrams":[1, 44,33,12,20,23,35,14]},
    {"name":"兑","element":"金","hexagrams":[58,47,45,31,39,15,62,61]},
    {"name":"离","element":"火","hexagrams":[30,56,50,64, 4,59, 6,13]},
    {"name":"震","element":"木","hexagrams":[51,16,40,32,46,48,28,17]},
    {"name":"巽","element":"木","hexagrams":[57, 9,37,42,25,21,27,18]},
    {"name":"坎","element":"水","hexagrams":[29,60, 3,63,49,55,36, 7]},
    {"name":"艮","element":"土","hexagrams":[52,22,26,41,38,10,54,53]},
    {"name":"坤","element":"土","hexagrams":[ 2,24,19,11,34,43, 5, 8]},
]

# hexagram_number -> (palace_dict, position_in_palace)
_HEXAGRAM_PALACE: dict[int, tuple] = {
    hn: (p, pos)
    for p in _BA_GONG
    for pos, hn in enumerate(p["hexagrams"])
}

# 世爻/应爻 by palace position (0-7)
_SHI_YING: dict[int, tuple[int, int]] = {
    0:(6,3), 1:(1,4), 2:(2,5), 3:(3,6),
    4:(4,1), 5:(5,2), 6:(4,1), 7:(3,6),
}

# 六神名 & 日干对应起始索引
_LIUSHEN = ["青龙","朱雀","勾陈","腾蛇","白虎","玄武"]
_STEM_SHEN_START = {
    "甲":0,"乙":0,"丙":1,"丁":1,"戊":2,
    "己":3,"庚":4,"辛":4,"壬":5,"癸":5,
}

# hexagram_number -> (lower_trigram, upper_trigram)
_HEX_TO_TRIGRAMS: dict[int, tuple[int, int]] = {v: k for k, v in _TRIGRAM_MAP.items()}


# ─── 干支历计算 ───────────────────────────────────────────────────────────────

def _day_gz_idx(year: int, month: int, day: int) -> int:
    """日干支序号 (0=甲子)，参考点：2000-01-07 = 甲子日。"""
    from datetime import date as _date
    return (_date(year, month, day) - _date(2000, 1, 7)).days % 60


def _year_gz(year: int, month: int, day: int) -> tuple[str, str]:
    """年干支，以立春（约2月4日）为界。"""
    y = year if (month > 2 or (month == 2 and day >= 4)) else year - 1
    idx = (y - 4) % 60
    return HEAVENLY_STEMS[idx % 10], EARTHLY_BRANCHES[idx % 12]


def _month_gz(year: int, month: int, day: int) -> tuple[str, str]:
    """月干支，以12节气为界（近似）。"""
    # (公历月, 日阈值, 月支序号0=子)
    JIEQI = [(1,6,1),(2,4,2),(3,6,3),(4,5,4),(5,6,5),(6,6,6),
             (7,7,7),(8,7,8),(9,8,9),(10,8,10),(11,7,11),(12,7,0)]
    di = 1  # default 丑
    for jm, jd, dzi in JIEQI:
        if month > jm or (month == jm and day >= jd):
            di = dzi
    ys, _ = _year_gz(year, month, day)
    yi = HEAVENLY_STEMS.index(ys)
    # 甲己年寅月起丙(2), 乙庚→戊(4), 丙辛→庚(6), 丁壬→壬(8), 戊癸→甲(0)
    starts = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]
    ms_idx = (starts[yi] + (di - 2) % 12) % 10
    return HEAVENLY_STEMS[ms_idx], EARTHLY_BRANCHES[di]


def compute_ganzhi(year: int, month: int, day: int, hour: int) -> dict:
    """返回完整干支信息及旬空。"""
    ys, yb = _year_gz(year, month, day)
    ms, mb = _month_gz(year, month, day)
    di = _day_gz_idx(year, month, day)
    ds = HEAVENLY_STEMS[di % 10]
    db = EARTHLY_BRANCHES[di % 12]
    hri = ((hour + 1) % 24) // 2
    hrb = EARTHLY_BRANCHES[hri]
    hrs_start = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8][di % 10]
    hrs_idx = (hrs_start + hri) % 10
    hrs = HEAVENLY_STEMS[hrs_idx]
    # 旬空：日干支序中，该旬剩余两个地支
    xk_start = (di % 12 - di % 10) % 12
    xk = [EARTHLY_BRANCHES[(xk_start + 10) % 12], EARTHLY_BRANCHES[(xk_start + 11) % 12]]
    return {
        "solar": f"{year}年{month}月{day}日 {hour:02d}时",
        "year_gz": ys + yb,
        "month_gz": ms + mb,
        "day_gz": ds + db,
        "hour_gz": hrs + hrb,
        "xunkong": xk,
        "day_stem": ds,
    }


# ─── 纳甲 / 六亲 ──────────────────────────────────────────────────────────────

def _najia_for_hex(hex_num: int) -> list[dict]:
    """返回该卦6爻的纳甲列表（line 1→index 0 ... line 6→index 5）。"""
    lt, ut = _HEX_TO_TRIGRAMS[hex_num]
    result = []
    for i in range(3):
        s = _NAJIA_TABLE[lt]["ls"]
        b = _NAJIA_TABLE[lt]["lb"][i]
        result.append({"ganzhi": s + b, "element": BRANCH_ELEMENT[b], "branch": b})
    for i in range(3):
        s = _NAJIA_TABLE[ut]["us"]
        b = _NAJIA_TABLE[ut]["ub"][i]
        result.append({"ganzhi": s + b, "element": BRANCH_ELEMENT[b], "branch": b})
    return result


def _liuqin(palace_e: str, line_e: str) -> str:
    """根据卦宫五行与爻五行计算六亲。"""
    if line_e == palace_e:                          return "兄弟"
    if WUXING_SHENG[palace_e] == line_e:            return "子孙"
    if WUXING_SHENG[line_e] == palace_e:            return "父母"
    if WUXING_KE[palace_e] == line_e:               return "妻财"
    return "官鬼"


# ─── 主标注函数 ────────────────────────────────────────────────────────────────

def compute_annotations(
    hex_num: int,
    year: int, month: int, day: int, hour: int,
    changed_hex_num: int | None = None,
) -> dict:
    """计算卦象完整批注：干支/六神/纳甲/六亲/世应爻/伏神。
    若传入 changed_hex_num 则同时返回变卦的 yao_info。
    """
    gz = compute_ganzhi(year, month, day, hour)

    palace_info, palace_pos = _HEXAGRAM_PALACE.get(hex_num, (_BA_GONG[0], 0))
    palace_e = palace_info["element"]
    pure_hex_num = palace_info["hexagrams"][0]  # 本宫八纯卦

    shi_yao, ying_yao = _SHI_YING.get(palace_pos, (6, 3))

    najia   = _najia_for_hex(hex_num)
    liuqin  = [_liuqin(palace_e, n["element"]) for n in najia]

    start_s = _STEM_SHEN_START.get(gz["day_stem"], 0)
    liushen = [_LIUSHEN[(start_s + i) % 6] for i in range(6)]

    # 伏神：本宫八纯卦对应爻位，若纳甲不同则为伏神
    pure_najia  = _najia_for_hex(pure_hex_num)
    pure_liuqin = [_liuqin(palace_e, n["element"]) for n in pure_najia]
    fuxin = [
        {"ganzhi": pure_najia[i]["ganzhi"], "liuqin": pure_liuqin[i]}
        if pure_najia[i]["ganzhi"] != najia[i]["ganzhi"] else None
        for i in range(6)
    ]

    xk_set = set(gz["xunkong"])
    yao_info = [
        {
            "liuqin":     liuqin[i],
            "najia":      najia[i]["ganzhi"],
            "element":    najia[i]["element"],
            "liushen":    liushen[i],
            "is_shi":     (i + 1) == shi_yao,
            "is_ying":    (i + 1) == ying_yao,
            "is_xunkong": najia[i]["branch"] in xk_set,
            "fuxin":      fuxin[i],
        }
        for i in range(6)
    ]

    # ── 变卦批注 ──────────────────────────────────────────────────────────────
    changed_yao_info: list[dict] | None = None
    changed_palace: str | None = None
    changed_shi_yao: int | None = None
    changed_ying_yao: int | None = None

    if changed_hex_num is not None:
        c_palace_info, c_palace_pos = _HEXAGRAM_PALACE.get(changed_hex_num, (_BA_GONG[0], 0))
        c_palace_e  = c_palace_info["element"]
        c_shi, c_ying = _SHI_YING.get(c_palace_pos, (6, 3))
        c_najia  = _najia_for_hex(changed_hex_num)
        c_liuqin = [_liuqin(c_palace_e, n["element"]) for n in c_najia]
        # 六神从第一爻到第六爻顺序不变（仍由本日日干决定）
        c_fuxin_pure_najia = _najia_for_hex(c_palace_info["hexagrams"][0])
        c_pure_lq = [_liuqin(c_palace_e, n["element"]) for n in c_fuxin_pure_najia]
        c_fuxin = [
            {"ganzhi": c_fuxin_pure_najia[i]["ganzhi"], "liuqin": c_pure_lq[i]}
            if c_fuxin_pure_najia[i]["ganzhi"] != c_najia[i]["ganzhi"] else None
            for i in range(6)
        ]
        changed_yao_info = [
            {
                "liuqin":     c_liuqin[i],
                "najia":      c_najia[i]["ganzhi"],
                "element":    c_najia[i]["element"],
                "liushen":    liushen[i],          # 六神顺序与本卦相同
                "is_shi":     (i + 1) == c_shi,
                "is_ying":    (i + 1) == c_ying,
                "is_xunkong": c_najia[i]["branch"] in xk_set,
                "fuxin":      c_fuxin[i],
            }
            for i in range(6)
        ]
        changed_palace    = c_palace_info["name"]
        changed_shi_yao   = c_shi
        changed_ying_yao  = c_ying

    return {
        "ganzhi":             gz,
        "palace":             palace_info["name"],
        "palace_element":     palace_e,
        "shi_yao":            shi_yao,
        "ying_yao":           ying_yao,
        "yao_info":           yao_info,
        "changed_palace":     changed_palace,
        "changed_shi_yao":    changed_shi_yao,
        "changed_ying_yao":   changed_ying_yao,
        "changed_yao_info":   changed_yao_info,
    }
