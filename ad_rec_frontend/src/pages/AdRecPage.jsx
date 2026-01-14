import React, { useState, useEffect } from 'react';
import { User, RefreshCw, Settings, Sparkles } from 'lucide-react';
import AdList from '../components/AdList';
import ClickAnalytics from '../components/ClickAnalytics';
import * as api from '../services/recApi';

/**
 * 广告推荐页面
 */
export default function AdRecPage() {
  // 状态
  const [visitors, setVisitors] = useState([]);
  const [selectedVisitor, setSelectedVisitor] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [similarAds, setSimilarAds] = useState([]);
  const [selectedAd, setSelectedAd] = useState(null);
  const [stats, setStats] = useState(null);
  const [recentClicks, setRecentClicks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('emb');

  // 加载访客列表
  useEffect(() => {
    loadVisitors();
    loadStats();
  }, []);

  // 当选择访客时加载推荐
  useEffect(() => {
    if (selectedVisitor) {
      loadRecommendations();
    }
  }, [selectedVisitor, model]);

  // 当选择广告时加载相似广告
  useEffect(() => {
    if (selectedAd) {
      loadSimilarAds();
    }
  }, [selectedAd]);

  const loadVisitors = async () => {
    try {
      const data = await api.getVisitors(50);
      setVisitors(data);
      if (data.length > 0) {
        setSelectedVisitor(data[0].visitor_id);
      }
    } catch (error) {
      console.error('Failed to load visitors:', error);
    }
  };

  const loadRecommendations = async () => {
    if (!selectedVisitor) return;
    setLoading(true);
    try {
      const data = await api.getRecommendedAds(selectedVisitor, 20, model);
      setRecommendations(data);
      if (data.length > 0) {
        setSelectedAd(data[0].ad_id);
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSimilarAds = async () => {
    if (!selectedAd) return;
    try {
      const data = await api.getSimilarAds(selectedAd, 5, model);
      setSimilarAds(data);
    } catch (error) {
      console.error('Failed to load similar ads:', error);
    }
  };

  const loadStats = async () => {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleAdClick = async (ad, position) => {
    if (!selectedVisitor) return;

    // 记录点击
    try {
      await api.recordClick(selectedVisitor, ad.ad_id, 1, position, {
        page: 'recommendations',
        model: model
      });

      // 更新本地状态
      setRecentClicks(prev => [
        { visitor_id: selectedVisitor, ad_id: ad.ad_id, clicked: 1 },
        ...prev.slice(0, 9)
      ]);

      // 选中这个广告显示相似广告
      setSelectedAd(ad.ad_id);

      // 刷新统计
      loadStats();
    } catch (error) {
      console.error('Failed to record click:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* 头部 */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-purple-500" />
            <h1 className="text-xl font-bold text-gray-800">Ad Rec System</h1>
          </div>

          {/* 控制区 */}
          <div className="flex items-center gap-4">
            {/* 访客选择 */}
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-500" />
              <select
                value={selectedVisitor || ''}
                onChange={(e) => setSelectedVisitor(parseInt(e.target.value))}
                className="border rounded px-2 py-1 text-sm"
              >
                {visitors.map((v) => (
                  <option key={v.visitor_id} value={v.visitor_id}>
                    Visitor {v.visitor_id}
                  </option>
                ))}
              </select>
            </div>

            {/* 模型选择 */}
            <div className="flex items-center gap-2">
              <Settings className="w-4 h-4 text-gray-500" />
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="border rounded px-2 py-1 text-sm"
              >
                <option value="emb">Embedding</option>
                <option value="neuralcf">NeuralCF</option>
                <option value="default">Default</option>
              </select>
            </div>

            {/* 刷新按钮 */}
            <button
              onClick={loadRecommendations}
              className="flex items-center gap-1 px-3 py-1 bg-purple-500 text-white rounded hover:bg-purple-600 text-sm"
            >
              <RefreshCw className="w-4 h-4" />
              刷新
            </button>
          </div>
        </div>
      </header>

      {/* 主体 */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 推荐列表 */}
          <div className="lg:col-span-3">
            <AdList
              ads={recommendations}
              title={`为访客 ${selectedVisitor} 推荐的广告`}
              onAdClick={handleAdClick}
              loading={loading}
            />

            {/* 相似广告 */}
            {selectedAd && similarAds.length > 0 && (
              <div className="mt-8">
                <AdList
                  ads={similarAds}
                  title={`与广告 ${selectedAd} 相似的广告`}
                  onAdClick={handleAdClick}
                />
              </div>
            )}
          </div>

          {/* 侧边栏 - 统计 */}
          <div className="lg:col-span-1">
            <ClickAnalytics stats={stats} recentClicks={recentClicks} />
          </div>
        </div>
      </main>
    </div>
  );
}
