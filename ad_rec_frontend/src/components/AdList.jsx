import React from 'react';
import AdCard from './AdCard';

/**
 * 广告列表组件
 */
export default function AdList({ ads, title, onAdClick, loading }) {
  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-32 mb-4"></div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-48"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!ads || ads.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>No ads to display</p>
      </div>
    );
  }

  return (
    <div>
      {title && (
        <h2 className="text-lg font-semibold text-gray-800 mb-4">{title}</h2>
      )}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {ads.map((ad, index) => (
          <AdCard
            key={ad.ad_id}
            ad={ad}
            position={index}
            onAdClick={onAdClick}
          />
        ))}
      </div>
    </div>
  );
}
