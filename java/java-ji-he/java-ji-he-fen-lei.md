---
cover: >-
  https://images.unsplash.com/photo-1735491428084-853fb91c09e7?crop=entropy&cs=srgb&fm=jpg&ixid=M3wxOTcwMjR8MHwxfHJhbmRvbXx8fHx8fHx8fDE3Mzg0MjU4NDF8&ixlib=rb-4.0.3&q=85
coverY: 0
---

# Java集合分类

<img src="../../.gitbook/assets/file.excalidraw.svg" alt="" class="gitbook-drawing">

````mermaid
确保：
- **Mermaid 代码块的前后都有三反引号（```）**
- `mermaid` 关键字必须紧跟反引号
- **不要在 Markdown 代码块外额外包裹 ` ```markdown `**

---

### **3. 尝试 GitBook 预览**
- 先保存你的页面，然后 **刷新** 试试看是否渲染成功。
- 如果 GitBook 仍然不渲染 Mermaid，尝试 **切换到 HTML 预览模式**（有些 GitBook 版本默认不渲染 Mermaid）。

---

### **4. 使用 HTML 直接嵌入 Mermaid**
如果 Mermaid 代码块仍然不渲染，你可以尝试用 HTML 方式：
```html
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({ startOnLoad: true });
</script>

<div class="mermaid">
graph TD;
    Collection -->|继承| List
    Collection -->|继承| Set
    List --> ArrayList
    List --> LinkedList
    Set --> HashSet
    Set --> LinkedHashSet
    Map --> HashMap
    Map --> SortedMap
    SortedMap --> TreeMap
    HashMap --> LinkedHashMap
</div>
````

