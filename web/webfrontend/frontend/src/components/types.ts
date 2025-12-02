// types.ts
export interface OutlineItemType {
  id: string
  title: string
  font: string
  size: string
  color: string
  bold: boolean
  italic: boolean
  children?: OutlineItemType[]
}
