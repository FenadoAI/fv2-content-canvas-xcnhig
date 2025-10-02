"""FastAPI server exposing AI agent endpoints and blogging platform APIs."""

import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Request, Header, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from ai_agents.agents import AgentConfig, ChatAgent, SearchAgent
from models import (
    User, UserCreate, UserLogin, UserPublic, AuthResponse, UpdateUserRole,
    Article, ArticleCreate, ArticleUpdate, ArticlePublic, ArticleStatus,
    Comment, CommentCreate, CommentPublic, CommentStatus,
    Like, Setting, SettingUpdate, GoogleAuthRequest, UserRole
)
from auth_utils import (
    hash_password, verify_password, create_access_token,
    get_current_user_id, get_current_user_info
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent


class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StatusCheckCreate(BaseModel):
    client_name: str


class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None


def _ensure_db(request: Request):
    try:
        return request.app.state.db
    except AttributeError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=503, detail="Database not ready") from exc


def _get_agent_cache(request: Request) -> Dict[str, object]:
    if not hasattr(request.app.state, "agent_cache"):
        request.app.state.agent_cache = {}
    return request.app.state.agent_cache


async def _get_or_create_agent(request: Request, agent_type: str):
    cache = _get_agent_cache(request)
    if agent_type in cache:
        return cache[agent_type]

    config: AgentConfig = request.app.state.agent_config

    if agent_type == "search":
        cache[agent_type] = SearchAgent(config)
    elif agent_type == "chat":
        cache[agent_type] = ChatAgent(config)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown agent type '{agent_type}'")

    return cache[agent_type]


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv(ROOT_DIR / ".env")

    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME")

    if not mongo_url or not db_name:
        missing = [name for name, value in {"MONGO_URL": mongo_url, "DB_NAME": db_name}.items() if not value]
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    client = AsyncIOMotorClient(mongo_url)

    try:
        app.state.mongo_client = client
        app.state.db = client[db_name]
        app.state.agent_config = AgentConfig()
        app.state.agent_cache = {}
        logger.info("AI Agents API starting up")
        yield
    finally:
        client.close()
        logger.info("AI Agents API shutdown complete")


app = FastAPI(
    title="AI Agents API",
    description="Minimal AI Agents API with LangGraph and MCP support",
    lifespan=lifespan,
)

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


# ===== AUTH ENDPOINTS =====

@api_router.post("/auth/register", response_model=AuthResponse)
async def register_user(user_data: UserCreate, request: Request):
    """Register a new user with email and password."""
    db = _ensure_db(request)

    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        return AuthResponse(success=False, error="Email already registered")

    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=hash_password(user_data.password),
        role=UserRole.READER
    )

    await db.users.insert_one(user.model_dump())

    # Create token
    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value
    })

    user_public = UserPublic(**user.model_dump())
    return AuthResponse(success=True, token=token, user=user_public)


@api_router.post("/auth/login", response_model=AuthResponse)
async def login_user(credentials: UserLogin, request: Request):
    """Login with email and password."""
    db = _ensure_db(request)

    user_doc = await db.users.find_one({"email": credentials.email})
    if not user_doc or not user_doc.get("password_hash"):
        return AuthResponse(success=False, error="Invalid credentials")

    if not verify_password(credentials.password, user_doc["password_hash"]):
        return AuthResponse(success=False, error="Invalid credentials")

    # Create token
    token = create_access_token({
        "user_id": user_doc["id"],
        "email": user_doc["email"],
        "role": user_doc["role"]
    })

    user = User(**user_doc)
    user_public = UserPublic(**user.model_dump())
    return AuthResponse(success=True, token=token, user=user_public)


@api_router.post("/auth/google", response_model=AuthResponse)
async def google_auth(auth_data: GoogleAuthRequest, request: Request):
    """Authenticate with Google OAuth token."""
    db = _ensure_db(request)

    try:
        # Verify Google token
        idinfo = id_token.verify_oauth2_token(
            auth_data.token,
            google_requests.Request()
        )

        google_id = idinfo['sub']
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        profile_pic = idinfo.get('picture')

        # Find or create user
        user_doc = await db.users.find_one({"$or": [{"google_id": google_id}, {"email": email}]})

        if user_doc:
            # Update Google ID if needed
            if not user_doc.get("google_id"):
                await db.users.update_one(
                    {"id": user_doc["id"]},
                    {"$set": {"google_id": google_id}}
                )
            user = User(**user_doc)
        else:
            # Create new user
            user = User(
                email=email,
                name=name,
                google_id=google_id,
                profile_pic=profile_pic,
                role=UserRole.READER
            )
            await db.users.insert_one(user.model_dump())

        # Create token
        token = create_access_token({
            "user_id": user.id,
            "email": user.email,
            "role": user.role.value
        })

        user_public = UserPublic(**user.model_dump())
        return AuthResponse(success=True, token=token, user=user_public)

    except Exception as e:
        logger.exception("Google auth error")
        return AuthResponse(success=False, error=f"Authentication failed: {str(e)}")


@api_router.get("/auth/me", response_model=UserPublic)
async def get_current_user(request: Request, authorization: Optional[str] = Header(None)):
    """Get current user info from token."""
    db = _ensure_db(request)
    user_id = get_current_user_id(authorization)

    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic(**user_doc)


# ===== USER ENDPOINTS =====

@api_router.get("/users", response_model=List[UserPublic])
async def list_users(request: Request, authorization: Optional[str] = Header(None)):
    """List all users (admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    if user_info.get("role") != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin access required")

    users = await db.users.find().to_list(1000)
    return [UserPublic(**user) for user in users]


@api_router.get("/users/{user_id}", response_model=UserPublic)
async def get_user(user_id: str, request: Request):
    """Get user profile by ID."""
    db = _ensure_db(request)

    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")

    return UserPublic(**user_doc)


@api_router.put("/users/{user_id}/role", response_model=UserPublic)
async def update_user_role(
    user_id: str,
    role_data: UpdateUserRole,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Update user role (admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    if user_info.get("role") != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.users.update_one(
        {"id": user_id},
        {"$set": {"role": role_data.role.value}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    user_doc = await db.users.find_one({"id": user_id})
    return UserPublic(**user_doc)


# ===== ARTICLE ENDPOINTS =====

@api_router.post("/articles", response_model=ArticlePublic)
async def create_article(
    article_data: ArticleCreate,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Create a new article (writer/admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    if user_info.get("role") not in [UserRole.WRITER.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Writer or admin access required")

    # Get user name
    user_doc = await db.users.find_one({"id": user_info["user_id"]})

    article = Article(
        **article_data.model_dump(),
        author_id=user_info["user_id"],
        author_name=user_doc.get("name", "Unknown")
    )

    await db.articles.insert_one(article.model_dump())
    return ArticlePublic(**article.model_dump())


@api_router.put("/articles/{article_id}", response_model=ArticlePublic)
async def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Update an article (owner/admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    # Check if article exists
    article_doc = await db.articles.find_one({"id": article_id})
    if not article_doc:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check permissions
    is_owner = article_doc["author_id"] == user_info["user_id"]
    is_admin = user_info.get("role") == UserRole.ADMIN.value

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Update article
    update_data = {k: v for k, v in article_data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)

    await db.articles.update_one(
        {"id": article_id},
        {"$set": update_data}
    )

    updated_doc = await db.articles.find_one({"id": article_id})
    return ArticlePublic(**updated_doc)


@api_router.delete("/articles/{article_id}")
async def delete_article(
    article_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Delete an article (owner/admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    # Check if article exists
    article_doc = await db.articles.find_one({"id": article_id})
    if not article_doc:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check permissions
    is_owner = article_doc["author_id"] == user_info["user_id"]
    is_admin = user_info.get("role") == UserRole.ADMIN.value

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Delete article and related data
    await db.articles.delete_one({"id": article_id})
    await db.comments.delete_many({"article_id": article_id})
    await db.likes.delete_many({"article_id": article_id})

    return {"success": True, "message": "Article deleted"}


@api_router.get("/articles", response_model=List[ArticlePublic])
async def list_articles(
    request: Request,
    status: Optional[str] = None,
    category: Optional[str] = None,
    author_id: Optional[str] = None,
    featured: Optional[bool] = None
):
    """List articles with optional filters."""
    db = _ensure_db(request)

    query = {}
    if status:
        query["status"] = status
    if category:
        query["category"] = category
    if author_id:
        query["author_id"] = author_id
    if featured is not None:
        query["featured"] = featured

    articles = await db.articles.find(query).sort("created_at", -1).to_list(1000)
    return [ArticlePublic(**article) for article in articles]


@api_router.get("/articles/{article_id}", response_model=ArticlePublic)
async def get_article(article_id: str, request: Request):
    """Get a single article and increment view count."""
    db = _ensure_db(request)

    article_doc = await db.articles.find_one({"id": article_id})
    if not article_doc:
        raise HTTPException(status_code=404, detail="Article not found")

    # Increment view count
    await db.articles.update_one(
        {"id": article_id},
        {"$inc": {"views_count": 1}}
    )
    article_doc["views_count"] = article_doc.get("views_count", 0) + 1

    return ArticlePublic(**article_doc)


@api_router.put("/articles/{article_id}/publish", response_model=ArticlePublic)
async def publish_article(
    article_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Publish an article (owner/admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    # Check if article exists
    article_doc = await db.articles.find_one({"id": article_id})
    if not article_doc:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check permissions
    is_owner = article_doc["author_id"] == user_info["user_id"]
    is_admin = user_info.get("role") == UserRole.ADMIN.value

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Publish article
    await db.articles.update_one(
        {"id": article_id},
        {"$set": {
            "status": ArticleStatus.PUBLISHED.value,
            "published_at": datetime.now(timezone.utc)
        }}
    )

    updated_doc = await db.articles.find_one({"id": article_id})
    return ArticlePublic(**updated_doc)


@api_router.post("/articles/{article_id}/like")
async def toggle_like(
    article_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Like or unlike an article."""
    db = _ensure_db(request)
    user_id = get_current_user_id(authorization)

    # Check if article exists
    article_doc = await db.articles.find_one({"id": article_id})
    if not article_doc:
        raise HTTPException(status_code=404, detail="Article not found")

    # Check if already liked
    existing_like = await db.likes.find_one({"article_id": article_id, "user_id": user_id})

    if existing_like:
        # Unlike
        await db.likes.delete_one({"id": existing_like["id"]})
        await db.articles.update_one(
            {"id": article_id},
            {"$inc": {"likes_count": -1}}
        )
        return {"success": True, "liked": False}
    else:
        # Like
        like = Like(article_id=article_id, user_id=user_id)
        await db.likes.insert_one(like.model_dump())
        await db.articles.update_one(
            {"id": article_id},
            {"$inc": {"likes_count": 1}}
        )
        return {"success": True, "liked": True}


@api_router.get("/articles/trending/list", response_model=List[ArticlePublic])
async def get_trending_articles(request: Request, limit: int = 10):
    """Get trending articles (by likes count)."""
    db = _ensure_db(request)

    articles = await db.articles.find(
        {"status": ArticleStatus.PUBLISHED.value}
    ).sort("likes_count", -1).limit(limit).to_list(limit)

    return [ArticlePublic(**article) for article in articles]


@api_router.get("/articles/featured/list", response_model=List[ArticlePublic])
async def get_featured_articles(request: Request, limit: int = 10):
    """Get featured articles."""
    db = _ensure_db(request)

    articles = await db.articles.find(
        {"status": ArticleStatus.PUBLISHED.value, "featured": True}
    ).sort("created_at", -1).limit(limit).to_list(limit)

    return [ArticlePublic(**article) for article in articles]


# ===== COMMENT ENDPOINTS =====

@api_router.post("/comments", response_model=CommentPublic)
async def create_comment(
    comment_data: CommentCreate,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Create a comment on an article."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    # Check if article exists
    article_doc = await db.articles.find_one({"id": comment_data.article_id})
    if not article_doc:
        raise HTTPException(status_code=404, detail="Article not found")

    # Get user name
    user_doc = await db.users.find_one({"id": user_info["user_id"]})

    comment = Comment(
        **comment_data.model_dump(),
        user_id=user_info["user_id"],
        user_name=user_doc.get("name", "Unknown")
    )

    await db.comments.insert_one(comment.model_dump())
    return CommentPublic(**comment.model_dump())


@api_router.get("/comments/{article_id}", response_model=List[CommentPublic])
async def get_article_comments(article_id: str, request: Request):
    """Get approved comments for an article."""
    db = _ensure_db(request)

    comments = await db.comments.find({
        "article_id": article_id,
        "status": CommentStatus.APPROVED.value
    }).sort("created_at", -1).to_list(1000)

    return [CommentPublic(**comment) for comment in comments]


@api_router.get("/comments/pending/list", response_model=List[CommentPublic])
async def get_pending_comments(
    request: Request,
    authorization: Optional[str] = Header(None),
    article_id: Optional[str] = None
):
    """Get pending comments (for admin or article author)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    query = {"status": CommentStatus.PENDING.value}

    # If not admin, only show comments on user's articles
    if user_info.get("role") != UserRole.ADMIN.value:
        user_articles = await db.articles.find({"author_id": user_info["user_id"]}).to_list(1000)
        article_ids = [article["id"] for article in user_articles]
        query["article_id"] = {"$in": article_ids}

    if article_id:
        query["article_id"] = article_id

    comments = await db.comments.find(query).sort("created_at", -1).to_list(1000)
    return [CommentPublic(**comment) for comment in comments]


@api_router.put("/comments/{comment_id}/approve")
async def approve_comment(
    comment_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Approve a comment (admin or article author)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    # Get comment
    comment_doc = await db.comments.find_one({"id": comment_id})
    if not comment_doc:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check permissions
    is_admin = user_info.get("role") == UserRole.ADMIN.value
    article_doc = await db.articles.find_one({"id": comment_doc["article_id"]})
    is_author = article_doc and article_doc["author_id"] == user_info["user_id"]

    if not (is_admin or is_author):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Approve comment
    await db.comments.update_one(
        {"id": comment_id},
        {"$set": {"status": CommentStatus.APPROVED.value}}
    )

    return {"success": True, "message": "Comment approved"}


@api_router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Delete a comment (admin or article author)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    # Get comment
    comment_doc = await db.comments.find_one({"id": comment_id})
    if not comment_doc:
        raise HTTPException(status_code=404, detail="Comment not found")

    # Check permissions
    is_admin = user_info.get("role") == UserRole.ADMIN.value
    article_doc = await db.articles.find_one({"id": comment_doc["article_id"]})
    is_author = article_doc and article_doc["author_id"] == user_info["user_id"]

    if not (is_admin or is_author):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Delete comment
    await db.comments.delete_one({"id": comment_id})

    return {"success": True, "message": "Comment deleted"}


# ===== SETTINGS ENDPOINTS =====

@api_router.get("/settings/{key}")
async def get_setting(key: str, request: Request):
    """Get a setting value."""
    db = _ensure_db(request)

    setting_doc = await db.settings.find_one({"key": key})
    if not setting_doc:
        return {"key": key, "value": None}

    return {"key": key, "value": setting_doc["value"]}


@api_router.put("/settings/{key}")
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """Update a setting (admin only)."""
    db = _ensure_db(request)
    user_info = get_current_user_info(authorization)

    if user_info.get("role") != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Upsert setting
    await db.settings.update_one(
        {"key": key},
        {"$set": {"key": key, "value": setting_data.value}},
        upsert=True
    )

    return {"success": True, "key": key, "value": setting_data.value}


@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate, request: Request):
    db = _ensure_db(request)
    status_obj = StatusCheck(**input.model_dump())
    await db.status_checks.insert_one(status_obj.model_dump())
    return status_obj


@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks(request: Request):
    db = _ensure_db(request)
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(chat_request: ChatRequest, request: Request):
    try:
        agent = await _get_or_create_agent(request, chat_request.agent_type)
        response = await agent.execute(chat_request.message)

        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=chat_request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error in chat endpoint")
        return ChatResponse(
            success=False,
            response="",
            agent_type=chat_request.agent_type,
            capabilities=[],
            error=str(exc),
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(search_request: SearchRequest, request: Request):
    try:
        search_agent = await _get_or_create_agent(request, "search")
        search_prompt = (
            f"Search for information about: {search_request.query}. "
            "Provide a comprehensive summary with key findings."
        )
        result = await search_agent.execute(search_prompt, use_tools=True)

        if result.success:
            metadata = result.metadata or {}
            return SearchResponse(
                success=True,
                query=search_request.query,
                summary=result.content,
                search_results=metadata,
                sources_count=int(metadata.get("tool_run_count", metadata.get("tools_used", 0)) or 0),
            )

        return SearchResponse(
            success=False,
            query=search_request.query,
            summary="",
            sources_count=0,
            error=result.error,
        )
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error in search endpoint")
        return SearchResponse(
            success=False,
            query=search_request.query,
            summary="",
            sources_count=0,
            error=str(exc),
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities(request: Request):
    try:
        search_agent = await _get_or_create_agent(request, "search")
        chat_agent = await _get_or_create_agent(request, "chat")

        return {
            "success": True,
            "capabilities": {
                "search_agent": search_agent.get_capabilities(),
                "chat_agent": chat_agent.get_capabilities(),
            },
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Error getting capabilities")
        return {"success": False, "error": str(exc)}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
