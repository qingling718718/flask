.container {
  display: flex;
}

.scrollArea {
  flex: 1;
  overflow: hidden;
}

.scrollContent {
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.scrollContent::-webkit-scrollbar {
  display: none;
}

.columnsWrapper {
  display: flex;
  height: 100%;
  min-width: 400%;
}

.column {
  display: flex;
  flex-shrink: 0;
  width: 25%;
}

.columnWithItems {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.firstRow {
  border: 1px solid hsl(var(--border));
  border-left: 0;
  background: hsl(var(--muted));
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.firstRow:first-child {
  border-left: 1px solid hsl(var(--border));
}

.secondRow {
  display: flex;
}

.subItem {
  flex: 1;
  border: 1px solid hsl(var(--border));
  border-top: 0;
  border-left: 0;
  background: hsl(var(--muted) / 0.5);
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  text-align: center;
}

.subItem:first-child {
  border-left: 1px solid hsl(var(--border));
}

.fullHeightCell {
  flex: 1;
  border: 1px solid hsl(var(--border));
  border-left: 0;
  background: hsl(var(--muted));
  padding: 0 1rem;
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  font-weight: 500;
}

.fullHeightCell:first-child {
  border-left: 1px solid hsl(var(--border));
}

.actionColumn {
  flex-shrink: 0;
  width: 64px;
  border: 1px solid hsl(var(--border));
  border-right: 0;
  background: hsl(var(--muted));
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 500;
}

import type React from "react"
import { forwardRef } from "react"
import styles from "./scrollable-table-header.module.css"

interface HeaderItem {
  label: string
  items?: { label: string }[]
}

interface ScrollableTableHeaderProps {
  headers: HeaderItem[]
  scrollRef?: React.RefObject<HTMLDivElement>
}

const ScrollableTableHeader = forwardRef<HTMLDivElement, ScrollableTableHeaderProps>(({ headers, scrollRef }, ref) => {
  // 检查是否有任何列包含items
  const hasSecondRow = headers.some((header) => header.items && header.items.length > 0)

  return (
    <div className={styles.container}>
      <div className={styles.actionColumn} style={{ width: "64px" }}>
        <div className={styles.actionText}>操作</div>
      </div>

      {/* 可滚动区域 */}
      <div className={styles.scrollArea}>
        <div
          ref={scrollRef || ref}
          className={styles.scrollContent}
          style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
        >
          <div className={styles.columnsWrapper} style={{ minWidth: "400%" }}>
            {headers.map((header, index) => {
              const hasItems = header.items && header.items.length > 0
              const columnWidth = "25%" // 100% / 4

              return (
                <div key={index} className={styles.column} style={{ width: columnWidth }}>
                  {hasItems ? (
                    // 有items的情况：两行结构
                    <div className={styles.columnWithItems}>
                      {/* 第一行 */}
                      <div className={styles.firstRow}>{header.label}</div>
                      {/* 第二行 */}
                      <div className={styles.secondRow}>
                        {header.items!.map((item, itemIndex) => (
                          <div key={itemIndex} className={styles.subItem}>
                            {item.label}
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <div className={styles.fullHeightCell}>{header.label}</div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
})

ScrollableTableHeader.displayName = "ScrollableTableHeader"

export default ScrollableTableHeader



