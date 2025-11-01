from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from markdown import markdown
from generate_image import generate_images_for_title_and_description
from groq_client import generate_blog_content
import logging
from pathlib import Path
from typing import Optional, List, Dict
import asyncio
from concurrent.futures import ThreadPoolExecutor
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="BlogAI", description="AI-powered blog generation tool")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Add thread pool executor for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=3)


@app.head("/")
async def head_check():
    return {"status": "ok"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    
    for error in exc.errors():
        if error.get('loc') == ['body', 'description'] and error.get('type') == 'missing':
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request, 
                    "error": "Please provide a blog description or use the quick generation method"
                },
                status_code=422
            )
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "error": "Please check your input and try again"
        },
        status_code=422
    )

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/examples", response_class=HTMLResponse)
async def examples(request: Request):
    return templates.TemplateResponse("examples.html", {"request": request})

@app.get("/create", response_class=HTMLResponse)
async def create(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})
@app.get("/contact",response_class=HTMLResponse)
async def contact(request: Request):
        return templates.TemplateResponse("contact.html", {"request": request})
    

@app.post("/generate", response_class=HTMLResponse)
async def generate_blog(
    request: Request,
    title: str = Form(...),
    generation_method: str = Form("detailed"),
    description: Optional[str] = Form(None),
    generate_image: Optional[str] = Form(None)
):
    try:
        generate_img = generate_image == 'on'

        # Handle different generation methods
        if generation_method == 'quick':
            final_description = f"Create a comprehensive blog post about {title}. Include relevant information, examples, and insights that would be valuable to readers interested in this topic."
            logger.info(f"📝 Quick generation for title: {title}")
        else:
            if not description or not description.strip():
                return templates.TemplateResponse(
                    "error.html",
                    {"request": request, "error": "Please provide a blog description for detailed generation"},
                    status_code=400
                )
            final_description = description.strip()
            logger.info(f"📝 Detailed generation for title: {title}")

        logger.info(f"📝 Generating 3 blog variations for: {title}")
        
        # Generate 3 different variations concurrently
        tasks = []
        for i in range(3):
            task = asyncio.get_event_loop().run_in_executor(
                executor, generate_blog_content, title, final_description, i+1
            )
            tasks.append(task)
        
        blog_contents = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for content generation errors
        for i, content in enumerate(blog_contents):
            if isinstance(content, Exception):
                logger.error(f"❌ Variation {i+1} failed: {str(content)}")
                return templates.TemplateResponse(
                    "error.html",
                    {"request": request, "error": f"Failed to generate blog variation {i+1}: {str(content)}"},
                    status_code=500
                )

        # Process each variation with images
        blog_variations = []
        for i, blog_md in enumerate(blog_contents):
            blog_html = markdown(blog_md, extensions=['fenced_code', 'tables'])
            preview = blog_md[:200] + "..." if len(blog_md) > 200 else blog_md
            
            # Generate 6 images for each variation (1 title + 5 content)
            images = []
            if generate_img:
                images = await asyncio.get_event_loop().run_in_executor(
                    executor, generate_images_for_title_and_description, title, final_description, 6
                )
            
            blog_variations.append({
                'id': i + 1,
                'content_md': blog_md,
                'content_html': blog_html,
                'preview': preview,
                'images': images
            })

        return templates.TemplateResponse(
            "blog_selection.html",
            {
                "request": request,
                "title": title,
                "description": final_description,
                "blog_variations": blog_variations,
                "generate_image": generate_img,
                "generation_method": generation_method
            }
        )

    except Exception as e:
        logger.error(f"❌ Blog generation failed: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

@app.post("/generate-final", response_class=HTMLResponse)
async def generate_final_blog(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    selected_blog: str = Form(...),
    generate_image: Optional[str] = Form(None)
):
    try:
        generate_img = generate_image == 'on'
        
        # Generate images based on title and description
        images = []
        if generate_img:
            images = await asyncio.get_event_loop().run_in_executor(
                executor, generate_images_for_title_and_description, title, description, 6
            )

        # Convert Markdown to HTML
        blog_html = markdown(selected_blog, extensions=['fenced_code', 'tables'])

        # Split blog content into sections based on Markdown headings
        sections = re.split(r'(?m)^##\s+', selected_blog)
        paragraphs = []
        for section in sections[1:]:  # Skip the first empty section before the first heading
            # Extract heading and content
            lines = section.strip().split('\n', 1)
            if len(lines) > 1:
                heading = f"<h2>{lines[0].strip()}</h2>"
                content = markdown(lines[1].strip(), extensions=['fenced_code', 'tables'])
                paragraphs.append(f"{heading}{content}")
            elif lines:
                heading = f"<h2>{lines[0].strip()}</h2>"
                paragraphs.append(heading)
        
        # Ensure at least 5 sections; raise error if content is invalid
        if len(paragraphs) < 5:
            raise ValueError("Generated blog content does not contain the required 5 sections")

        # Prepare featured image and content images
        featured_image = images[0] if images else None
        content_images = images[1:] if len(images) > 1 else []

        return templates.TemplateResponse(
            "blog_result.html",
            {
                "request": request,
                "title": title,
                "description": description,
                "blog_content": blog_html,
                "featured_image": featured_image,
                "content_images": content_images,
                "total_images": len(images) if generate_img else 0,
                "paragraphs": paragraphs[:5]
            }
        )

    except Exception as e:
        logger.error(f"❌ Final blog generation failed: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    import uvicorn
    Path("static").mkdir(exist_ok=True)
    Path("static/images").mkdir(parents=True, exist_ok=True)
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        workers=1,
        timeout_keep_alive=30,
        limit_concurrency=10
    )