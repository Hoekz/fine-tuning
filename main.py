from unsloth import FastLanguageModel
import torch

max_seq_len = 2 ** 14
dtype = None
model_name = 'unsloth/Llama-3.2-1B'

model, tokenizer = FastLanguageModel.from_pretrained(model_name=model_name, max_seq_lentgh=max_seq_len, dtype=dtype)

model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                      "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)


