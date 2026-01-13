import os
"""AI service for generating insights.

This module tries to import the OpenAI client. If the optional dependency
is not installed (for example in testing or constrained environments), the
generate_insights function will return a helpful error instead of
attempting to call the missing library. This avoids runtime import
errors when the openai package is not available.
"""
try:
    from openai import OpenAI  # type: ignore
except ImportError:
    # Fallback stub when openai is not installed
    OpenAI = None  # type: ignore
import json
import traceback

# Hardcoded API Key as requested by user
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

def generate_insights(data: dict, api_key: str = None) -> str:
    """
    Generates financial insights using OpenAI's GPT model.
    """
    # Use provided key or fallback to hardcoded key
    final_api_key = api_key if api_key else OPENAI_API_KEY
    
    if not final_api_key:
        # No API key provided
        return "Error: API Key is missing."

    # Clean the API key
    final_api_key = final_api_key.strip()

    try:
        # If OpenAI library is unavailable, return a clear error
        if OpenAI is None:
            return "Error: OpenAI library is not installed. Please install the openai package."

        print(f"Attempting to call OpenAI with key: {final_api_key[:8]}...{final_api_key[-4:]}")
        client = OpenAI(api_key=final_api_key)

        # Prepare a summary of the data for the prompt
        kpis = data.get("kpis", {})
        monthly_data = data.get("monthly_data", [])
        
        # Simplify monthly data for the prompt to save tokens
        monthly_summary = []
        for item in monthly_data:
            monthly_summary.append(f"{item.get('month')}: Rev={item.get('revenue')}, Cost={item.get('costs')}, Profit={item.get('net_result')}")
        
        prompt = f"""
        You are an expert financial analyst. Analyze the following financial data for a company and provide sincere, actionable insights and recommendations.
        
        KPIs:
        - Total Revenue: {kpis.get('total_revenue')}
        - Net Result: {kpis.get('net_result')}
        - Gross Margin: {kpis.get('gross_margin')}
        - EBITDA: {kpis.get('ebitda')}
        
        Monthly Trends (Revenue, Costs, Net Result):
        {json.dumps(monthly_summary, indent=2)}
        
        Please provide the output in TWO sections:
        
        ### 🇧🇷 Análise Financeira (PT-BR)
        1. Opinião sincera sobre a situação atual.
        2. 3-5 recomendações específicas.
        3. Tendências preocupantes.

        ---

        ### 🇺🇸 Financial Analysis (English)
        1. Sincere opinion on the current situation.
        2. 3-5 specific recommendations.
        3. Highlight worrying trends.
        
        Format the output in Markdown. Be professional but direct.
        """

        # List of models to try in order of preference
        models_to_try = ["gpt-5.1", "gpt-5", "gpt-5-nano", "gpt5nano"]
        
        last_exception = None
        
        print("Sending request to OpenAI...")
        
        for model in models_to_try:
            try:
                print(f"Attempting with model: {model}")
                response = client.chat.completions.create(
                    model=model, 
                    messages=[
                        {"role": "system", "content": "You are a helpful and critical financial assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                )
                print(f"✅ Success with model: {model}")
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"⚠️ Failed with model {model}: {str(e)}")
                last_exception = e
                # If it's an auth error (incorrect key), no point trying other models
                if "Incorrect API key" in str(e) or "quota" in str(e).lower():
                    raise e
                continue

        # If we get here, all models failed
        if last_exception:
            raise last_exception
            
    except Exception as e:
        print(f"❌ Error generating insights: {str(e)}")
        traceback.print_exc()
        
        error_msg = str(e)
        if "Incorrect API key" in error_msg:
            return "Error: The provided API key is incorrect. Please check your OpenAI dashboard."
        elif "You exceeded your current quota" in error_msg:
            return "Error: You have exceeded your OpenAI API quota. Please check your billing details."
        elif "The model" in error_msg and "does not exist" in error_msg:
            return f"Error: None of the requested models ({', '.join(models_to_try)}) are available for your API key. Please check your access."
        else:
            return f"Error generating insights: {error_msg}"
