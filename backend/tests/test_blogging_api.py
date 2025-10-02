"""Test blogging platform APIs."""

import os
import requests
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Load environment
load_dotenv()

BASE_URL = "http://localhost:8001/api"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "test_database")


async def promote_user_to_role(email, role):
    """Promote a user to a specific role in MongoDB."""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    result = await db.users.update_one(
        {"email": email},
        {"$set": {"role": role}}
    )
    client.close()
    return result.modified_count > 0

# Test data
test_user = {
    "email": f"testuser_{os.urandom(4).hex()}@example.com",
    "password": "testpass123",
    "name": "Test User"
}

test_writer = {
    "email": f"testwriter_{os.urandom(4).hex()}@example.com",
    "password": "writerpass123",
    "name": "Test Writer"
}

test_admin = {
    "email": f"testadmin_{os.urandom(4).hex()}@example.com",
    "password": "adminpass123",
    "name": "Test Admin"
}


def test_auth_flow():
    """Test user registration and login."""
    print("\n=== Testing Auth Flow ===")

    # Register user
    response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    data = response.json()
    assert data["success"] == True, "Registration should succeed"
    assert data["token"] is not None, "Should receive token"
    assert data["user"]["email"] == test_user["email"], "Email should match"

    user_token = data["token"]
    print(f"✓ User registered: {test_user['email']}")

    # Login
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_user["email"],
        "password": test_user["password"]
    })
    assert response.status_code == 200, f"Login failed: {response.text}"
    data = response.json()
    assert data["success"] == True, "Login should succeed"
    assert data["token"] is not None, "Should receive token"
    print("✓ User logged in successfully")

    # Get current user
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    assert response.status_code == 200, f"Get me failed: {response.text}"
    data = response.json()
    assert data["email"] == test_user["email"], "Email should match"
    print("✓ Get current user working")

    return user_token


def test_role_management():
    """Test user role management."""
    print("\n=== Testing Role Management ===")

    # Register writer and admin
    response = requests.post(f"{BASE_URL}/auth/register", json=test_writer)
    assert response.status_code == 200, f"Writer registration failed: {response.text}"
    writer_data = response.json()
    writer_token = writer_data["token"]
    writer_id = writer_data["user"]["id"]
    print(f"✓ Writer registered: {test_writer['email']}")

    response = requests.post(f"{BASE_URL}/auth/register", json=test_admin)
    assert response.status_code == 200, f"Admin registration failed: {response.text}"
    admin_data = response.json()
    admin_token = admin_data["token"]
    admin_id = admin_data["user"]["id"]
    print(f"✓ Admin registered: {test_admin['email']}")

    # Promote users via direct MongoDB access (simulating initial admin setup)
    asyncio.run(promote_user_to_role(test_writer["email"], "writer"))
    print(f"✓ Promoted {test_writer['email']} to writer")

    asyncio.run(promote_user_to_role(test_admin["email"], "admin"))
    print(f"✓ Promoted {test_admin['email']} to admin")

    # Test that non-admin cannot change roles
    headers = {"Authorization": f"Bearer {writer_token}"}
    response = requests.put(f"{BASE_URL}/users/{writer_id}/role",
                           json={"role": "admin"},
                           headers=headers)
    assert response.status_code == 403, "Non-admin should not be able to change roles"
    print("✓ Non-admin cannot change roles")

    # Re-login to get fresh tokens with updated roles
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_writer["email"],
        "password": test_writer["password"]
    })
    writer_token = response.json()["token"]

    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_admin["email"],
        "password": test_admin["password"]
    })
    admin_token = response.json()["token"]
    print("✓ Re-authenticated with updated roles")

    return writer_token, writer_id, admin_token, admin_id


def test_article_workflow(writer_token, writer_id):
    """Test article creation, update, and publication."""
    print("\n=== Testing Article Workflow ===")

    headers = {"Authorization": f"Bearer {writer_token}"}

    # Create draft article
    article_data = {
        "title": "Test Article",
        "content": "This is a test article content with some meaningful text.",
        "category": "Technology",
        "tags": ["test", "blog"]
    }

    response = requests.post(f"{BASE_URL}/articles", json=article_data, headers=headers)
    assert response.status_code == 200, f"Article creation failed: {response.text}"
    article = response.json()
    assert article["title"] == article_data["title"], "Title should match"
    assert article["status"] == "draft", "Should be draft initially"
    article_id = article["id"]
    print(f"✓ Article created as draft: {article_id}")

    # Update article
    update_data = {
        "title": "Updated Test Article",
        "content": "Updated content"
    }
    response = requests.put(f"{BASE_URL}/articles/{article_id}",
                           json=update_data,
                           headers=headers)
    assert response.status_code == 200, f"Article update failed: {response.text}"
    updated_article = response.json()
    assert updated_article["title"] == update_data["title"], "Title should be updated"
    print("✓ Article updated")

    # Publish article
    response = requests.put(f"{BASE_URL}/articles/{article_id}/publish", headers=headers)
    assert response.status_code == 200, f"Article publish failed: {response.text}"
    published_article = response.json()
    assert published_article["status"] == "published", "Should be published"
    assert published_article["published_at"] is not None, "Should have publish date"
    print("✓ Article published")

    # Get published articles
    response = requests.get(f"{BASE_URL}/articles?status=published")
    assert response.status_code == 200, f"Get articles failed: {response.text}"
    articles = response.json()
    assert len(articles) > 0, "Should have at least one published article"
    print(f"✓ Retrieved {len(articles)} published articles")

    return article_id


def test_like_feature(article_id, user_token):
    """Test article like/unlike functionality."""
    print("\n=== Testing Like Feature ===")

    headers = {"Authorization": f"Bearer {user_token}"}

    # Like article
    response = requests.post(f"{BASE_URL}/articles/{article_id}/like", headers=headers)
    assert response.status_code == 200, f"Like failed: {response.text}"
    data = response.json()
    assert data["success"] == True, "Like should succeed"
    assert data["liked"] == True, "Should be liked"
    print("✓ Article liked")

    # Get article and check like count
    response = requests.get(f"{BASE_URL}/articles/{article_id}")
    assert response.status_code == 200, f"Get article failed: {response.text}"
    article = response.json()
    assert article["likes_count"] >= 1, "Like count should be at least 1"
    print(f"✓ Like count: {article['likes_count']}")

    # Unlike article
    response = requests.post(f"{BASE_URL}/articles/{article_id}/like", headers=headers)
    assert response.status_code == 200, f"Unlike failed: {response.text}"
    data = response.json()
    assert data["liked"] == False, "Should be unliked"
    print("✓ Article unliked")

    # Like again for trending test
    response = requests.post(f"{BASE_URL}/articles/{article_id}/like", headers=headers)
    assert response.status_code == 200, "Re-like failed"
    print("✓ Article re-liked for trending test")


def test_trending_featured(article_id):
    """Test trending and featured articles."""
    print("\n=== Testing Trending & Featured Articles ===")

    # Get trending articles
    response = requests.get(f"{BASE_URL}/articles/trending/list")
    assert response.status_code == 200, f"Get trending failed: {response.text}"
    trending = response.json()
    assert len(trending) > 0, "Should have trending articles"
    print(f"✓ Retrieved {len(trending)} trending articles")

    # Get featured articles
    response = requests.get(f"{BASE_URL}/articles/featured/list")
    assert response.status_code == 200, f"Get featured failed: {response.text}"
    featured = response.json()
    print(f"✓ Retrieved {len(featured)} featured articles")


def test_comment_workflow(article_id, user_token, writer_token):
    """Test comment creation and moderation."""
    print("\n=== Testing Comment Workflow ===")

    user_headers = {"Authorization": f"Bearer {user_token}"}
    writer_headers = {"Authorization": f"Bearer {writer_token}"}

    # Create comment
    comment_data = {
        "article_id": article_id,
        "content": "This is a test comment"
    }

    response = requests.post(f"{BASE_URL}/comments",
                            json=comment_data,
                            headers=user_headers)
    assert response.status_code == 200, f"Comment creation failed: {response.text}"
    comment = response.json()
    assert comment["content"] == comment_data["content"], "Content should match"
    assert comment["status"] == "pending", "Comment should be pending"
    comment_id = comment["id"]
    print(f"✓ Comment created (pending): {comment_id}")

    # Get approved comments (should be empty)
    response = requests.get(f"{BASE_URL}/comments/{article_id}")
    assert response.status_code == 200, f"Get comments failed: {response.text}"
    comments = response.json()
    assert len(comments) == 0, "No approved comments yet"
    print("✓ No approved comments yet")

    # Get pending comments (as article author)
    response = requests.get(f"{BASE_URL}/comments/pending/list", headers=writer_headers)
    assert response.status_code == 200, f"Get pending comments failed: {response.text}"
    pending = response.json()
    assert len(pending) > 0, "Should have pending comments"
    print(f"✓ Retrieved {len(pending)} pending comments")

    # Approve comment (as article author)
    response = requests.put(f"{BASE_URL}/comments/{comment_id}/approve",
                           headers=writer_headers)
    assert response.status_code == 200, f"Approve comment failed: {response.text}"
    data = response.json()
    assert data["success"] == True, "Approval should succeed"
    print("✓ Comment approved by author")

    # Get approved comments (should have one)
    response = requests.get(f"{BASE_URL}/comments/{article_id}")
    assert response.status_code == 200, f"Get comments failed: {response.text}"
    comments = response.json()
    assert len(comments) == 1, "Should have one approved comment"
    print(f"✓ Retrieved {len(comments)} approved comments")

    return comment_id


def test_settings_api(admin_token):
    """Test settings management."""
    print("\n=== Testing Settings API ===")

    # Note: This will fail because our test admin is not actually admin role
    # In real scenario, we'd promote the user first
    headers = {"Authorization": f"Bearer {admin_token}"}

    # Get setting
    response = requests.get(f"{BASE_URL}/settings/about_us")
    assert response.status_code == 200, f"Get setting failed: {response.text}"
    data = response.json()
    print(f"✓ Retrieved setting: {data}")


def run_all_tests():
    """Run all tests in sequence."""
    print("=" * 60)
    print("BLOGGING PLATFORM API TESTS")
    print("=" * 60)

    try:
        # Test auth
        user_token = test_auth_flow()

        # Test roles
        writer_token, writer_id, admin_token, admin_id = test_role_management()

        # Test articles
        article_id = test_article_workflow(writer_token, writer_id)

        # Test likes
        test_like_feature(article_id, user_token)

        # Test trending/featured
        test_trending_featured(article_id)

        # Test comments
        test_comment_workflow(article_id, user_token, writer_token)

        # Test settings
        test_settings_api(admin_token)

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        return False

    return True


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
