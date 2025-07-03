<template>
  <div class="chat-container">
    <!-- 头部标题 -->
    <header class="chat-header">
      <div class="header-left">
        <div class="logo">
          <el-icon><ChatRound /></el-icon>
        </div>
        <div class="title-info">
          <h1>阑珊 AI</h1>
          <span class="subtitle">智能问答助手</span>
        </div>
      </div>
      <div class="header-actions">
        <el-tooltip content="清空对话">
          <el-button @click="clearChat" :icon="Delete" circle type="info" />
        </el-tooltip>
        <el-tooltip content="设置">
          <el-button @click="showSettings = true" :icon="Setting" circle type="primary" />
        </el-tooltip>
      </div>
    </header>

    <!-- 聊天区域 -->
    <main class="chat-main">
      <!-- 侧边栏 -->
      <aside class="chat-sidebar">
        <div class="sidebar-header">
          <h3>对话历史</h3>
          <el-button @click="newChat" type="text" size="small">
            <el-icon><Plus /></el-icon>
            新对话
          </el-button>
        </div>
        <div class="chat-sessions">
          <div v-for="(session, index) in chatSessions" :key="index" 
               class="session-item" 
               :class="{ active: currentSessionIndex === index }"
               @click="switchSession(index)">
            <div class="session-content">
              <div class="session-title">{{ session.title || '新对话' }}</div>
              <div class="session-time">{{ formatDate(session.createdAt) }}</div>
            </div>
            <div class="session-actions" @click.stop>
              <el-tooltip content="删除对话">
                <el-button 
                  @click="deleteSession(index)" 
                  :icon="Delete" 
                  text 
                  size="small" 
                  class="delete-btn"
                />
              </el-tooltip>
            </div>
          </div>
        </div>
      </aside>

      <!-- 消息区域 -->
      <div class="chat-content">
        <div class="chat-messages" ref="messagesContainer">
          <!-- 欢迎页面 -->
          <div v-if="currentSession.messages.length === 0" class="welcome-section">
            <div class="welcome-card">
              <div class="welcome-icon">
                <el-icon :size="64"><ChatRound /></el-icon>
              </div>
              <h2>欢迎使用阑珊 AI</h2>
              <p>基于知识库的智能问答助手，为您提供准确、可信的信息回答</p>
              <div class="quick-actions">
                <div class="action-card" @click="sendQuickMessage('劳动者的权利有哪些？')">
                  <el-icon><DocumentCopy /></el-icon>
                  <span>劳动者权利</span>
                </div>
                <div class="action-card" @click="sendQuickMessage('工作时间的规定是什么？')">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>工作时间</span>
                </div>
                <div class="action-card" @click="sendQuickMessage('劳动合同应该包含什么内容？')">
                  <el-icon><Edit /></el-icon>
                  <span>劳动合同</span>
                </div>
                <div class="action-card" @click="sendQuickMessage('女职工保护的相关规定')">
                  <el-icon><Star /></el-icon>
                  <span>女职工保护</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <div v-for="(message, index) in currentSession.messages" :key="index" class="message-wrapper">
            <!-- 用户消息 -->
            <div v-if="message.type === 'user'" class="message user-message">
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-meta">
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                </div>
              </div>
              <div class="message-avatar">
                <el-avatar :size="36">
                  <el-icon><User /></el-icon>
                </el-avatar>
              </div>
            </div>

            <!-- AI消息 -->
            <div v-else-if="message.type === 'assistant'" class="message ai-message">
              <div class="message-avatar">
                <el-avatar :size="36" style="background-color: #67c23a;">AI</el-avatar>
              </div>
              <div class="message-content">
                <!-- 思考过程 -->
                <div v-if="message.thinking" class="thinking-content">
                  <div class="thinking-header">
                    <el-icon><Loading /></el-icon>
                    <span>AI 思考过程</span>
                  </div>
                  <div class="thinking-text">{{ message.thinking }}</div>
                </div>
                
                <!-- 回答内容 -->
                <div v-if="message.content" class="message-text" v-html="formatAnswer(message.content)"></div>
                
                <!-- 信息来源 -->
                <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                  <div class="sources-header">
                    <el-icon><DocumentCopy /></el-icon>
                    <span>信息来源</span>
                  </div>
                  <div class="sources-list">
                    <el-tag v-for="(source, idx) in message.sources" :key="idx" size="small">
                      {{ source }}
                    </el-tag>
                  </div>
                </div>

                <div class="message-meta">
                  <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                  <div class="message-actions">
                    <el-button @click="copyText(message.content)" :icon="DocumentCopy" text size="small">复制</el-button>
                    <el-button @click="likeMessage(index)" :icon="StarFilled" text size="small">点赞</el-button>
                    <el-button @click="regenerateResponse(index)" :icon="Refresh" text size="small">重新生成</el-button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 输入中状态 -->
          <div v-if="loading" class="message ai-message typing-message">
            <div class="message-avatar">
              <el-avatar :size="36" style="background-color: #67c23a;">AI</el-avatar>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <div class="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span class="typing-text">正在思考中...</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <footer class="chat-input">
          <div class="input-wrapper">
            <div class="input-box">
              <el-input
                v-model="msg"
                type="textarea"
                :rows="1"
                placeholder="输入您的问题... (Ctrl+Enter 发送)"
                @keydown.ctrl.enter="sendMsg"
                @input="handleInput"
                :disabled="loading"
                resize="none"
                class="message-input"
              />
              <div class="input-tools">
                <div class="input-tools-left">
                  <el-tooltip content="知识库模式">
                    <el-button 
                      :type="useKnowledgeBase ? 'primary' : 'info'" 
                      text 
                      size="small" 
                      @click="useKnowledgeBase = !useKnowledgeBase"
                    >
                      <el-icon><DataAnalysis /></el-icon>
                      {{ useKnowledgeBase ? '知识库' : '聊天' }}
                    </el-button>
                  </el-tooltip>
                </div>
                <div class="input-tools-right">
                  <el-button 
                    @click="sendMsg" 
                    type="primary" 
                    :disabled="!msg.trim() || loading"
                    :loading="loading"
                    class="send-button"
                  >
                    <template v-if="!loading">
                      <el-icon><Promotion /></el-icon>
                      发送
                    </template>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </main>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="AI 助手设置" width="500px">
      <el-form label-width="120px">
        <el-form-item label="知识库模式">
          <el-switch v-model="useKnowledgeBase" active-text="启用" inactive-text="禁用" />
          <div style="font-size: 12px; color: #999; margin-top: 4px;">
            启用后，AI将基于知识库内容回答问题
          </div>
        </el-form-item>

        <el-form-item label="知识库地址">
          <el-input v-model="knowledgeBaseUrl" placeholder="http://localhost:8000" />
        </el-form-item>

        <el-form-item label="检索数量">
          <el-slider v-model="searchTopK" :min="1" :max="10" show-input />
        </el-form-item>

        <el-form-item label="上下文长度">
          <el-slider v-model="maxContextLength" :min="500" :max="5000" :step="100" show-input />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSettings = false">取消</el-button>
        <el-button type="primary" @click="saveSettings">保存设置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch, computed } from 'vue'
import axios from 'axios'
import { 
  ChatRound, User, Setting, Delete, Loading, Plus,
  DocumentCopy, StarFilled, Refresh, Link,
  ChatDotRound, Promotion, Edit, DataAnalysis, Star, Close
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const msg = ref('')
const loading = ref(false)
const messagesContainer = ref(null)
const showSettings = ref(false)

// 知识库相关配置
const useKnowledgeBase = ref(true) // 默认启用知识库
const knowledgeBaseUrl = ref('/api/knowledge') // 知识库API地址
const maxContextLength = ref(3000) // 最大上下文长度
const searchTopK = ref(5) // 检索返回的文档数量

// 会话管理
const chatSessions = ref([])
const currentSessionIndex = ref(0)

// 计算当前会话
const currentSession = computed(() => {
  if (chatSessions.value.length === 0) {
    return { messages: [], title: '', createdAt: Date.now() }
  }
  return chatSessions.value[currentSessionIndex.value] || { messages: [], title: '', createdAt: Date.now() }
})

// 初始化第一个会话
onMounted(async () => {
  // 加载会话
  const saved = localStorage.getItem('deepseek-sessions')
  if (saved) {
    chatSessions.value = JSON.parse(saved)
  }
  if (chatSessions.value.length === 0) {
    newChat()
  }

  // 加载设置
  const savedSettings = localStorage.getItem('ai-settings')
  if (savedSettings) {
    const settings = JSON.parse(savedSettings)
    useKnowledgeBase.value = settings.useKnowledgeBase ?? true
    knowledgeBaseUrl.value = settings.knowledgeBaseUrl || '/api/knowledge'
    maxContextLength.value = settings.maxContextLength ?? 3000
    searchTopK.value = settings.searchTopK ?? 5
  }
})

// 新建对话
function newChat() {
  const newSession = {
    title: '',
    messages: [],
    createdAt: Date.now()
  }
  chatSessions.value.unshift(newSession)
  currentSessionIndex.value = 0
}

// 切换会话
function switchSession(index) {
  currentSessionIndex.value = index
  scrollToBottom()
}

// 删除会话
function deleteSession(index) {
  ElMessageBox.confirm(
    '确定要删除这个对话吗？删除后无法恢复。',
    '删除对话',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 删除指定会话
    chatSessions.value.splice(index, 1)
    
    // 如果删除的是当前会话
    if (currentSessionIndex.value === index) {
      // 如果还有会话，切换到第一个
      if (chatSessions.value.length > 0) {
        currentSessionIndex.value = 0
      } else {
        // 如果没有会话了，创建新会话
        newChat()
      }
    } else if (currentSessionIndex.value > index) {
      // 如果当前会话在被删除会话之后，索引需要减1
      currentSessionIndex.value--
    }
    
    ElMessage.success('对话已删除')
  }).catch(() => {
    // 用户取消删除
  })
}

// 快速发送消息
function sendQuickMessage(message) {
  msg.value = message
  sendMsg()
}

// 格式化时间
function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

// 格式化日期
function formatDate(timestamp) {
  const date = new Date(timestamp)
  const today = new Date()
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  
  if (date.toDateString() === today.toDateString()) {
    return '今天'
  } else if (date.toDateString() === yesterday.toDateString()) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
  }
}

// 格式化答案
function formatAnswer(text) {
  return text.replace(/\n/g, '<br>')
}

// 处理输入
function handleInput() {
  // 自动调整输入框高度
  nextTick(() => {
    const textarea = document.querySelector('.message-input textarea')
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
  })
}

// 复制文本
function copyText(text) {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}

// 点赞消息
function likeMessage(index) {
  ElMessage.success('感谢您的反馈！')
}

// 重新生成回复
function regenerateResponse(index) {
  ElMessage.info('重新生成功能开发中...')
}

// 清空聊天
function clearChat() {
  currentSession.value.messages = []
  ElMessage.success('当前对话已清空')
}

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 发送消息 - 修改后的版本
async function sendMsg() {
  if (!msg.value.trim()) {
    ElMessage.warning('请输入您的问题')
    return
  }

  const userMessage = {
    type: 'user',
    content: msg.value,
    timestamp: Date.now()
  }
  
  currentSession.value.messages.push(userMessage)
  
  if (!currentSession.value.title) {
    currentSession.value.title = msg.value.length > 20 ? 
      msg.value.substring(0, 20) + '...' : msg.value
  }
  
  const currentQuestion = msg.value
  msg.value = ''
  loading.value = true
  scrollToBottom()

  // 知识库问答模式：后端直接生成答案
  if (useKnowledgeBase.value) {
    try {
      // 显示检索状态
      const searchMessage = {
        type: 'assistant',
        content: '',
        thinking: '正在搜索知识库并生成答案...',
        timestamp: Date.now()
      }
      currentSession.value.messages.push(searchMessage)
      const searchIndex = currentSession.value.messages.length - 1
      scrollToBottom()

      // 调用后端知识库问答API（直接生成答案）
      const answerResponse = await axios.post(`${knowledgeBaseUrl.value}/answer`, {
        query: currentQuestion,
        top_k: searchTopK.value,
        max_length: maxContextLength.value
      })
      
      if (answerResponse.data && answerResponse.data.answer) {
        // 直接使用后端生成的答案
        currentSession.value.messages[searchIndex].content = answerResponse.data.answer
        currentSession.value.messages[searchIndex].sources = answerResponse.data.sources.map(s => s.title)
        currentSession.value.messages[searchIndex].thinking = `知识库问答完成 (${answerResponse.data.method})`
        loading.value = false
        scrollToBottom()
        return // 直接返回，不需要再调用LLM
      } else {
        currentSession.value.messages[searchIndex].content = '知识库未找到相关内容，无法回答您的问题。'
        currentSession.value.messages[searchIndex].thinking = '知识库未命中'
        loading.value = false
        scrollToBottom()
        return
      }
    } catch (error) {
      console.error('知识库问答失败:', error)
      ElMessage.warning('知识库问答失败，请稍后重试')
      const searchIndex = currentSession.value.messages.length - 1
      currentSession.value.messages[searchIndex].content = '知识库服务暂时不可用，请稍后重试。'
      currentSession.value.messages[searchIndex].thinking = '服务异常'
      loading.value = false
      scrollToBottom()
      return
    }
  } else {
    // 普通聊天模式
    const aiMessage = {
      type: 'assistant',
      content: '抱歉，普通聊天模式尚未实现。请启用知识库模式以获得基于知识库的专业回答。',
      thinking: '普通聊天模式',
      sources: [],
      timestamp: Date.now()
    }
    currentSession.value.messages.push(aiMessage)
    loading.value = false
    scrollToBottom()
  }
}

// 保存设置
function saveSettings() {
  const settings = {
    useKnowledgeBase: useKnowledgeBase.value,
    knowledgeBaseUrl: knowledgeBaseUrl.value,
    maxContextLength: maxContextLength.value,
    searchTopK: searchTopK.value
  }
  localStorage.setItem('ai-settings', JSON.stringify(settings))
  showSettings.value = false
  ElMessage.success('设置已保存')
}

// 监听会话变化，自动保存
watch(chatSessions, (newValue) => {
  localStorage.setItem('deepseek-sessions', JSON.stringify(newValue))
}, { deep: true })
</script>

<style scoped>
.chat-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

/* 背景装饰 */
.chat-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(circle at 20% 20%, rgba(255, 255, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 40% 70%, rgba(255, 255, 255, 0.03) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 72px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
  transition: transform 0.3s ease;
}

.logo:hover {
  transform: scale(1.05);
}

.title-info h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.header-actions .el-button {
  border-radius: 12px;
  padding: 12px;
  transition: all 0.3s ease;
}

.header-actions .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.chat-main {
  flex: 1;
  display: flex;
  min-height: 0;
  position: relative;
  z-index: 1;
}

.chat-sidebar {
  width: 320px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  border-right: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  flex-direction: column;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.08);
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #1e293b;
  font-weight: 600;
}

.chat-sessions {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.session-item {
  padding: 16px;
  border-radius: 16px;
  cursor: pointer;
  margin-bottom: 8px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
}

.session-item:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
  transform: translateX(4px);
}

.session-item.active {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.15));
  border-color: #667eea;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
}

.session-content {
  flex: 1;
  min-width: 0;
}

.session-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
  margin-left: 8px;
}

.session-item:hover .session-actions {
  opacity: 1;
}

.delete-btn {
  color: #ef4444 !important;
  padding: 4px !important;
  min-height: auto !important;
  width: auto !important;
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1) !important;
  transform: scale(1.1);
}

.session-title {
  font-size: 15px;
  color: #1e293b;
  margin-bottom: 6px;
  font-weight: 600;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: rgba(248, 250, 252, 0.8);
  backdrop-filter: blur(20px);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  scroll-behavior: smooth;
}

.welcome-section {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 500px;
}

.welcome-card {
  text-align: center;
  max-width: 680px;
  padding: 56px 48px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border-radius: 32px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.welcome-icon {
  margin-bottom: 32px;
  color: #667eea;
  filter: drop-shadow(0 4px 8px rgba(102, 126, 234, 0.3));
}

.welcome-card h2 {
  margin: 0 0 24px 0;
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -1px;
}

.welcome-card p {
  margin: 0 0 40px 0;
  color: #475569;
  font-size: 18px;
  line-height: 1.7;
  font-weight: 500;
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.action-card {
  padding: 28px 24px;
  background: rgba(255, 255, 255, 0.8);
  border: 2px solid rgba(102, 126, 234, 0.1);
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  position: relative;
  overflow: hidden;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.1), transparent);
  transition: left 0.6s ease;
}

.action-card:hover::before {
  left: 100%;
}

.action-card:hover {
  border-color: #667eea;
  background: rgba(255, 255, 255, 0.95);
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
}

.action-card .el-icon {
  font-size: 32px;
  color: #667eea;
  transition: transform 0.3s ease;
}

.action-card:hover .el-icon {
  transform: scale(1.1);
}

.action-card span {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.message-wrapper {
  margin-bottom: 32px;
  animation: messageSlideIn 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

@keyframes messageSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  max-width: 85%;
}

.user-message {
  flex-direction: row-reverse;
  margin-left: auto;
}

.ai-message {
  margin-right: auto;
}

.message-avatar {
  flex-shrink: 0;
  position: relative;
}

.message-avatar .el-avatar {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border: 3px solid rgba(255, 255, 255, 0.9);
}

.user-message .message-avatar .el-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.ai-message .message-avatar .el-avatar {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  font-weight: 700;
  font-size: 16px;
}

.message-content {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px) saturate(180%);
  border-radius: 24px;
  padding: 24px 28px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  word-wrap: break-word;
  line-height: 1.6;
}

.user-message .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 24px 24px 8px 24px;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
}

.ai-message .message-content {
  border-radius: 24px 24px 24px 8px;
  background: rgba(255, 255, 255, 0.95);
}

.thinking-content {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.08), rgba(59, 130, 246, 0.08)) !important;
  border: 2px dashed rgba(139, 92, 246, 0.3) !important;
  position: relative;
  padding: 28px 32px;
  margin-bottom: 16px;
  border-radius: 16px;
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #8b5cf6;
  margin-bottom: 20px;
  font-size: 16px;
}

.thinking-text {
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'SimSun', sans-serif;
  font-size: 15px;
  color: #374151;
  line-height: 1.8;
  background: rgba(255, 255, 255, 0.8);
  padding: 20px;
  border-radius: 16px;
  border: 1px solid rgba(139, 92, 246, 0.25);
  font-weight: 400;
  letter-spacing: 0.3px;
}

.message-text {
  font-size: 16px;
  line-height: 1.7;
  margin-bottom: 16px;
  font-weight: 500;
}

.user-message .message-text {
  color: rgba(255, 255, 255, 0.95);
}

.message-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-top: 12px;
}

.user-message .message-meta {
  opacity: 0.8;
}

.ai-message .message-meta {
  opacity: 0.7;
}

.message-time {
  font-weight: 500;
  color: inherit;
}

/* 信息来源样式 */
.message-sources {
  margin-top: 16px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.message-sources:hover {
  background: rgba(102, 126, 234, 0.08);
  border-color: rgba(102, 126, 234, 0.2);
}

.sources-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #667eea;
}

.sources-header .el-icon {
  font-size: 16px;
}

.sources-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.sources-list .el-tag {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(102, 126, 234, 0.2);
  color: #667eea;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.sources-list .el-tag:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
}

/* 输入框样式 */
.chat-input {
  padding: 24px 32px 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
}

.input-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.input-box {
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 24px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(20px);
  width: 100%;
}

.input-box:focus-within {
  border-color: #667eea;
  box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1), 0 12px 40px rgba(0, 0, 0, 0.12);
  transform: translateY(-2px);
}

.message-input {
  border: none !important;
  width: 100%;
}

.message-input :deep(.el-textarea__inner) {
  border: none !important;
  box-shadow: none !important;
  padding: 28px 32px 0 32px;
  font-size: 16px;
  line-height: 1.6;
  min-height: 80px;
  max-height: 200px;
  resize: none;
  background: transparent;
  color: #1e293b;
  font-weight: 500;
  width: 100%;
  box-sizing: border-box;
}

.message-input :deep(.el-textarea__inner)::placeholder {
  color: #94a3b8;
  font-weight: 500;
}

.input-tools {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 32px 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(248, 250, 252, 0.5);
}

.input-tools-left .el-button {
  border-radius: 12px;
  padding: 10px 16px;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transition: all 0.3s ease;
  font-weight: 600;
}

.input-tools-left .el-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.input-tools-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.send-button {
  border-radius: 16px !important;
  font-weight: 700 !important;
  padding: 12px 24px !important;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4) !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
  font-size: 15px !important;
  min-height: 44px !important;
}

.send-button:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5) !important;
}

.send-button:disabled {
  opacity: 0.5 !important;
  transform: none !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2) !important;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
}

.typing-dots {
  display: flex;
  gap: 4px;
}

.typing-dots span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #667eea;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dots span:nth-child(1) { animation-delay: -0.32s; }
.typing-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.typing-text {
  color: #667eea;
  font-weight: 500;
}
</style>
