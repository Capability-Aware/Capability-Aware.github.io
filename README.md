# Capability-Aware.github.io

研究主页：https://capability-aware.github.io/

汇总 Capability-Aware 系列论文的静态学术主页，无需安装依赖或构建。

## 发布

在仓库 Settings → Pages 中，将 Source 设为 Deploy from a branch，选择 main 分支和 / (root) 目录并保存。

## 本地预览

运行 `python3 -m http.server 8000`，然后访问 http://localhost:8000。

首页：`index.html`。

## 多论文主页（待填入真实论文）

`templates/research-home.html` 是独立编写的学术项目汇总页模板，参考 Project Instinct 的“总主页 + 论文项目入口”组织方式。没有复用其论文、作者、图片或源码。根目录 `index.html` 已采用该结构。

将确认的论文信息填入 `index.html` 中 `id="papers"` 的 JSON 数组，每篇包含以下字段（按数组顺序显示）：

```json
{
  "title": "论文完整标题",
  "authors": "作者列表",
  "venue": "会议或期刊与年份；未发表时填写真实状态",
  "summary": "一句话介绍，可省略",
  "image": "预览图网址或相对路径，可省略",
  "imageAlt": "预览图的文字描述",
  "links": {
    "Project": "论文项目页的完整网址",
    "Paper": "论文或 arXiv 的完整网址",
    "Code": "代码仓库的完整网址",
    "Video": "演示视频的完整网址"
  }
}
```

没有对应资源时删除该链接字段。修改首页后提交并推送到 main 分支即可发布。图片路径按发布后的根目录解析。JSON 文本中不要使用原始 `</script>` 字符串，应将 `<` 写成 `\u003c`。

每篇论文可以链接到现有外部网站，也可以在本仓库建立 `论文简称/index.html`，网址即 `https://capability-aware.github.io/论文简称/`。不需要为每篇论文注册新的 GitHub 账号。
