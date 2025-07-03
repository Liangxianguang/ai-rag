import axios from 'axios'
import { ElMessage } from 'element-plus'

// AI 服务类
export class AIService {
  constructor(settings) {
    this.settings = settings
  }

  // 解析包含思考标签的内容
  parseContentWithThinkTag(raw) {
    if (!raw) return { thinking: '', answer: '' }
    
    const thinkMatch = raw.match(/<think>([\s\S]*?)<\/think>/)
    let thinking = ''
    let answer = raw
    
    if (thinkMatch) {
      thinking = thinkMatch[1].trim()
      answer = raw.replace(thinkMatch[0], '').trim()
    } else {
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

  // 调用知识库流式API
  async callKnowledgeBaseStream(question, messages, messageIndex, scrollToBottom) {
    try {
      const streamMessage = {
        type: 'assistant',
        content: '',
        thinking: '正在准备回答...',
        timestamp: Date.now()
      }
      messages.push(streamMessage)
      scrollToBottom()

      const response = await fetch(`${this.settings.knowledgeBaseUrl.value}/answer_stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: question,
          top_k: this.settings.searchTopK.value,
          max_length: this.settings.maxContextLength.value
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      const streamIndex = messages.length - 1

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              
              if (data.type === 'thinking') {
                messages[streamIndex].thinking = data.content
                scrollToBottom()
              } else if (data.type === 'answer_start') {
                messages[streamIndex].thinking = '正在生成答案...'
                messages[streamIndex].method = data.method
                scrollToBottom()
              } else if (data.type === 'answer') {
                messages[streamIndex].content += data.content
                scrollToBottom()
              } else if (data.type === 'sources') {
                messages[streamIndex].sources = data.sources.map(s => 
                  typeof s === 'object' ? s.title : s
                )
                scrollToBottom()
              } else if (data.type === 'done') {
                const method = messages[streamIndex].method || 'unknown'
                messages[streamIndex].thinking = `问答完成 (${method})`
                return { success: true }
              } else if (data.type === 'error') {
                messages[streamIndex].content = data.content
                messages[streamIndex].thinking = '发生错误'
                return { success: false }
              }
            } catch (e) {
              console.error('解析流式数据失败:', e)
            }
          }
        }
      }
      
      return { success: true }
    } catch (error) {
      console.error('流式知识库问答失败:', error)
      return { success: false, error }
    }
  }

  // 调用本地 Ollama API
  async callOllamaAPI(messages, messageIndex, updateMessage, scrollToBottom) {
    try {
      const response = await fetch(`${this.settings.ollamaBaseUrl.value}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.settings.currentModel.value,
          messages: messages,
          stream: true,
          options: {
            temperature: this.settings.temperature.value,
            num_predict: this.settings.maxTokens.value
          }
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let rawContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line)
            if (data.message && data.message.content) {
              rawContent += data.message.content
              
              const { thinking, answer } = this.parseContentWithThinkTag(rawContent)
              updateMessage(messageIndex, { thinking, content: answer })
              scrollToBottom()
            }
            
            if (data.done) {
              return { success: true }
            }
          } catch (error) {
            console.error('解析 Ollama 响应失败:', error)
          }
        }
      }
    } catch (error) {
      console.error('Ollama API 调用失败:', error)
      ElMessage.error(`本地模型调用失败: ${error.message}`)
      return { success: false, error }
    }
  }

  // 调用远程 API
  async callRemoteAPI(messages, messageIndex, updateMessage, scrollToBottom) {
    try {
      const data = {
        model: this.settings.remoteModel.value,
        messages: messages,
        stream: true,
        max_tokens: this.settings.maxTokens.value,
        temperature: this.settings.temperature.value
      }

      const response = await axios.request({
        url: 'https://api.siliconflow.cn/v1/chat/completions',
        method: 'post',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json', 
          'Authorization': `Bearer ${this.settings.apiKey.value}`
        },
        data: JSON.stringify(data)
      })

      const array = response.data.split('\n\n')
      
      for (let i in array) {
        if (array[i] === '') continue
        
        const str = array[i].substring(6)
        if (str === '[DONE]') break
        
        try {
          const json = JSON.parse(str)
          setTimeout(() => {
            if (json.choices[0].delta.reasoning_content) {
              updateMessage(messageIndex, { thinking: json.choices[0].delta.reasoning_content })
            }
            if (json.choices[0].delta.content) {
              updateMessage(messageIndex, { content: json.choices[0].delta.content }, true)
            }
            scrollToBottom()
          }, 30 * i)
        } catch (error) {
          console.error('解析失败:', error)
        }
      }

      return { success: true }
    } catch (error) {
      console.error('请求失败:', error)
      ElMessage.error('请求失败，请稍后重试')
      return { success: false, error }
    }
  }
}

// 构建消息上下文
export function buildMessageContext(messages, currentQuestion) {
  const systemPrompt = {
    role: "system",
    content: "您是一个专业的AI助手，请根据提供的信息回答用户问题。"
  }
  
  const N = 8 // 历史对话数量
  const history = messages.slice(0, -2).filter(m => m.type === 'user' || m.type === 'assistant')
  let context = []
  
  if (history.length > 0) {
    const grouped = []
    for (let i = 0; i < history.length; i += 2) {
      grouped.push(history.slice(i, i + 2))
    }
    const lastN = grouped.slice(-N)
    context = lastN.flat()
  }
  
  const apiMessages = [systemPrompt]
  context.forEach(message => {
    if (message.type === 'user') {
      apiMessages.push({ role: "user", content: message.content })
    }
    if (message.type === 'assistant') {
      apiMessages.push({ role: "assistant", content: message.content })
    }
  })
  apiMessages.push({ role: "user", content: currentQuestion })

  return apiMessages
}
