import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  BarChart3,
  Users,
  Layers,
  Zap,
  Settings,
  Bell,
  Plus,
  UploadCloud,
  Target,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  MoreHorizontal,
  ChevronRight,
  HelpCircle,
  Play,
  Pause,
  Filter,
  Download,
  BrainCircuit,
  MousePointerClick,
  DollarSign,
  ShoppingBag,
  Edit2,
  Copy,
  Trash2,
  Eye,
  RefreshCw,
  Wallet,
  Wrench
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Mock Data for Charts (Keep existing)
const performanceData = [
  { time: '00:00', spend: 1200, gmv: 4500, roas: 3.75 },
  { time: '04:00', spend: 800, gmv: 3200, roas: 4.0 },
  { time: '08:00', spend: 2400, gmv: 12000, roas: 5.0 },
  { time: '12:00', spend: 3500, gmv: 15000, roas: 4.28 },
  { time: '16:00', spend: 4100, gmv: 18000, roas: 4.39 },
  { time: '20:00', spend: 5800, gmv: 26000, roas: 4.48 },
  { time: '23:59', spend: 3200, gmv: 11000, roas: 3.43 },
];

// Components (Keep existing MetricCard & DiagnosticCard)
const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex items-center w-full px-4 py-3 mb-1 text-sm font-medium transition-colors rounded-lg ${active
      ? 'bg-blue-50 text-blue-600'
      : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
      }`}
  >
    <Icon className="w-5 h-5 mr-3" />
    {label}
  </button>
);

const MetricCard = ({ title, value, change, trend, icon: Icon, colorClass }) => (
  <div className="p-5 bg-white border border-slate-100 rounded-xl shadow-sm hover:shadow-md transition-shadow">
    <div className="flex items-center justify-between mb-4">
      <div className={`p-2 rounded-lg ${colorClass}`}>
        <Icon className="w-5 h-5" />
      </div>
      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${trend === 'up' ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'
        }`}>
        {change}
      </span>
    </div>
    <div className="text-slate-500 text-sm font-medium mb-1">{title}</div>
    <div className="text-2xl font-bold text-slate-900">{value}</div>
  </div>
);

const DiagnosticCard = ({ type, title, desc, action }) => (
  <div className="flex items-start p-4 mb-3 border border-slate-100 rounded-lg bg-slate-50 hover:bg-white hover:border-blue-100 transition-colors">
    <div className="mt-1 mr-3">
      {type === 'warning' ? (
        <AlertCircle className="w-5 h-5 text-amber-500" />
      ) : (
        <Zap className="w-5 h-5 text-blue-500" />
      )}
    </div>
    <div className="flex-1">
      <h4 className="text-sm font-semibold text-slate-800 mb-1">{title}</h4>
      <p className="text-xs text-slate-500 mb-3 leading-relaxed">{desc}</p>
      <button className="text-xs font-medium text-blue-600 hover:text-blue-700 flex items-center">
        {action} <ChevronRight className="w-3 h-3 ml-1" />
      </button>
    </div>
  </div>
);

// Initial Campaign Data with detailed DSP metrics
const initialCampaigns = [
  {
    id: 101,
    name: '新品推广_冬季大衣_V1',
    status: 'active',
    budget: 5000,
    bid: 45.00,
    spend: 3200.50,
    impressions: 85200,
    clicks: 2130,
    ctr: 2.50,
    cvr: 3.2,
    cpa: 47.06,
    roi: 3.8,
    learningStage: 'passed', // learning, passed, failed
    bidType: 'oCPM'
  },
  {
    id: 102,
    name: '双11预热_美妆礼盒_自动出价',
    status: 'learning',
    budget: 2000,
    bid: 120.00,
    spend: 450.00,
    impressions: 12000,
    clicks: 180,
    ctr: 1.50,
    cvr: 1.1,
    cpa: 225.00,
    roi: 0.8,
    learningStage: 'learning',
    bidType: 'NOBID'
  },
  {
    id: 103,
    name: '库存清仓_长尾流量_003',
    status: 'paused',
    budget: 1000,
    bid: 20.00,
    spend: 890.00,
    impressions: 150000,
    clicks: 4500,
    ctr: 3.00,
    cvr: 0.5,
    cpa: 39.55,
    roi: 1.2,
    learningStage: 'failed',
    bidType: 'CPC'
  }
];

export default function AdPlatform() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [campaigns, setCampaigns] = useState(initialCampaigns);
  const [editingId, setEditingId] = useState(null); // Track which row is being edited
  const [tempBid, setTempBid] = useState(0);

  // Toggle Campaign Status
  const toggleStatus = (id) => {
    setCampaigns(campaigns.map(c => {
      if (c.id === id) {
        const newStatus = c.status === 'active' || c.status === 'learning' ? 'paused' : 'active';
        return { ...c, status: newStatus };
      }
      return c;
    }));
  };

  // Start Editing Bid
  const startEditBid = (campaign) => {
    setEditingId(campaign.id);
    setTempBid(campaign.bid);
  };

  // Save Bid
  const saveBid = (id) => {
    setCampaigns(campaigns.map(c => c.id === id ? { ...c, bid: Number(tempBid) } : c));
    setEditingId(null);
  };

  // Render Learning Stage Badge
  const getStageBadge = (stage) => {
    switch (stage) {
      case 'passed':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-green-100 text-green-700 border border-green-200">学习成功</span>;
      case 'learning':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-blue-100 text-blue-700 border border-blue-200 animate-pulse">冷启动中</span>;
      case 'failed':
        return <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-red-100 text-red-700 border border-red-200">学习失败</span>;
      default:
        return null;
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans text-slate-900">
      {/* Sidebar (Unchanged) */}
      <aside className="w-64 bg-white border-r border-slate-200 hidden md:flex flex-col z-10">
        <div className="p-6 flex items-center">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
            <TrendingUp className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-slate-900">GrowEngine</span>
        </div>

        <div className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 mt-2">
            投放管理
          </div>
          <SidebarItem
            icon={LayoutDashboard}
            label="综述看板"
            active={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          />
          <SidebarItem icon={Layers} label="计划管理" active={activeTab === 'campaigns'} onClick={() => setActiveTab('campaigns')} />
          <SidebarItem icon={UploadCloud} label="素材中心" active={activeTab === 'creatives'} onClick={() => setActiveTab('creatives')} />
          <SidebarItem icon={Users} label="人群资产" active={activeTab === 'audience'} onClick={() => setActiveTab('audience')} />

          <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 mt-6">
            财务与工具
          </div>
          <SidebarItem icon={Wallet} label="财务管理" active={activeTab === 'finance'} onClick={() => setActiveTab('finance')} />
          <SidebarItem icon={Wrench} label="投放工具" active={activeTab === 'tools'} onClick={() => setActiveTab('tools')} />

          <div className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 mt-6">
            数据与设置
          </div>
          <SidebarItem icon={BarChart3} label="报表分析" active={activeTab === 'reports'} onClick={() => setActiveTab('reports')} />
          <SidebarItem icon={BrainCircuit} label="智能诊断" active={activeTab === 'diagnosis'} onClick={() => setActiveTab('diagnosis')} />
          <SidebarItem icon={Settings} label="系统设置" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
        </div>

        <div className="p-4 border-t border-slate-100">
          <div className="flex items-center">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="User" className="w-9 h-9 rounded-full bg-slate-100" />
            <div className="ml-3">
              <p className="text-sm font-medium text-slate-700">Admin User</p>
              <p className="text-xs text-slate-500">ByteDance Ads</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navigation (Unchanged) */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-20">
          <div className="flex items-center flex-1">
            <h1 className="text-xl font-semibold text-slate-800">
              {activeTab === 'dashboard' ? '投放概览' :
                activeTab === 'campaigns' ? '广告计划' : '素材库'}
            </h1>
            <span className="ml-4 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              系统运行正常
            </span>
          </div>

          <div className="flex items-center space-x-4">
            <button className="p-2 text-slate-400 hover:text-slate-600 transition-colors relative">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-white"></span>
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm shadow-blue-200"
            >
              <Plus className="w-4 h-4 mr-2" />
              新建投放
            </button>
          </div>
        </header>

        {/* Dashboard Content */}
        <div className="flex-1 overflow-auto p-6 scroll-smooth">

          {/* 1. Metrics (Unchanged) */}
          <section className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold text-slate-800 flex items-center">
                实时数据
                <span className="ml-2 text-xs font-normal text-slate-500 bg-slate-100 px-2 py-1 rounded">更新于 1 分钟前</span>
              </h2>
              <div className="flex space-x-2">
                <select className="text-sm border-slate-200 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500">
                  <option>今天</option>
                  <option>昨天</option>
                  <option>过去7天</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
              <MetricCard
                title="总消耗 (Cost)"
                value="¥ 21,450"
                change="+12.5%"
                trend="up"
                icon={DollarSign}
                colorClass="bg-blue-100 text-blue-600"
              />
              <MetricCard
                title="GMV (成交额)"
                value="¥ 98,320"
                change="+24.2%"
                trend="up"
                icon={ShoppingBag}
                colorClass="bg-purple-100 text-purple-600"
              />
              <MetricCard
                title="ROI (投入产出比)"
                value="4.58"
                change="-1.2%"
                trend="down"
                icon={TrendingUp}
                colorClass="bg-orange-100 text-orange-600"
              />
              <MetricCard
                title="点击率 (CTR)"
                value="3.2%"
                change="+0.4%"
                trend="up"
                icon={MousePointerClick}
                colorClass="bg-emerald-100 text-emerald-600"
              />
            </div>
          </section>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {/* 2. Chart (Unchanged) */}
            <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-base font-semibold text-slate-800">消耗与GMV趋势对比</h3>
                <div className="flex items-center space-x-4 text-sm text-slate-500">
                  <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-blue-500 mr-2"></span>消耗</span>
                  <span className="flex items-center"><span className="w-3 h-3 rounded-full bg-purple-500 mr-2"></span>GMV</span>
                </div>
              </div>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorGmv" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.1} />
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      itemStyle={{ fontSize: '12px' }}
                    />
                    <Area type="monotone" dataKey="gmv" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorGmv)" />
                    <Area type="monotone" dataKey="spend" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorSpend)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 3. Diagnosis (Unchanged) */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <BrainCircuit className="w-5 h-5 text-indigo-600" />
                  <h3 className="text-base font-semibold text-slate-800">智能经营诊断</h3>
                </div>
                <span className="text-xs font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">3项建议</span>
              </div>

              <div className="flex-1 overflow-y-auto pr-1">
                <DiagnosticCard
                  type="warning"
                  title="起量困难预警"
                  desc="计划 [双11-爆款A] 出价竞争力低于行业 Top 20%，导致展现量受限。建议结合 oCPM 策略提价。"
                  action="一键提价 +10%"
                />
                <DiagnosticCard
                  type="opportunity"
                  title="高潜人群未覆盖"
                  desc="系统发现 [精致妈妈] 人群在同类商品中转化率极高，但在当前投放中占比不足 5%。"
                  action="添加定向包"
                />
                <DiagnosticCard
                  type="warning"
                  title="素材疲劳度高"
                  desc="视频素材 [Video_003] 点击率连续 3 天下滑，建议更换前 3 秒黄金帧或新增素材。"
                  action="前往素材中心"
                />
              </div>
              <div className="mt-4 pt-4 border-t border-slate-100">
                <button className="w-full py-2 text-sm text-slate-600 hover:text-slate-900 font-medium text-center">
                  查看全部诊断报告
                </button>
              </div>
            </div>
          </div>

          {/* 4. Active Campaigns Table (IMPROVED) */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden mb-12">
            <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h3 className="text-base font-semibold text-slate-800">在投计划列表</h3>
                <p className="text-xs text-slate-500 mt-1">实时监控所有推广计划的转化效果与学习状态。</p>
              </div>
              <div className="flex space-x-3">
                <div className="relative">
                  <input type="text" placeholder="搜索计划ID或名称" className="pl-9 pr-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:border-blue-500 w-48" />
                  <div className="absolute left-3 top-2 text-slate-400"><Filter className="w-3 h-3" /></div>
                </div>
                <button className="flex items-center px-3 py-1.5 text-sm font-medium text-slate-600 bg-slate-50 rounded hover:bg-slate-100 border border-slate-200">
                  <RefreshCw className="w-3 h-3 mr-2" /> 刷新
                </button>
                <button className="flex items-center px-3 py-1.5 text-sm font-medium text-slate-600 bg-slate-50 rounded hover:bg-slate-100 border border-slate-200">
                  <Download className="w-3 h-3 mr-2" /> 导出
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs uppercase text-slate-500 font-medium">
                  <tr>
                    <th className="px-4 py-3 w-16 text-center">开关</th>
                    <th className="px-4 py-3 min-w-[200px]">计划名称 / ID</th>
                    <th className="px-4 py-3 text-center">系统状态</th>
                    <th className="px-4 py-3">出价 (CNY)</th>
                    <th className="px-4 py-3">消耗</th>
                    <th className="px-4 py-3">展现 / 点击</th>
                    <th className="px-4 py-3">CTR / CVR</th>
                    <th className="px-4 py-3">CPA</th>
                    <th className="px-4 py-3">ROI</th>
                    <th className="px-4 py-3 text-right">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {campaigns.map((item) => (
                    <tr key={item.id} className={`hover:bg-slate-50 transition-colors ${item.status === 'paused' ? 'bg-slate-50/50 grayscale-[0.5]' : ''}`}>
                      {/* Toggle Switch */}
                      <td className="px-4 py-4 text-center">
                        <button
                          onClick={() => toggleStatus(item.id)}
                          className={`w-10 h-5 rounded-full relative transition-colors duration-200 ease-in-out focus:outline-none ${item.status === 'paused' ? 'bg-slate-300' : 'bg-blue-600'
                            }`}
                        >
                          <span
                            className={`absolute top-1 left-1 bg-white w-3 h-3 rounded-full shadow-sm transition-transform duration-200 ease-in-out ${item.status === 'paused' ? 'translate-x-0' : 'translate-x-5'
                              }`}
                          />
                        </button>
                      </td>

                      {/* Name & ID */}
                      <td className="px-4 py-4">
                        <div className="font-medium text-slate-900 truncate max-w-[200px]" title={item.name}>
                          {item.name}
                        </div>
                        <div className="text-[10px] text-slate-400 mt-1 font-mono flex items-center">
                          ID: {item.id}
                          <span className="ml-2 px-1 border border-slate-200 rounded bg-white text-slate-500">{item.bidType}</span>
                        </div>
                      </td>

                      {/* Learning Status */}
                      <td className="px-4 py-4 text-center">
                        {getStageBadge(item.learningStage)}
                        {item.status === 'paused' && <div className="text-[10px] text-slate-400 mt-1">已暂停</div>}
                      </td>

                      {/* Bid (Editable) */}
                      <td className="px-4 py-4">
                        {editingId === item.id ? (
                          <div className="flex items-center space-x-1">
                            <input
                              type="number"
                              value={tempBid}
                              onChange={(e) => setTempBid(e.target.value)}
                              className="w-16 px-1 py-1 text-xs border border-blue-400 rounded focus:outline-none"
                              autoFocus
                            />
                            <button onClick={() => saveBid(item.id)} className="text-green-600 hover:text-green-800"><CheckCircle2 className="w-4 h-4" /></button>
                          </div>
                        ) : (
                          <div className="flex items-center group cursor-pointer" onClick={() => startEditBid(item)}>
                            <span className="font-medium">¥ {item.bid.toFixed(2)}</span>
                            <Edit2 className="w-3 h-3 text-slate-300 ml-2 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </div>
                        )}
                      </td>

                      {/* Spend */}
                      <td className="px-4 py-4 font-mono text-slate-700">¥ {item.spend.toLocaleString()}</td>

                      {/* Imp/Click */}
                      <td className="px-4 py-4 text-xs">
                        <div className="text-slate-700 font-medium">{item.impressions.toLocaleString()} <span className="text-slate-400 font-normal">展</span></div>
                        <div className="text-slate-500 mt-1">{item.clicks.toLocaleString()} <span className="text-slate-400 font-normal">点</span></div>
                      </td>

                      {/* CTR/CVR */}
                      <td className="px-4 py-4 text-xs">
                        <div className={`${item.ctr > 2 ? 'text-green-600' : 'text-slate-600'} font-medium`}>{item.ctr}% <span className="text-slate-400 font-normal">CTR</span></div>
                        <div className="text-slate-500 mt-1">{item.cvr}% <span className="text-slate-400 font-normal">CVR</span></div>
                      </td>

                      {/* CPA */}
                      <td className="px-4 py-4 font-medium text-slate-700">¥ {item.cpa}</td>

                      {/* ROI */}
                      <td className="px-4 py-4">
                        <span className={`font-bold ${item.roi >= 3 ? 'text-emerald-600' : item.roi < 1 ? 'text-red-500' : 'text-amber-600'}`}>
                          {item.roi}
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <button className="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded" title="查看详情">
                            <Eye className="w-4 h-4" />
                          </button>
                          <button className="p-1 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded" title="复制计划">
                            <Copy className="w-4 h-4" />
                          </button>
                          <button className="p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded" title="删除">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {/* Pagination Footer */}
            <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
              <span>共 128 条计划，显示 1-3</span>
              <div className="flex space-x-2">
                <button className="px-2 py-1 bg-white border border-slate-200 rounded disabled:opacity-50" disabled>上一页</button>
                <button className="px-2 py-1 bg-white border border-slate-200 rounded hover:bg-slate-50">下一页</button>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Create Modal (Unchanged) */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                <h2 className="text-xl font-bold text-slate-800">新建广告投放计划</h2>
                <p className="text-sm text-slate-500 mt-1">配置素材、定向人群与出价策略，系统将自动预估效果。</p>
              </div>
              <button
                onClick={() => setShowCreateModal(false)}
                className="text-slate-400 hover:text-slate-600 p-2 hover:bg-slate-100 rounded-full"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-8 bg-slate-50/30">
              <div className="grid grid-cols-12 gap-8">
                {/* Form Side */}
                <div className="col-span-8 space-y-8">

                  {/* Step 1: Material */}
                  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="font-semibold text-slate-900 flex items-center mb-4">
                      <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs mr-2">1</span>
                      创意素材上传
                    </h3>
                    <div className="border-2 border-dashed border-slate-200 rounded-lg p-8 flex flex-col items-center justify-center text-center hover:border-blue-400 hover:bg-blue-50/30 transition-colors cursor-pointer">
                      <UploadCloud className="w-10 h-10 text-blue-500 mb-3" />
                      <p className="text-sm font-medium text-slate-700">点击上传视频或图片</p>
                      <p className="text-xs text-slate-400 mt-1">支持 MP4, PNG, JPG (最大 500MB)</p>
                    </div>
                  </div>

                  {/* Step 2: Targeting */}
                  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="font-semibold text-slate-900 flex items-center mb-4">
                      <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs mr-2">2</span>
                      人群定向设置
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">投放目标</label>
                        <div className="grid grid-cols-3 gap-3">
                          {['商品购买', '表单提交', '应用下载'].map(opt => (
                            <button key={opt} className={`py-2 px-3 text-sm rounded-lg border ${opt === '商品购买' ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-slate-200 hover:border-slate-300'}`}>
                              {opt}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">智能人群包</label>
                        <div className="flex flex-wrap gap-2">
                          {['近30天浏览未购买', '高净值人群', 'Lookalike 拓展'].map(tag => (
                            <span key={tag} className="inline-flex items-center px-3 py-1 rounded-full text-xs bg-slate-100 text-slate-600 border border-slate-200 cursor-pointer hover:bg-slate-200">
                              {tag} <Plus className="w-3 h-3 ml-1" />
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Step 3: Bidding */}
                  <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                    <h3 className="font-semibold text-slate-900 flex items-center mb-4">
                      <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs mr-2">3</span>
                      出价与预算 (Smart Bidding)
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">日预算 (¥)</label>
                        <input type="number" className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none" defaultValue={5000} />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">目标转化出价 (oCPM)</label>
                        <input type="number" className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none" defaultValue={65} />
                      </div>
                    </div>
                    <div className="mt-3 flex items-start gap-2 p-3 bg-emerald-50 rounded-lg text-xs text-emerald-800">
                      <CheckCircle2 className="w-4 h-4 mt-0.5 text-emerald-600" />
                      <p>系统预测：当前出价具有较强竞争力，预计覆盖 85% 目标流量。建议开启“最大转化量”策略以平滑冷启动。</p>
                    </div>
                  </div>

                </div>

                {/* Preview Side */}
                <div className="col-span-4">
                  <div className="sticky top-0 space-y-4">
                    {/* Mobile Preview */}
                    <div className="bg-slate-900 rounded-[2rem] border-[8px] border-slate-800 overflow-hidden shadow-2xl mx-auto w-64 h-[500px] relative">
                      <div className="absolute top-0 w-full h-full bg-black opacity-40 z-10 flex items-center justify-center">
                        <Play className="w-12 h-12 text-white opacity-80" />
                      </div>
                      {/* Mock App Interface */}
                      <div className="bg-gray-100 w-full h-full">
                        <div className="h-full bg-cover bg-center" style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80)' }}>
                          <div className="absolute bottom-0 w-full p-4 bg-gradient-to-t from-black/80 to-transparent z-20">
                            <div className="text-white text-sm font-bold mb-1">品牌名称 Brand</div>
                            <div className="text-white/90 text-xs mb-3">冬季保暖时尚大衣，限时5折优惠...</div>
                            <button className="w-full bg-blue-600 text-white py-2 rounded text-xs font-bold">立即购买</button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                      <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">预估效果</h4>
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-slate-600">预估展现</span>
                        <span className="text-sm font-bold text-slate-900">120,000+</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-slate-600">预估转化</span>
                        <span className="text-sm font-bold text-slate-900">350 - 480</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-100 bg-white flex justify-end gap-3 rounded-b-2xl">
              <button
                onClick={() => setShowCreateModal(false)}
                className="px-6 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
              >
                存草稿
              </button>
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  alert("计划已提交审核！");
                }}
                className="px-6 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-md shadow-blue-200 transition-colors flex items-center"
              >
                <Zap className="w-4 h-4 mr-2" />
                立即投放
              </button>
            </div>

          </div>
        </div>
      )}
    </div>
  );
}