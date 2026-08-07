"""
Clinical Report Generator
"""

class ReportService:

    @staticmethod
    def generate(result):

        diagnosis = result["predicted_classes"][0]

        confidence = list(result["confidence"].values())[0]

        probabilities = result["probabilities"]

        if diagnosis == "NORM":

            risk = "Low"

            recommendation = (
                "No significant ECG abnormalities detected. "
                "Routine clinical follow-up is recommended."
            )

        elif diagnosis == "MI":

            risk = "High"

            recommendation = (
                "Possible Myocardial Infarction detected. "
                "Immediate cardiology consultation is recommended."
            )

        elif diagnosis == "HYP":

            risk = "Moderate"

            recommendation = (
                "Possible Hypertrophy detected. "
                "Further clinical evaluation is advised."
            )

        elif diagnosis == "CD":

            risk = "Moderate"

            recommendation = (
                "Possible Conduction Disturbance detected."
            )

        else:

            risk = "Moderate"

            recommendation = (
                "Possible ST/T abnormalities detected."
            )

        return {

            "diagnosis": diagnosis,

            "confidence": round(confidence * 100, 2),

            "risk_level": risk,

            "recommendation": recommendation,

            "probabilities": {
                k: round(v * 100, 2)
                for k, v in probabilities.items()
            }

        }