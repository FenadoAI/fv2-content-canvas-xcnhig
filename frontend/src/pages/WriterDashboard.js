import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getArticles, deleteArticle, publishArticle, getPendingComments, approveComment, deleteComment as deleteCommentApi } from '../services/api';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { PenSquare, Trash2, Eye, Check, X } from 'lucide-react';
import { toast } from 'sonner';

const WriterDashboard = () => {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [pendingComments, setPendingComments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      navigate('/signin');
      return;
    }
    loadDashboardData();
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const params = isAdmin() ? {} : { author_id: user.id };
      const [articlesData, commentsData] = await Promise.all([
        getArticles(params),
        getPendingComments()
      ]);
      setArticles(articlesData);
      setPendingComments(commentsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async (articleId) => {
    try {
      await publishArticle(articleId);
      toast.success('Article published successfully!');
      loadDashboardData();
    } catch (error) {
      toast.error('Failed to publish article');
    }
  };

  const handleDelete = async (articleId) => {
    if (!window.confirm('Are you sure you want to delete this article?')) return;

    try {
      await deleteArticle(articleId);
      toast.success('Article deleted successfully');
      loadDashboardData();
    } catch (error) {
      toast.error('Failed to delete article');
    }
  };

  const handleApproveComment = async (commentId) => {
    try {
      await approveComment(commentId);
      toast.success('Comment approved');
      loadDashboardData();
    } catch (error) {
      toast.error('Failed to approve comment');
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await deleteCommentApi(commentId);
      toast.success('Comment deleted');
      loadDashboardData();
    } catch (error) {
      toast.error('Failed to delete comment');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isAdmin() ? 'Admin Dashboard' : 'Writer Dashboard'}
            </h1>
            <p className="text-gray-600">Manage your content and engagement</p>
          </div>
          <Button onClick={() => navigate('/article/new')} className="flex items-center space-x-2">
            <PenSquare className="w-4 h-4" />
            <span>New Article</span>
          </Button>
        </div>

        <Tabs defaultValue="articles" className="space-y-6">
          <TabsList>
            <TabsTrigger value="articles">My Articles ({articles.length})</TabsTrigger>
            <TabsTrigger value="comments">Pending Comments ({pendingComments.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="articles">
            <div className="space-y-4">
              {articles.length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center">
                    <p className="text-gray-500 mb-4">No articles yet</p>
                    <Button onClick={() => navigate('/article/new')}>Write your first article</Button>
                  </CardContent>
                </Card>
              ) : (
                articles.map((article) => (
                  <Card key={article.id}>
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="text-lg font-semibold text-gray-900">{article.title}</h3>
                            <Badge variant={article.status === 'published' ? 'default' : 'secondary'}>
                              {article.status}
                            </Badge>
                            {article.featured && <Badge className="bg-yellow-500">Featured</Badge>}
                          </div>
                          <p className="text-sm text-gray-600 mb-2 line-clamp-2">{article.content}</p>
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>{formatDate(article.created_at)}</span>
                            <span>❤️ {article.likes_count || 0}</span>
                            <span>👁️ {article.views_count || 0}</span>
                            {article.category && <Badge variant="outline">{article.category}</Badge>}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          {article.status === 'draft' && (
                            <Button size="sm" onClick={() => handlePublish(article.id)}>
                              Publish
                            </Button>
                          )}
                          <Button size="sm" variant="outline" onClick={() => navigate(`/article/${article.id}`)}>
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => navigate(`/article/${article.id}/edit`)}>
                            <PenSquare className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="destructive" onClick={() => handleDelete(article.id)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="comments">
            <div className="space-y-4">
              {pendingComments.length === 0 ? (
                <Card>
                  <CardContent className="pt-6 text-center">
                    <p className="text-gray-500">No pending comments</p>
                  </CardContent>
                </Card>
              ) : (
                pendingComments.map((comment) => (
                  <Card key={comment.id}>
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="font-medium text-gray-900">{comment.user_name}</span>
                            <span className="text-sm text-gray-500">{formatDate(comment.created_at)}</span>
                          </div>
                          <p className="text-gray-700 mb-2">{comment.content}</p>
                          <Badge variant="secondary">Pending Approval</Badge>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <Button
                            size="sm"
                            variant="default"
                            onClick={() => handleApproveComment(comment.id)}
                          >
                            <Check className="w-4 h-4 mr-1" />
                            Approve
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => handleDeleteComment(comment.id)}
                          >
                            <X className="w-4 h-4 mr-1" />
                            Reject
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default WriterDashboard;
