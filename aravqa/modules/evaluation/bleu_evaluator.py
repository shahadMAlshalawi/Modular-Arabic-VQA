from typing import List,Dict
from tqdm import tqdm
from .base import BaseEvaluator
import evaluate
# TODO: Use Arabic tokenizer from ...... import ....._tokenize
#from camel_tools.morphology.database import MorphologyDB 
#from camel_tools.tokenizers.word import simple_word_tokenize
# TODO: Use NLTK tokenizer
import nltk
from nltk.tokenize import word_tokenize
# TODO: Remove punctuation
import string


class BLEUEvaluator(BaseEvaluator):
    def __init__(self, max_order: int = 1):
        self.max_order = max_order
        self.bleu_scorer = evaluate.load("bleu")
        super().__init__()


    def evaluate(self, predictions: List[str], references: List[List[str]]) -> Dict:
        """
        Evaluates predictions against references.

        Args:
            predictions (List[str]): List of predicted sentences.
            references (List[List[str]]): List of lists of reference sentences.

        Returns:
            Dict: The computed evaluation score.
        """

        results = {
            "overall_bleu":float('-inf'),
            "overall_precisions_bleu":float('-inf'),
            "bleu":[]
        }

        for pred, ref in tqdm(zip(predictions, references), total=len(predictions), desc="Evaluating BLEU scores"):
            bleu = self._compute_bleu_score([pred],[ref])["bleu"]
            results["bleu"].append(round(bleu, 3))
        
        overall= self._compute_bleu_score(predictions,references)
        results["overall_bleu"] = round(overall["bleu"], 3)
        results["overall_precisions_bleu"] = overall["precisions"]

        return results
    
    
    def _compute_bleu_score(self, predictions: List[str], references: List[List[str]]) -> Dict:
        """
        Evaluates predictions against references.

        Args:
            predictions (List[str]): List of predicted sentences.
            references (List[List[str]]): List of lists of reference sentences.

        Returns:
            Dict: The computed evaluation score.  {"bleu":float("-inf"),"precisions":float('-inf')} if computation fails.
        """
        if not predictions or not references:
            raise ValueError("Predictions and references must not be empty.")
        if len(predictions) != len(references):
            raise ValueError("The number of predictions must match the number of reference sets.")

        try:
            def remove_punctuation(text: str) -> str:
                return text.translate(str.maketrans('', '', string.punctuation))

            predictions = [remove_punctuation(pred) for pred in predictions]
            references = [[remove_punctuation(ref) for ref in refs] for refs in references]
            result = self.bleu_scorer.compute(predictions=predictions, references=references, max_order=self.max_order)
            # TODO: Use Arabic tokenizer result = self.bleu_scorer.compute(predictions=predictions, references=references,tokenizer=..._tokenize, max_order=self.max_order)
            return result
        except Exception as e:
            print(f"Error computing BLEU score: {e}")
            return {"bleu":float("-inf"),"precisions":float('-inf')}  # Indicate computation failure
    
    
    def export(self, results: Dict, path: str) -> None:
        """
        Exports the evaluation results to a JSON file.

        Args:
            results (Dict): The evaluation results.
            path (str): Path to the output file.
        """
        super().export(results, path)