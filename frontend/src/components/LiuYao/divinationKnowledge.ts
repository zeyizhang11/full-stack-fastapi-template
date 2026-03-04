// ─── 六爻解卦知识库 ────────────────────────────────────────────────────────────
// 鼠标悬停时展示的解卦参考知识。

export interface KnowledgeEntry {
  title: string
  summary: string         // 一句话概括
  represents: string[]   // 代表事物
  favorable: string      // 旺相时含义
  unfavorable: string    // 休囚时含义
  notes?: string         // 特殊注意事项
}

// ─── 六亲知识 ─────────────────────────────────────────────────────────────────

export const LIUQIN_KNOWLEDGE: Record<string, KnowledgeEntry> = {
  父母: {
    title: "父母爻",
    summary: "主保护、文书、操劳、房屋",
    represents: [
      "父母、长辈、上级、老师、领导",
      "文书、合同、证件、学业、印章",
      "房屋、车辆、衣物（蔽体之物）",
      "天气（问天气）、船（问出行水路）",
    ],
    favorable: "文书顺利、长辈助力、住宅安稳、学业有成",
    unfavorable: "文书受阻、父母操劳、房产有忧、证件难办",
    notes: "父母爻为子孙爻的克星，父母旺则子孙受压。占子女健康忌父母爻过旺。",
  },
  兄弟: {
    title: "兄弟爻",
    summary: "主竞争、劫财、兄弟朋友",
    represents: [
      "兄弟、姐妹、朋友、同辈、合伙人",
      "竞争者、障碍、阻隔",
      "分散、耗费（财的克星）",
    ],
    favorable: "朋友助力、共同合作、兄弟扶持",
    unfavorable: "钱财被夺、合伙受损、竞争激烈、官司中阻碍",
    notes: "兄弟爻为妻财爻的克神。占财运忌兄弟爻发动克世或持世。",
  },
  妻财: {
    title: "妻财爻",
    summary: "主钱财、妻子、饮食享用",
    represents: [
      "妻子（男占）、财富、钱财",
      "飞禽走兽、食物、享受之物",
      "雇员、下属、仆人",
    ],
    favorable: "财运亨通、妻子贤惠、饮食丰足",
    unfavorable: "财运不佳、妻缘有忧、饮食不调",
    notes: "妻财爻为父母爻的克神，占文书、学业时忌妻财爻过旺。",
  },
  子孙: {
    title: "子孙爻",
    summary: "主福德、子女、医药、喜庆",
    represents: [
      "子女、晚辈、学生",
      "医药、医生（问病）",
      "福气、喜庆、享乐",
      "僧道、术士、宠物",
    ],
    favorable: "子嗣顺利、病情好转、福气降临、出行平安",
    unfavorable: "子女有难、病情反复（若无子孙可用）",
    notes: "子孙爻为官鬼爻的克神，求官忌子孙爻发动。问病则喜子孙爻旺相。",
  },
  官鬼: {
    title: "官鬼爻",
    summary: "主官职、疾病、惊忧、男方",
    represents: [
      "官职、仕途、公务、考试（求官）",
      "丈夫（女占）",
      "疾病、祸患、鬼怪、灾难",
      "诉讼、官非、压力",
    ],
    favorable: "仕途顺遂、官运亨通、婚姻中夫君有力（女占）",
    unfavorable: "疾病缠身、诉讼凶险、工作压力大、多惊多忧",
    notes: "女命婚姻以官鬼为夫星。问病、问官司时需重点关注官鬼爻的动静。",
  },
}

// ─── 六神知识 ─────────────────────────────────────────────────────────────────

export interface ShenKnowledgeEntry {
  title: string
  nature: "吉" | "凶" | "中"
  summary: string
  represents: string[]
  auspicious: string    // 逢吉事时
  inauspicious: string  // 逢凶事时
}

export const LIUSHEN_KNOWLEDGE: Record<string, ShenKnowledgeEntry> = {
  青龙: {
    title: "青龙",
    nature: "吉",
    summary: "主喜庆、财运、升迁、吉祥",
    represents: ["官职升迁", "财喜临门", "婚姻美满", "贵人相助"],
    auspicious: "大吉大利，所问之事皆顺，财运官运俱佳",
    inauspicious: "虽有喜事，但恐喜中藏忧；或虚名无实",
  },
  朱雀: {
    title: "朱雀",
    nature: "凶",
    summary: "主口舌是非、文书、消息、火",
    represents: ["口舌纷争", "消息通讯", "文书合同", "火灾灾情"],
    auspicious: "文书大利，书信往来顺畅，好消息将至",
    inauspicious: "口舌是非缠身，争吵诉讼，谨防火灾",
  },
  勾陈: {
    title: "勾陈",
    nature: "凶",
    summary: "主田土、纠纷、牵绊、迟滞",
    represents: ["田地房产纠纷", "官司拖延", "事事牵绊", "土地争执"],
    auspicious: "田土之事有望，产业可守",
    inauspicious: "官司缠身，事情拖延，进退两难，小心被牵连",
  },
  腾蛇: {
    title: "腾蛇",
    nature: "凶",
    summary: "主惊扰、虚诈、梦幻、变动",
    represents: ["虚惊、恐吓", "虚假欺诈", "奇异梦境", "反复无常"],
    auspicious: "变动中有惊无险，事情有转机",
    inauspicious: "谨防虚假欺骗，多惊多梦，事情变化无常不可信",
  },
  白虎: {
    title: "白虎",
    nature: "凶",
    summary: "主凶险、血光、丧事、刀兵",
    represents: ["意外受伤血光", "丧葬服丧", "手术开刀", "争斗冲突"],
    auspicious: "武事（军警、手术）可用，逢金水爻或可化解",
    inauspicious: "血光之灾，凶险之象。问病尤恶，主病情危重",
  },
  玄武: {
    title: "玄武",
    nature: "凶",
    summary: "主暗昧、偷盗、桃花、阴私",
    represents: ["小偷、盗贼", "桃花情爱", "暗中谋划", "不正之事"],
    auspicious: "情感桃花颇旺，暗中有贵人",
    inauspicious: "防盗防骗，暗事阴谋，感情上恐有不正之事，谨防失窃",
  },
}

// ─── 爻位知识（六爻层位含义）──────────────────────────────────────────────────

export interface YaoPositionEntry {
  name: string
  represents: string
  shiYing: string
}

export const YAO_POSITION_KNOWLEDGE: Record<number, YaoPositionEntry> = {
  1: { name: "初爻", represents: "地基、开端、潜伏期", shiYing: "事情初起阶段，结果尚未显现" },
  2: { name: "二爻", represents: "地上、内部、民间", shiYing: "事情发展中，局面逐渐清晰" },
  3: { name: "三爻", represents: "人位下、内外交界", shiYing: "转折点，容易出变数，需谨慎" },
  4: { name: "四爻", represents: "人位上、忧惧之位", shiYing: "近于高层，暗中变动，多忧虑" },
  5: { name: "五爻", represents: "天子之位、最尊贵", shiYing: "主事之爻，结果最关键之位" },
  6: { name: "上爻", represents: "极位、终结、化外", shiYing: "事情终结，过犹不及，物极必反" },
}

// ─── 世应知识 ─────────────────────────────────────────────────────────────────

export const SHI_YING_KNOWLEDGE = {
  shi: {
    title: "世爻",
    description:
      "代表占卦者本人（我方）。世爻旺相则自身强盛，有力气主动争取；世爻衰弱则自身被动，宜守不宜攻。",
  },
  ying: {
    title: "应爻",
    description:
      "代表所求之人、事、物（对方）。应爻旺相则对方积极有力；应爻衰弱则对方消极被动。世应生合为吉，世应冲克需详辨。",
  },
}

// ─── 旬空知识 ─────────────────────────────────────────────────────────────────

export const XUNKONG_KNOWLEDGE = {
  title: "旬空",
  description:
    "旬空之爻，力量大减，所代表之事物暂时落空或作用削弱。但出旬后（月破除外）力量恢复，届时应验。占卜结果忌所用关键爻落空。",
}
