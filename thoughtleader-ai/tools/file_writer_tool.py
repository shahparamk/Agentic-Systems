import os
from datetime import datetime
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FileWriterInput(BaseModel):
    content: str = Field(description="The final content to save to a file")
    filename: str = Field(description="Name of the file without extension")


class FileWriterTool(BaseTool):
    name: str = "File Writer Tool"
    description: str = (
        "Saves the final generated content to a markdown file in the outputs/ directory. "
        "Use this as the last step after content has been written and edited."
    )
    args_schema: type[BaseModel] = FileWriterInput

    def _run(self, content: str, filename: str) -> str:
        try:
            os.makedirs("outputs", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in filename)
            filepath = f"outputs/{safe_name}_{timestamp}.md"

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {filename}\n\n")
                f.write(f"*Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*\n\n")
                f.write("---\n\n")
                f.write(content)

            return f"File saved successfully: {filepath}"

        except Exception as e:
            return f"Failed to save file: {str(e)}"