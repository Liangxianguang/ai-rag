import { ref, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 聊天状态管理
export function useChat(sendMsgCallback) { // 接收发送消息的回调
  const chatSessions = ref([])
  const currentSessionIndex = ref(0)
  const loading = ref(false)
  const messagesContainer = ref(null)

  // 计算当前会话
  const currentSession = computed(() => {
    if (chatSessions.value.length === 0) {
      return { messages: [], title: '', createdAt: Date.now() }
    }
    return chatSessions.value[currentSessionIndex.value] || { messages: [], title: '', createdAt: Date.now() }
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
      chatSessions.value.splice(index, 1)
      
      if (currentSessionIndex.value === index) {
        if (chatSessions.value.length > 0) {
          currentSessionIndex.value = 0
        } else {
          newChat()
        }
      } else if (currentSessionIndex.value > index) {
        currentSessionIndex.value--
      }
      
      ElMessage.success('对话已删除')
    }).catch(() => {})
  }

  // 新增：重新生成回答的函数
  function regenerateResponse(index) {
    if (loading.value) {
      ElMessage.warning('请等待当前回答生成完毕后再试。')
      return
    }
    
    // 确保我们操作的是一个AI消息，并且它前面有一个用户消息
    if (index > 0 && currentSession.value.messages[index].type === 'assistant') {
      const userMessage = currentSession.value.messages[index - 1]
      
      if (userMessage.type === 'user') {
        // 1. 获取用户的问题
        const questionToResend = userMessage.content
        
        // 2. 从消息列表中删除旧的AI回答
        currentSession.value.messages.splice(index, 1)
        
        // 3. 调用发送消息的逻辑，并标记为重新生成
        if (sendMsgCallback && typeof sendMsgCallback === 'function') {
          sendMsgCallback(questionToResend, true)
        } else {
          console.error("sendMsgCallback is not a function or not provided to useChat.")
        }
        
      } else {
        ElMessage.error('无法找到对应的用户问题来重新生成。')
      }
    } else {
      ElMessage.error('无法对该消息进行重新生成操作。')
    }
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

  // 初始化会话
  function initSessions() {
    const saved = localStorage.getItem('deepseek-sessions')
    if (saved) {
      chatSessions.value = JSON.parse(saved)
    }
    if (chatSessions.value.length === 0) {
      newChat()
    }
  }

  // 保存会话
  function saveSessions() {
    localStorage.setItem('deepseek-sessions', JSON.stringify(chatSessions.value))
  }

  return {
    chatSessions,
    currentSessionIndex,
    currentSession,
    loading,
    messagesContainer,
    newChat,
    switchSession,
    deleteSession,
    clearChat,
    regenerateResponse, // 暴露新函数
    scrollToBottom,
    formatTime,
    formatDate,
    initSessions,
    saveSessions
  }
}
