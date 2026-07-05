from app.schemas import Option, Question, Quiz


def generate_mock_quiz(content: str) -> Quiz:
    topic = content.strip()
    safe_topic = topic[:40] if topic else "自定义知识"

    questions = [
        Question(
            id="q1",
            type="single",
            stem=f"学习“{safe_topic}”时，第一步最应该做什么？",
            options=[
                Option(key="A", text="先理解核心概念"),
                Option(key="B", text="直接背所有细节"),
                Option(key="C", text="跳过基础只看难题"),
                Option(key="D", text="完全依赖猜测"),
            ],
            answer=["A"],
            explanation="初学一个知识点时，先理解核心概念能降低后续学习难度。",
            knowledge_point="学习起点",
            difficulty="easy",
        ),
        Question(
            id="q2",
            type="single",
            stem="为什么答题后要立刻看讲解？",
            options=[
                Option(key="A", text="可以马上纠正理解偏差"),
                Option(key="B", text="只是为了增加页面数量"),
                Option(key="C", text="可以跳过知识点"),
                Option(key="D", text="与学习效果无关"),
            ],
            answer=["A"],
            explanation="即时反馈能帮助你在记忆还新鲜时修正错误。",
            knowledge_point="即时反馈",
            difficulty="easy",
        ),
        Question(
            id="q3",
            type="single",
            stem=f"围绕“{safe_topic}”复盘时，最有价值的信息是什么？",
            options=[
                Option(key="A", text="错题和薄弱知识点"),
                Option(key="B", text="按钮颜色"),
                Option(key="C", text="页面滚动距离"),
                Option(key="D", text="无关话题"),
            ],
            answer=["A"],
            explanation="复盘的重点是找出还没掌握的地方，并形成下一步计划。",
            knowledge_point="学习复盘",
            difficulty="medium",
        ),
        Question(
            id="q4",
            type="multiple",
            stem="一套有效的闯关题通常应该包含哪些内容？",
            options=[
                Option(key="A", text="题干"),
                Option(key="B", text="选项"),
                Option(key="C", text="正确答案"),
                Option(key="D", text="详细讲解"),
            ],
            answer=["A", "B", "C", "D"],
            explanation="题干、选项、答案和讲解共同构成完整的练习体验。",
            knowledge_point="题目结构",
            difficulty="medium",
        ),
        Question(
            id="q5",
            type="judge",
            stem="判断：用户输入内容太短时，AI 可以合理补充常识，但不能偏离主题。",
            options=[
                Option(key="true", text="正确"),
                Option(key="false", text="错误"),
            ],
            answer=["true"],
            explanation="合理补充能帮助生成题目，但必须围绕用户原始主题。",
            knowledge_point="内容边界",
            difficulty="easy",
        ),
    ]

    return Quiz(
        quizId="quiz-" + str(abs(hash(topic)) % 1_000_000),
        title=safe_topic,
        summary=f"围绕“{safe_topic}”生成的 5 题闯关练习。",
        questions=questions,
    )
