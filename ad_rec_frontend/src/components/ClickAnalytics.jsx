import React from 'react';
import { BarChart3, MousePointerClick, Eye, TrendingUp } from 'lucide-react';

/**
 * 点击数据分析组件
 */
export default function ClickAnalytics({ stats, recentClicks }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <BarChart3 className="w-5 h-5" />
        点击分析
      </h3>

      {/* 总体统计 */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-3 text-center">
          <Eye className="w-6 h-6 text-blue-500 mx-auto mb-1" />
          <div className="text-2xl font-bold text-blue-600">
            {stats?.total_impressions?.toLocaleString() || 0}
          </div>
          <div className="text-xs text-gray-500">总曝光</div>
        </div>

        <div className="bg-green-50 rounded-lg p-3 text-center">
          <MousePointerClick className="w-6 h-6 text-green-500 mx-auto mb-1" />
          <div className="text-2xl font-bold text-green-600">
            {stats?.total_clicks?.toLocaleString() || 0}
          </div>
          <div className="text-xs text-gray-500">总点击</div>
        </div>

        <div className="bg-purple-50 rounded-lg p-3 text-center">
          <TrendingUp className="w-6 h-6 text-purple-500 mx-auto mb-1" />
          <div className="text-2xl font-bold text-purple-600">
            {((stats?.ctr || 0) * 100).toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500">CTR</div>
        </div>
      </div>

      {/* 最近点击 */}
      {recentClicks && recentClicks.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-600 mb-2">最近点击</h4>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {recentClicks.map((click, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-sm bg-gray-50 rounded p-2"
              >
                <span className="text-gray-600">
                  访客 {click.visitor_id} → 广告 {click.ad_id}
                </span>
                <span className={`px-2 py-0.5 rounded text-xs ${
                  click.clicked ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-500'
                }`}>
                  {click.clicked ? '点击' : '曝光'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
