// YOLOv26 前端逻辑

// DOM 元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const modelSelect = document.getElementById('modelSelect');
const confSlider = document.getElementById('confSlider');
const confValue = document.getElementById('confValue');
const iouSlider = document.getElementById('iouSlider');
const iouValue = document.getElementById('iouValue');
const detectBtn = document.getElementById('detectBtn');
const resetBtn = document.getElementById('resetBtn');
const errorMsg = document.getElementById('errorMsg');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const originalImage = document.getElementById('originalImage');
const resultImage = document.getElementById('resultImage');
const detectionList = document.getElementById('detectionList');
const stats = document.getElementById('stats');

// 状态变量
let selectedFile = null;
let originalImageUrl = null;

// 初始化
function init() {
    // 文件上传事件
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    fileInput.addEventListener('change', handleFileSelect);
    
    // 滑块事件
    confSlider.addEventListener('input', updateConfValue);
    iouSlider.addEventListener('input', updateIouValue);
    
    // 按钮事件
    detectBtn.addEventListener('click', startDetection);
    resetBtn.addEventListener('click', resetAll);
    
    // 初始化显示
    updateConfValue();
    updateIouValue();
}

// 拖拽处理
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// 文件选择处理
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
        showError('请上传图片文件（JPG、PNG 等格式）');
        return;
    }
    
    // 验证文件大小（10MB）
    if (file.size > 10 * 1024 * 1024) {
        showError('文件大小不能超过 10MB');
        return;
    }
    
    selectedFile = file;
    
    // 显示原始图片
    if (originalImageUrl) {
        URL.revokeObjectURL(originalImageUrl);
    }
    originalImageUrl = URL.createObjectURL(file);
    originalImage.src = originalImageUrl;
    
    // 更新上传区域显示
    uploadArea.innerHTML = `
        <div class="upload-icon">✅</div>
        <div class="upload-text">${file.name}</div>
        <div class="upload-hint">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
    `;
    
    // 启用检测按钮
    detectBtn.disabled = false;
    
    // 隐藏之前的结果
    results.classList.remove('show');
    errorMsg.classList.remove('show');
}

// 更新置信度显示
function updateConfValue() {
    confValue.textContent = confSlider.value;
}

// 更新 IoU 显示
function updateIouValue() {
    iouValue.textContent = iouSlider.value;
}

// 开始检测
async function startDetection() {
    if (!selectedFile) {
        showError('请先上传图片');
        return;
    }
    
    // 显示加载状态
    loading.classList.add('show');
    results.classList.remove('show');
    errorMsg.classList.remove('show');
    detectBtn.disabled = true;
    
    try {
        // 创建 FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('model_name', modelSelect.value);
        formData.append('conf', confSlider.value);
        formData.append('iou', iouSlider.value);
        
        // 调用 API
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || '检测失败');
        }
        
        const data = await response.json();
        
        // 显示结果
        displayResults(data);
        
    } catch (error) {
        showError('检测失败: ' + error.message);
    } finally {
        loading.classList.remove('show');
        detectBtn.disabled = false;
    }
}

// 显示结果
function displayResults(data) {
    // 显示统计信息
    stats.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${data.count}</div>
            <div class="stat-label">检测目标数</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${modelSelect.value.replace('yolo26', 'YOLOv26-').replace('.pt', '')}</div>
            <div class="stat-label">使用模型</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${(data.detections.reduce((sum, d) => sum + d.confidence, 0) / data.count * 100).toFixed(1)}%</div>
            <div class="stat-label">平均置信度</div>
        </div>
    `;
    
    // 显示结果图片
    if (data.result_image) {
        resultImage.src = data.result_image;
    }
    
    // 显示检测列表
    detectionList.innerHTML = '';
    data.detections.forEach((detection, index) => {
        const item = document.createElement('div');
        item.className = 'detection-item';
        item.innerHTML = `
            <div class="detection-class">${index + 1}. ${detection.class_name}</div>
            <div class="detection-info">
                <span>置信度: ${(detection.confidence * 100).toFixed(1)}%</span>
                <span>边界框: [${detection.bbox.map(b => b.toFixed(0)).join(', ')}]</span>
            </div>
        `;
        detectionList.appendChild(item);
    });
    
    // 显示结果区域
    results.classList.add('show');
}

// 显示错误
function showError(message) {
    errorMsg.textContent = message;
    errorMsg.classList.add('show');
}

// 重置所有
function resetAll() {
    selectedFile = null;
    if (originalImageUrl) {
        URL.revokeObjectURL(originalImageUrl);
        originalImageUrl = null;
    }
    
    // 重置上传区域
    uploadArea.innerHTML = `
        <div class="upload-icon">📷</div>
        <div class="upload-text">点击或拖拽上传图片</div>
        <div class="upload-hint">支持 JPG、PNG 格式，最大 10MB</div>
    `;
    
    // 重置文件输入
    fileInput.value = '';
    
    // 禁用检测按钮
    detectBtn.disabled = true;
    
    // 隐藏结果和错误
    results.classList.remove('show');
    errorMsg.classList.remove('show');
    loading.classList.remove('show');
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);
