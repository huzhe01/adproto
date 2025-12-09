// 检查数据是否存在
if (typeof window.SIMULATION_DATA === 'undefined') {
    alert("未找到数据文件 data/simulation_data.js。请先运行 Python 生成脚本。");
}

const META = window.SIMULATION_DATA.meta;
const HISTORY = window.SIMULATION_DATA.history;
const TOTAL_STEPS = HISTORY.length - 1; // 0-based index max

// 初始化 DOM 元素
const elAdvertiserInfo = document.getElementById('advertiser-info');
const elStatCost = document.getElementById('stat-cost');
const elProgressBudget = document.getElementById('progress-budget');
const elStatBudgetPct = document.getElementById('stat-budget-pct');
const elStatCv = document.getElementById('stat-cv');
const elStatCpa = document.getElementById('stat-cpa');
const elStatCpaConstraint = document.getElementById('stat-cpa-constraint');
const elStatWins = document.getElementById('stat-wins');
const elSlider = document.getElementById('time-slider');
const elCurrentStepDisplay = document.getElementById('current-step-display');
const btnPlay = document.getElementById('btn-play');

// 设置静态信息
elAdvertiserInfo.textContent = `Advertiser: ${META.advertiser_number} | Category: ${META.category} | Budget: ${META.initial_budget}`;
elStatCpaConstraint.textContent = META.cpa_constraint.toFixed(2);
elSlider.max = TOTAL_STEPS;

// 准备图表数据
const xData = HISTORY.map(h => h.step);
const sAlpha = HISTORY.map(h => h.alpha);
const sRealCpa = HISTORY.map(h => h.real_cpa);
const sTotalCost = HISTORY.map(h => h.total_cost);
const sStepCost = HISTORY.map(h => h.step_cost);
const sStepConversion = HISTORY.map(h => h.step_conversion);
const sStepWins = HISTORY.map(h => h.step_wins);

// 初始化 ECharts
const chartAlpha = echarts.init(document.getElementById('chart-alpha'));
const chartCost = echarts.init(document.getElementById('chart-cost'));
const chartWins = echarts.init(document.getElementById('chart-wins'));

// 通用配置
const commonGrid = { left: '3%', right: '4%', bottom: '3%', containLabel: true };
const commonTooltip = { trigger: 'axis', axisPointer: { type: 'cross' } };

// 1. Alpha & Real CPA Chart
const optionAlpha = {
    tooltip: commonTooltip,
    legend: { data: ['Alpha (Bid Price Scale)', 'Real CPA'] },
    grid: commonGrid,
    xAxis: { type: 'category', boundaryGap: false, data: xData },
    yAxis: { type: 'value' },
    series: [
        {
            name: 'Alpha (Bid Price Scale)',
            type: 'line',
            data: sAlpha,
            smooth: true,
            lineStyle: { width: 3, color: '#ffc107' },
            itemStyle: { color: '#ffc107' }
        },
        {
            name: 'Real CPA',
            type: 'line',
            data: sRealCpa,
            smooth: true,
            lineStyle: { type: 'dashed', color: '#17a2b8' },
            itemStyle: { color: '#17a2b8' },
            markLine: {
                data: [{ yAxis: META.cpa_constraint, name: 'CPA Constraint' }],
                lineStyle: { color: 'red' }
            }
        }
    ]
};

// 2. Cost Chart
const optionCost = {
    tooltip: commonTooltip,
    legend: { data: ['Total Cost', 'Step Cost'] },
    grid: commonGrid,
    xAxis: { type: 'category', boundaryGap: false, data: xData },
    yAxis: [
        { type: 'value', name: 'Total' },
        { type: 'value', name: 'Step', position: 'right' }
    ],
    series: [
        {
            name: 'Total Cost',
            type: 'line',
            areaStyle: {},
            data: sTotalCost,
            color: '#28a745'
        },
        {
            name: 'Step Cost',
            type: 'bar',
            yAxisIndex: 1,
            data: sStepCost,
            color: 'rgba(40, 167, 69, 0.3)'
        }
    ]
};

// 3. Wins & Conversion Chart
const optionWins = {
    tooltip: commonTooltip,
    legend: { data: ['Step Wins', 'Step Conversion'] },
    grid: commonGrid,
    xAxis: { type: 'category', data: xData },
    yAxis: { type: 'value' },
    series: [
        {
            name: 'Step Wins',
            type: 'line',
            data: sStepWins,
            smooth: true,
            color: '#17a2b8'
        },
        {
            name: 'Step Conversion',
            type: 'bar',
            data: sStepConversion,
            color: '#fd7e14'
        }
    ]
};

// 渲染初始图表
chartAlpha.setOption(optionAlpha);
chartCost.setOption(optionCost);
chartWins.setOption(optionWins);

// 状态更新逻辑
let isPlaying = false;
let playInterval = null;
let currentStep = 0;

function updateDashboard(step) {
    const data = HISTORY[step];
    
    // 更新数字
    elCurrentStepDisplay.textContent = data.step;
    elStatCost.textContent = data.total_cost.toFixed(2);
    elStatCv.textContent = data.total_conversion;
    elStatWins.textContent = data.total_wins;
    elStatCpa.textContent = data.real_cpa.toFixed(2);
    elStatBudgetPct.textContent = data.budget_percentage.toFixed(1);
    
    // 更新进度条
    elProgressBudget.style.width = `${data.budget_percentage}%`;
    
    // 更新图表的高亮线 (MarkLine)
    const markLineOpt = {
        animation: false,
        data: [{ xAxis: step }]
    };
    
    // 我们可以通过 dispatchAction 来高亮当前点，或者简单地添加一个 markLine
    // ECharts 更新 markLine 需要 merge option
    const updateChartMarker = (chart) => {
        chart.setOption({
            series: [{
                markLine: {
                    symbol: 'none',
                    label: { show: false },
                    lineStyle: { type: 'solid', color: '#333', width: 1 },
                    data: [{ xAxis: data.step }] // 使用 step number 作为 x 轴坐标
                }
            }]
        });
    };
    
    // 注意：这里我们假设 series[0] 是我们要加 markLine 的地方
    // 这种做法会覆盖之前的 markLine (如 CPA Constraint)，所以对 Alpha 图表要小心
    chartCost.setOption({ series: [{ id: 'mk', markLine: { symbol: 'none', data: [{ xAxis: data.step }] } }] });
    chartWins.setOption({ series: [{ id: 'mk', markLine: { symbol: 'none', data: [{ xAxis: data.step }] } }] });
    
    // 对于 Alpha 图表，保留 CPA 约束线
    chartAlpha.setOption({
        series: [{
            // 这里的 index 0 是 Alpha 线
            markLine: {
                symbol: 'none',
                data: [
                    { xAxis: data.step, lineStyle: { color: '#333' } }
                ]
            }
        }]
    });
}

// 事件监听
elSlider.addEventListener('input', (e) => {
    currentStep = parseInt(e.target.value);
    updateDashboard(currentStep);
    if (isPlaying) stopPlay();
});

function startPlay() {
    isPlaying = true;
    btnPlay.textContent = '⏸ 暂停';
    playInterval = setInterval(() => {
        if (currentStep < TOTAL_STEPS) {
            currentStep++;
            elSlider.value = currentStep;
            updateDashboard(currentStep);
        } else {
            stopPlay();
        }
    }, 500); // 500ms per step
}

function stopPlay() {
    isPlaying = false;
    btnPlay.textContent = '▶ 播放';
    clearInterval(playInterval);
}

btnPlay.addEventListener('click', () => {
    if (isPlaying) stopPlay();
    else {
        if (currentStep >= TOTAL_STEPS) {
            currentStep = 0;
            elSlider.value = 0;
        }
        startPlay();
    }
});

// 窗口大小改变时重绘
window.addEventListener('resize', () => {
    chartAlpha.resize();
    chartCost.resize();
    chartWins.resize();
});

// 初始化显示
updateDashboard(0);
