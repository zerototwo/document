---
cover: >-
  https://images.unsplash.com/photo-1738629532760-35a06d9fa9a3?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3MzkyNjExODl8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# 页分裂与页合并

## 1.页分裂 (Page Split)

页分裂是指当 InnoDB 的 B+ 树索引页（Node Page）已满，在插入新的数据时，InnoDB 需要创建一个新的页，并将部分数据迁移到新页中，以保持 B+ 树的平衡。

### 触发条件：

* 目标页（Leaf Page）已满。
* 插入的数据导致页的容量超出设定值（一般是 16KB）。
* 需要重新分配数据，使 B+ 树保持有序。

### 分裂流程：

1. 创建一个新的页（New Page）。
2. 将部分记录从原页（Old Page）移动到新页。
3. 更新父节点，使其指向新的页。

## 2.页合并 (Page Merge)

页合并是指当数据删除后，导致某个页的利用率过低，InnoDB 会尝试将两个相邻的页合并，以减少存储空间的浪费。

### 触发条件：

* 叶子节点的填充率低于一定阈值（一般为 50%）。
* 该页的数据量较少，合并后仍能适应一个页的大小。
* 相邻页存在合并的可能。

### 合并流程：

1. 将当前页的数据移动到相邻页。
2. 删除原页的索引引用，更新父节点的指针。
3. 释放多余的页，以减少空间占用。

## 3.示例

<figure><img src="../../.gitbook/assets/image.png" alt=""><figcaption><p>Page split and Page merge</p></figcaption></figure>

## 4.总结

* 页分裂 主要用于 插入 时，页已满的情况下，创建新页并重新分配数据。
* 页合并 主要用于 删除 数据后，导致页利用率过低时，合并相邻页以减少存储空间浪费。
* InnoDB 通过 页分裂 和 页合并 来保持 B+ 树的平衡，提高查询效率，避免存储浪费。

🔹 页分裂 适用于写密集型场景，而 页合并 适用于删除和更新频繁的场景。
