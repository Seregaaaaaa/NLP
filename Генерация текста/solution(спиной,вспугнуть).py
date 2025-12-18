seed = 6208
prompt = "В такой звенящей тишине страшно было даже вздохнуть. Олень стоял к нам"

import torch
import random
import numpy as np
from transformers import GPT2LMHeadModel, GPT2Tokenizer

model_name = "ai-forever/rugpt3large_based_on_gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)


device = torch.device("cpu")
    
model.to(device)

# 1. Фиксация
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)

input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
attention_mask = torch.ones_like(input_ids)

out = model.generate(
    input_ids,
    attention_mask=attention_mask,
    max_length=100, do_sample=True,
    top_k=200, top_p=0.95, temperature=1.0, repetition_penalty=1.0,
    pad_token_id=tokenizer.eos_token_id
)

result_text = tokenizer.decode(out[0], skip_special_tokens=True)
print(result_text)

"""
Вывод:
В такой звенящей тишине страшно было даже вздохнуть. Олень стоял к нам спиной, как статуя, и я, наверное, впервые отчетливо осознала, что он представляет собой реальную угрозу.

Но Олень обернулся. И, мягко, будто боясь вспугнуть наше оцепенение, сказал — а потом добавил:

— Это мир Зверя…

Кто-то громко вскрикнул, зажав уши ладонями. Олень сделал несколько шагов вперед и остановился.

Что-то глухо"""