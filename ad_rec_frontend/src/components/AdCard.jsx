import React from 'react';
import { MousePointerClick, Eye, TrendingUp } from 'lucide-react';

/**
 * 广告卡片组件
 */
export default function AdCard({ ad, position, onAdClick, onAdView }) {
  const handleClick = () => {
    if (onAdClick) {
      onAdClick(ad, position);
    }
  };

  // 生成随机背景色
  const colors = [
    'bg-gradient-to-br from-blue-500 to-blue-600',
    'bg-gradient-to-br from-purple-500 to-purple-600',
    'bg-gradient-to-br from-green-500 to-green-600',
    'bg-gradient-to-br from-orange-500 to-orange-600',
    'bg-gradient-to-br from-pink-500 to-pink-600',
    'bg-gradient-to-br from-indigo-500 to-indigo-600',
  ];
  const colorClass = colors[ad.ad_id % colors.length];

  return (
    <div
      className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
      onClick={handleClick}
    >
      {/* 广告图片区域 (模拟) */}
      <div className={`h-32 ${colorClass} flex items-center justify-center`}>
        <span className="text-white text-4xl font-bold opacity-50">
          AD
        </span>
      </div>

      {/* 广告信息 */}
      <div className="p-4">
        <h3 className="font-semibold text-gray-800 text-sm truncate" title={ad.title}>
          {ad.title}
        </h3>

        {/* 类别标签 */}
        <div className="flex flex-wrap gap-1 mt-2">
          {ad.categories.slice(0, 3).map((cat, idx) => (
            <span
              key={idx}
              className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded"
            >
              {cat}
            </span>
          ))}
        </div>

        {/* 统计数据 */}
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Eye className="w-3 h-3" />
            <span>{ad.impression_count.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <MousePointerClick className="w-3 h-3" />
            <span>{ad.click_count.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            <span>{(ad.ctr * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
