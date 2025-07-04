import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { KnowledgeService } from '@/services/knowledgeService'

// 消息发送处理
export function useMessageSender(chatComposable, settings) {
  const { currentSession, loading, scrollToBottom } = chatComposable
  
  // 发送消息
  async function sendMsg(messageContent, isRegeneration = false) {
    if (!messageContent.trim()) {
      ElMessage.warning('请输入您的问题')
      return
    }

    // 如果不是重新生成，才添加新的用户消息
    if (!isRegeneration) {
      const userMessage = {
        type: 'user',
        content: messageContent,
        timestamp: Date.now()
      }
      currentSession.value.messages.push(userMessage)
      
      if (!currentSession.value.title) {
        currentSession.value.title = messageContent.length > 20 ? 
          messageContent.substring(0, 20) + '...' : messageContent
      }
    }
    
    const currentQuestion = messageContent
    loading.value = true
    scrollToBottom()

    // 创建知识库服务实例，从 computed ref 获取最新值
    const knowledgeService = new KnowledgeService(settings.value)

    // 准备接收AI响应的消息体
    const aiMessage = {
      type: 'assistant',
      content: '',
      thinking: '正在准备回答...',
      sources: [],
      timestamp: Date.now()
    }
    currentSession.value.messages.push(aiMessage)
    const messageIndex = currentSession.value.messages.length - 1

    try {
      // 统一调用新的流式生成接口
      await knowledgeService.generateAnswerStream(currentQuestion, currentSession.value.messages, (update) => {
        const msg = currentSession.value.messages[messageIndex]
        if (!msg) return

        if (update.type === 'thinking') {
          msg.thinking = update.content
        } else if (update.type === 'answer_start') {
          msg.thinking = `正在生成答案...`
          msg.method = update.method
        } else if (update.type === 'answer') {
          msg.content += update.content
        } else if (update.type === 'sources') {
          msg.sources = update.sources
        } else if (update.type === 'done') {
          msg.thinking = `问答完成 (${msg.method || 'unknown'})`
        } else if (update.type === 'error') {
          msg.content = update.content
          msg.thinking = '生成失败'
        }
        scrollToBottom()
      })
    } catch (error) {
      console.error('消息发送处理失败:', error)
      const msg = currentSession.value.messages[messageIndex]
      if (msg) {
        msg.content = `处理请求时发生错误: ${error.message}`
        msg.thinking = '服务异常'
      }
    }

    loading.value = false
  }

  return {
    sendMsg
  }
}
