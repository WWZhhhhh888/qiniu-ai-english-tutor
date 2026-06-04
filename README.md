```markdown
# 🗣️ AI英语口语陪练

> 七牛云 · XEngineer 暑期实训营  
> 语音对话 + 实时纠错 + 三维评分 + 学习报告

---

## 📌 实训营题目要求完成情况

| 要求 | 是否实现 | 说明 |
|------|----------|------|
| 场景选择（面试/点餐/会议/旅游） | ✅ | 支持 4 种真实对话场景 |
| 实时语音对话 | ✅ | Whisper 语音输入 + 文字对话 |
| 语法/表达纠错 | ✅ | 实时返回错误类型与修正建议 |
| 课后总结 | ✅ | 自动生成学习报告 |
| 可量化反馈 | ✅ | 语法、流利度、词汇 0–100 分 |
| 错误统计 & 可视化 | ✅ | 错误类型分布柱状图 |

---

## ✨ 核心功能

- 🎙️ **语音输入**（Whisper）+ 文字输入  
- 🤖 **场景化英语对话**  
- 📝 **实时纠错 + 错误类型分析**  
- 📊 **语法 / 流利度 / 词汇三维评分**  
- 📈 **错误统计图表**  
- 📚 **学习报告自动生成**

---

## 🧪 测试示例（可直接用于演示）

### 点餐场景

| 用户 | AI 回复 |
|------|---------|
| I want to order a pizza. | Sure, what kind of pizza would you like? |
| How much is this? | This pizza is $12.99. |
| Can I have a coffee please? | Of course, one coffee coming right up! |

### 纠错示例（故意输入错误）

> **用户**：I go to restaurant yesterday.  
> **AI 纠错**：go → went（Tense 错误）

---

## 🚀 快速运行

```bash
# 1. 克隆仓库
git clone https://github.com/WWZhhhhh888/qiniu-ai-english-tutor.git
cd qiniu-ai-english-tutor

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 DeepSeek API Key
echo "DEEPSEEK_API_KEY=你的API密钥" > .env

# 4. 启动应用
streamlit run app.py
```

---

## 🧰 技术栈

| 模块 | 技术 |
|------|------|
| 前端界面 | Streamlit |
| 语音识别 | Faster‑Whisper |
| 大模型 | DeepSeek API |
| 音频录制 | sounddevice + scipy |
| 数据分析 | pandas + numpy |

---

## 📁 项目结构

```
qiniu-ai-english-tutor/
├── app.py                # 主程序
├── requirements.txt      # 依赖列表
├── README.md             # 项目说明
├── .gitignore            # 忽略文件
└── (models/)             # Whisper 模型（可选）
```

---

## 🧠 作品亮点

- ✅ 真实语音输入 + 实时对话  
- ✅ 三维可量化评分（语法 / 流利度 / 词汇）  
- ✅ 错误类型统计与可视化  
- ✅ 闭环学习：对话 → 纠错 → 报告  
- ✅ 场景可扩展（4 种真实场景）

---

## 👤 作者

**王子涵**  
上海电力大学 自动化专业  
GitHub：[WWZhhhhh888](https://github.com/WWZhhhhh888)

---

## 📎 实训营提交信息

- **仓库地址**：https://github.com/WWZhhhhh888/qiniu-ai-english-tutor  
- **演示视频**：

---

## 📄 许可证

MIT License
```
