from fastapi import APIRouter, UploadFile, File
from app.services.opik_service import OpikService
from app.core.classifier import RecyclingClassifier


router = APIRouter()

# Carrega key da variável de ambiente
import os
OPIK_API_KEY = os.getenv("OPIK_API_KEY")
OPIK_PROJECT = os.getenv("OPIK_PROJECT_NAME", "Default")

opik_service = OpikService(api_key=OPIK_API_KEY, project_name=OPIK_PROJECT)
classifier = RecyclingClassifier(opik_service=opik_service)

@router.post("/classify")
async def classify(file: UploadFile = File(None), text: str = ""):
    image_bytes = None
    if file:
        image_bytes = await file.read()

    result = classifier.classify(text=text, image_bytes=image_bytes)
    return {
        "item": result.item,
        "category": result.category,
        "instruction": result.instruction,
        "confidence": result.confidence
    }
