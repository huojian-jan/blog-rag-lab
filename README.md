# Blog RAG Demo

一个用于学习 RAG 的小项目：把 `data/` 目录下保存的博客链接抓取下来，提取网页正文、向量化并写入 Chroma，然后通过 LlamaIndex 做检索问答。

当前项目使用的是 OpenAI 兼容接口，因此既可以接 OpenAI，也可以接支持 OpenAI API 格式的中转或自建服务。

## 功能概览

- 读取 `data/` 下的链接清单文件
- 抓取博客网页并提取正文文本
- 使用 `SentenceSplitter` 对文档分块
- 使用 embedding 模型写入 Chroma 本地向量库
- 通过命令行提问，基于检索结果生成回答
- 输出回答时打印参考片段和来源链接，便于检查命中内容

## 技术栈

- Python
- LlamaIndex
- ChromaDB
- OpenAI-compatible API
- `python-dotenv`
- `requests`
- Beautiful Soup

## 项目结构

```text
rag/
├── app/
│   ├── config.py      # 路径和环境变量配置
│   ├── ingest.py      # 读取链接并构建向量索引
│   ├── chat.py        # 命令行问答入口
│   ├── url_loader.py  # 抓取网页并提取正文
│   └── agents.py      # 预留实验文件，当前主流程未使用
├── data/              # 博客链接清单
├── storage/chroma/    # Chroma 持久化数据
├── requirements.txt
└── README.md
```

## 运行环境

- Python 3.10+
- 可用的 LLM 和 Embedding API Key
- 可访问博客网页的网络环境

## 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 环境变量

项目通过 `.env` 读取配置。仓库已经忽略 `.env`，你可以在根目录手动创建。

示例：

```env
OPENAI_BASE_URL=https://api.openai.com/v1

OPENAI_MODEL=gpt-4o-mini
OPENAI_MODEL_API_KEY=your_llm_api_key

OPENAI_EMBED_MODEL=text-embedding-3-small
OPENAI_EMBED_API_KEY=your_embedding_api_key
```

说明：

- `OPENAI_BASE_URL` 默认值写在代码里是 `https://aihubmix.com/v1`
- `OPENAI_MODEL` 用于问答生成
- `OPENAI_EMBED_MODEL` 用于向量化
- 如果你的服务同时支持 LLM 和 Embedding，也可以把两个 API Key 配成同一个值

## 准备数据

`data/` 目录里只放一个链接清单文件，不再放博客源码。当前代码会递归读取这些文本文件：

- `.md`
- `.txt`

一个文件里可以写多个博客地址，支持一行一个 URL，也支持混在普通文本里。

例如：

```text
https://your-blog.com/post-1
https://your-blog.com/post-2
```

导入后会保存这些元信息：

- 来源链接
- 来源文件名
- 页面标题

## 构建索引

首次运行或更新 `data/` 后，先执行：

```bash
python app/ingest.py
```

这个脚本会做几件事：

1. 读取 `data/` 下的链接清单文件
2. 提取其中的 URL 并抓取网页内容
3. 按 `chunk_size=500`、`chunk_overlap=80` 切分
4. 将向量写入本地 `storage/chroma/`
5. 使用名为 `blog_rag` 的集合保存索引

每次执行都会先清空旧的 `blog_rag` 集合，再重建索引，避免重复写入。

## 启动问答

```bash
python app/chat.py
```

启动后可在命令行持续提问，输入以下任一命令退出：

- `quit`
- `exit`
- `q`

程序会输出：

- 用户问题
- 最终回答
- 参考片段
- 来源链接
- 相似度分数

## 重建索引

如果你替换了链接、更新了博客文章内容、修改了 embedding 模型，或者想从头重建，可以删除已有 Chroma 数据后重新执行 `ingest.py`。

```bash
rm -rf storage/chroma
python app/ingest.py
```

## 示例问题

示例清单文件可以参考 [data/blog_links.txt](/Users/huojian/Desktop/build_your_own_x/rag/data/blog_links.txt)。

基于当前博客内容，可以尝试问：

- 作者是如何克服收集癖的？
- 作者为什么会用 RSS 订阅独立博客？
- 作者从工程管理转码的经历里提到了哪些关键转折？
- 什么是圈复杂度？

## 当前实现限制

- 只有命令行交互，没有 Web UI
- 检索策略比较基础，当前只配置了 `similarity_top_k=4`
- 网页正文提取使用的是通用 HTML 解析，对强依赖前端渲染的网站效果可能一般
- 没有对回答结果做引用格式化，只打印原始参考片段
- `app/agents.py` 还不是完整功能入口，当前主流程请使用 `ingest.py` 和 `chat.py`

## 后续可扩展方向

- 增加 Streamlit / Gradio Web 界面
- 支持多轮对话上下文
- 加入 rerank
- 支持引用高亮和来源链接
- 为不同知识库拆分不同 collection

## License

当前仓库未声明 License，如需开源发布，建议补充。
