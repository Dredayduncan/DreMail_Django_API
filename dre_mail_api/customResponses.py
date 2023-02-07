class CustomResponses:

    @staticmethod
    def errorResponse(message):
        return {
       "error": {
        "detail": message
       }
    }

    @staticmethod
    def successResponse(message):
        return {
            "detail": message
        }