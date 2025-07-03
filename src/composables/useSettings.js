import { ref } from 'vue'
import { ElMessage } from 'element-plus'

// 设置管理
export function useSettings() {
  // 本地模型设置
  const useLocalModel = ref(true)
  const currentModel = ref('deepseek-r1:1.5b')
  const ollamaBaseUrl = ref('/api/ollama')
  const availableModels = ref([])
  
  // 远程模型设置
  const remoteModel = ref('deepseek-ai/DeepSeek-R1-0528-Qwen3-8B')
  const apiKey = ref('sk-dhyofqmlqevepadtfbjjmtvelluvgoqixawhgqcyhmiysdtl')
  
  // 通用设置
  const temperature = ref(0.7)
  const maxTokens = ref(2000)
  
  // 知识库设置
  const useKnowledgeBase = ref(true)
  const knowledgeBaseUrl = ref('/api/knowledge')
  const maxContextLength = ref(3000)
  const searchTopK = ref(5)

  // 加载设置
  function loadSettings() {
    const savedSettings = localStorage.getItem('ai-settings')
    if (savedSettings) {
      const settings = JSON.parse(savedSettings)
      useLocalModel.value = settings.useLocalModel ?? true
      currentModel.value = settings.currentModel || 'deepseek-r1:1.5b'
      remoteModel.value = settings.remoteModel || 'deepseek-ai/DeepSeek-R1-0528-Qwen3-8B'
      apiKey.value = settings.apiKey || apiKey.value
      ollamaBaseUrl.value = settings.ollamaBaseUrl || '/api/ollama'
      temperature.value = settings.temperature ?? 0.7
      maxTokens.value = settings.maxTokens ?? 2000
      useKnowledgeBase.value = settings.useKnowledgeBase ?? true
      knowledgeBaseUrl.value = settings.knowledgeBaseUrl || '/api/knowledge'
      maxContextLength.value = settings.maxContextLength ?? 3000
      searchTopK.value = settings.searchTopK ?? 5
    }
  }

  // 保存设置
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
    ElMessage.success('设置已保存')
  }

  // 测试 Ollama 连接并获取模型列表
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

  return {
    useLocalModel,
    currentModel,
    ollamaBaseUrl,
    availableModels,
    remoteModel,
    apiKey,
    temperature,
    maxTokens,
    useKnowledgeBase,
    knowledgeBaseUrl,
    maxContextLength,
    searchTopK,
    loadSettings,
    saveSettings,
    loadOllamaModels
  }
}
