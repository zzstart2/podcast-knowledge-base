// 扩展的播客数据库 - 包含"无人知晓"和"得意忘形"
const podcastData = [
    // === 无人知晓播客 ===
    {
        "id": 101,
        "title": "E45 孟岩对话李继刚：人何以自处",
        "podcast_name": "无人知晓",
        "description": "三小时深度对话：AI时代后人的价值与自处之道",
        "content_summary": "探讨工业革命拿走体力、AI拿走脑力后，留给人的'心力'。讨论AI时代的阅读、表达、教育以及信息输入如何塑造人的命运，最终指向'人何以自处'的核心问题。",
        "key_insights": ["AI时代心力", "信息塑造命运", "自我教育", "深度阅读", "人机共存"],
        "duration_minutes": 180,
        "publish_date": "2026-03-03",
        "guests": [{"name": "李继刚", "title": "AI专家"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/69a64629de29766da93331ec"},
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/无人知晓/id1234567895"},
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMp"}
        ],
        "quality_score": 4.9,
        "keywords": ["AI时代", "人工智能", "自我成长", "哲学思考", "未来社会", "心力", "教育"]
    },
    {
        "id": 102,
        "title": "E44 李晓波对话孟岩：这次，就这样吧？",
        "podcast_name": "无人知晓",
        "description": "关于选择、妥协与人生态度的深度思考",
        "content_summary": "探讨人生中的重要选择时刻，如何在理想与现实之间找到平衡。讨论妥协的智慧、接受的艺术，以及'就这样吧'背后的人生哲学。",
        "key_insights": ["人生选择", "妥协智慧", "接受艺术", "理想现实", "生活态度"],
        "duration_minutes": 150,
        "publish_date": "2026-01-06",
        "guests": [{"name": "李晓波", "title": "生活观察者"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/69a64629de29766da93331ed"},
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/无人知晓/id1234567895"}
        ],
        "quality_score": 4.7,
        "keywords": ["人生哲学", "选择", "妥协", "生活态度", "内心成长", "接受"]
    },
    {
        "id": 103,
        "title": "E43 张潇雨、孟岩对话许哲：没有更好的生活",
        "podcast_name": "无人知晓",
        "description": "三人对话：关于生活本质的哲学思辨",
        "content_summary": "深入探讨'更好生活'的定义，质疑消费主义和成功学的标准答案。讨论简单生活、内在满足与外在追求的关系，重新定义幸福的含义。",
        "key_insights": ["生活本质", "幸福定义", "简单生活", "内在满足", "消费主义反思"],
        "duration_minutes": 165,
        "publish_date": "2025-12-23",
        "guests": [{"name": "张潇雨", "title": "得意忘形主播"}, {"name": "许哲", "title": "生活哲学家"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/episode/69a64629de29766da93331ee"},
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMp"}
        ],
        "quality_score": 4.8,
        "keywords": ["生活哲学", "幸福", "简单生活", "消费主义", "内在成长"]
    },

    // === 得意忘形播客 ===
    {
        "id": 201,
        "title": "EP215 投资的本质是什么？",
        "podcast_name": "得意忘形",
        "description": "深度解析投资哲学与财富增长的底层逻辑",
        "content_summary": "探讨投资的本质不是赚钱，而是认知的变现。分析价值投资、风险管理、长期思维的重要性，以及如何建立正确的投资心态和框架。",
        "key_insights": ["投资本质", "认知变现", "价值投资", "风险管理", "长期思维"],
        "duration_minutes": 85,
        "publish_date": "2026-03-15",
        "guests": [{"name": "张潇雨", "title": "主播"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611f0"},
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/得意忘形/id1234567896"},
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMq"}
        ],
        "quality_score": 4.8,
        "keywords": ["投资", "理财", "财富", "认知", "价值投资", "风险管理"]
    },
    {
        "id": 202,
        "title": "EP214 如何做出更好的决策？",
        "podcast_name": "得意忘形",
        "description": "决策科学与理性思维的实用指南",
        "content_summary": "分析决策的心理偏误，介绍理性决策的框架和工具。讨论如何避免情绪化决策，建立系统性思维，提升决策质量。",
        "key_insights": ["决策科学", "理性思维", "认知偏误", "系统思维", "决策框架"],
        "duration_minutes": 75,
        "publish_date": "2026-03-08",
        "guests": [{"name": "张潇雨", "title": "主播"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611f0"},
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/得意忘形/id1234567896"}
        ],
        "quality_score": 4.7,
        "keywords": ["决策", "理性思维", "认知偏误", "系统思维", "思维模型"]
    },
    {
        "id": 203,
        "title": "EP213 读书的意义是什么？",
        "podcast_name": "得意忘形",
        "description": "重新审视阅读的价值与深度思考的重要性",
        "content_summary": "探讨在信息爆炸时代，深度阅读的价值。分析如何选书、读书、思考书，以及阅读如何塑造认知和人格。讨论碎片化阅读vs深度阅读的差异。",
        "key_insights": ["深度阅读", "认知升级", "思考方法", "知识管理", "智慧获取"],
        "duration_minutes": 68,
        "publish_date": "2026-03-01",
        "guests": [{"name": "张潇雨", "title": "主播"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611f0"},
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMq"}
        ],
        "quality_score": 4.6,
        "keywords": ["阅读", "学习", "思考", "认知", "知识", "智慧"]
    },
    {
        "id": 204,
        "title": "EP212 工作与生活的平衡真的存在吗？",
        "podcast_name": "得意忘形",
        "description": "重新定义工作生活平衡的现代思考",
        "content_summary": "质疑传统的工作生活平衡概念，提出工作生活整合的新思路。探讨如何在快节奏时代找到内在的平衡点，以及意义感对幸福的重要性。",
        "key_insights": ["工作整合", "生活平衡", "意义感", "幸福定义", "时间管理"],
        "duration_minutes": 72,
        "publish_date": "2026-02-22",
        "guests": [{"name": "张潇雨", "title": "主播"}],
        "links": [
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611f0"},
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/得意忘形/id1234567896"}
        ],
        "quality_score": 4.5,
        "keywords": ["工作生活平衡", "时间管理", "意义感", "幸福", "生活方式"]
    },

    // === 原有播客数据 ===
    {
        "id": 1,
        "title": "高效工作的五个底层逻辑",
        "podcast_name": "得到头条",
        "description": "从心理学角度解析工作效率的本质",
        "content_summary": "深入探讨工作效率的心理学基础，提出专注力管理、优先级排序、能量管理、习惯培养和反馈循环五个关键逻辑。",
        "key_insights": ["番茄工作法", "优先级矩阵", "能量管理", "习惯养成", "即时反馈"],
        "duration_minutes": 42,
        "publish_date": "2026-03-10",
        "guests": [{"name": "张三", "title": "时间管理专家"}],
        "links": [
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/得到头条/id1234567890"},
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMk"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611f9"}
        ],
        "quality_score": 4.7,
        "keywords": ["工作效率", "时间管理", "专注力", "习惯", "心理学", "生产力"]
    },
    {
        "id": 2, 
        "title": "从拖延到高效的心理转变",
        "podcast_name": "心理FM",
        "description": "深度分析拖延症的心理根源",
        "content_summary": "从心理学角度剖析拖延行为的根本原因，包括完美主义、恐惧失败等，提供系统性的拖延症治疗方案。",
        "key_insights": ["拖延机制", "完美主义", "恐惧应对", "行动思维", "小步快跑"],
        "duration_minutes": 38,
        "publish_date": "2026-02-28",
        "guests": [{"name": "李四", "title": "心理学博士"}],
        "links": [
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/心理fm/id1234567891"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611fa"}
        ],
        "quality_score": 4.5,
        "keywords": ["拖延症", "心理健康", "完美主义", "恐惧", "行动力"]
    },
    {
        "id": 3,
        "title": "情绪管理：从焦虑到平静",
        "podcast_name": "心理成长",
        "description": "学会管理情绪，找到内心平静",
        "content_summary": "分享情绪管理的核心技巧，通过冥想、呼吸法等实操方法，帮助建立情绪稳定性。",
        "key_insights": ["情绪识别", "正念冥想", "呼吸调节", "认知重构", "情绪日记"],
        "duration_minutes": 35,
        "publish_date": "2026-03-05",
        "guests": [{"name": "简里里", "title": "心理咨询师"}],
        "links": [
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMj"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611fb"}
        ],
        "quality_score": 4.6,
        "keywords": ["情绪管理", "焦虑", "压力", "冥想", "心理健康"]
    },
    {
        "id": 4,
        "title": "创业思维：从0到1的突破",
        "podcast_name": "创业内参",
        "description": "成功创业者的思维模式解析",
        "content_summary": "深入分析创业思维的核心要素，包括机会识别、资源整合、风险管理、团队建设等关键能力。",
        "key_insights": ["机会识别", "MVP验证", "资源杠杆", "快速迭代", "团队搭建"],
        "duration_minutes": 52,
        "publish_date": "2026-02-20",
        "guests": [{"name": "王五", "title": "创业导师"}],
        "links": [
            {"platform": "apple_podcasts", "platform_name": "Apple Podcasts", "url": "https://podcasts.apple.com/cn/podcast/创业内参/id1234567892"},
            {"platform": "ximalaya", "platform_name": "喜马拉雅", "url": "https://www.ximalaya.com/album/123456789"}
        ],
        "quality_score": 4.4,
        "keywords": ["创业", "商业模式", "团队管理", "机会识别", "风险管理"]
    },
    {
        "id": 5,
        "title": "理财入门：普通人的财富增长",
        "podcast_name": "财富密码",
        "description": "适合普通人的理财投资策略",
        "content_summary": "从理财基础知识开始，逐步介绍适合普通人的投资方法，涵盖基金定投、保险配置等。",
        "key_insights": ["理财规划", "基金定投", "保险配置", "风险平衡", "复利威力"],
        "duration_minutes": 40,
        "publish_date": "2026-03-12",
        "guests": [{"name": "赵六", "title": "理财规划师"}],
        "links": [
            {"platform": "spotify", "platform_name": "Spotify", "url": "https://open.spotify.com/show/4rOoJ6Egrf8K2IrywzwOMl"},
            {"platform": "xiaoyuzhou", "platform_name": "小宇宙", "url": "https://www.xiaoyuzhoufm.com/podcast/5e280fab418a84a0461611fc"},
            {"platform": "lizhi", "platform_name": "荔枝FM", "url": "https://www.lizhi.fm/podcast/123456789"}
        ],
        "quality_score": 4.3,
        "keywords": ["理财", "投资", "基金定投", "保险", "财务规划"]
    }
];