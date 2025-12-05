"""
Local waste classification using pre-trained MobileNetV2
Falls back to Gemini for unknown/low-confidence items
"""
import os
import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from PIL import Image

# Only import TensorFlow if available
try:
    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logging.warning("TensorFlow not available. Local classification disabled.")

from backend.waste_database import search_waste_item


class WasteClassifier:
    """
    Hybrid waste classifier using MobileNetV2 for quick local inference
    with database lookup for disposal instructions
    """
    
    def __init__(self):
        self.model = None
        self.enabled = False
        
        if TF_AVAILABLE:
            try:
                # Load pre-trained MobileNetV2 (lightweight, fast)
                self.model = MobileNetV2(weights='imagenet', include_top=True)
                self.enabled = True
                logging.info("✅ MobileNetV2 loaded for local waste classification")
            except Exception as e:
                logging.warning(f"Failed to load MobileNetV2: {e}")
                self.enabled = False
    
    def preprocess_image(self, img: Image.Image) -> np.ndarray:
        """Preprocess image for MobileNetV2"""
        # Resize to 224x224
        img_resized = img.resize((224, 224))
        # Convert to array
        img_array = np.array(img_resized)
        # Expand dimensions
        img_array = np.expand_dims(img_array, axis=0)
        # Preprocess
        return preprocess_input(img_array)
    
    def classify_local(self, img: Image.Image) -> Tuple[Optional[str], float, List[str]]:
        """
        Classify image using local model
        Returns: (predicted_label, confidence, top_5_labels)
        """
        if not self.enabled or self.model is None:
            return None, 0.0, []
        
        try:
            # Preprocess
            processed = self.preprocess_image(img)
            
            # Predict
            predictions = self.model.predict(processed, verbose=0)
            
            # Decode top 5 predictions
            decoded = decode_predictions(predictions, top=5)[0]
            
            # Extract labels and confidences
            top_label = decoded[0][1]  # imagenet class name
            top_confidence = float(decoded[0][2])
            all_labels = [label[1] for label in decoded]
            
            return top_label, top_confidence, all_labels
            
        except Exception as e:
            logging.error(f"Local classification failed: {e}")
            return None, 0.0, []
    
    def map_imagenet_to_waste(self, imagenet_label: str) -> Optional[str]:
        """
        Map ImageNet class to waste category
        Returns waste category or None if not waste-related
        """
        waste_mappings = {
            # Organic
            "banana": "banana_peel",
            "orange": "organic",
            "lemon": "organic",
            "apple": "organic",
            
            # Plastic
            "water_bottle": "plastic_bottle",
            "pop_bottle": "plastic_bottle",
            "plastic_bag": "plastic_bag",
            
            # Paper/Cardboard
            "carton": "cardboard",
            "envelope": "paper",
            "notebook": "paper",
            
            # Metal
            "can": "aluminum_can",
            "beer_bottle": "glass_bottle",
            "wine_bottle": "glass_bottle",
            
            # E-waste
            "cellular_telephone": "phone",
            "laptop": "laptop",
            "desktop_computer": "laptop",
            "remote_control": "e_waste",
            
            # Hazardous
            "pill_bottle": "medicine",
            "lighter": "hazardous"
        }
        
        # Check for direct match
        label_lower = imagenet_label.lower().replace("_", " ")
        for key, waste_type in waste_mappings.items():
            if key in label_lower or label_lower in key:
                return waste_type
        
        return None
    
    def analyze(self, img: Image.Image, confidence_threshold: float = 0.6) -> Dict:
        """
        Analyze image with local model and database lookup
        Returns classification result with disposal info
        """
        if not self.enabled:
            return {
                "local_classification": False,
                "should_use_gemini": True,
                "reason": "Local model not available"
            }
        
        # Get local prediction
        pred_label, confidence, top_labels = self.classify_local(img)
        
        if pred_label is None:
            return {
                "local_classification": False,
                "should_use_gemini": True,
                "reason": "Classification failed"
            }
        
        logging.info(f"Local prediction: {pred_label} ({confidence:.2f})")
        
        # Try to map to waste category
        waste_type = self.map_imagenet_to_waste(pred_label)
        
        # If low confidence or not waste-related, use Gemini
        if confidence < confidence_threshold or waste_type is None:
            return {
                "local_classification": True,
                "should_use_gemini": True,
                "reason": f"Low confidence ({confidence:.2f}) or non-waste item",
                "predicted_label": pred_label,
                "confidence": confidence,
                "top_predictions": top_labels
            }
        
        # High confidence waste item - lookup in database
        db_result = search_waste_item(waste_type)
        
        if db_result:
            return {
                "local_classification": True,
                "should_use_gemini": False,
                "confidence": confidence,
                "predicted_label": pred_label,
                "waste_category": db_result["category"],
                "item": db_result,
                "disposal_info": {
                    "disposal": db_result["disposal"],
                    "impact": db_result["impact"],
                    "recyclable": db_result.get("recyclable", False)
                }
            }
        
        # Waste item but no detailed info - use Gemini for details
        return {
            "local_classification": True,
            "should_use_gemini": True,
            "reason": "Waste item detected but needs detailed analysis",
            "predicted_label": pred_label,
            "confidence": confidence
        }


# Global classifier instance
_classifier = None

def get_classifier() -> WasteClassifier:
    """Get or create global classifier instance"""
    global _classifier
    if _classifier is None:
        _classifier = WasteClassifier()
    return _classifier
