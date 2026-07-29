# Markdown Viewer v3

单文件 HTML 桌面 Markdown 编辑器，支持块编辑、符号工具栏、公式可视化编辑。

## 架构概要

```
OpenMarkdown.bat → OpenMarkdown.ps1 → file_helper.py (port 18520) → viewer.html (浏览器)
```

- **viewer.html**：主程序，纯前端。Markdown 渲染 + 块编辑器 + KaTeX 数学 + 公式编辑器
- **file_helper.py**：本地 HTTP 服务，提供 `/api/read` `/api/write`，同时 serving viewer.html
- **OpenMarkdown.ps1**：启动脚本，检测端口→启动 helper→打开浏览器
- **OpenMarkdown.bat**：Windows 入口，调用 ps1

## 关键模式

- **块编辑**：Markdown 按空行/标题分割为 block，双击进入 `<textarea>` 编辑，失焦或点 ✔完成 保存
- **KaTeX 渲染**：初始化时全页渲染，编辑完成后重渲染 `#preview` 整个容器
- **公式编辑器**：`#feCanvas` 可视化公式块（分式有横线、根号有 √ 符号），`feUpdate()` 生成 LaTeX + KaTeX 预览，`feInsert()` 插入到 textarea
- **符号工具栏**：`#tbSymWrap` 25 个 LaTeX 符号按钮，`_insertSymbol()` 插入到光标位置
- **保存**：调用 `/api/write` POST 写回文件

## 已知问题

1. KaTeX CDN（jsdelivr）在内地可能加载慢或失败 → `_renderMath` 有手动兜底，但还是依赖 CDN
2. `file_helper.py` 单线程，多连接会卡
3. 表格编辑功能不完善（`_handleTableEnter` 未完全实现）
4. 公式编辑器目前只支持 8 种模板，更复杂的公式（嵌套分式、多行公式）需手写 LaTeX

## 避坑

- **不能 `file://` 打开**：必须通过 `http://localhost:18520/` 才能读写文件
- **修改后必须刷新**：浏览器可能缓存旧版，看右上角版本号确认
- **编辑时失焦会自动保存**：点工具栏/目录/公式面板不会触发失焦，但点其他地方会
- **KaTeX 脚本在 body 末尾同步加载**：不要改成 defer，否则 `_renderMath` 调用时 KaTeX 未就绪
- **公式编辑器用 `insertAdjacentHTML`**：不要用 `innerHTML +=`，会销毁已填的槽位
