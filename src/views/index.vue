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
          <!-- 欢迎界面 -->
          <div v-if="currentSession.messages.length === 0" class="welcome-section">
            <div class="welcome-card">
              <div class="welcome-icon">
                <el-icon size="60"><ChatRound /></el-icon>
              </div>
              <h2>欢迎使用阑珊 AI</h2>
              <p>我是您的智能助手，可以帮助您解答问题、协助工作、进行对话交流</p>
              <div class="quick-actions">
                <div class="action-card" @click="sendQuickMessage('你好，请介绍一下自己')">
                  <el-icon><User /></el-icon>
                  <span>自我介绍</span>
                </div>
                <div class="action-card" @click="sendQuickMessage('请给我一些写作建议')">
                  <el-icon><Edit /></el-icon>
                  <span>写作助手</span>
                </div>
                <div class="action-card" @click="sendQuickMessage('帮我分析一个问题')">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>问题分析</span>
                </div>
                <div class="action-card" @click="sendQuickMessage('我需要一些创意想法')">
                  <el-icon><Star /></el-icon>
                  <span>创意思考</span>
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
                <el-avatar :size="36" style="background-color: #409eff;">
                  <el-icon><User /></el-icon>
                </el-avatar>
              </div>
            </div>

            <!-- AI 思考过程（单独气泡） -->
            <div v-if="message.type === 'assistant' && message.thinking" class="message ai-thinking">
              <div class="message-avatar">
                <el-avatar :size="36" style="background-color: #909399;">
                  <el-icon><Loading class="thinking-icon" /></el-icon>
                </el-avatar>
              </div>
              <div class="message-content thinking-content">
                <div class="thinking-header">
                  <span>思考过程</span>
                </div>
                <div class="thinking-text">{{ message.thinking }}</div>
              </div>
            </div>

            <!-- AI 回答（单独气泡） -->
            <div v-if="message.type === 'assistant' && message.content" class="message ai-message">
              <div class="message-avatar">
                <el-avatar :size="36" style="background-color: #67c23a;">AI</el-avatar>
              </div>
              <div class="message-content">
                <div class="message-text" v-html="formatAnswer(message.content)"></div>
                
                <!-- 新增：显示信息来源 -->
                <div v-if="message.sources && message.sources.length > 0" class="message-sources">
                  <div class="sources-header">
                    <el-icon><Document /></el-icon>
                    <span>信息来源</span>
                  </div>
                  <div class="sources-list">
                    <el-tag v-for="(source, index) in message.sources" :key="index" 
                            size="small" type="info" class="source-tag">
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
              <el-tooltip content="上传文件">
                <el-button :icon="Link" text size="small" @click="handleFileUpload" />
              </el-tooltip>
              <el-tooltip content="表情">
                <el-button :icon="ChatDotRound" text size="small" @click="showEmojiPicker = !showEmojiPicker" />
              </el-tooltip>
            </div>
            <div class="input-tools-right">
              <el-button 
                type="primary" 
                @click="sendMsg" 
                :loading="loading"
                :disabled="!msg.trim()"
                size="small"
                class="send-button"
              >
                <el-icon><Promotion /></el-icon>
                发送
              </el-button>
            </div>
          </div>
        </div>

        <!-- 表情选择器 -->
        <div v-if="showEmojiPicker" class="emoji-picker">
          <div class="emoji-header">
            <span>选择表情</span>
            <el-button class="close-btn" @click="showEmojiPicker = false" type="text" size="small">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          <div class="emoji-grid">
            <div v-for="emoji in commonEmojis" :key="emoji" class="emoji-item" @click="insertEmoji(emoji)">
              {{ emoji }}
            </div>
          </div>
        </div>

        <!-- 隐藏的文件输入 -->
        <input 
          ref="fileInputRef" 
          type="file" 
          style="display: none" 
          @change="onFileSelected"
          accept="image/*,text/*,.pdf,.doc,.docx"
        />
      </div>
    </footer>
      </div>
    </main>

    <!-- 设置对话框 -->
    <el-dialog v-model="showSettings" title="AI 助手设置" width="500px">
      <el-form label-width="120px">
        <el-form-item label="使用模式">
          <el-radio-group v-model="useLocalModel">
            <el-radio :label="true">本地模型 (Ollama)</el-radio>
            <el-radio :label="false">远程 API</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <!-- 本地模型设置 -->
        <template v-if="useLocalModel">
          <el-form-item label="Ollama 地址">
            <el-input v-model="ollamaBaseUrl" placeholder="http://localhost:11434" />
            <div style="font-size: 12px; color: #999; margin-top: 4px;">
              Ollama 服务地址，默认为 localhost:11434
            </div>
          </el-form-item>
          
          <el-form-item label="本地模型">
            <el-select v-model="currentModel" style="width: 100%" filterable>
              <el-option 
                v-for="model in availableModels" 
                :key="model.name"
                :label="model.name" 
                :value="model.name"
              >
                <div style="line-height: 1.4;">
                  <div style="font-weight: 500;">{{ model.name }}</div>
                  <div style="font-size: 12px; color: #999;">
                    大小: {{ formatSize(model.size) }}
                  </div>
                </div>
              </el-option>
            </el-select>
            <div style="margin-top: 8px;">
              <el-button @click="loadOllamaModels" size="small" type="primary">
                刷新模型列表
              </el-button>
            </div>
          </el-form-item>
        </template>
        
        <!-- 远程 API 设置 -->
        <template v-else>
          <el-form-item label="AI 模型">
            <el-select v-model="remoteModel" style="width: 100%">
              <el-option 
                label="DeepSeek-R1" 
                value="deepseek-ai/DeepSeek-R1-0528-Qwen3-8B" 
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="API Key">
            <el-input v-model="apiKey" type="password" show-password />
          </el-form-item>
        </template>
        
        <!-- 通用设置 -->
        <el-form-item label="温度">
          <el-slider v-model="temperature" :min="0" :max="2" :step="0.1" show-tooltip />
          <div style="font-size: 12px; color: #999; margin-top: 4px;">控制回答的创造性</div>
        </el-form-item>
        
        <el-form-item label="最大长度">
          <el-input-number v-model="maxTokens" :min="100" :max="4000" :step="100" />
        </el-form-item>

        <!-- 知识库设置 -->
        <el-form-item label="知识库启用">
          <el-switch v-model="useKnowledgeBase" active-text="启用" inactive-text="禁用" />
        </el-form-item>

        <el-form-item v-if="useKnowledgeBase" label="知识库 API 地址">
          <el-input v-model="knowledgeBaseUrl" placeholder="/api/knowledge" />
          <div style="font-size: 12px; color: #999; margin-top: 4px;">
            知识库服务地址，默认为 /api/knowledge
          </div>
        </el-form-item>
        
        <el-form-item v-if="useKnowledgeBase" label="最大上下文长度">
          <el-input-number v-model="maxContextLength" :min="100" :max="10000" :step="100" />
        </el-form-item>
        
        <el-form-item v-if="useKnowledgeBase" label="检索返回文档数量">
          <el-input-number v-model="searchTopK" :min="1" :max="100" :step="1" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showSettings = false">取消</el-button>
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
        </div>
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
const showEmojiPicker = ref(false) // 新增：表情选择器显示状态
const fileInputRef = ref(null) // 新增：文件输入引用

// 新增：本地模型支持
const useLocalModel = ref(true) // 默认使用本地模型
const currentModel = ref('deepseek-r1:1.5b') // 本地模型名称
const remoteModel = ref('deepseek-ai/DeepSeek-R1-0528-Qwen3-8B') // 远程模型
const apiKey = ref('sk-dhyofqmlqevepadtfbjjmtvelluvgoqixawhgqcyhmiysdtl')
const ollamaBaseUrl = ref('/api/ollama') // 新增
const availableModels = ref([]) // 新增：本地模型列表
const temperature = ref(0.7)
const maxTokens = ref(2000)

// 新增：知识库相关配置
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
    useLocalModel.value = settings.useLocalModel ?? true
    currentModel.value = settings.currentModel || 'deepseek-r1:1.5b'
    remoteModel.value = settings.remoteModel || 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B'
    apiKey.value = settings.apiKey || apiKey.value
    ollamaBaseUrl.value = settings.ollamaBaseUrl || 'http://localhost:11434'
    temperature.value = settings.temperature ?? 0.7
    maxTokens.value = settings.maxTokens ?? 2000
  }

  // 如果使用本地模型，尝试加载模型列表
  if (useLocalModel.value) {
    await loadOllamaModels()
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
function sendQuickMessage(message = '你好，我是阑珊 AI，有什么可以帮助您？') {
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

// 发送消息
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

  // 新增：知识库问答逻辑（支持流式输出）
  if (useKnowledgeBase.value) {
    try {
      // 显示初始状态
      const streamMessage = {
        type: 'assistant',
        content: '',
        thinking: '正在准备回答...',
        timestamp: Date.now()
      }
      currentSession.value.messages.push(streamMessage)
      const streamIndex = currentSession.value.messages.length - 1
      scrollToBottom()

      // 调用流式知识库问答API
      const response = await fetch(`${knowledgeBaseUrl.value}/answer_stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: currentQuestion,
          top_k: searchTopK.value,
          max_length: maxContextLength.value
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let currentSources = []

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || '' // 保留不完整的行

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'thinking') {
                // 更新思考过程
                currentSession.value.messages[streamIndex].thinking = data.content
                scrollToBottom()
              } else if (data.type === 'answer_start') {
                // 开始答案输出
                currentSession.value.messages[streamIndex].thinking = '正在生成答案...'
                currentSession.value.messages[streamIndex].method = data.method
                scrollToBottom()
              } else if (data.type === 'answer') {
                // 追加答案内容
                currentSession.value.messages[streamIndex].content += data.content
                scrollToBottom()
              } else if (data.type === 'sources') {
                // 设置信息来源
                currentSources = data.sources
                currentSession.value.messages[streamIndex].sources = data.sources.map(s => 
                  typeof s === 'object' ? s.title : s
                )
                scrollToBottom()
              } else if (data.type === 'done') {
                // 完成
                const method = currentSession.value.messages[streamIndex].method || 'unknown'
                currentSession.value.messages[streamIndex].thinking = `问答完成 (${method})`
                loading.value = false
                scrollToBottom()
                return
              } else if (data.type === 'error') {
                // 错误处理
                currentSession.value.messages[streamIndex].content = data.content
                currentSession.value.messages[streamIndex].thinking = '发生错误'
                loading.value = false
                scrollToBottom()
                return
              }
            } catch (e) {
              console.error('解析流式数据失败:', e)
            }
          }
        }
      }
      
      loading.value = false
      scrollToBottom()
      return
      
    } catch (error) {
      console.error('流式知识库问答失败:', error)
      ElMessage.warning('知识库问答失败，请稍后重试')
      
      // 降级到普通API
      try {
        const fallbackResponse = await axios.post(`${knowledgeBaseUrl.value}/answer`, {
          query: currentQuestion,
          top_k: searchTopK.value,
          max_length: maxContextLength.value
        })
        
        if (fallbackResponse.data && fallbackResponse.data.answer) {
          const fullAnswer = fallbackResponse.data.answer
          const sources = fallbackResponse.data.sources || []
          const method = fallbackResponse.data.method || 'unknown'
          
          const { thinking, answer } = parseContentWithThinkTag(fullAnswer)
          
          const fallbackMessage = {
            type: 'assistant',
            content: answer || fullAnswer,
            thinking: thinking || `问答完成 (${method})`,
            sources: sources.map(s => typeof s === 'object' ? s.title : s),
            timestamp: Date.now()
          }
          
          currentSession.value.messages.push(fallbackMessage)
          loading.value = false
          scrollToBottom()
          return
        }
      } catch (fallbackError) {
        console.error('降级API也失败了:', fallbackError)
      }
      
      // 最终错误处理
      const errorMessage = {
        type: 'assistant',
        content: '知识库服务暂时不可用，请稍后重试。',
        thinking: '服务异常',
        timestamp: Date.now()
      }
      currentSession.value.messages.push(errorMessage)
      loading.value = false
      scrollToBottom()
      return
    }
  }

  // 构建消息数组（备用：如果流式API失败时使用）
  const systemPrompt = {
    role: "system",
    content: "您是一个专业的AI助手，请根据提供的信息回答用户问题。"
  }
  
  // 构建对话历史（只取最近N轮，防止上下文过长）
  const N = 8 // 历史对话数量
  const history = currentSession.value.messages.slice(0, -2).filter(m => m.type === 'user' || m.type === 'assistant')
  let context = []
  if (history.length > 0) {
    const grouped = []
    for (let i = 0; i < history.length; i += 2) {
      grouped.push(history.slice(i, i + 2))
    }
    const lastN = grouped.slice(-N)
    context = lastN.flat()
  }
  
  // 转换为API格式
  const messages = [systemPrompt]
  context.forEach(message => {
    if (message.type === 'user') {
      messages.push({ role: "user", content: message.content })
    }
    if (message.type === 'assistant') {
      messages.push({ role: "assistant", content: message.content })
    }
  })
  messages.push({ role: "user", content: currentQuestion })

  const aiMessage = {
    type: 'assistant',
    content: '',
    thinking: '',
    sources: [], // 信息来源
    timestamp: Date.now()
  }
  currentSession.value.messages.push(aiMessage)
  const messageIndex = currentSession.value.messages.length - 1

  // 根据配置选择本地或远程模型
  if (useLocalModel.value) {
    callOllamaAPI(messages, messageIndex)
  } else {
    callRemoteAPI(messages, messageIndex)
  }
}

function parseContentWithThinkTag(raw) {
  if (!raw) return { thinking: '', answer: '' }
  
  // 匹配 <think>...</think> 标签
  const thinkMatch = raw.match(/<think>([\s\S]*?)<\/think>/)
  let thinking = ''
  let answer = raw
  
  if (thinkMatch) {
    thinking = thinkMatch[1].trim()
    answer = raw.replace(thinkMatch[0], '').trim()
  } else {
    // 如果没有think标签，但内容中包含"AI智能生成回答"等标识，
    // 尝试提取思考过程部分
    const lines = raw.split('\n')
    let thinkingLines = []
    let answerLines = []
    let inThinking = false
    
    for (const line of lines) {
      if (line.includes('嗯，') || line.includes('这可能是因为') || 
          line.includes('我需要') || line.includes('让我想想') ||
          line.includes('分析一下') || line.includes('考虑到')) {
        inThinking = true
        thinkingLines.push(line)
      } else if (line.includes('【') && line.includes('】')) {
        // 遇到格式化的标题，思考过程结束
        inThinking = false
        answerLines.push(line)
      } else if (inThinking) {
        thinkingLines.push(line)
      } else {
        answerLines.push(line)
      }
    }
    
    if (thinkingLines.length > 0) {
      thinking = thinkingLines.join('\n').trim()
      answer = answerLines.join('\n').trim()
    }
  }
  
  return { thinking, answer }
}

// 新增：调用本地 Ollama API
async function callOllamaAPI(messages, messageIndex) {
  try {
    const response = await fetch(`${ollamaBaseUrl.value}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: currentModel.value,
        messages: messages,
        stream: true,
        options: {
          temperature: temperature.value,
          num_predict: maxTokens.value
        }
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let rawContent = '' // 新增：累积原始内容

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      const lines = chunk.split('\n').filter(line => line.trim())
      
      for (const line of lines) {
        try {
          const data = JSON.parse(line)
          if (data.message && data.message.content) {
            // 累积原始内容
            rawContent += data.message.content
            
            // 实时分离思考过程和回答内容
            const { thinking, answer } = parseContentWithThinkTag(rawContent)
            currentSession.value.messages[messageIndex].thinking = thinking
            currentSession.value.messages[messageIndex].content = answer
            
            scrollToBottom()
          }
          
          if (data.done) {
            loading.value = false
            return
          }
        } catch (error) {
          console.error('解析 Ollama 响应失败:', error)
        }
      }
    }
  } catch (error) {
    console.error('Ollama API 调用失败:', error)
    ElMessage.error(`本地模型调用失败: ${error.message}`)
    currentSession.value.messages.splice(-2)
    loading.value = false
  }
}

// 新增：调用远程 API
function callRemoteAPI(messages, messageIndex) {
  const data = {
    model: remoteModel.value,
    messages: messages,
    stream: true,
    max_tokens: maxTokens.value,
    temperature: temperature.value
  }

  axios.request({
    url: 'https://api.siliconflow.cn/v1/chat/completions',
    method: 'post',
    headers: { 
      'Content-Type': 'application/json', 
      'Accept': 'application/json', 
      'Authorization': `Bearer ${apiKey.value}`
    },
    data: JSON.stringify(data)
  }).then(response => {
    const array = response.data.split('\n\n')
    
    for (let i in array) {
      if (array[i] === '') continue
      
      const str = array[i].substring(6)
      if (str === '[DONE]') break
      
      try {
        const json = JSON.parse(str)
        setTimeout(() => {
          if (json.choices[0].delta.reasoning_content) {
            currentSession.value.messages[messageIndex].thinking += json.choices[0].delta.reasoning_content
          }
          if (json.choices[0].delta.content) {
            currentSession.value.messages[messageIndex].content += json.choices[0].delta.content
          }
          scrollToBottom()
        }, 30 * i)
      } catch (error) {
        console.error('解析失败:', error)
      }
    }
  }).catch(error => {
    console.error('请求失败:', error)
    ElMessage.error('请求失败，请稍后重试')
    currentSession.value.messages.splice(-2)
  }).finally(() => {
    loading.value = false
  })
}

// 新增：测试 Ollama 连接并获取模型列表
async function loadOllamaModels() {
  try {
    const response = await fetch(`${ollamaBaseUrl.value}/api/tags`)
    if (response.ok) {
      const data = await response.json()
      availableModels.value = data.models || []
      ElMessage.success(`连接成功！找到 ${availableModels.value.length} 个本地模型`)
      return true
    } else {
      throw new Error('连接失败')
    }
  } catch (error) {
    ElMessage.error(`无法连接到 Ollama: ${error.message}`)
    return false
  }
}

// 新增：格式化文件大小
function formatSize(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 新增：保存设置
function saveSettings() {
  const settings = {
    useLocalModel: useLocalModel.value,
    currentModel: currentModel.value,
    remoteModel: remoteModel.value,
    apiKey: apiKey.value,
    ollamaBaseUrl: ollamaBaseUrl.value,
    temperature: temperature.value,
    maxTokens: maxTokens.value,
    useKnowledgeBase: useKnowledgeBase.value,
    knowledgeBaseUrl: knowledgeBaseUrl.value,
    maxContextLength: maxContextLength.value,
    searchTopK: searchTopK.value
  }
  localStorage.setItem('ai-settings', JSON.stringify(settings))
  showSettings.value = false
  ElMessage.success('设置已保存')
}

// 插入表情
function insertEmoji(emoji) {
  msg.value += emoji
  showEmojiPicker.value = false
  // 聚焦到输入框
  nextTick(() => {
    const textarea = document.querySelector('.message-input textarea')
    if (textarea) {
      textarea.focus()
    }
  })
}

// 处理文件上传
function handleFileUpload() {
  if (!fileInputRef.value) return
  fileInputRef.value.click()
}

// 文件选择处理
function onFileSelected(event) {
  const files = event.target.files
  if (!files || files.length === 0) return
  
  const file = files[0]
  
  // 检查文件大小 (限制10MB)
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过10MB')
    return
  }
  
  // 检查文件类型
  const allowedTypes = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'text/plain', 'text/markdown', 'application/pdf',
    'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
  ]
  
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error('不支持的文件类型。支持图片、文本、PDF、Word文档')
    return
  }
  
  // 处理图片文件
  if (file.type.startsWith('image/')) {
    const reader = new FileReader()
    reader.onload = (e) => {
      const imageUrl = e.target.result
      // 添加图片消息
      const imageMessage = {
        type: 'user',
        content: `[图片: ${file.name}]`,
        image: imageUrl,
        timestamp: Date.now()
      }
      currentSession.value.messages.push(imageMessage)
      scrollToBottom()
      
      ElMessage.success(`已上传图片: ${file.name}`)
    }
    reader.readAsDataURL(file)
  } 
  // 处理文本文件
  else if (file.type.startsWith('text/') || file.type === 'application/pdf') {
    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target.result
      // 将文件内容添加到输入框
      msg.value += `\n\n[文件: ${file.name}]\n${content.substring(0, 1000)}${content.length > 1000 ? '...' : ''}`
      
      ElMessage.success(`已读取文件: ${file.name}`)
    }
    reader.readAsText(file)
  } else {
    // 其他文件类型，显示文件信息
    const fileMessage = {
      type: 'user',
      content: `[文件: ${file.name}] (${(file.size / 1024 / 1024).toFixed(2)}MB)`,
      timestamp: Date.now()
    }
    currentSession.value.messages.push(fileMessage)
    scrollToBottom()
    
    ElMessage.success(`已上传文件: ${file.name}`)
  }
  
  // 清空文件选择
  event.target.value = ''
}

// 监听会话变化，自动保存
watch(chatSessions, (newValue) => {
  localStorage.setItem('deepseek-sessions', JSON.stringify(newValue))
}, { deep: true })

// 新增：常用表情数据
const commonEmojis = [
  '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇',
  '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚',
  '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩',
  '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣',
  '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬',
  '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓', '🤗',
  '🤔', '🤭', '🤫', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯',
  '😦', '😧', '😮', '😲', '🥱', '😴', '🤤', '😪', '😵', '🤐',
  '👍', '👎', '👌', '✌️', '🤞', '🤟', '🤘', '🤙', '👈', '👉',
  '👆', '👇', '☝️', '👋', '🤚', '🖐️', '✋', '🖖', '👏', '🙌',
  '🤝', '🙏', '✍️', '💪', '❤️', '🧡', '💛', '💚', '💙', '💜',
  '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖'
]
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

.session-content {
  flex: 1;
  min-width: 0; /* 允许文字截断 */
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

.ai-message, .ai-thinking {
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

.ai-message .message-avatar .el-avatar,
.ai-thinking .message-avatar .el-avatar {
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
  padding: 28px 32px; /* 增加内边距 */
}

.thinking-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  color: #8b5cf6;
  margin-bottom: 20px; /* 增加底部间距 */
  font-size: 16px; /* 增大字体 */
}

.thinking-text {
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', 'SimSun', sans-serif; /* 改为中文友好字体 */
  font-size: 15px; /* 增大字体 */
  color: #374151; /* 调整颜色更易读 */
  line-height: 1.8; /* 增加行高 */
  background: rgba(255, 255, 255, 0.8); /* 增加背景透明度 */
  padding: 20px; /* 增加内边距 */
  border-radius: 16px; /* 增大圆角 */
  border: 1px solid rgba(139, 92, 246, 0.25);
  font-weight: 400; /* 调整字重 */
  letter-spacing: 0.3px; /* 增加字间距 */
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

/* 输入框和思考过程样式优化 */
.chat-input {
  padding: 24px 32px 32px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
}

.input-wrapper {
  max-width: 1500px; /* 优化：减小最大宽度，避免输入区过宽 */
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
  width: 100%; /* 占满父容器宽度 */
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
  padding: 28px 32px 0 32px; /* 增加左右内边距 */
  font-size: 16px;
  line-height: 1.6;
  min-height: 80px; /* 增加最小高度 */
  max-height: 200px; /* 增加最大高度 */
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
  padding: 20px 32px 24px; /* 增加内边距 */
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  background: rgba(248, 250, 252, 0.5);
}

/* 表情选择器样式 */
.emoji-picker {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  width: 320px;
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(20px) saturate(180%);
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  margin-bottom: 16px;
  z-index: 1000;
  animation: emojiPickerSlideUp 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.emoji-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: rgba(248, 250, 252, 0.8);
  border-radius: 18px 18px 0 0;
}

.emoji-header span {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  padding: 4px !important;
  min-height: auto !important;
  color: #64748b !important;
  transition: all 0.2s ease !important;
}

.close-btn:hover {
  color: #ef4444 !important;
  transform: scale(1.1) !important;
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 8px;
  padding: 16px;
  max-height: 240px;
  overflow-y: auto;
}

.emoji-item {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  user-select: none;
}

.emoji-item:hover {
  background: rgba(102, 126, 234, 0.1);
  transform: scale(1.2);
  border-radius: 12px;
}

.emoji-item:active {
  transform: scale(1.1);
}

/* 美化输入工具按钮 */
.input-tools-left .el-button {
  border-radius: 12px;
  padding: 10px;
  border: none;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
  transition: all 0.3s ease;
  min-height: 36px;
  width: 36px;
}

.input-tools-left .el-button:hover {
  background: rgba(102, 126, 234, 0.2);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.input-tools-left .el-button.is-disabled {
  opacity: 0.5;
  transform: none;
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

/* 表情选择器动画 */
@keyframes emojiPickerSlideUp {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(20px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0) scale(1);
  }
}

/* 表情选择器滚动条美化 */
.emoji-grid::-webkit-scrollbar {
  width: 6px;
}

.emoji-grid::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 3px;
}

.emoji-grid::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
}

.emoji-grid::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

/* ...existing styles... */
</style>