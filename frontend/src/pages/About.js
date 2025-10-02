import React, { useState, useEffect } from 'react';
import { getSetting } from '../services/api';
import { Card, CardContent, CardHeader } from '../components/ui/card';

const About = () => {
  const [aboutContent, setAboutContent] = useState('');

  useEffect(() => {
    loadAboutContent();
  }, []);

  const loadAboutContent = async () => {
    try {
      const setting = await getSetting('about_us');
      setAboutContent(setting.value || 'Welcome to BlogHub - Your platform for sharing amazing stories!');
    } catch (error) {
      console.error('Failed to load about content:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">About Us</h1>
          <p className="text-xl text-gray-600">
            Connecting writers and readers through great content
          </p>
        </div>

        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {aboutContent}
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <Card>
            <CardHeader>
              <h3 className="text-xl font-bold text-center">Our Mission</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 text-center">
                To empower writers and provide readers with high-quality, engaging content
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-xl font-bold text-center">Our Vision</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 text-center">
                To be the go-to platform for discovering and sharing amazing stories
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-xl font-bold text-center">Our Values</h3>
            </CardHeader>
            <CardContent>
              <p className="text-gray-600 text-center">
                Quality content, community engagement, and creative expression
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default About;
