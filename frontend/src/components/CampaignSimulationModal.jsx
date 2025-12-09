import React, { useState, useEffect, useRef } from 'react';
import {
    X,
    Play,
    Pause,
    RotateCcw,
    TrendingUp,
    DollarSign,
    Target,
    Award
} from 'lucide-react';
import {
    ComposedChart,
    Line,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    ReferenceLine,
    Area
} from 'recharts';
import * as api from '../services/api';

export default function CampaignSimulationModal({ campaign, onClose }) {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);
    const [currentStep, setCurrentStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const playIntervalRef = useRef(null);

    useEffect(() => {
        async function fetchData() {
            try {
                const result = await api.simulateBidding(campaign.id);
                setData(result);
                setLoading(false);
            } catch (err) {
                console.error("Simulation failed:", err);
                setError(err.message || '加载失败');
                setLoading(false);
            }
        }
        fetchData();
    }, [campaign.id]);

    useEffect(() => {
        if (isPlaying) {
            playIntervalRef.current = setInterval(() => {
                setCurrentStep(prev => {
                    if (data && prev < data.history.length - 1) {
                        return prev + 1;
                    } else {
                        setIsPlaying(false);
                        return prev;
                    }
                });
            }, 500); // 500ms per step
        } else {
            clearInterval(playIntervalRef.current);
        }
        return () => clearInterval(playIntervalRef.current);
    }, [isPlaying, data]);

    const handleSliderChange = (e) => {
        setCurrentStep(parseInt(e.target.value));
        setIsPlaying(false);
    };

    const handlePlayPause = () => {
        if (isPlaying) {
            setIsPlaying(false);
        } else {
            if (data && currentStep >= data.history.length - 1) {
                setCurrentStep(0);
            }
            setIsPlaying(true);
        }
    };

    const handleReset = () => {
        setIsPlaying(false);
        setCurrentStep(0);
    };

    if (loading) {
        return (
            <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center backdrop-blur-sm">
                <div className="bg-white p-8 rounded-2xl shadow-2xl flex flex-col items-center animate-in fade-in zoom-in duration-300">
                    <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                    <p className="text-slate-600 font-medium">正在运行 OnlineLp 竞价模拟...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center backdrop-blur-sm p-4">
                <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-in fade-in zoom-in duration-300 text-center">
                    <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <X className="w-6 h-6 text-red-600" />
                    </div>
                    <h3 className="text-lg font-bold text-slate-800 mb-2">模拟失败</h3>
                    <p className="text-slate-500 mb-6">{error}</p>
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg font-medium transition-colors"
                    >
                        关闭
                    </button>
                </div>
            </div>
        );
    }

    if (!data) return null;

    const currentData = data.history[currentStep];
    const maxSteps = data.history.length - 1;

    // Custom Tick for X-Axis to reduce clutter
    const renderCustomAxisTick = ({ x, y, payload }) => {
        if (payload.value % 5 !== 0) return null;
        return (
            <g transform={`translate(${x},${y})`}>
                <text x={0} y={0} dy={16} textAnchor="middle" fill="#94a3b8" fontSize={12}>
                    {payload.value}
                </text>
            </g>
        );
    };

    return (
        <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center backdrop-blur-sm p-4 overflow-hidden">
            <div className="bg-white rounded-2xl shadow-2xl w-full max-w-6xl max-h-[90vh] flex flex-col animate-in fade-in zoom-in duration-300">

                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                    <div>
                        <h2 className="text-xl font-bold text-slate-800 flex items-center">
                            <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                            竞价模拟可视化: {campaign.name}
                        </h2>
                        <p className="text-sm text-slate-500 mt-1">
                            基于 OnlineLp 算法还原历史竞价过程 · 步长: {currentStep}/{maxSteps}
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-600"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content - Scrollable */}
                <div className="flex-1 overflow-y-auto p-6 bg-slate-50/50">

                    {/* 1. Metrics Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-slate-500 font-medium">累计消耗</span>
                                <DollarSign className="w-4 h-4 text-emerald-500" />
                            </div>
                            <div className="text-2xl font-bold text-slate-900">
                                ¥ {currentData.total_cost.toLocaleString()}
                            </div>
                            <div className="mt-2 w-full bg-slate-100 rounded-full h-1.5">
                                <div
                                    className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
                                    style={{ width: `${currentData.budget_percentage}%` }}
                                ></div>
                            </div>
                            <div className="mt-1 text-xs text-slate-400 flex justify-between">
                                <span>预算进度</span>
                                <span>{currentData.budget_percentage}%</span>
                            </div>
                        </div>

                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-slate-500 font-medium">累计转化 (CV)</span>
                                <Target className="w-4 h-4 text-purple-500" />
                            </div>
                            <div className="text-2xl font-bold text-slate-900">
                                {currentData.total_conversions}
                            </div>
                            <div className="mt-2 text-xs text-purple-600 bg-purple-50 px-2 py-0.5 rounded inline-block">
                                Step Win: +{currentData.conversions}
                            </div>
                        </div>

                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-slate-500 font-medium">实际 CPA</span>
                                <div className="text-xs font-mono text-slate-400">Constraint: {data.meta.cpa_constraint}</div>
                            </div>
                            <div className="text-2xl font-bold text-slate-900">
                                ¥ {currentData.real_cpa}
                            </div>
                            <div className={`mt-2 text-xs px-2 py-0.5 rounded inline-block ${currentData.real_cpa > data.meta.cpa_constraint ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600'}`}>
                                {currentData.real_cpa > data.meta.cpa_constraint ? '高于约束' : '达标'}
                            </div>
                        </div>

                        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-sm text-slate-500 font-medium">累计获胜 (Wins)</span>
                                <Award className="w-4 h-4 text-blue-500" />
                            </div>
                            <div className="text-2xl font-bold text-slate-900">
                                {currentData.total_wins}
                            </div>
                            <div className="mt-2 text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded inline-block">
                                Win Rate: {(currentData.wins / (currentData.traffic || 1) * 100).toFixed(1)}%
                            </div>
                        </div>
                    </div>

                    {/* 2. Controls */}
                    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm mb-6 flex items-center gap-4">
                        <button
                            onClick={handlePlayPause}
                            className={`flex items-center px-4 py-2 rounded-lg font-medium transition-all ${isPlaying
                                ? 'bg-amber-100 text-amber-700 hover:bg-amber-200'
                                : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md shadow-blue-200'
                                }`}
                        >
                            {isPlaying ? <Pause className="w-4 h-4 mr-2" /> : <Play className="w-4 h-4 mr-2" />}
                            {isPlaying ? '暂停演示' : '开始回放'}
                        </button>

                        <button
                            onClick={handleReset}
                            className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                            title="重置"
                        >
                            <RotateCcw className="w-4 h-4" />
                        </button>

                        <div className="flex-1 px-4">
                            <input
                                type="range"
                                min="0"
                                max={maxSteps}
                                value={currentStep}
                                onChange={handleSliderChange}
                                className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                            />
                            <div className="flex justify-between text-xs text-slate-400 mt-1">
                                <span>Start</span>
                                <span>Step {currentStep}</span>
                                <span>End</span>
                            </div>
                        </div>
                    </div>

                    {/* 3. Charts Grid */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-6">

                        {/* Chart 1: Cost & Step Cost */}
                        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                            <h3 className="text-sm font-bold text-slate-800 mb-4 border-l-4 border-emerald-500 pl-3">
                                消耗趋势 (Cost Trend)
                            </h3>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <ComposedChart data={data.history}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="step" tick={renderCustomAxisTick} axisLine={false} tickLine={false} />
                                        <YAxis yAxisId="total" orientation="left" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} label={{ value: 'Total', angle: -90, position: 'insideLeft' }} />
                                        <YAxis yAxisId="step" orientation="right" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} label={{ value: 'Step', angle: 90, position: 'insideRight' }} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                            labelStyle={{ color: '#64748b' }}
                                        />
                                        <Legend />
                                        <Area type="monotone" yAxisId="total" dataKey="total_cost" fill="rgba(16, 185, 129, 0.1)" stroke="#10b981" strokeWidth={2} name="Total Cost" />
                                        <Bar yAxisId="step" dataKey="cost" fill="#34d399" opacity={0.4} name="Step Cost" barSize={8} />
                                        <ReferenceLine x={currentStep} stroke="#f59e0b" strokeDasharray="3 3" />
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Chart 2: Alpha & Real CPA */}
                        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                            <h3 className="text-sm font-bold text-slate-800 mb-4 border-l-4 border-amber-500 pl-3">
                                出价系数与 CPA (Alpha & CPA)
                            </h3>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <ComposedChart data={data.history}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="step" tick={renderCustomAxisTick} axisLine={false} tickLine={false} />
                                        <YAxis yAxisId="cpa" orientation="left" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                                        <YAxis yAxisId="alpha" orientation="right" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} domain={['dataMin', 'dataMax']} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                        />
                                        <Legend />
                                        <Line yAxisId="cpa" type="monotone" dataKey="real_cpa" stroke="#6366f1" strokeWidth={2} dot={false} name="Real CPA" />
                                        <Line yAxisId="alpha" type="monotone" dataKey="alpha" stroke="#f59e0b" strokeWidth={2} dot={false} name="Alpha (Bid)" />
                                        <ReferenceLine yAxisId="cpa" y={data.meta.cpa_constraint} stroke="#ef4444" strokeDasharray="3 3" label="Limit" />
                                        <ReferenceLine x={currentStep} stroke="#f59e0b" strokeDasharray="3 3" />
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Chart 3: Wins & Conversions */}
                        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm lg:col-span-2">
                            <h3 className="text-sm font-bold text-slate-800 mb-4 border-l-4 border-blue-500 pl-3">
                                转化与获胜 (Step Level)
                            </h3>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <ComposedChart data={data.history}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                        <XAxis dataKey="step" tick={renderCustomAxisTick} axisLine={false} tickLine={false} />
                                        <YAxis orientation="left" axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                                        <Tooltip
                                            contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                                        />
                                        <Legend />
                                        <Line type="monotone" dataKey="wins" stroke="#3b82f6" strokeWidth={2} dot={false} name="Wins" />
                                        <Bar dataKey="conversions" fill="#a855f7" name="Conversions" barSize={8} />
                                        <ReferenceLine x={currentStep} stroke="#f59e0b" strokeDasharray="3 3" />
                                    </ComposedChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                    </div>
                </div>
            </div>
        </div>
    );
}
