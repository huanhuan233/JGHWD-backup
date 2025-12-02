def build_content_prompt(article_title: str, section_outline: str, kb_text: str = "", hw_text: str = "", min_words: str = "",prev_content: str="") -> str:
    """
    构造用于大模型生成结构化段落的提示词 prompt，强化 Markdown 格式严谨性。
    """
    return (
        f"你是一个文章撰写专家，你在为一个名字叫《{article_title}》的大纲内容进行扩写，"
        + (f"上一小节内容：\n\n{prev_content}>\n\n" if prev_content else "")
        + f"请结合如下信息并联系上一节内容进行扩写生成：\n\n{section_outline}\n\n{kb_text}\n\n"
        + (f"行文风格按照：\n\n{hw_text}>撰写\n\n" if hw_text else "")
        + f"返回markdown格式，标题文本必须完全保留【当前小节标题】中的原始内容（包括序号、括号等符号）（例：若当前小节标题为“（一）XXXX”，则一级标题需写为 `# （一）XXXX`）。\n\n"
        + f"若需拆分小节，使用 `##`（二级标题）、`###`（三级标题）等级标题\n\n"
        + f"无需返回多少字数\n\n"
        + (f"无需返回上一小节的内容只是要求联系上下文继续书写写下面小节内容\n\n" if prev_content else "")
        + f"要求内容不少于 {min_words} 字。\n"
        + f"\n【补充提示】{custom_prompt}\n"
    )