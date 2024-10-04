import os
import sys
import torch
from datasets import Dataset
from unsloth import FastLanguageModel, is_bfloat16_supported
from trl import SFTTrainer
from transformers import TrainingArguments

max_seq_length = 2 ** 14
dtype = None
model_name = 'unsloth/Llama-3.2-1B'

def train_model(folder):
  model, tokenizer = FastLanguageModel.from_pretrained(model_name=model_name, max_seq_length=max_seq_length, dtype=dtype)

  model = FastLanguageModel.get_peft_model(
    model,
    r = 16,
    target_modules = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj",],
    lora_alpha = 16,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
  )
  
  def generator():
    for file in os.listdir(folder):
      with open(os.path.join(folder, file), "r") as f:
        yield { "text": f.read() + tokenizer.eos_token }

  dataset = Dataset.from_generator(generator)

  trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    dataset_text_field = "text",
    max_seq_length = max_seq_length,
    dataset_num_proc = 2,
    packing = False, # Can make training 5x faster for short sequences.
    args = TrainingArguments(
      per_device_train_batch_size = 2,
      gradient_accumulation_steps = 4,
      warmup_steps = 5,
      max_steps = 60,
      # num_train_epochs = 1, # For longer training runs!
      learning_rate = 2e-4,
      fp16 = not is_bfloat16_supported(),
      bf16 = is_bfloat16_supported(),
      logging_steps = 1,
      optim = "adamw_8bit",
      weight_decay = 0.01,
      lr_scheduler_type = "linear",
      seed = 3407,
      output_dir = "outputs",
    ),
  )
  
  trainer_stats = trainer.train()
  
  print(trainer_stats)
  
  model.save_pretrained("lemme_llama_lora") # Local saving
  tokenizer.save_pretrained("lemme_llama_lora")

if __name__ == "__main__":
  train_model(sys.argv[1])
