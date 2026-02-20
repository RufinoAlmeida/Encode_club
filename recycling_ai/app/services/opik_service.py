from typing import Optional
import opik
from opik.rest_api.core.api_error import ApiError

class OpikService:
    """
    Integra com o Opik REST API, usando o cliente oficial disponível em
    client.rest_client conforme especificado na documentação.
    """

    def __init__(self, api_key: str, project_name: str):
        # Inicializa o cliente Opik com API key e configuração
        self.client = opik.Opik(project_name=project_name, api_key=api_key)
        self.rest_client = self.client.rest_client

    def log_classification(self, input_data: dict, output_data: dict) -> Optional[dict]:
        """
        Cria e envia um trace ao Opik, para monitorar a classificação.

        input_data: Dados enviados à IA (texto/imagem)
        output_data: Resultado de classificação retornado
        """
        trace_body = {
            "input": input_data,
            "output": output_data,
            "metadata": {},
            "tags": ["classification", "recycle"]
        }
        try:
            trace = self.rest_client.traces.trace(
                name="recycle_classification",
                input=input_data,
                output=output_data,
            )
            return trace
        except ApiError as e:
            print(f"[Opik] Error logging trace: {e.status_code} - {e.body}")
            return None
