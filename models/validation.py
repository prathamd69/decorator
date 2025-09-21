from transformers import BlipForConditionalGeneration, BlipProcessor
import torch
from PIL import Image
import requests
from sentence_transformers import SentenceTransformer, util
from io import BytesIO

class ReportValidator:
    """
    Validates a civic issue report by checking if the image and description are semantically similar.
    Uses BLIP for image captioning and SentenceTransformer for similarity.
    """

    def __init__(self, image_url):
        """
        Initialize the validator with the image URL.

        Args:
            image_url (str): URL of the image to validate.
        """
        self.image_url = image_url

    def generate_caption(self, image_url, device='cuda' if torch.cuda.is_available() else 'cpu'):
        """
        Generate a caption for the given image using BLIP.

        Args:
            image_url (str): URL of the image.
            device (str): Device to run the model on ('cuda' or 'cpu').

        Returns:
            str: Generated caption for the image.
        """
        self.device = device
        # Load BLIP processor and model
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(self.device)
        
        # Download and prepare the image
        image = Image.open(BytesIO(requests.get(image_url).content)).convert('RGB')
        # Preprocess the image for the BLIP model
        inputs = self.blip_processor(image, return_tensors="pt").to(device)
        # Generate a caption using the BLIP model
        out = self.blip_model.generate(
            **inputs,                # The preprocessed image tensor inputs for the model.
            min_length=25,           # Minimum number of tokens in the generated caption.
            num_beams=6,             # Number of beams for beam search (controls diversity and quality).
            early_stopping=True,     # Stop beam search when at least num_beams sentences are finished.
            no_repeat_ngram_size=3   # Prevents repeating any 3-word sequences in the output.
        )
        # Decode the generated caption
        caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
        return caption

    def compute_similarity(self, caption, description):
        """
        Compute the semantic similarity between the generated caption and the provided description.

        Args:
            caption (str): Caption generated from the image.
            description (str): User-provided description.

        Returns:
            float: Cosine similarity score between caption and description.
        """
        self.model = 'all-MiniLM-L6-v2'
        self.similarity_model = SentenceTransformer(self.model)

        # Compute embeddings for both caption and description
        caption_embedding = self.similarity_model.encode(caption, convert_to_tensor=True)
        description_embedding = self.similarity_model.encode(description, convert_to_tensor=True)
       
        # Compute cosine similarity
        similarity = util.pytorch_cos_sim(caption_embedding, description_embedding).item()
        return similarity

    def validate(self, image_url, description, threshold=0.4):
        """
        Validate the report by checking if the image and description are semantically similar.

        Args:
            image_url (str): URL of the image.
            description (str): User-provided description.
            threshold (float): Minimum similarity score to consider the report valid.

        Returns:
            bool: True if validation passes, False otherwise.
        """
        # Generate caption from image
        caption = self.generate_caption(image_url)
        # Compute similarity score
        score = self.compute_similarity(caption, description)

        # Check if similarity meets the threshold
        if score >= threshold:
            print(f"Validation passed with score: {score:.4f}")
            print(f"Generated Caption: {caption}")
            print(f"Description: {description}")
            print("Complaint is valid.")
            return True