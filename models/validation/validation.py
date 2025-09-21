from transformers import BlipForConditionalGeneration, BlipProcessor
import torch
from PIL import Image
import requests
from sentence_transformers import SentenceTransformer, util
from io import BytesIO


class ReportValidator:
    
    def generate_caption(self, image_url,device='cuda' if torch.cuda.is_available() else 'cpu'):
        
        self.device = device
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        
        # Prepare the image and generate caption using BLIP
        image = Image.open(BytesIO(requests.get(image_url).content)).convert('RGB')
        # Preprocess the image for the BLIP model.
        inputs = self.blip_processor(image, return_tensors="pt").to(device)
        # Generate a caption using the BLIP model.
        out = self.blip_model.generate(
            **inputs,                # The preprocessed image tensor inputs for the model.
            min_length=25,           # Minimum number of tokens in the generated caption.
            num_beams=6,             # Number of beams for beam search (controls diversity and quality).
            early_stopping=True,     # Stop beam search when at least num_beams sentences are finished.
            no_repeat_ngram_size=3   # Prevents repeating any 3-word sequences in the output.
        )
        # Decode the generated caption.
        caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
        return caption

    def compute_similarity(self, caption, description):
        self.model = 'all-MiniLM-L6-v2'
        self.similarity_model = SentenceTransformer(self.model)

        # Compute cosine similarity between two captions
        caption_embedding = self.similarity_model.encode(caption, convert_to_tensor=True)
        description_embedding = self.similarity_model.encode(description, convert_to_tensor=True)
       
        similarity = util.pytorch_cos_sim(caption_embedding,description_embedding).item()
        return similarity

    def validate(self, image_url, description, threshold=0.4):
        
        caption = self.generate_caption(image_url)
        
        score = self.compute_similarity(caption, description)

        if score >= threshold:
            print(f"Validation passed with score: {score:.4f}")
            print(f"Generated Caption: {caption}")
            print(f"Description: {description}")
            print("Complaint is valid.")
            return True