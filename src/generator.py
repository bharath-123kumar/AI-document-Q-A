import google.generativeai as genai
from typing import List, Dict, Any, Tuple
from src.utils import get_gemini_api_key, get_gemini_model

class Generator:
    def __init__(self):
        self.api_key = get_gemini_api_key()
        self.model_name = get_gemini_model()
        self.initialized = False
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.initialized = True
        else:
            print("WARNING: GOOGLE_API_KEY environment variable not set. Gemini generation will not work.")

    def generate_answer(self, query: str, context_chunks: List[Dict[str, Any]]) -> Tuple[str, str]:
        """
        Generate answer from retrieved context.
        Returns:
            Tuple[str, str]: (generated_answer, raw_prompt)
        """
        if not self.initialized:
            return (
                "Error: Gemini API key is not configured. Please set the GOOGLE_API_KEY environment variable in your .env file.",
                ""
            )

        # Build context string
        context_str = ""
        for i, chunk in enumerate(context_chunks):
            context_str += f"--- CONTEXT BLOCK {i+1} ---\n"
            context_str += f"Source Document: {chunk['source']}\n"
            context_str += f"Page/Section: {chunk['page']}\n"
            context_str += f"Content: {chunk['text']}\n\n"

        # System and User prompt
        system_instruction = (
            "You are an expert AI assistant that answers questions based STRICTLY on the provided context blocks. "
            "Follow these rules precisely:\n"
            "1. Answer the question using ONLY information from the context blocks below.\n"
            "2. If the context blocks do not contain enough information to answer the question, state exactly: "
            "'I'm sorry, but the provided documents do not contain the information needed to answer this question.'\n"
            "3. Do NOT use any external knowledge or your own pre-training data to answer or extrapolate if the facts are not present.\n"
            "4. Include inline citations to the source document and page/section where you found the information. "
            "Format citations as [Source: filename, Page: number] at the end of the sentence or paragraph containing the fact.\n"
            "5. Keep the tone professional, direct, and fact-based."
        )

        user_prompt = f"""
Query: {query}

Provided Context Blocks:
{context_str}

Please generate the answer matching the rules:
"""

        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_instruction
            )
            
            response = model.generate_content(
                user_prompt,
                generation_config={"temperature": 0.0}  # Low temperature for factual generation
            )
            return response.text, user_prompt
        except Exception as e:
            return f"Error during Gemini API generation: {str(e)}", user_prompt
base_dir = None
