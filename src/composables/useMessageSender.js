import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { AIService, buildMessageContext } from '@/services/aiService'

// 消息发送处理
export function useMessageSender(chatComposable, settings) {
  const { currentSession, loading, scrollToBottom } = chatComposable
  
  // 发送消息
  async function sendMsg(message) {
    if (!message.trim()) {
      ElMessage.warning('请输入您的问题')
      return
    }

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: Date.now()
    }
    
    currentSession.value.messages.push(userMessage)
    
    if (!currentSession.value.title) {
      currentSession.value.title = message.length > 20 ? 
        message.substring(0, 20) + '...' : message
    }
    
    const currentQuestion = message
    loading.value = true
    scrollToBottom()

    // 创建AI服务实例
    const aiService = new AIService(settings)

    // 知识库问答逻辑（支持流式输出）
    if (settings.useKnowledgeBase.value) {
      const result = await aiService.callKnowledgeBaseStream(
        currentQuestion, 
        currentSession.value.messages, 
        null, 
        scrollToBottom
      )

      if (result.success) {
        loading.value = false
        return
      }

      // 降级到普通API
      try {
        const fallbackResponse = await fetch(`${settings.knowledgeBaseUrl.value}/answer`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: currentQuestion,
            top_k: settings.searchTopK.value,
            max_length: settings.maxContextLength.value
          })
        })
        
        if (fallbackResponse.ok) {
          const data = await fallbackResponse.json()
          if (data && data.answer) {
            const fullAnswer = data.answer
            const sources = data.sources || []
            const method = data.method || 'unknown'
            
            const { thinking, answer } = aiService.parseContentWithThinkTag(fullAnswer)
            
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

    // 构建消息上下文
    const apiMessages = buildMessageContext(currentSession.value.messages, currentQuestion)

    const aiMessage = {
      type: 'assistant',
      content: '',
      thinking: '',
      sources: [],
      timestamp: Date.now()
    }
    currentSession.value.messages.push(aiMessage)
    const messageIndex = currentSession.value.messages.length - 1

    // 更新消息的辅助函数
    function updateMessage(index, updates, append = false) {
      if (append && updates.content) {
        currentSession.value.messages[index].content += updates.content
      } else {
        Object.assign(currentSession.value.messages[index], updates)
      }
    }

    // 根据配置选择本地或远程模型
    let result
    if (settings.useLocalModel.value) {
      result = await aiService.callOllamaAPI(apiMessages, messageIndex, updateMessage, scrollToBottom)
    } else {
      result = await aiService.callRemoteAPI(apiMessages, messageIndex, updateMessage, scrollToBottom)
    }

    if (!result.success) {
      currentSession.value.messages.splice(-1) // 删除失败的消息
    }

    loading.value = false
  }

  // 快速发送消息
  function sendQuickMessage(message = '你好，我是阑珊 AI，有什么可以帮助您？') {
    sendMsg(message)
  }

  return {
    sendMsg,
    sendQuickMessage
  }
}
