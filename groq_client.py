import os
import logging
from groq import Groq
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
try:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    logger.error(f"❌ Failed to initialize Groq client: {str(e)}")
    raise ValueError("Please ensure GROQ_API_KEY is set in your .env file")

def generate_blog_content(title: str, description: str, variation: int = 1) -> str:
    """
    Generate blog content using Groq API with a specific structure.
    Args:
        title: Blog title
        description: Blog description or prompt
        variation: Variation number (1, 2, or 3) to determine blog style
    Returns:
        Markdown-formatted blog content
    """
    try:
        # Define blog style based on variation
        styles = {
            1: "Informative and educational with detailed explanations and examples",
            2: "Comparative and analytical with pros/cons and insights",
            3: "Opinion-based and thought-provoking with bold perspectives"
        }
        style = styles.get(variation, styles[1])

        # Create prompt for structured blog content
        prompt = f"""
        Write a blog post with exactly 5 sections based on the title "{title}" and description "{description}". 
        The blog should be written in a {style} style. Follow this structure:

        1. **Introduction**
           - Brief overview of the topic
           - Engaging hook to grab attention
           - State the problem or promise a benefit
           - 100-150 words

        2. **Understanding the Core Concepts**
           - Detailed explanation of the main topic
           - Include examples, stats, or case studies
           - Use bullet points or numbered lists for clarity
           - 200-300 words

        3. **Practical Applications and Benefits**
           - Discuss how the topic applies in real-world scenarios
           - Provide actionable insights or solutions
           - Include supporting points like quotes or visuals (describe if applicable)
           - 200-300 words

        4. **Conclusion**
           - Summarize key points
           - Provide final thoughts or takeaways
           - Re-emphasize the benefit or solution
           - 100-150 words

        5. **Call to Action**
           - Encourage reader engagement (e.g., comment, share, subscribe)
           - Suggest next steps or related resources
           - 50-100 words

        Format the content in Markdown with appropriate headings (## for section titles).
        Ensure each section is clearly separated and follows the word count guidelines.
        Do not include images or alt text in the content.
        """

        logger.info(f"📝 Generating blog variation {variation} for title: {title}")
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=1500,
            temperature=0.7
        )
        
        if not response.choices[0].message.content:
            raise ValueError("Empty response from Groq API")
        
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"❌ Blog content generation failed: {str(e)}")
        raise ValueError(f"Blog content generation failed: {str(e)}")