import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { createArticle, updateArticle, getArticle } from '../services/api';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { toast } from 'sonner';

const ArticleEditor = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isWriter } = useAuth();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingArticle, setLoadingArticle] = useState(false);

  const isEditMode = !!id && id !== 'new';

  useEffect(() => {
    if (!user || !isWriter()) {
      navigate('/');
      toast.error('You must be a writer to create articles');
      return;
    }

    if (isEditMode) {
      loadArticle();
    }
  }, [id, user]);

  const loadArticle = async () => {
    try {
      setLoadingArticle(true);
      const article = await getArticle(id);
      setTitle(article.title);
      setContent(article.content);
      setCategory(article.category || '');
      setTags(article.tags?.join(', ') || '');
    } catch (error) {
      console.error('Failed to load article:', error);
      toast.error('Failed to load article');
      navigate('/dashboard/writer');
    } finally {
      setLoadingArticle(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim() || !content.trim()) {
      toast.error('Title and content are required');
      return;
    }

    setLoading(true);

    try {
      const articleData = {
        title: title.trim(),
        content: content.trim(),
        category: category.trim() || null,
        tags: tags.split(',').map(t => t.trim()).filter(t => t)
      };

      if (isEditMode) {
        await updateArticle(id, articleData);
        toast.success('Article updated successfully!');
      } else {
        const newArticle = await createArticle(articleData);
        toast.success('Article created successfully!');
        navigate(`/article/${newArticle.id}`);
        return;
      }

      navigate(`/article/${id}`);
    } catch (error) {
      console.error('Failed to save article:', error);
      toast.error('Failed to save article');
    } finally {
      setLoading(false);
    }
  };

  if (loadingArticle) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-600">Loading article...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">
              {isEditMode ? 'Edit Article' : 'Create New Article'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  type="text"
                  placeholder="Enter article title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  type="text"
                  placeholder="e.g., Technology, Lifestyle, Business"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="tags">Tags (comma separated)</Label>
                <Input
                  id="tags"
                  type="text"
                  placeholder="e.g., programming, tutorial, javascript"
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="content">Content *</Label>
                <Textarea
                  id="content"
                  placeholder="Write your article content here..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  required
                  rows={20}
                  className="font-mono"
                />
                <p className="text-sm text-gray-500">
                  {content.length} characters
                </p>
              </div>

              <div className="flex items-center space-x-4">
                <Button type="submit" disabled={loading}>
                  {loading ? 'Saving...' : (isEditMode ? 'Update Article' : 'Create Article')}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => navigate('/dashboard/writer')}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default ArticleEditor;
