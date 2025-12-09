/**
 * GrowEngine API 服务
 * ==================
 * 统一管理所有后端 API 调用
 */

// API 基础地址配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * 通用请求封装
 */
async function request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Request failed: ${endpoint}`, error);
        throw error;
    }
}

// ==================== 广告计划 API ====================

/**
 * 获取广告计划列表
 */
export async function getCampaigns(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/api/campaigns?${queryString}` : '/api/campaigns';
    return request(endpoint);
}

/**
 * 获取单个广告计划
 */
export async function getCampaign(id) {
    return request(`/api/campaigns/${id}`);
}

/**
 * 创建广告计划
 */
export async function createCampaign(data) {
    return request('/api/campaigns', {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

/**
 * 更新广告计划
 */
export async function updateCampaign(id, data) {
    return request(`/api/campaigns/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

/**
 * 删除广告计划
 */
export async function deleteCampaign(id) {
    return request(`/api/campaigns/${id}`, {
        method: 'DELETE',
    });
}

/**
 * 切换广告计划状态
 */
export async function toggleCampaignStatus(id) {
    return request(`/api/campaigns/${id}/toggle`, {
        method: 'POST',
    });
}

// ==================== 指标 API ====================

/**
 * 获取实时指标
 */
export async function getRealtimeMetrics() {
    return request('/api/metrics/realtime');
}

/**
 * 获取趋势数据
 */
export async function getMetricsTrend(hours = 24) {
    return request(`/api/metrics/trend?hours=${hours}`);
}

// ==================== 竞价 API ====================

/**
 * 计算竞价
 */
export async function calculateBid(campaignId, pValue, userFeatures = {}) {
    return request('/api/bidding/calculate', {
        method: 'POST',
        body: JSON.stringify({
            campaign_id: campaignId,
            p_value: pValue,
            user_features: userFeatures,
        }),
    });
}

/**
 * 模拟竞价过程
 */
export async function simulateBidding(campaignId, steps = 48) {
    return request(`/api/bidding/simulate?campaign_id=${campaignId}&steps=${steps}`, {
        method: 'POST',
    });
}

// ==================== AI 诊断 API ====================

/**
 * 获取智能诊断
 */
export async function getDiagnosis() {
    return request('/api/diagnosis');
}

/**
 * AI 对话
 */
export async function chatWithAI(message) {
    return request(`/api/ai/chat?message=${encodeURIComponent(message)}`, {
        method: 'POST',
    });
}

// ==================== 健康检查 ====================

/**
 * 检查 API 服务状态
 */
export async function healthCheck() {
    return request('/health');
}

export default {
    getCampaigns,
    getCampaign,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    toggleCampaignStatus,
    getRealtimeMetrics,
    getMetricsTrend,
    calculateBid,
    simulateBidding,
    getDiagnosis,
    chatWithAI,
    healthCheck,
};
