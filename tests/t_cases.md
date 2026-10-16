# 公式渲染回归用例（独立测试文件，不涉及任何笔记）

## 1. 裸小于号
若 $x<y$ 且 $0<x<1$，则 $y>x$。

正文里的裸小于：a < b 这种情况。

**粗体行**：$a-b\in\mathbb{P}$ 时写 $a>b$（或 $b<a$）。

> 引用里的 $k<n$ 与 $I_n\subseteq I_k$。

- 列表里的 $0<x<1$ 时成立

## 2. 星号上标
例如 $x^*=-\varepsilon/2$ 满足 $\lvert x^*-0\rvert<\varepsilon$ 却在 $I$ 外。

## 3. 表格（单元格里含绝对值竖线）
| 情形 | 不等式 | 结果 |
|---|---|---|
| (b) | $\forall\varepsilon>0:\ |x_n-x|<\varepsilon$ | $x-\varepsilon<x_n<x+\varepsilon$ |
| (i) | $|x-1|<|x|$ | $x>1/2$ |

## 4. 显示公式（不应被段落标签包裹）
$$0<x<1$$

## 5. 代码块与行内代码
```js
if (a<b) { return a; }
```

写 `a<b` 这样。

## 6. HTML 标签
<details><summary>答案</summary>

$x<y$

</details>

## 7. 其他边界
价格 \$5 与公式 $a+b$。集合 A & B 的并。

[链接](http://x.com?a=1&b=2) 与 $a<b$。

## 8. 标题里的公式 $\sup$ 与 $\sqrt2$ 与 $\mathbb{R}$
标题公式进目录时也应该渲染。

## 9. 文件末尾的表格（无尾随换行）
| 列A | 列B |
|---|---|
| $a<b$ | $c>d$ |