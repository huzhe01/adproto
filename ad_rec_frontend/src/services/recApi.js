/**
 * 广告推荐 API 服务
 */

const API_BASE = '/api/rec';

/**
 * 获取个性化推荐广告
 */
export async function getRecommendedAds(visitorId, size = 10, model = 'emb') {
  const response = await fetch(
    `${API_BASE}/ads?visitor_id=${visitorId}&size=${size}&model=${model}`
  );
  if (!response.ok) throw new Error('Failed to fetch recommendations');
  return response.json();
}

/**
 * 获取相似广告
 */
export async function getSimilarAds(adId, size = 5, model = 'emb') {
  const response = await fetch(
    `${API_BASE}/similar?ad_id=${adId}&size=${size}&model=${model}`
  );
  if (!response.ok) throw new Error('Failed to fetch similar ads');
  return response.json();
}

/**
 * 获取热门广告
 */
export async function getTopAds(size = 10, sortBy = 'ctr') {
  const response = await fetch(
    `${API_BASE}/top?size=${size}&sort_by=${sortBy}`
  );
  if (!response.ok) throw new Error('Failed to fetch top ads');
  return response.json();
}

/**
 * 获取广告详情
 */
export async function getAd(adId) {
  const response = await fetch(`${API_BASE}/ad/${adId}`);
  if (!response.ok) throw new Error('Failed to fetch ad');
  return response.json();
}

/**
 * 获取访客列表
 */
export async function getVisitors(limit = 100) {
  const response = await fetch(`${API_BASE}/visitors?limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch visitors');
  return response.json();
}

/**
 * 获取访客详情
 */
export async function getVisitor(visitorId) {
  const response = await fetch(`${API_BASE}/visitor/${visitorId}`);
  if (!response.ok) throw new Error('Failed to fetch visitor');
  return response.json();
}

/**
 * 记录点击事件
 */
export async function recordClick(visitorId, adId, clicked = 1, position = 0, context = null) {
  const response = await fetch(`${API_BASE}/click`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      visitor_id: visitorId,
      ad_id: adId,
      clicked,
      position,
      context
    })
  });
  if (!response.ok) throw new Error('Failed to record click');
  return response.json();
}

/**
 * 获取点击统计
 */
export async function getStats() {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

/**
 * 获取所有类别
 */
export async function getCategories() {
  const response = await fetch(`${API_BASE}/categories`);
  if (!response.ok) throw new Error('Failed to fetch categories');
  return response.json();
}

/**
 * 健康检查
 */
export async function healthCheck() {
  const response = await fetch('/health');
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}
