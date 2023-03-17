from setting import config
import openai
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW

# 设置openai api密钥
openai.api_key = config.key

# 初始化tokenizer和模型
tokenizer = AutoTokenizer.from_pretrained("textattack/bert-base-uncased-imdb")
model = AutoModelForSequenceClassification.from_pretrained(
    "textattack/bert-base-uncased-imdb")

# 定义优化器和损失函数
optimizer = AdamW(model.parameters(), lr=1e-5)
loss_fn = torch.nn.CrossEntropyLoss()

# 准备训练数据和标签
train_texts = ["I love this movie",
               "This movie is terrible", "This is a great movie"]
train_labels = [1, 0, 1]
train_encodings = tokenizer(train_texts, truncation=True, padding=True)

# 将数据转换为torch tensor格式
train_inputs = torch.tensor(train_encodings['input_ids'])
train_labels = torch.tensor(train_labels)

# 训练模型
model.train()
for epoch in range(3):
    # 前向计算
    outputs = model(train_inputs)
    loss = loss_fn(outputs.logits, train_labels)

    # 反向传播
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    print(f"Epoch {epoch+1} Loss: {loss.item()}")

# 预测测试数据
test_texts = ["This movie is great", "This movie is terrible"]
test_encodings = tokenizer(test_texts, truncation=True, padding=True)
test_inputs = torch.tensor(test_encodings['input_ids'])
model.eval()
with torch.no_grad():
    outputs = model(test_inputs)
    predictions = torch.argmax(outputs.logits, dim=1)
print(predictions)
