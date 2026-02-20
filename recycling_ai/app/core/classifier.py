from typing import Optional

class ClassificationResult:
    def __init__(self, item: str, category: str, instruction: str, confidence: float):
        self.item = item
        self.category = category
        self.instruction = instruction
        self.confidence = confidence

class RecyclingClassifier:
    def __init__(self, opik_service):
        self.opik_service = opik_service

    def classify(self, text: str, image_bytes: bytes = None):
        """
        Lógica interna de classificação (texto/imagem), que pode ser
        substituída por uma chamada real a um modelo multimodal.
        """

        # Exemplo simples de regra
        result = ClassificationResult(
            item="Plastic Cup",
            category="Plastic",
            instruction="Clean and place in red bin",
            confidence=0.95,
        )

        # Log de trace no Opik
        self.opik_service.log_classification(
            input_data={"text": text, "has_image": image_bytes is not None},
            output_data=result.__dict__
        )

        return result
