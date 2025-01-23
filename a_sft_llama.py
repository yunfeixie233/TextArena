import datasets 

MODEL_INSTRUCTION = "You are a competitive game player. Make sure you read the game instructions carefully, and always follow the required format."
model_name = "meta-llama/Llama-3.2-1B"


def prepare_dataset_for_training(X, y):
    formatted_texts = []
    for observation, action in zip(X, y):
        formatted_text = f"### Instruction: {MODEL_INSTRUCTION}\n\n### Input: {observation}\n\n### Response: {action}

    return Dataset.from_dict({"text": formatted_texts})


# load the dataset



# Initialize model and tokenizer with unsloth
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name,
    max_seq_length=4096,
    load_in_4bit=False
)

# Define data collator
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False,  # Causal LM does not use masked language modeling
)


# Set up training arguments
training_args = TrainingArguments(
    output_dir=f"checkpoints/{model_name}_game-tuning-{timestamp}",
    run_name=f"{model_name}_game-tuning",
    num_train_epochs=10,
    per_device_train_batch_size=2, 
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=1e-5,
    weight_decay=0.01,
    lr_scheduler_type="cosine",
    warmup_steps=100,
    logging_steps=10,
    evaluation_strategy="steps",
    eval_steps=100,
    save_strategy="epoch",
    report_to="wandb",
    fp16=True,  # Enable mixed precision training
    gradient_checkpointing=True,  # Reduce memory usage
    optim="adamw_torch",
    save_total_limit=3,  # Limit the number of saved checkpoints
    load_best_model_at_end=True,
    metric_for_best_model="loss",
)

# Initialize Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)


# Start training
trainer.train()

# Evaluate the model
trainer.evaluate()

# Save the final model
trainer.save_model(f"final_model/{model_name}_game-tuning")
