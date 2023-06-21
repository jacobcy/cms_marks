# cms_marks

CMS Marks 是一个新闻质量评分应用，使用 OpenAI API 对新闻质量和流行趋势进行评分，并提供理由。用户可以对评分结果进行微调后，用于生成一个专门用来打分的模型。

## 安装

- 克隆项目到本地：git clone https://github.com/yourusername/cms_marks.git
- 进入项目目录：cd cms_marks
- 安装依赖：pip install -r requirements.txt

## 使用

- 在 OpenAI 上注册账号，并创建 API Key
- 复制 setting-sample.py 文件并重命名为 setting.py，将你的 API Key 替换其中的 YOUR_API_KEY
- 运行应用：python main.py
- 应用运行后，输入新闻内容，即可得到新闻质量评分和相应理由
