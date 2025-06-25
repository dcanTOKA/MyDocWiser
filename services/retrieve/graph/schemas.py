from pydantic import BaseModel, Field


class GradeQuestion(BaseModel):
    score: str = Field(
        description=(
            "You are DocWiser, an assistant designed to help users with software libraries, SDKs, APIs, and developer documentation.\n\n"
            "Your goal is to determine whether the user's question is relevant to this purpose. A relevant question is typically:\n"
            "- asking how to use a tool, library, or API\n"
            "- requesting code examples or usage patterns\n"
            "- asking about installation, integration, or documentation-related information\n\n"
            "Respond with:\n"
            "- 'Yes' if the question is about the practical or theoretical use of a software tool or documentation.\n"
            "- 'No' otherwise."
        )
    )


class RephrasedQuestion(BaseModel):
    rewritten: str = Field(
        description="A rewritten version of the question, phrased clearly and technically for an AI assistant to understand."
    )


class DetectedLibrary(BaseModel):
    library: str = Field(
        description="The name of the software library or framework mentioned in the question. "
                    "If no library is mentioned, respond with 'none'."
    )
