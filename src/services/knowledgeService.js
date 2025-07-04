import axios from 'axios'
import { ElMessage } from 'element-plus'

/**
 * 构建用于API请求的消息上下文
 * @param {Array} messages - 聊天历史消息
 * @param {String} currentQuestion - 当前用户问题
 * @returns {Array} - 格式化后的消息数组
 */
function buildMessageContext(messages, currentQuestion) {
  const systemPrompt = {
    role: "system",
    content: "您是一个专业的AI助手，请根据提供的信息回答用户问题。"
  }
  
  const N = 8 // 上下文历史对话数量
  // 过滤掉当前正在生成的消息和最后一条用户消息
  const history = messages.slice(0, -1).filter(m => m.type === 'user' || m.type === 'assistant')
  let context = []
  
  if (history.length > 0) {
    const grouped = []
    for (let i = 0; i < history.length; i += 2) {
      if (history[i].type === 'user' && history[i+1]?.type === 'assistant') {
        grouped.push(history.slice(i, i + 2))
      }
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


/**
 * 知识库与AI服务 - 处理知识库检索和LLM调用
 */
export class KnowledgeService {
  constructor(settings) {
    this.settings = settings
  }

  /**
   * 主入口：流式生成答案
   * 1. 检索知识库
   * 2. 如果知识库有内容，模拟流式返回
   * 3. 如果知识库无内容，根据设置调用Ollama或远程API进行流式生成
   */
  async generateAnswerStream(question, messages, onUpdate) {
    try {
      // 1. 检索知识库 (仅当启用时)
      if (this.settings.useKnowledgeBase.value) {
        onUpdate({ type: 'thinking', content: '正在搜索知识库...' })
        const knowledgeResult = await this.searchKnowledgeBase(question)
        
        if (knowledgeResult.success && knowledgeResult.documents.length > 0) {
          // 知识库找到内容
          onUpdate({ type: 'answer_start', method: 'knowledge_base' })
          onUpdate({ type: 'sources', sources: knowledgeResult.documents.map(d => d.title) })
          
          const formattedAnswer = this.formatKnowledgeAnswer(knowledgeResult.documents, question)
          
          // 模拟流式输出
          let currentIndex = 0
          const streamChunk = () => {
            if (currentIndex < formattedAnswer.length) {
              const chunk = formattedAnswer.slice(currentIndex, currentIndex + 15)
              onUpdate({ type: 'answer', content: chunk })
              currentIndex += 15
              setTimeout(streamChunk, 30)
            } else {
              onUpdate({ type: 'done' })
            }
          }
          streamChunk()
          return // 找到答案，流程结束
        }
      }

      // 2. 知识库未启用或未找到，调用LLM
      onUpdate({ type: 'thinking', content: '知识库未找到答案，正在调用语言模型...' })

      // 在调用 LLM 前构建完整的消息上下文
      const apiMessages = buildMessageContext(messages, question)

      if (this.settings.useLocalModel.value) {
        await this.callOllamaAPI(apiMessages, onUpdate)
      } else {
        await this.callRemoteAPI(apiMessages, onUpdate)
      }
    } catch (error) {
      console.error('生成答案时出错:', error)
      onUpdate({ type: 'error', content: `处理请求时发生错误: ${error.message}` })
    }
  }

  /**
   * 检索知识库
   */
  async searchKnowledgeBase(question) {
    try {
      const response = await axios.post(`${this.settings.knowledgeBaseUrl.value}/retrieve`, {
        query: question,
        collection_name: this.settings.knowledgeBaseCollection.value, // 传递集合名称
        top_k: this.settings.searchTopK.value, // 传递 top_k
        similarity_threshold: 0.65 // 直接使用 0.65 作为阈值
      })
      return { success: true, documents: response.data.documents || [] }
    } catch (error) {
      console.error('知识库检索失败:', error)
      // 检索失败不应中断流程，而是当作没有结果处理
      return { success: false, documents: [] }
    }
  }

  /**
   * 调用本地 Ollama API (流式)
   */
  async callOllamaAPI(apiMessages, onUpdate) {
    try {
      onUpdate({ type: 'answer_start', method: `ollama:${this.settings.currentModel.value}` })
      const response = await fetch(`${this.settings.ollamaBaseUrl.value}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: this.settings.currentModel.value,
          messages: apiMessages,
          stream: true,
          options: {
            temperature: this.settings.temperature.value,
            num_predict: this.settings.maxTokens.value
          }
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          onUpdate({ type: 'done' })
          break
        }

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.trim())
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line)
            if (data.message && data.message.content) {
              onUpdate({ type: 'answer', content: data.message.content })
            }
            if (data.done) {
              onUpdate({ type: 'done' })
              return
            }
          } catch (error) {
            console.error('解析Ollama响应失败:', error, '原始行:', line)
          }
        }
      }
    } catch (error) {
      console.error('Ollama API 调用失败:', error)
      ElMessage.error(`本地模型调用失败: ${error.message}`)
      onUpdate({ type: 'error', content: `本地模型调用失败: ${error.message}` })
    }
  }

  /**
   * 调用远程 API (流式)
   */
  async callRemoteAPI(apiMessages, onUpdate) {
    // 双重检查：确保在执行此函数时，确实是远程模式
    if (this.settings.useLocalModel.value) {
      console.warn('callRemoteAPI 被意外调用，但当前设置为使用本地模型。已中止。')
      onUpdate({ type: 'error', content: '配置不一致：尝试调用远程 API，但设置为本地模型。' })
      return
    }

    if (!this.settings.apiKey.value) {
      const errorMsg = '远程模型的 API Key 未设置。请在设置中填写。'
      console.error('远程 API 调用失败:', errorMsg)
      ElMessage.error(errorMsg)
      onUpdate({ type: 'error', content: errorMsg })
      return
    }

    try {
      onUpdate({ type: 'answer_start', method: `remote:${this.settings.remoteModel.value}` })
      
      const response = await fetch('https://api.siliconflow.cn/v1/chat/completions', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'text/event-stream', // 必须使用 event-stream 来处理流式响应
          'Authorization': `Bearer ${this.settings.apiKey.value}`
        },
        body: JSON.stringify({
          model: this.settings.remoteModel.value,
          messages: apiMessages,
          stream: true,
          max_tokens: this.settings.maxTokens.value,
          temperature: this.settings.temperature.value
        })
      })

      if (!response.ok) {
        // 如果是 401 错误，给出更具体的提示
        if (response.status === 401) {
            throw new Error(`HTTP 401 Unauthorized: API Key 无效或已过期。请检查您的设置。`)
        }
        throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      
      while (true) {
        const { done, value } = await reader.read()
        if (done) {
          onUpdate({ type: 'done' })
          break
        }
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n\n').filter(line => line.trim())

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const str = line.substring(6)
            if (str === '[DONE]') {
              onUpdate({ type: 'done' })
              return
            }
            try {
              const json = JSON.parse(str)
              if (json.choices[0].delta.content) {
                onUpdate({ type: 'answer', content: json.choices[0].delta.content })
              }
            } catch (error) {
              console.error('解析远程API响应失败:', error, '原始行:', line)
            }
          }
        }
      }
    } catch (error) {
      console.error('远程 API 调用失败:', error)
      ElMessage.error(`远程模型调用失败: ${error.message}`)
      onUpdate({ type: 'error', content: `远程模型调用失败: ${error.message}` })
    }
  }

  /**
   * 格式化知识库答案
   */
  formatKnowledgeAnswer(documents, question) {
    let answer = `【基于知识库】根据您的问题「${question}」，找到以下内容：\n\n`
    documents.forEach((doc, index) => {
      answer += `**${index + 1}. ${doc.title}**\n`
      answer += `> ${doc.content.replace(/\n/g, '\n> ')}\n\n`
      if (doc.score) {
        answer += `*(相似度: ${doc.score.toFixed(4)})*\n\n`
      }
    })
    return answer
  }
}
