from transformers import pipeline
import json
import re

class ReportRouter:
    """
    Classifies civic issue reports and routes them to the appropriate department
    using zero-shot classification.
    """

    def __init__(self, categories_file, departments_file, model_name="roberta-large-mnli"):
        """
        Initialize the router with category and department mappings, and load the model.

        Args:
            categories_file (str): Path to JSON file with list of civic categories.
            departments_file (str): Path to JSON file mapping categories to departments.
            model_name (str): HuggingFace model name for zero-shot classification.
        """
        with open(categories_file, "r") as f:
            self.categories = json.load(f)

        with open(departments_file, "r") as f:
            self.departments = json.load(f)

        # Load the zero-shot classification pipeline
        self.model = pipeline("zero-shot-classification", model=model_name)

    def _is_civic_related(self, text):
        """
        Check if the text contains at least one civic-related keyword.
        Prevents false positives like 'fight with neighbour'.

        Args:
            text (str): Input text to check.

        Returns:
            bool: True if civic-related, False otherwise.
        """
        civic_keywords = [
            "garbage", "waste", "trash", "sewage", "drain", "toilet",
            "pothole", "road", "streetlight", "electricity", "wire",
            "traffic", "signal", "tree", "playground", "garden",
            "drainage", "sidewalk", "footpath", "lamp", "light"
        ]
        text_lower = text.lower()
        # Return True if any civic keyword is present in the text
        return any(word in text_lower for word in civic_keywords)

    def _is_gibberish(self, text):
        """
        Simple check: reject if too short or mostly random characters.

        Args:
            text (str): Input text to check.

        Returns:
            bool: True if gibberish, False otherwise.
        """
        # Reject if less than 3 words
        if len(text.split()) < 3:
            return True
        # Reject if only a short string of letters (e.g., 'abc')
        if re.fullmatch(r"[a-z]+", text.lower()) and len(text) < 6:
            return True
        return False

    def classify_and_route(self, text, threshold_gap=0.15, min_confidence=0.65):
        """
        Classify text into civic categories. If no category passes min_confidence,
        or if text is gibberish, return 'out_of_scope'.

        Args:
            text (str): The report text to classify.
            threshold_gap (float): Minimum confidence gap between top 2 departments for auto assignment.
            min_confidence (float): Minimum confidence required for auto assignment.

        Returns:
            dict: Routing decision and details.
        """
        # Reject gibberish or too short text
        if self._is_gibberish(text):
            return {
                "status": "rejected",
                "reason": "Input not valid for civic issue categories"
            }
        # Reject if not civic-related
        if not self._is_civic_related(text):
            return {
                "status": "rejected",
                "reason": "This platform is for civic issues only"
            }
        
        # Run zero-shot classification
        result = self.model(
            text,
            candidate_labels=self.categories,
            multi_label=True
        )

        # Pair each label with its score and sort by score descending
        predictions = list(zip(result["labels"], result["scores"]))
        predictions.sort(key=lambda x: x[1], reverse=True)

        # If best score < min_confidence → out of scope
        top_label, top_score = predictions[0]
        if top_score < min_confidence:
            return {
                "status": "rejected",
                "reason": "This issue is not designed for the platform",
                # "predictions": predictions[:2]
            }

        # Collapse scores by department, keeping the highest score per department
        dept_scores = {}
        dept_examples = {}
        for label, score in predictions:
            dept = self.departments.get(label, "Unknown Department")
            if dept not in dept_scores or score > dept_scores[dept]:
                dept_scores[dept] = score
                dept_examples[dept] = label

        # Sort departments by their highest score
        sorted_depts = sorted(dept_scores.items(), key=lambda x: x[1], reverse=True)

        top1_dept, top1_score = sorted_depts[0]
        if len(sorted_depts) > 1:
            top2_dept, top2_score = sorted_depts[1]
        else:
            top2_dept, top2_score = None, 0.0

        # If top 2 departments are too close, require manual review
        if top2_dept and (top1_score - top2_score) <= threshold_gap:
            return {
                "status": "manual",
                "possible_departments": [
                    (top1_dept, round(top1_score, 2)),
                    (top2_dept, round(top2_score, 2))
                ],
                # "predictions": predictions[:5]
            }
        else:
            # Auto-assign to the top department and category
            best_category = dept_examples[top1_dept]
            return {
                "status": "auto",
                "assigned_department": top1_dept,
                "best_category": best_category,
                "confidence": round(top1_score, 2),
                # "predictions": predictions[:5]
            }
