import base64
import json
import traceback

import google.generativeai as genai

import os

# Unified API Configuration
# Prioritize environment variable for security and flexibility
api_key = os.environ.get("GOOGLE_API_KEY", "AIzaSyCmbq7S3wcMTJhMVqvDzWZWXUWx_Lh3boE")
genai.configure(api_key=api_key)


from PIL import Image
import io

def extract_cheque_info(image_path):
    """
    Combined function to Validate and Extract details in a SINGLE Gemini call.
    Uses response_mime_type to ensure valid JSON output.
    Optimized for Speed (< 5s) and Robustness (Google & Original images).
    """
    try:
        if not hasattr(genai, "GenerativeModel"):
            return {
                "is_cheque": False,
                "prediction": "INVALID",
                "message": "Cloud AI Service not correctly initialized",
                "details": {},
            }

        # 🚀 OPTIMIZATION: Resize image if too large, but keep enough resolution for details
        with Image.open(image_path) as img:
            max_size = 2000 # Increased for better OCR accuracy
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG', quality=90)
            img_bytes = img_byte_arr.getvalue()

        img_b64 = base64.b64encode(img_bytes).decode()

        prompt = """
        You are a strict bank document auditor. Analyze the provided image of a bank cheque.
        
        GOALS:
        1. IDENTIFY: Determine if this image is a BANK CHEQUE. 
           - Set 'is_cheque' to true ONLY if it is a cheque document.
        
        2. VALIDATE & SCORE:
           - 'prediction' is "VALID" ONLY IF ALL of these are clearly visible and filled:
             * Payee Name
             * Amount (in words and numbers)
             * Account Number
             * IFSC Code
             * Cheque Number
             * Signature present (Check if the signature area has any ink markings)
           - 'prediction' is "INVALID" IF ANY ONE of the above fields is missing, blank, or unreadable.
           - For a blank cheque (no payee/amount), mark as "INVALID".

        3. EXTRACT: Extract fields with 100% precision. 
           - Locate the Account Number, IFSC, and Cheque Number.
           - Identify the Payee and the Amount.
           - If a field is missing or unreadable, use "N/A".

        RETURN ONLY JSON with this structure:
        {
          "is_cheque": true/false,
          "prediction": "VALID" or "INVALID",
          "message": "Specify exactly which field is missing if it's INVALID (e.g. 'Invalid: IFSC code missing')",
          "details": {
            "account_number": "number or N/A",
            "ifsc_code": "code or N/A",
            "cheque_number": "number or N/A",
            "payee_name": "name or N/A",
            "amount_words": "words or N/A",
            "amount_number": "number or N/A",
            "signature_present": "Yes/No",
            "signature_remarks": "Comment on the signature presence"
          }
        }
        """

        # 🚀 ROBUST MODEL SELECTION: Try multiple models in case of Quota (429) or 404
        available_models = ["gemini-flash-latest", "gemini-1.5-flash", "gemini-2.0-flash-lite", "gemini-2.0-flash"]
        
        last_error = ""
        for model_name in available_models:
            try:
                print(f"DEBUG: Attempting AI processing with model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    contents=[
                        {
                            "role": "user",
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": img_b64,
                                     }
                                },
                                {"text": prompt},
                            ],
                        }
                    ],
                    generation_config={"response_mime_type": "application/json"},
                )

                if not response or not response.text:
                    print(f"DEBUG: Empty response from model: {model_name}")
                    continue

                result = json.loads(response.text)
                
                # Check for prediction key
                if "prediction" not in result:
                    result["prediction"] = "VALID" if result.get("is_cheque") else "INVALID"
                
                print(f"DEBUG: AI Processing Success for model {model_name}. Prediction: {result['prediction']}")
                # Success - return result
                return result

            except Exception as e:
                last_error = str(e)
                print(f"DEBUG: Model {model_name} failed: {last_error}")
                continue # Try next model
        
        # If all models failed
        return {
            "is_cheque": False,
            "prediction": "INVALID",
            "message": f"AI Service Exhausted. Error: {last_error}",
            "details": {},
        }

    except Exception as e:
        print(f"ERROR in Gemini Service: {str(e)}")
        return {
            "is_cheque": False,
            "prediction": "INVALID",
            "message": f"Processing Error: {str(e)}",
            "details": {
                "account_number": "N/A",
                "ifsc_code": "N/A",
                "cheque_number": "N/A",
                "payee_name": "N/A",
                "amount_words": "N/A",
                "amount_number": "N/A",
                "signature_present": "N/A",
                "signature_remarks": f"Service Error: {str(e)}",
            },
        }
