// types.ts or useOutlineParser.ts

export interface OutlineSection {
  title: string
  content: string
}

/**
 * 从格式模板结构中提取所有二级标题（id_level = 2）
 */
/**
 * 提取模板中的标题：优先二级标题，若无则用一级标题
 */
export function extractEffectiveTitles(structure: any[]): string[] {
  const result: string[] = []

  function dfs(nodes: any[], parentLevel1Title: string | null = null) {
    for (const node of nodes) {
      if (node.id_level === 1) {
        parentLevel1Title = node.title.trim()
      }

      if (node.id_level === 2) {
        result.push(node.title.trim())
      } else if (node.id_level === 1 && !node.children?.some(n => n.id_level === 2)) {
        // 如果一级标题下没有二级标题，使用一级标题作为段落
        result.push(node.title.trim())
      }

      if (node.children?.length) {
        dfs(node.children, parentLevel1Title)
      }
    }
  }

  dfs(structure)
  return result
}


/**
 * 接收后端返回的 OutlineSection[]，并按二级标题分段处理
 */
export function splitByLevel2TitlesFromStructure(
  structure: OutlineSection[],
  level2Titles: string[]
): OutlineSection[] {
  const lines: string[] = structure.flatMap(item =>
    typeof item.content === 'string' ? item.content.split('\n') : []
  )

  return splitByLevel2Titles(lines, level2Titles)
}

/**
 * 根据二级标题列表分割大纲文本行数组
 */
export function splitByLevel2Titles(
  lines: string[],
  level2Titles: string[]
): OutlineSection[] {
  const result: OutlineSection[] = []
  let current: OutlineSection | null = null
  const titleSet = new Set(level2Titles)

  for (const line of lines) {
    if (typeof line !== 'string') continue // 🛡️ 安全防护

    const trimmed = line.trim()
    if (titleSet.has(trimmed)) {
      if (current) result.push(current)
      current = { title: trimmed, content: '' }
    } else if (current) {
      current.content += trimmed + '\n'
    }
  }

  if (current) result.push(current)
  return result
}

/**
 * 过滤可视段落，只展示模板结构中的二级标题（或无二级标题时的一级标题）
 */
export function filterVisibleSections(
  fullOutline: OutlineSection[],
  structure: any[]
): OutlineSection[] {
  const visibleTitles = extractEffectiveTitles(structure)
  return fullOutline.filter(section =>
    visibleTitles.some(title => section.title.trim().startsWith(title))
  )
}