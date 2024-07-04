import transformers as tf
import torch
import asyncio
import torchaudio


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model,tokenizer='',''
is_llama_loaded=False
modelLoding = False

async def loadLlama():
    
    global model,tokenizer,modelLoding
    modelLoding = True
    model_id = '../models/llama-3-8b-instruct'
    # device = f'cuda:{torch.cuda.current_device()}' if torch.cuda.is_available() else 'cpu'
    device='cuda:0'
    bnb_config = tf.BitsAndBytesConfig(
        load_in_8bit=True,
        bnb_8bit_quant_type='nf4',
        bnb_8bit_use_double_quant=True,
        bnb_8bit_compute_dtype=torch.bfloat16
    )
    hf_auth = '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'
    model_config = tf.AutoConfig.from_pretrained(
        model_id,
        token=hf_auth
    )
    
    model = tf.AutoModelForCausalLM.from_pretrained(
        model_id,
        trust_remote_code=True,
        config=model_config,
        quantization_config=bnb_config,
        device_map='cuda:0',
        token=hf_auth
    )
    model.eval()
    print(f"Model loaded on {device}")

    tokenizer = tf.AutoTokenizer.from_pretrained(
        model_id,
        token=hf_auth
    )
    global is_llama_loaded
    is_llama_loaded = True
    modelLoding == False
    
    return model,tokenizer

def loadWhisper():
    

    model_id = "../models/whisper-2b"

    model = tf.AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)

    processor = tf.AutoProcessor.from_pretrained(model_id)
   
    return model,processor
    

def llama(prompt,sys_prompt):
    global model,tokenizer
    # loop = asyncio.new_event_loop()
    # llama_data = loop.run_until_complete(backgri())
    # loop.close()
    
    if is_llama_loaded==False:
        print('sync loading')
        model,tokenizer = asyncio.run(loadLlama())
    print("Loaded and ineencing")
    pipeline = tf.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    
    model_kwargs={"torch_dtype": torch.bfloat16},
    
)
    messages = [
    {"role": "system", "content": sys_prompt},
    {"role": "user", "content": prompt},
]

    input_ids = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=False,
        return_tensors="pt"
    ).to(model.device)

    # terminators = [
    #     tokenizer.eos_token_id,
    #     tokenizer.convert_tokens_to_ids("<|eot_id|>")
    # ]
    terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]
    prompt = pipeline.tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
)
    output = pipeline(prompt, max_new_tokens=8000,
    eos_token_id=terminators,
    do_sample=True,
    temperature=0.5,
    top_p=0.9,)
    return output

def TTS(text,path):
    
    model_id = "../models/mms-tts-eng"
    model = tf.VitsModel.from_pretrained(model_id)
    tokenizer = tf.AutoTokenizer.from_pretrained(model_id)

    inputs = tokenizer(text, return_tensors="pt")

    with torch.no_grad():
        output = model(**inputs).waveform

    output_waveform = output # Remove batch dimension and move to CPU if necessary
    sample_rate = model.config.sampling_rate  # Example sample rate, adjust based on your needs

    # Define the file path for the output audio file
    output_file_path = path+"/tts.wav"

    # Use torchaudio to save the waveform to a file
    torchaudio.save(output_file_path, output_waveform, sample_rate)
    return output_file_path