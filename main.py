import pytesseract
import cv2
import os
import re
import random
from typing import List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OMRProcessor:
    def __init__(self, config: Optional[dict] = None):
        """
        Initialize OMR processor with configuration
        
        Args:
            config (dict): Configuration dictionary with:
                - name_region: (x, y, w, h) coordinates for name extraction
                - tesseract_path: Path to tesseract executable (if not in PATH)
                - default_lang: Default OCR language
        """
        self.config = config or {
            'name_region': (30, 20, 500, 100),  # Default coordinates
            'default_lang': 'eng',
            'min_name_length': 2
        }
        
        # Set tesseract path if specified
        if config and 'tesseract_path' in config:
            pytesseract.pytesseract.tesseract_cmd = config['tesseract_path']

    def extract_student_name(self, image_path: str) -> str:
        """
        Extract student name from OMR sheet image using OCR with filename fallback
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Extracted student name
        """
        text = ""
        
        try:
            # Validate image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            # Read and preprocess image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
                
            x, y, w, h = self.config['name_region']
            name_region = img[y:y + h, x:x + w]
            
            # Image processing pipeline
            gray = cv2.cvtColor(name_region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR with error handling
            text = pytesseract.image_to_string(
                thresh, 
                lang=self.config['default_lang']
            ).strip()
            
            logger.info(f"OCR extracted name: {text}")
            
        except Exception as e:
            logger.error(f"Name extraction error: {str(e)}")
            
        # Fallback to filename if OCR fails
        if not text or len(text) < self.config['min_name_length']:
            text = self._fallback_name_from_filename(image_path)
            logger.info(f"Using fallback name: {text}")
            
        return text

    def _fallback_name_from_filename(self, image_path: str) -> str:
        """
        Extract name from filename when OCR fails
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            str: Cleaned name from filename
        """
        filename = os.path.splitext(os.path.basename(image_path))[0]
        
        # Handle common WhatsApp filename patterns
        if "WhatsApp" in filename or "WA" in filename:
            time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
            if time_match:
                return f"Student_{time_match.group(1).replace('.', '')}"
            parts = filename.split('_')
            if len(parts) > 1:
                return f"Student_{parts[-1][:8]}"
        
        # General filename cleaning
        clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
        clean_name = re.sub(r'_+', '_', clean_name).strip('_')
        
        return clean_name[:20] if clean_name else "Student_Unknown"

    def extract_student_answers(
        self, 
        image_path: str, 
        total_questions: int,
        choices: List[str] = ['A', 'B', 'C', 'D']
    ) -> List[str]:
        """
        Extract student answers (placeholder - currently generates random answers)
        
        Args:
            image_path (str): Path to the image file
            total_questions (int): Number of questions
            choices (List[str]): Possible answer choices
            
        Returns:
            List[str]: List of answers
        """
        logger.info(f"Generating random answers for {total_questions} questions")
        return [random.choice(choices) for _ in range(total_questions)]

    def process_omr_sheet(
        self,
        image_path: str,
        total_questions: int
    ) -> Tuple[str, List[str]]:
        """
        Complete OMR processing pipeline
        
        Args:
            image_path (str): Path to the image file
            total_questions (int): Number of questions
            
        Returns:
            Tuple[str, List[str]]: (student_name, answers)
        """
        name = self.extract_student_name(image_path)
        answers = self.extract_student_answers(image_path, total_questions)
        return name, answers


# Example usage
if __name__ == "__main__":
    # Initialize processor with configuration
    config = {
        'name_region': (30, 20, 500, 100),  # Adjust these coordinates
        'tesseract_path': '/usr/bin/tesseract',  # Only needed if not in PATH
        'default_lang': 'eng'
    }
    
    processor = OMRProcessor(config)
    
    # Process a sample image
    sample_image = "sample_omr.jpg"
    student_name, answers = processor.process_omr_sheet(sample_image, 20)
    
    print(f"Student: {student_name}")
    print(f"Answers: {answers}")
