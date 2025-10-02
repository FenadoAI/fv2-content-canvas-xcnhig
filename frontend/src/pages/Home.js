import React, { useState, useEffect } from 'react';
import { getTrendingArticles, getFeaturedArticles, getArticles } from '../services/api';
import ArticleCard from '../components/ArticleCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Skeleton } from '../components/ui/skeleton';

const Home = () => {
  const [trendingArticles, setTrendingArticles] = useState([]);
  const [featuredArticles, setFeaturedArticles] = useState([]);
  const [recentArticles, setRecentArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const [trending, featured, recent] = await Promise.all([
        getTrendingArticles(6),
        getFeaturedArticles(6),
        getArticles({ status: 'published' })
      ]);
      setTrendingArticles(trending);
      setFeaturedArticles(featured);
      setRecentArticles(recent.slice(0, 12));
    } catch (error) {
      console.error('Failed to load articles:', error);
    } finally {
      setLoading(false);
    }
  };

  const ArticleGrid = ({ articles }) => {
    if (loading) {
      return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="space-y-3">
              <Skeleton className="h-48 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-1/2" />
            </div>
          ))}
        </div>
      );
    }

    if (articles.length === 0) {
      return (
        <div className="text-center py-12">
          <p className="text-gray-500">No articles found</p>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-5xl font-bold mb-4">Welcome to BlogHub</h1>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              Discover amazing stories, insights, and ideas from writers around the world
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Tabs defaultValue="trending" className="space-y-8">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-3">
            <TabsTrigger value="trending">Trending</TabsTrigger>
            <TabsTrigger value="featured">Featured</TabsTrigger>
            <TabsTrigger value="recent">Recent</TabsTrigger>
          </TabsList>

          <TabsContent value="trending">
            <div className="space-y-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  🔥 Trending Articles
                </h2>
                <p className="text-gray-600">Most liked articles right now</p>
              </div>
              <ArticleGrid articles={trendingArticles} />
            </div>
          </TabsContent>

          <TabsContent value="featured">
            <div className="space-y-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  ⭐ Featured Articles
                </h2>
                <p className="text-gray-600">Hand-picked by our editors</p>
              </div>
              <ArticleGrid articles={featuredArticles} />
            </div>
          </TabsContent>

          <TabsContent value="recent">
            <div className="space-y-6">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  📰 Recent Articles
                </h2>
                <p className="text-gray-600">Latest published content</p>
              </div>
              <ArticleGrid articles={recentArticles} />
            </div>
          </TabsContent>
        </Tabs>

        {/* Instagram Widget Section */}
        <div className="mt-16 py-12 bg-white rounded-lg shadow-sm">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Follow Us on Instagram
            </h2>
            <p className="text-gray-600">Stay connected with our latest updates</p>
          </div>
          <div className="flex justify-center">
            <div className="w-full max-w-md">
              {/* Instagram Embed - Simple iframe embed */}
              <div className="bg-gradient-to-br from-purple-500 via-pink-500 to-orange-500 p-1 rounded-lg shadow-lg">
                <div className="bg-white rounded-lg p-6 text-center">
                  <div className="mb-4">
                    <svg className="w-16 h-16 mx-auto text-pink-500" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">@BlogHub</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    Check out our Instagram for behind-the-scenes content and writer spotlights
                  </p>
                  <a
                    href="https://instagram.com/bloghub"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block bg-gradient-to-r from-purple-500 to-pink-500 text-white px-6 py-2 rounded-lg font-semibold hover:opacity-90 transition-opacity"
                  >
                    Follow Us
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
